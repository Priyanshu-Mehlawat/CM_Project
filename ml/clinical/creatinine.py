"""Creatinine-only arithmetic with an explicit reference, for synthetic validation.

No baseline selection, cohort extraction, urine/KRT labeling or training is done.
A production protocol must resolve those choices before use on research data.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Observation:
    sample_id: str
    measured_hour: float
    available_hour: float
    creatinine_mg_dl: float

    def __post_init__(self):
        values = (self.measured_hour, self.available_hour, self.creatinine_mg_dl)
        if not self.sample_id or not all(isfinite(v) for v in values):
            raise ValueError("Finite observation fields and sample identity required")
        if self.available_hour < self.measured_hour or not 0.1 <= self.creatinine_mg_dl <= 30:
            raise ValueError("Invalid availability order or creatinine range")


def available_samples(observations: list[Observation], cutoff: float) -> list[Observation]:
    if not isfinite(cutoff):
        raise ValueError("Finite cutoff required")
    versions = {}
    samples = {}
    for row in observations:
        if row.sample_id in samples and samples[row.sample_id] != row.measured_hour:
            raise ValueError("A sample cannot change collection time")
        samples[row.sample_id] = row.measured_hour
        key = (row.sample_id, row.available_hour)
        if key in versions and versions[key] != row:
            raise ValueError("Conflicting simultaneous sample revisions")
        versions[key] = row
    latest = {}
    for row in sorted(observations, key=lambda r: (r.available_hour, r.sample_id)):
        if row.measured_hour <= cutoff and row.available_hour <= cutoff:
            latest[row.sample_id] = row
    return sorted(latest.values(), key=lambda r: (r.measured_hour, r.sample_id))


def stage_at_sample(row: Observation, known: list[Observation], reference_id: str) -> int | None:
    """KDIGO 2012 serum-creatinine branches, with a supplied earlier reference.

    Temporal/reference eligibility is explicit. Values are mg/dL. Stage 3's 4.0
    branch requires AKI first; a qualifying ratio can establish that AKI.
    """
    reference = next((r for r in known if r.sample_id == reference_id), None)
    if reference is None or not 0 < row.measured_hour - reference.measured_hour <= 168:
        return None
    prior48 = [r.creatinine_mg_dl for r in known if 0 < row.measured_hour - r.measured_hour <= 48]
    ratio = row.creatinine_mg_dl / reference.creatinine_mg_dl
    rise = row.creatinine_mg_dl - min(prior48) if prior48 else None
    aki = ratio >= 1.5 - 1e-9 or (rise is not None and rise >= 0.3 - 1e-9)
    if not aki:
        return 0
    if ratio >= 3 - 1e-9 or row.creatinine_mg_dl >= 4:
        return 3
    return 2 if ratio >= 2 - 1e-9 else 1


def assessment(observations: list[Observation], cutoff: float, reference_id: str) -> dict:
    known = available_samples(observations, cutoff)
    latest = known[-1] if known else None
    stages = [(r, stage_at_sample(r, known, reference_id)) for r in known]
    events = [(r, stage) for r, stage in stages if stage]
    return {
        "stage": stage_at_sample(latest, known, reference_id) if latest else None,
        "observed_aki": bool(events),
        "reference_sample_id": reference_id,
        "known_sample_count": len(known),
        "latest_creatinine_mg_dl": latest.creatinine_mg_dl if latest else None,
        "latest_measured_hour": latest.measured_hour if latest else None,
        "basis": "KDIGO_2012_creatinine_only_explicit_synthetic_reference",
    }
