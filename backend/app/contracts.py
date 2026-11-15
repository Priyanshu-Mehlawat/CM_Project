"""Public, versioned demo response contracts. No clinical calculations."""

from typing import Literal

from pydantic import BaseModel, ConfigDict


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: Literal["v1"] = "v1"


class Health(Contract):
    service_alive: bool = True
    model_available: Literal[False] = False
    mode: Literal["synthetic_demo"] = "synthetic_demo"


class SystemInfo(Contract):
    name: str = "RENAL-GUARD"
    version: str = "0.2.0"
    mode: Literal["synthetic_demo"] = "synthetic_demo"
    research_mode_enabled: Literal[False] = False
    model_available: Literal[False] = False
    model_version: None = None
    evaluation_state: Literal["not_yet_evaluated"] = "not_yet_evaluated"
    protocol_state: Literal["pending_G1"] = "pending_G1"


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(Contract):
    error: ErrorDetail


class ClinicalAssessment(BaseModel):
    stage: int | None
    observed_aki: bool
    reference_sample_id: str
    known_sample_count: int
    latest_creatinine_mg_dl: float | None
    latest_measured_hour: float | None
    basis: str


class TimelinePoint(BaseModel):
    sample_id: str
    measured_hour: float
    available_hour: float
    creatinine_mg_dl: float


class Outcome(BaseModel):
    state: Literal["progressed", "non_progressed", "unknown"]
    reason: str
    event_hour: float | None
    followup_note: str


class Prediction(BaseModel):
    state: Literal["unavailable"] = "unavailable"
    probability: None = None
    reason: str = "validated_progression_model_unavailable"
    model_version: None = None


class EpisodeView(Contract):
    id: str
    name: str
    description: str
    source: Literal["independently_authored_synthetic"]
    cutoff_hour: float
    index_hour: float | None
    horizon_hours: Literal[48]
    protocol_version: str
    assessment: ClinicalAssessment
    timeline: list[TimelinePoint]
    outcome: Outcome
    prediction: Prediction


class EpisodeSummary(BaseModel):
    id: str
    name: str
    description: str


class EpisodeList(Contract):
    episodes: list[EpisodeSummary]
    source: Literal["independently_authored_synthetic"] = "independently_authored_synthetic"


class PredictionRequest(Contract):
    episode_id: str
    horizon_hours: Literal[48] = 48


class ResearchStatus(Contract):
    state: Literal["not_yet_evaluated"] = "not_yet_evaluated"
    metrics: None = None
    protocol_state: Literal["pending_G1"] = "pending_G1"
    reason: str = "No approved clinical cohort or validated progression model is available."
