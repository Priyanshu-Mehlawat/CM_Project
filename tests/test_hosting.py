"""Public hosting must never enable arbitrary patient uploads."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.samples import CASES


def test_public_samples_and_download_roundtrip(monkeypatch):
    monkeypatch.setenv("RENAL_GUARD_PUBLIC_DEMO", "1")
    with TestClient(app) as client:
        assert client.get("/api/v1/model/status").json()["public_demo"] is True
        assert client.post("/api/v1/assessments/import", json={}).status_code == 403
        for sample in CASES:
            result = client.get(f"/api/v1/samples/{sample}/assessment")
            assert result.status_code == 200
            assert result.json()["prediction"]["probability"] is None
            assert client.get(f"/api/v1/samples/{sample}/download?format=csv").status_code == 200
            assert client.get(f"/api/v1/samples/{sample}/download").json()["source"] == "synthetic"
        assert client.get("/api/v1/samples/unknown/download").status_code == 404


@pytest.mark.parametrize(
    "key,value",
    [("RENAL_GUARD_ENABLE_PATIENT_IMPORT", "1"), ("RENAL_GUARD_MODEL_PATH", "not-read")],
)
def test_public_host_refuses_private_configuration(monkeypatch, key, value):
    monkeypatch.setenv("RENAL_GUARD_PUBLIC_DEMO", "1")
    monkeypatch.setenv(key, value)
    with pytest.raises(RuntimeError, match="Public sample hosting"):
        with TestClient(app):
            pass
