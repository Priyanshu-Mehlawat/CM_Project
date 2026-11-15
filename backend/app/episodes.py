"""Independently authored, synthetic progression episodes. No source patient data."""

from dataclasses import dataclass

from ml.clinical.creatinine import Observation, assessment, available_samples, stage_at_sample


@dataclass(frozen=True)
class Episode:
    id: str
    name: str
    description: str
    observations: tuple[Observation, ...]
    reference_id: str = "ref"
    # This is an explicit illustrative ascertainment assertion, NOT a research rule.
    negative_ascertainment_hour: float | None = None
    followup_note: str = "No adequate negative-outcome ascertainment was asserted."


def obs(sample, measured, value, available=None):
    return Observation(sample, measured, measured if available is None else available, value)


EPISODES = (
    Episode(
        "synthetic-progressor",
        "Example A · Observed progression",
        "An invented Stage 1 episode with later Stage 2; collection and availability differ.",
        (obs("ref", 0, 1), obs("index", 12, 1.6, 14), obs("repeat", 30, 2.1, 32)),
    ),
    Episode(
        "synthetic-observed-negative",
        "Example B · Adequate illustrative follow-up",
        "An invented non-progressor with an explicitly asserted synthetic ascertainment marker.",
        (obs("ref", 0, 1), obs("index", 12, 1.6), obs("repeat", 36, 1.5), obs("late", 60, 1.3)),
        negative_ascertainment_hour=60,
        followup_note=("Fixture-only ascertainment asserted at hour 60; not a clinical policy."),
    ),
    Episode(
        "synthetic-unknown",
        "Example C · Outcome unknown",
        "No adequate follow-up: absence of a later severe measurement is not a negative.",
        (obs("ref", 0, 1), obs("index", 12, 1.6), obs("last", 20, 1.5)),
    ),
    Episode(
        "synthetic-correction",
        "Example D · Corrected laboratory result",
        "A withdrawn abnormal result is replaced when its correction becomes available.",
        (obs("ref", 0, 0.8), obs("index", 6, 1.2), obs("index", 6, 0.9, 20)),
    ),
    Episode(
        "synthetic-stage3",
        "Example E · Stage 3 boundary",
        "AKI established by a seven-day ratio can qualify for the 4.0 mg/dL Stage 3 branch.",
        (obs("ref", 0, 2.5), obs("index", 24, 3.8), obs("severe", 72, 4)),
    ),
)


def find_episode(episode_id: str) -> Episode | None:
    return next((e for e in EPISODES if e.id == episode_id), None)


def index_hour(episode: Episode, cutoff: float) -> float | None:
    """First as-of Stage 1 in this fixture; a retraction can invalidate the episode.

    The fixture reference is explicit. This is not a population eligibility policy.
    """
    rows = list(episode.observations)
    final_known = available_samples(rows, cutoff)
    valid_ids = {
        r.sample_id
        for r in final_known
        if stage_at_sample(r, final_known, episode.reference_id) == 1
    }
    for t in sorted({r.available_hour for r in rows if 0 <= r.available_hour <= cutoff}):
        known = available_samples(rows, t)
        stage = assessment(rows, t, episode.reference_id)["stage"]
        if stage in (2, 3):
            return None
        if stage == 1 and known[-1].sample_id in valid_ids:
            return t
    return None


def episode_view(episode: Episode, cutoff: float) -> dict:
    rows = list(episode.observations)
    known = available_samples(rows, cutoff)
    index = index_hour(episode, cutoff)
    event_hour = None
    if index is not None:
        events = [
            r.measured_hour
            for r in known
            if index < r.measured_hour <= index + 48
            and stage_at_sample(r, known, episode.reference_id) in (2, 3)
        ]
        event_hour = min(events) if events else None
    outcome, reason = "unknown", "insufficient_followup"
    if index is None:
        reason = "no_confirmed_stage1_index"
    elif event_hour is not None:
        outcome, reason = "progressed", "stage2_or_3_observed_in_48h"
    elif cutoff < index + 48:
        reason = "outcome_window_not_complete"
    elif (
        episode.negative_ascertainment_hour is not None
        and index + 48 <= episode.negative_ascertainment_hour <= cutoff
    ):
        outcome, reason = "non_progressed", "explicit_synthetic_ascertainment"
    return {
        "schema_version": "v1",
        "id": episode.id,
        "name": episode.name,
        "description": episode.description,
        "source": "independently_authored_synthetic",
        "cutoff_hour": cutoff,
        "index_hour": index,
        "horizon_hours": 48,
        "protocol_version": "synthetic-fixture-v1-not-approved-for-research",
        "assessment": assessment(rows, cutoff, episode.reference_id),
        "timeline": [
            {
                "sample_id": r.sample_id,
                "measured_hour": r.measured_hour,
                "available_hour": r.available_hour,
                "creatinine_mg_dl": r.creatinine_mg_dl,
            }
            for r in known
        ],
        "outcome": {
            "state": outcome,
            "reason": reason,
            "event_hour": event_hour,
            "followup_note": episode.followup_note,
        },
        "prediction": {
            "state": "unavailable",
            "probability": None,
            "reason": "validated_progression_model_unavailable",
            "model_version": None,
        },
    }
