"""Local research API: synthetic replay, transient assessments and trusted inference."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from backend.app.contracts import (
    EpisodeList,
    EpisodeSummary,
    EpisodeView,
    ErrorDetail,
    ErrorResponse,
    Health,
    ModelStatus,
    PatientAssessment,
    Prediction,
    PredictionRequest,
    ResearchStatus,
    SystemInfo,
)
from backend.app.episodes import EPISODES, episode_view, find_episode
from backend.app.patient import ImportInput, PatientInput, assess, parse_import
from ml.inference.bundle import configured_bundle


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("RENAL_GUARD_MODE", "demo") != "demo":
        raise RuntimeError(
            "Only synthetic demo mode is supported; research requires approved G1 decisions"
        )
    try:
        app.state.bundle = configured_bundle()
    except (OSError, ValueError):
        raise RuntimeError("Configured progression bundle failed integrity/schema checks") from None
    yield


app = FastAPI(title="RENAL-GUARD · Research Prototype", version="0.3.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Accept", "Content-Type"],
)


def error(status: int, code: str, message: str) -> JSONResponse:
    body = ErrorResponse(error=ErrorDetail(code=code, message=message))
    return JSONResponse(status_code=status, content=body.model_dump())


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    codes = {404: "not_found", 405: "method_not_allowed"}
    return error(exc.status_code, codes.get(exc.status_code, "http_error"), "Request not supported")


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    # Never echo submitted input, paths or validation values.
    return error(422, "invalid_request", "Request does not match the API contract")


@app.exception_handler(Exception)
async def internal_error(request: Request, exc: Exception):
    return error(500, "internal_error", "An internal error occurred")


@app.get("/api/v1/health", response_model=Health)
def health() -> Health:
    return Health(model_available=getattr(app.state, "bundle", None) is not None)


@app.get("/api/v1/system/info", response_model=SystemInfo)
def system_info() -> SystemInfo:
    bundle = getattr(app.state, "bundle", None)
    return SystemInfo(
        model_available=bundle is not None, model_version=bundle.model_version if bundle else None
    )


@app.get("/api/v1/episodes", response_model=EpisodeList)
def episodes() -> EpisodeList:
    return EpisodeList(
        episodes=[EpisodeSummary(id=e.id, name=e.name, description=e.description) for e in EPISODES]
    )


@app.get("/api/v1/episodes/{episode_id}", response_model=EpisodeView)
def episode(episode_id: str, cutoff_hour: float = Query(default=14, ge=0, le=168)):
    item = find_episode(episode_id)
    if item is None:
        raise HTTPException(404)
    return episode_view(item, cutoff_hour)


@app.post("/api/v1/predictions", response_model=Prediction)
def prediction(request: PredictionRequest) -> Prediction:
    if find_episode(request.episode_id) is None:
        raise HTTPException(404)
    return Prediction()


@app.get("/api/v1/research/status", response_model=ResearchStatus)
def research_status() -> ResearchStatus:
    return ResearchStatus()


@app.middleware("http")
async def local_upload_boundary(request: Request, call_next):
    if request.url.path.startswith("/api/v1/assessments"):
        origin = request.headers.get("origin")
        if request.client and request.client.host not in ("127.0.0.1", "::1", "testclient"):
            return error(403, "local_only", "Patient import is restricted to this device")
        if origin and origin not in (
            "http://127.0.0.1:5173",
            "http://localhost:5173",
            "http://127.0.0.1:8000",
            "http://localhost:8000",
        ):
            return error(403, "origin_denied", "Origin is not allowed")
        if request.method == "POST":
            size = 0
            chunks = []
            async for chunk in request.stream():
                size += len(chunk)
                if size > 128_000:
                    return error(413, "upload_too_large", "Maximum request size is 128 KB")
                chunks.append(chunk)
            request._body = b"".join(chunks)
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response


@app.get("/api/v1/model/status", response_model=ModelStatus)
def model_status():
    bundle = getattr(app.state, "bundle", None)
    return ModelStatus(
        state="ready" if bundle else "not_configured",
        model_version=bundle.model_version if bundle else None,
        protocol_version=bundle.protocol_version if bundle else None,
        calibration=bundle.calibration if bundle else None,
        metrics=bundle.metrics if bundle else None,
        patient_import_enabled=os.environ.get("RENAL_GUARD_ENABLE_PATIENT_IMPORT") == "1",
    )


def evaluate_patient(patient):
    if (
        patient.source == "authorized_research"
        and os.environ.get("RENAL_GUARD_ENABLE_PATIENT_IMPORT") != "1"
    ):
        return error(
            403,
            "patient_import_disabled",
            "Enable local patient import only in your authorized isolated environment",
        )
    return assess(patient, getattr(app.state, "bundle", None))


@app.post("/api/v1/assessments", response_model=PatientAssessment)
def patient_assessment(patient: PatientInput):
    return evaluate_patient(patient)


@app.post("/api/v1/assessments/import", response_model=PatientAssessment)
def import_assessment(request: ImportInput):
    try:
        patient = parse_import(request)
    except (ValueError, ValidationError, TypeError, KeyError):
        return error(
            422, "invalid_upload", "Upload does not match the documented CSV/JSON template"
        )
    return evaluate_patient(patient)
