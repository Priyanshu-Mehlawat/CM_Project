import pytest
from fastapi.testclient import TestClient

from backend.app.episodes import EPISODES, episode_view
from backend.app.main import app
from ml.clinical.creatinine import Observation as O
from ml.clinical.creatinine import assessment


@pytest.mark.parametrize(
    "baseline,value,hour,expected",
    [
        (0.6, 0.9, 48, 1),
        (0.6, 0.89, 48, 0),
        (1, 2, 24, 2),
        (1, 3, 24, 3),
        (2.5, 4, 72, 3),
        (4.1, 4.1, 24, 0),
        (1, 1.6, 169, None),
    ],
)
def test_kdigo_branch_boundaries(baseline, value, hour, expected):
    rows = [O("ref", 0, 0, baseline), O("current", hour, hour, value)]
    assert assessment(rows, hour, "ref")["stage"] == expected


def test_retraction_replaces_sample_and_future_revision_does_not_change_past():
    rows = [O("ref", 0, 0, 0.8), O("repeat", 6, 6, 1.2)]
    amended = [*rows, O("repeat", 6, 20, 0.9)]
    assert assessment(amended, 12, "ref") == assessment(rows, 12, "ref")
    assert assessment(amended, 24, "ref")["observed_aki"] is False
    assert assessment(amended, 24, "ref")["known_sample_count"] == 2


def test_future_and_unavailable_results_are_not_in_assessment():
    rows = [O("ref", 0, 0, 1), O("repeat", 12, 15, 1.6), O("future", 24, 24, 4)]
    assert assessment(rows, 14, "ref")["stage"] is None
    assert assessment(rows, 15, "ref")["stage"] == 1


def test_conflicting_revisions_fail_instead_of_relying_on_input_order():
    with pytest.raises(ValueError, match="Conflicting"):
        assessment([O("ref", 0, 0, 1), O("ref", 0, 0, 2)], 1, "ref")


def test_progression_uses_index_availability_and_future_only_measurements():
    progressor = EPISODES[0]
    early = episode_view(progressor, 14)
    assert early["index_hour"] == 14
    assert len(early["timeline"]) == 2
    assert early["outcome"]["state"] == "unknown"
    assert episode_view(progressor, 30)["outcome"]["state"] == "unknown"
    later = episode_view(progressor, 32)
    assert later["outcome"]["state"] == "progressed"
    assert later["outcome"]["event_hour"] == 30


def test_unknown_followup_and_explicit_synthetic_negative_are_distinct():
    assert episode_view(EPISODES[1], 59)["outcome"]["state"] == "unknown"
    assert episode_view(EPISODES[1], 60)["outcome"]["state"] == "non_progressed"
    assert episode_view(EPISODES[2], 72)["outcome"]["state"] == "unknown"
    assert episode_view(EPISODES[3], 24)["index_hour"] is None


def test_exact_horizon_endpoint_is_included():
    view = episode_view(EPISODES[4], 72)
    assert view["index_hour"] == 24
    assert view["outcome"]["event_hour"] == 72
    assert view["outcome"]["state"] == "progressed"


def test_connected_episode_prediction_research_contract_without_artifacts():
    with TestClient(app) as client:
        cases = client.get("/api/v1/episodes").json()["episodes"]
        assert len(cases) == 5
        case = client.get(f"/api/v1/episodes/{cases[0]['id']}?cutoff_hour=32").json()
        assert case["assessment"]["stage"] == 2
        assert case["horizon_hours"] == 48
        response = client.post("/api/v1/predictions", json={"episode_id": cases[0]["id"]})
        assert response.status_code == 200
        assert response.json()["probability"] is None
        assert client.get("/api/v1/research/status").json()["metrics"] is None
        assert (
            client.post(
                "/api/v1/predictions", json={"episode_id": cases[0]["id"], "horizon_hours": 24}
            ).status_code
            == 422
        )
        assert client.get("/api/v1/episodes/missing").status_code == 404
        assert (
            client.get("/api/v1/episodes/synthetic-progressor?cutoff_hour=nan").status_code == 422
        )
        assert (
            client.post(
                "/api/v1/predictions", json={"episode_id": cases[0]["id"], "patient_record": {}}
            ).status_code
            == 422
        )
