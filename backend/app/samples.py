"""Independently authored examples; never derived from patient records."""

from copy import deepcopy

BASE = {
    "source": "synthetic",
    "age": 62,
    "cutoff_hour": 8,
    "reference_creatinine_mg_dl": 1,
    "reference_measured_hour": -12,
    "reference_available_hour": -11,
    "reference_confirmed": True,
    "eligibility_confirmed": True,
    "protocol_version": "example-only-v1",
    "observations": [
        {
            "concept": "creatinine",
            "value": 1.3,
            "unit": "mg/dL",
            "measured_hour": 2,
            "available_hour": 3,
        },
        {
            "concept": "creatinine",
            "value": 1.6,
            "unit": "mg/dL",
            "measured_hour": 7,
            "available_hour": 8,
        },
    ]
    + [
        {"concept": concept, "value": value, "unit": unit, "measured_hour": 1, "available_hour": 1}
        for concept, value, unit in [
            ("heart_rate", 94, "bpm"),
            ("map", 74, "mmHg"),
            ("respiratory_rate", 21, "/min"),
            ("spo2", 96, "%"),
            ("temperature", 37.2, "C"),
            ("bun", 31, "mg/dL"),
            ("potassium", 4.6, "mmol/L"),
        ]
    ],
}


def catalog():
    cases = {}
    for name, values in {
        "stable-no-aki": [1.0, 1.1],
        "stage1-rising": [1.3, 1.6],
        "stage1-falling": [1.8, 1.5],
        "stage2-observed": [1.5, 2.1],
        "stage3-observed": [1.5, 3.1],
    }.items():
        case = deepcopy(BASE)
        for o, value in zip(case["observations"][:2], values, strict=True):
            o["value"] = value
        cases[name] = case
    case = deepcopy(BASE)
    case["observations"] = case["observations"][:2]
    cases["missing-vitals"] = case
    case = deepcopy(BASE)
    case["observations"][1]["available_hour"] = 12
    cases["delayed-result"] = case
    case = deepcopy(BASE)
    for o in case["observations"][:2]:
        o["value"] *= 88.4
        o["unit"] = "umol/L"
    cases["micromol-units"] = case
    case = deepcopy(BASE)
    case["reference_measured_hour"] = -168
    case["reference_available_hour"] = -167
    cases["expired-reference"] = case
    return cases


CASES = catalog()
