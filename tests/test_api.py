import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


def test_health_is_liveness_not_model_readiness():
    with TestClient(app) as client:
        response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {
        "schema_version": "v1",
        "service_alive": True,
        "model_available": False,
        "mode": "synthetic_demo",
    }


def test_system_explicitly_disables_research_and_evaluation():
    with TestClient(app) as client:
        info = client.get("/api/v1/system/info").json()
    assert info["research_mode_enabled"] is False
    assert info["model_version"] is None
    assert info["evaluation_state"] == "not_yet_evaluated"
    assert info["protocol_state"] == "pending_G1"


def test_examples_are_synthetic_and_have_no_fabricated_predictions():
    with TestClient(app) as client:
        cases = client.get("/api/v1/episodes").json()
        assert cases["source"] == "independently_authored_synthetic"
        assert len(cases["episodes"]) == 5
        for case in cases["episodes"]:
            view = client.get(f"/api/v1/episodes/{case['id']}").json()
            assert view["prediction"]["probability"] is None
            assert view["source"] == "independently_authored_synthetic"


def test_cors_allows_only_local_frontend():
    with TestClient(app) as client:
        for origin in ["http://127.0.0.1:5173", "http://localhost:5173"]:
            response = client.get("/api/v1/health", headers={"Origin": origin})
            assert response.headers["access-control-allow-origin"] == origin
        response = client.get("/api/v1/health", headers={"Origin": "https://example.com"})
        assert "access-control-allow-origin" not in response.headers


def test_research_mode_fails_closed(monkeypatch):
    monkeypatch.setenv("RENAL_GUARD_MODE", "research")
    with pytest.raises(RuntimeError, match="Only synthetic demo"):
        with TestClient(app):
            pass


def test_unsupported_routes_and_methods_have_redacted_errors():
    with TestClient(app) as client:
        missing = client.get("/private-synthetic-marker")
        unsupported = client.post("/api/v1/health", json={"value": "synthetic-marker"})
        prediction = client.post("/api/v1/predictions", json={})
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "not_found"
    assert "private-synthetic-marker" not in missing.text
    assert unsupported.status_code == 405
    assert unsupported.json()["error"]["code"] == "method_not_allowed"
    assert "synthetic-marker" not in unsupported.text
    assert prediction.status_code == 422
