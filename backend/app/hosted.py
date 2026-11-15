"""Single-origin deployment entry point. Public runtime exposes authored samples only."""

import os
from pathlib import Path

from fastapi import HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.main import app

DIST = Path(os.environ.get("RENAL_GUARD_STATIC_DIR", "frontend/dist")).resolve()
if not (DIST / "index.html").is_file():
    raise RuntimeError("Build the frontend before starting the hosted entry point")

app.mount("/assets", StaticFiles(directory=DIST / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str):
    if path.startswith("api/"):
        raise HTTPException(404)
    return FileResponse(DIST / "index.html", headers={"Cache-Control": "no-store"})
