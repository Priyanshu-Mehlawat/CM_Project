"""Local synthetic demo. No data connectors, artifact loaders or research endpoints."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from backend.app.contracts import (
    EpisodeList,
    EpisodeSummary,
    EpisodeView,
    ErrorDetail,
    ErrorResponse,
    Health,
    Prediction,
    PredictionRequest,
    ResearchStatus,
    SystemInfo,
)
from backend.app.episodes import EPISODES, episode_view, find_episode


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("RENAL_GUARD_MODE", "demo") != "demo":
        raise RuntimeError(
            "Only synthetic demo mode is supported; research requires approved G1 decisions"
        )
    yield


app = FastAPI(title="RENAL-GUARD · Research Prototype", version="0.2.0", lifespan=lifespan)
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
    return Health()


@app.get("/api/v1/system/info", response_model=SystemInfo)
def system_info() -> SystemInfo:
    return SystemInfo()


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
