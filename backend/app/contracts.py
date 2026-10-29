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
    version: str = "0.1.0"
    mode: Literal["synthetic_demo"] = "synthetic_demo"
    research_mode_enabled: Literal[False] = False
    model_available: Literal[False] = False
    model_version: None = None
    evaluation_state: Literal["not_yet_evaluated"] = "not_yet_evaluated"
    protocol_state: Literal["pending_G1"] = "pending_G1"


class DemoCase(Contract):
    id: str
    name: str
    source: Literal["independently_authored_synthetic"] = "independently_authored_synthetic"
    description: str
    model_state: Literal["unavailable"] = "unavailable"
    probability: None = None
    clinical_stage: None = None


class DemoCases(Contract):
    cases: list[DemoCase]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(Contract):
    error: ErrorDetail
