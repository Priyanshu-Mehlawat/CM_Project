"""Strict, hash-pinned logistic bundles. No artifact directory scanning."""

import hashlib
import json
import math
import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ml.features.patient import FEATURE_VERSION, FEATURES


class Bundle(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)
    bundle_version: Literal["1"] = "1"
    model_version: str = Field(min_length=1, max_length=100)
    feature_version: Literal["progression-v1"] = FEATURE_VERSION
    target: Literal["stage1_to_stage2_or_3_48h"] = "stage1_to_stage2_or_3_48h"
    protocol_version: str = Field(min_length=1, max_length=100)
    data_version: str = Field(min_length=1, max_length=100)
    trained_at: str
    training_source: Literal["authorized_research", "synthetic_test"]
    features: list[str]
    medians: list[float]
    means: list[float]
    scales: list[float]
    coefficients: list[float]
    intercept: float
    calibration: Literal["not_calibrated"] = "not_calibrated"
    missing_policy: Literal["median_plus_indicator"] = "median_plus_indicator"
    training_config: dict[str, str | float | int] = Field(default_factory=dict)
    metrics: dict[str, dict[str, float]]

    @model_validator(mode="after")
    def dimensions(self):
        n = len(FEATURES)
        if self.features != list(FEATURES):
            raise ValueError("Feature order mismatch")
        if any(len(x) != n for x in (self.medians, self.means, self.scales)):
            raise ValueError("Preprocessing shape mismatch")
        if len(self.coefficients) != n * 2 or any(s <= 0 for s in self.scales):
            raise ValueError("Model shape mismatch")
        return self


def transform(bundle, values):
    x, missing = [], []
    for i, name in enumerate(FEATURES):
        value = values[name]
        missing.append(float(value is None))
        x.append(
            ((bundle.medians[i] if value is None else value) - bundle.means[i]) / bundle.scales[i]
        )
    return x + missing


def infer(bundle, values):
    x = transform(bundle, values)
    terms = [a * b for a, b in zip(x, bundle.coefficients, strict=True)]
    logit = bundle.intercept + sum(terms)
    probability = 1 / (1 + math.exp(-max(-700, min(700, logit))))
    contributions = sorted(
        zip(list(FEATURES) + [f"{f}_missing" for f in FEATURES], terms, strict=True),
        key=lambda pair: abs(pair[1]),
        reverse=True,
    )
    return probability, [{"feature": k, "log_odds_contribution": v} for k, v in contributions]


def configured_bundle():
    path = os.environ.get("RENAL_GUARD_MODEL_PATH")
    digest = os.environ.get("RENAL_GUARD_MODEL_SHA256")
    if not path and not digest:
        return None
    if not path or not digest or len(digest) != 64:
        raise ValueError("Both model path and SHA256 required")
    file = Path(path)
    if file.is_symlink() or file.stat().st_size > 100_000:
        raise ValueError("Invalid bundle file")
    raw = file.read_bytes()
    if hashlib.sha256(raw).hexdigest() != digest.lower():
        raise ValueError("Bundle digest mismatch")
    bundle = Bundle.model_validate(json.loads(raw))
    if bundle.training_source != "authorized_research":
        raise ValueError("Synthetic test model cannot serve patient forecasts")
    return bundle
