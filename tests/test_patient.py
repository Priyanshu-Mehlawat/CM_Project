"""All measurements, outcomes and model weights here are independently synthetic."""

import hashlib
import json
import math

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.patient import PatientInput, assess
from ml.features.patient import FEATURES
from ml.inference.bundle import Bundle, configured_bundle, infer
from scripts.train_progression import fit, metrics


def payload():
    vitals = [
        ("heart_rate", 90, "bpm"),
        ("map", 75, "mmHg"),
        ("respiratory_rate", 20, "/min"),
        ("spo2", 96, "%"),
        ("temperature", 37, "C"),
        ("bun", 28, "mg/dL"),
        ("potassium", 4.2, "mmol/L"),
    ]
    observations = [
        {"concept": c, "value": v, "unit": u, "measured_hour": 1, "available_hour": 1}
        for c, v, u in vitals
    ]
    observations += [
        {
            "concept": "creatinine",
            "value": 1.5,
            "unit": "mg/dL",
            "measured_hour": 2,
            "available_hour": 3,
        }
    ]
    return {
        "source": "synthetic",
        "age": 62,
        "cutoff_hour": 8,
        "reference_creatinine_mg_dl": 1,
        "reference_measured_hour": -12,
        "reference_available_hour": -11,
        "reference_confirmed": True,
        "eligibility_confirmed": True,
        "protocol_version": "test-v1",
        "observations": observations,
    }


def bundle():
    return Bundle(
        model_version="synthetic-unit-test",
        protocol_version="test-v1",
        data_version="synthetic",
        trained_at="2026-11-15",
        training_source="synthetic_test",
        features=list(FEATURES),
        medians=[1.0] * len(FEATURES),
        means=[0.0] * len(FEATURES),
        scales=[1.0] * len(FEATURES),
        coefficients=[0.01] * (len(FEATURES) * 2),
        intercept=-1.0,
        metrics={},
    )


def test_assessment_infers_using_exact_index_inputs_not_future_measurements():
    p = payload()
    original = assess(PatientInput.model_validate(p), bundle())
    p["observations"].extend(
        [
            {
                "concept": "map",
                "value": 45,
                "unit": "mmHg",
                "measured_hour": 7,
                "available_hour": 7,
            },
            {
                "concept": "creatinine",
                "value": 1.8,
                "unit": "mg/dL",
                "measured_hour": 7,
                "available_hour": 8,
            },
            {
                "concept": "creatinine",
                "value": 3,
                "unit": "mg/dL",
                "measured_hour": 9,
                "available_hour": 10,
            },
        ]
    )
    result = assess(PatientInput.model_validate(p), bundle())
    assert result["index_hour"] == 3
    assert result["stage"] == 1
    assert result["features"] == original["features"]
    assert result["prediction"] == original["prediction"]
    assert result["latest_creatinine_mg_dl"] == 1.8
    assert result["prediction"]["state"] == "available"
    assert len(result["timeline"]) == 3
    contributions = result["prediction"]["contributions"]
    logit = bundle().intercept + sum(c["log_odds_contribution"] for c in contributions)
    assert result["prediction"]["probability"] == pytest.approx(1 / (1 + math.exp(-logit)))


def test_units_current_severity_and_model_scope():
    p = payload()
    p["observations"][-1]["value"] = 1.5 * 88.4
    p["observations"][-1]["unit"] = "umol/L"
    assert assess(PatientInput.model_validate(p))["stage"] == 1
    p["observations"].append(
        {
            "concept": "creatinine",
            "value": 2.1,
            "unit": "mg/dL",
            "measured_hour": 7,
            "available_hour": 8,
        }
    )
    result = assess(PatientInput.model_validate(p), bundle())
    assert result["stage"] == 2
    assert result["prediction"]["state"] == "withheld"


@pytest.mark.parametrize(
    "change",
    [
        {"age": 17},
        {"reference_confirmed": False},
        {"eligibility_confirmed": False},
        {"reference_available_hour": 100},
        {"patient_name": "synthetic-marker"},
    ],
)
def test_invalid_uploads_are_redacted(change):
    p = {**payload(), **change}
    with TestClient(app) as client:
        response = client.post("/api/v1/assessments", json=p)
    assert response.status_code == 422
    assert "synthetic-marker" not in response.text
    assert "no-store" == response.headers["cache-control"]


def test_import_parity_permissions_and_request_limits():
    p = payload()
    with TestClient(app) as client:
        direct = client.post("/api/v1/assessments", json=p)
        imported = client.post(
            "/api/v1/assessments/import", json={"format": "json", "content": json.dumps(p)}
        )
        assert imported.json() == direct.json()
        assert imported.json()["prediction"]["probability"] is None
        assert (
            client.post(
                "/api/v1/assessments", json=p, headers={"Origin": "https://attacker.example"}
            ).status_code
            == 403
        )
        assert client.post("/api/v1/assessments/import", content="x" * 129000).status_code == 413
        p["source"] = "authorized_research"
        assert client.post("/api/v1/assessments", json=p).status_code == 403


def test_csv_matches_json_and_rejects_inconsistent_metadata():
    p = payload()
    meta = {
        k: str(v).lower() if isinstance(v, bool) else v for k, v in p.items() if k != "observations"
    }
    header = ",".join([*meta, *p["observations"][0]])
    rows = [",".join(map(str, [*meta.values(), *o.values()])) for o in p["observations"]]
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/assessments/import",
            json={"format": "csv", "content": "\n".join([header, *rows])},
        )
        assert response.status_code == 200
        assert response.json()["stage"] == 1
        bad = "\n".join([header, *rows]).replace("62", "17", 1)
        assert (
            client.post(
                "/api/v1/assessments/import", json={"format": "csv", "content": bad}
            ).status_code
            == 422
        )


def test_missingness_protocol_mismatch_duplicates_and_unavailable_baseline():
    p = payload()
    p["observations"] = p["observations"][-1:]
    assert assess(PatientInput.model_validate(p), bundle())["prediction"]["state"] == "withheld"
    p = payload()
    p["protocol_version"] = "other"
    assert assess(PatientInput.model_validate(p), bundle())["prediction"]["probability"] is None
    p = payload()
    p["observations"].append(p["observations"][-1])
    with pytest.raises(ValueError):
        PatientInput.model_validate(p)
    p = payload()
    p["reference_available_hour"] = 8
    result = assess(PatientInput.model_validate(p))
    assert result["index_hour"] == 8


def test_bundle_integrity_and_no_synthetic_model_serving(tmp_path, monkeypatch):
    path = tmp_path / "unit-test.json"
    raw = bundle().model_dump_json().encode()
    path.write_bytes(raw)
    monkeypatch.setenv("RENAL_GUARD_MODEL_PATH", str(path))
    monkeypatch.setenv("RENAL_GUARD_MODEL_SHA256", "a" * 64)
    with pytest.raises(ValueError, match="digest"):
        configured_bundle()
    monkeypatch.setenv("RENAL_GUARD_MODEL_SHA256", hashlib.sha256(raw).hexdigest())
    with pytest.raises(ValueError, match="Synthetic"):
        configured_bundle()
    weights = bundle().model_dump()
    weights["coefficients"] = [1]
    with pytest.raises(ValueError):
        Bundle.model_validate(weights)


def synthetic_rows():
    result = []
    for i in range(160):
        # Independently authored values; test runtime only, never clinical performance.
        values = {
            "age": 30 + i % 50,
            "reference_creatinine": 1.0,
            "creatinine": 1.5,
            "creatinine_ratio": 1.5,
            "creatinine_delta": 0.5,
            "heart_rate": 60 + i % 60,
            "map": 65 + i % 30,
            "respiratory_rate": 15 + i % 10,
            "spo2": 95 + i % 5,
            "temperature": 37.0,
            "bun": 20 + i % 30,
            "potassium": 4.0,
        }
        result.append(
            {
                "patient_group": f"synthetic-{i // 2}",
                "outcome": str(i % 2),
                "index_stage": "1",
                "features_available_by_index": "true",
                **{k: str(v) for k, v in values.items()},
            }
        )
    return result


def test_training_roundtrip_and_metric_ties():
    model = fit(synthetic_rows(), "test-v1", "synthetic")
    assert model.metrics["test"]["n"] > 10
    values = assess(PatientInput.model_validate(payload()))["features"]
    assert infer(Bundle.model_validate_json(model.model_dump_json()), values) == infer(
        model, values
    )
    assert metrics([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5])["auroc"] == 0.5
    assert metrics([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5])["average_precision"] == 0.5


def test_http_inference_and_model_metrics_are_from_installed_pipeline():
    with TestClient(app) as client:
        app.state.bundle = bundle()  # Synthetic weights injected only inside this test.
        response = client.post("/api/v1/assessments", json=payload())
        expected = assess(PatientInput.model_validate(payload()), bundle())
        assert response.status_code == 200
        assert response.json()["prediction"] == expected["prediction"]
        assert client.get("/api/v1/model/status").json()["state"] == "ready"
        assert client.get("/api/v1/health").json()["model_available"] is True
        assert client.get("/api/v1/system/info").json()["model_version"] == "synthetic-unit-test"


def test_progressed_then_recovered_history_is_not_a_new_stage1_forecast():
    p = payload()
    p["cutoff_hour"] = 14
    p["observations"].extend(
        [
            {
                "concept": "creatinine",
                "value": 2.1,
                "unit": "mg/dL",
                "measured_hour": 9,
                "available_hour": 10,
            },
            {
                "concept": "creatinine",
                "value": 1.7,
                "unit": "mg/dL",
                "measured_hour": 13,
                "available_hour": 14,
            },
        ]
    )
    result = assess(PatientInput.model_validate(p), bundle())
    assert result["stage"] == 1
    assert result["prediction"]["state"] == "withheld"
    assert "already observed" in result["prediction"]["reason"]
    p = payload()
    p["cutoff_hour"] = 52
    assert "ended" in assess(PatientInput.model_validate(p), bundle())["prediction"]["reason"]


def test_heldout_values_do_not_change_fitted_preprocessing_or_coefficients():
    import random

    rows = synthetic_rows()
    groups = sorted({r["patient_group"] for r in rows})
    random.Random(31).shuffle(groups)
    heldout = set(groups[int(0.6 * len(groups)) :])
    original = fit(rows, "test-v1", "synthetic")
    for r in rows:
        if r["patient_group"] in heldout:
            r["age"] = "110"
    changed = fit(rows, "test-v1", "synthetic")
    assert changed.medians == original.medians
    assert changed.means == original.means
    assert changed.scales == original.scales
    assert changed.coefficients == original.coefficients
    assert changed.intercept == original.intercept
