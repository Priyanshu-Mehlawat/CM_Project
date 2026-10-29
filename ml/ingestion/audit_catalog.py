"""Public schema *candidates* for offline inventory, not validated mappings.

Only names listed here can appear in an audit report. Every column may be absent in
an installed version. A source name in this file is not evidence of clinical meaning.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class TableSpec:
    columns: tuple[str, ...]
    person_key: str | None = None
    stay_key: str | None = None
    hospital_key: str | None = None
    measurement_time: str | None = None
    availability_time: str | None = None
    concept: str | None = None
    value: str | None = None
    unit: str | None = None


CATALOG: dict[str, dict[str, TableSpec]] = {
    "mimic": {
        "patients": TableSpec(("subject_id", "anchor_age", "anchor_year", "gender"), "subject_id"),
        "admissions": TableSpec(
            ("subject_id", "hadm_id", "admittime", "dischtime", "deathtime"),
            "subject_id",
        ),
        "icustays": TableSpec(
            ("subject_id", "hadm_id", "stay_id", "intime", "outtime"),
            "subject_id",
            "stay_id",
        ),
        "labevents": TableSpec(
            ("subject_id", "hadm_id", "itemid", "charttime", "storetime", "valuenum", "valueuom"),
            "subject_id",
            None,
            None,
            "charttime",
            "storetime",
            "itemid",
            "valuenum",
            "valueuom",
        ),
        "d_labitems": TableSpec(("itemid", "label", "fluid", "category"), concept="label"),
        "chartevents": TableSpec(
            (
                "subject_id",
                "hadm_id",
                "stay_id",
                "itemid",
                "charttime",
                "storetime",
                "valuenum",
                "valueuom",
            ),
            "subject_id",
            "stay_id",
            None,
            "charttime",
            "storetime",
            "itemid",
            "valuenum",
            "valueuom",
        ),
        "d_items": TableSpec(("itemid", "label", "category", "unitname"), concept="label"),
    },
    "eicu": {
        "patient": TableSpec(
            (
                "uniquepid",
                "patientunitstayid",
                "patienthealthsystemstayid",
                "hospitalid",
                "age",
                "gender",
                "unitdischargeoffset",
                "hospitaldischargeoffset",
            ),
            "uniquepid",
            "patientunitstayid",
            "hospitalid",
        ),
        "hospital": TableSpec(
            ("hospitalid", "region", "teachingstatus", "numbedscategory"), hospital_key="hospitalid"
        ),
        "lab": TableSpec(
            (
                "patientunitstayid",
                "labresultoffset",
                "labresultrevisedoffset",
                "labname",
                "labresult",
                "labmeasurenamesystem",
            ),
            None,
            "patientunitstayid",
            None,
            "labresultoffset",
            "labresultrevisedoffset",
            "labname",
            "labresult",
            "labmeasurenamesystem",
        ),
        "vitalPeriodic": TableSpec(
            (
                "patientunitstayid",
                "observationoffset",
                "heartrate",
                "systemicsystolic",
                "systemicdiastolic",
                "systemicmean",
                "respiration",
                "temperature",
                "sao2",
            ),
            None,
            "patientunitstayid",
            None,
            "observationoffset",
        ),
        "vitalAperiodic": TableSpec(
            (
                "patientunitstayid",
                "observationoffset",
                "noninvasivesystolic",
                "noninvasivediastolic",
                "noninvasivemean",
            ),
            None,
            "patientunitstayid",
            None,
            "observationoffset",
        ),
        # Optional signal inventory only; presence does not establish dialysis status.
        "treatment": TableSpec(
            ("patientunitstayid", "treatmentoffset", "treatmentstring"),
            stay_key="patientunitstayid",
            measurement_time="treatmentoffset",
            concept="treatmentstring",
        ),
    },
}

REQUIRED_TABLES = {
    "mimic": ("patients", "admissions", "icustays", "labevents", "d_labitems"),
    "eicu": ("patient", "hospital", "lab"),
}

# Candidate search terms only. Clinical code/item mapping needs human verification.
CREATININE_TERM = "creatinine"
DIALYSIS_TERMS = ("dialysis", "renal replacement", "hemofiltration")
