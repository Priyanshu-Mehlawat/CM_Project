# CODEX PROMPT 02 — KDIGO engine and outcome ascertainment

Read AGENTS and clinical protocol. **Precondition: Gate G1 human-reviewed clinical decisions are documented and signed off.** If the exact baseline/index/outcome/follow-up definitions are missing, implement only pure synthetic-friendly interfaces/tests and STOP; do not guess.

## Objective
Implement an independently testable, versioned creatinine-based KDIGO staging and Stage1→Stage2/3 48h outcome engine.

## Implement
- Explicit baseline strategy implementation with unit conversions and documented lookbacks, as approved by G1. No future creatinine as a baseline for prior index.
- Time-aware `Observation` and `PredictionEpisode` typed schemas tracking measurement and credible availability timestamps; preserve unknown timestamp states and source-specific latency policy.
- Index at first confirmed Stage1 available during ICU using approved eligibility rules, before Stage2/3; exclude chronic KRT per policy. Only one primary episode per ICU stay; patient grouping later.
- Outcome `progressed`, `not_progressed_with_adequate_followup`, `unknown` with event time and follow-up reason; do not automatically label discharge/death/missing tests as negative. Stage3 creatinine absolute threshold as defined by guideline; do not silently include new KRT in primary creatinine-only endpoint.
- Tests: 0.3 mg/dL 48h boundary, 1.5x, 2x, 3x, >=4 mg/dL with qualifying rise, nonqualifying contexts, lookback boundaries, timestamp ordering, result-after-cutoff, chronic dialysis exclusions, prior Stage2/3, death, discharge, incomplete follow-up, repeat stays, unknown baseline, source unit variation.
- Synthetic cohort flow builder and structured reason codes; version clinical rules.

## Gate G2
Full synthetic KDIGO suite passes with documented expected stages; chronological invariants and unknown-outcome tests pass; clinical policy version in metadata; no real patient data inspected by Codex. Report potential disagreement points against KDIGO reference, clinical decisions, and remaining limitations. **No training until G2 approved.**
