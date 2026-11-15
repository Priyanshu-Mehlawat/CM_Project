"""Versioned, index-only features shared by offline fitting and API inference."""

FEATURE_VERSION = "progression-v1"
FEATURES = (
    "age",
    "reference_creatinine",
    "creatinine",
    "creatinine_ratio",
    "creatinine_delta",
    "heart_rate",
    "map",
    "respiratory_rate",
    "spo2",
    "temperature",
    "bun",
    "potassium",
)
# Plausibility bounds, NOT outcome/alert thresholds.
BOUNDS = {
    "age": (18, 120),
    "reference_creatinine": (0.1, 30),
    "creatinine": (0.1, 30),
    "creatinine_ratio": (0, 300),
    "creatinine_delta": (-30, 30),
    "heart_rate": (15, 300),
    "map": (15, 200),
    "respiratory_rate": (1, 100),
    "spo2": (20, 100),
    "temperature": (25, 45),
    "bun": (1, 300),
    "potassium": (1, 12),
}


def feature_vector(age, reference, current, observations):
    values = {
        "age": age,
        "reference_creatinine": reference,
        "creatinine": current,
        "creatinine_ratio": current / reference,
        "creatinine_delta": current - reference,
    }
    for name in FEATURES[5:]:
        candidates = [o for o in observations if o.concept == name]
        values[name] = (
            max(candidates, key=lambda o: (o.measured_hour, o.available_hour)).value
            if candidates
            else None
        )
    return values
