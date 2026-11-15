"""Transient local assessment. Never persists uploads or invents future outcomes."""

import csv
import io
import json
import math
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ml.clinical.creatinine import Observation, available_samples, stage_at_sample
from ml.features.patient import BOUNDS, FEATURE_VERSION, FEATURES, feature_vector
from ml.inference.bundle import infer


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Measurement(InputModel):
    concept: Literal[
        "creatinine",
        "heart_rate",
        "map",
        "respiratory_rate",
        "spo2",
        "temperature",
        "bun",
        "potassium",
    ]
    value: float
    unit: str
    measured_hour: float = Field(ge=-168, le=168)
    available_hour: float = Field(ge=-168, le=336)

    @model_validator(mode="after")
    def validate_measurement(self):
        units = {
            "creatinine": ("mg/dL", "umol/L"),
            "heart_rate": ("bpm",),
            "map": ("mmHg",),
            "respiratory_rate": ("/min",),
            "spo2": ("%",),
            "temperature": ("C",),
            "bun": ("mg/dL",),
            "potassium": ("mmol/L",),
        }
        if self.unit not in units[self.concept] or self.available_hour < self.measured_hour:
            raise ValueError("Invalid unit or result availability")
        value = self.value / 88.4 if self.unit == "umol/L" else self.value
        low, high = BOUNDS[self.concept]
        if not math.isfinite(value) or not low <= value <= high:
            raise ValueError("Measurement outside supported plausibility range")
        return self

    @property
    def normalized(self):
        return self.value / 88.4 if self.unit == "umol/L" else self.value


class PatientInput(InputModel):
    source: Literal["synthetic", "authorized_research"]
    age: float = Field(ge=18, le=120)
    cutoff_hour: float = Field(ge=0, le=168)
    reference_creatinine_mg_dl: float = Field(ge=0.1, le=30)
    reference_measured_hour: float = Field(ge=-168, lt=168)
    reference_available_hour: float = Field(ge=-168, le=168)
    reference_confirmed: Literal[True]
    eligibility_confirmed: Literal[True]
    protocol_version: str = Field(pattern=r"^[A-Za-z0-9._-]{1,100}$")
    observations: list[Measurement] = Field(min_length=1, max_length=1000)

    @model_validator(mode="after")
    def timing(self):
        if not (self.reference_measured_hour <= self.reference_available_hour <= self.cutoff_hour):
            raise ValueError("Reference must be available by assessment")
        keys = [(o.concept, o.measured_hour) for o in self.observations]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate measurements; resolve corrections before upload")
        return self


class ImportInput(InputModel):
    format: Literal["json", "csv"]
    content: str = Field(max_length=100_000)


def parse_import(request):
    if request.format == "json":
        return PatientInput.model_validate(json.loads(request.content))
    rows = list(csv.DictReader(io.StringIO(request.content)))
    if not rows or len(rows) > 1000:
        raise ValueError("Expected 1–1000 measurement rows")
    meta = [name for name in PatientInput.model_fields if name != "observations"]
    measurement = list(Measurement.model_fields)
    if set(rows[0]) != set(meta + measurement):
        raise ValueError("CSV columns do not match template")
    if any(any(row[name] != rows[0][name] for name in meta) for row in rows):
        raise ValueError("One patient and consistent metadata required")
    payload = {k: rows[0][k] for k in meta}
    for name in ("reference_confirmed", "eligibility_confirmed"):
        if payload[name].lower() != "true":
            raise ValueError("Reference and eligibility confirmation required")
        payload[name] = True
    payload["observations"] = [{k: row[k] for k in measurement} for row in rows]
    return PatientInput.model_validate(payload)


def assess(patient, bundle=None):
    reference = Observation(
        "reference",
        patient.reference_measured_hour,
        patient.reference_available_hour,
        patient.reference_creatinine_mg_dl,
    )
    labs = [reference] + [
        Observation(str(i), o.measured_hour, o.available_hour, o.normalized)
        for i, o in enumerate(patient.observations)
        if o.concept == "creatinine"
    ]
    known = available_samples(labs, patient.cutoff_hour)
    latest = known[-1]
    stage = stage_at_sample(latest, known, "reference")
    index = None
    prior_severe = False
    # Index is determined by information available at each result time, not future labs.
    for hour in sorted(
        {o.available_hour for o in labs if 0 <= o.available_hour <= patient.cutoff_hour}
    ):
        visible = available_samples(labs, hour)
        stages = [stage_at_sample(o, visible, "reference") for o in visible]
        if any(s in (2, 3) for s in stages):
            prior_severe = True
        if not prior_severe and any(s == 1 for s in stages):
            index = hour
            break
    previous = known[-2] if len(known) > 1 else None
    delta = latest.creatinine_mg_dl - previous.creatinine_mg_dl if previous else None
    trend = (
        "insufficient_measurements"
        if delta is None
        else ("rising" if delta > 1e-9 else "falling" if delta < -1e-9 else "unchanged")
    )
    warnings = ["Creatinine-only assessment; urine-output and dialysis criteria are not evaluated."]
    hidden = sum(
        o.measured_hour > patient.cutoff_hour or o.available_hour > patient.cutoff_hour
        for o in patient.observations
    )
    if hidden:
        warnings.append(f"{hidden} measurements after the cutoff were excluded.")
    if patient.cutoff_hour - latest.measured_hour > 24:
        warnings.append("Latest creatinine is over 24 hours old; current status may differ.")
    values = None
    if index is not None:
        at_index = available_samples(labs, index)[-1]
        vitals = [
            o
            for o in patient.observations
            if o.concept != "creatinine"
            and o.available_hour <= index
            and index - 24 <= o.measured_hour <= index
        ]
        values = feature_vector(
            patient.age, reference.creatinine_mg_dl, at_index.creatinine_mg_dl, vitals
        )
    prediction = {
        "state": "withheld",
        "probability": None,
        "model_version": None,
        "reason": "No eligible Stage 1 index in the supplied history.",
        "contributions": [],
        "calibration": "not_calibrated",
    }
    if values is not None:
        prediction["reason"] = (
            "Install the privately trained progression bundle to enable forecasting."
        )
        prediction["state"] = "model_required"
        if bundle is not None:
            prediction["model_version"] = bundle.model_version
            if bundle.protocol_version != patient.protocol_version:
                prediction.update(
                    state="withheld", reason="Patient and model protocol versions differ."
                )
            elif any(
                stage_at_sample(o, known, "reference") in (2, 3)
                for o in known
                if o.measured_hour > index
            ):
                prediction.update(
                    state="withheld", reason="Progression is already observed in history."
                )
            elif patient.cutoff_hour > index + 48:
                prediction.update(
                    state="withheld", reason="The index-time forecast window has ended."
                )
            elif stage != 1:
                prediction.update(
                    state="withheld", reason="Current stage is outside Stage 1 model use."
                )
            elif sum(values[k] is None for k in FEATURES) > 4:
                prediction.update(
                    state="withheld", reason="More than four model inputs are missing."
                )
            else:
                probability, contributions = infer(bundle, values)
                prediction.update(
                    state="available",
                    probability=probability,
                    contributions=contributions,
                    reason="48h forecast frozen at first eligible Stage 1 index; research use.",
                )
    return {
        "schema_version": "v1",
        "source": patient.source,
        "stage": stage,
        "trend": trend,
        "latest_creatinine_mg_dl": latest.creatinine_mg_dl,
        "change_mg_dl": delta,
        "index_hour": index,
        "horizon_hours": 48,
        "feature_version": FEATURE_VERSION,
        "features": values,
        "missing_features": [k for k, v in (values or {}).items() if v is None],
        "warnings": warnings,
        "prediction": prediction,
        "timeline": [
            {"measured_hour": o.measured_hour, "creatinine_mg_dl": o.creatinine_mg_dl}
            for o in known
        ],
    }
