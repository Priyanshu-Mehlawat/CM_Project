"""Local synthetic demo. No data connectors, artifact loaders or research endpoints."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from backend.app.contracts import DemoCases, ErrorDetail, ErrorResponse, Health, SystemInfo
from backend.app.demo import synthetic_cases


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.environ.get("RENAL_GUARD_MODE", "demo") != "demo":
        raise RuntimeError("Only synthetic demo mode is supported in Stage 00")
    yield


app = FastAPI(title="RENAL-GUARD · Research Prototype", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_credentials=False,
    allow_methods=["GET"],
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


@app.get("/api/v1/demo/cases", response_model=DemoCases)
def cases() -> DemoCases:
    return synthetic_cases()
