# CODEX PROMPT 08 — Reliability experiments and historical replay

Precondition: G5 verified external evaluation and G7 clinical UI exist. Code/tests only from synthetic fixtures; real calculations run separately.

## Objective
Deliver meaningful reliability research visualizations and signature historical replay, respecting frozen index-time prediction.

## Implement
- Reliability checks: input schema/unit/timing, missingness/imputation warnings, version mismatch, clearly caveated distribution-shift summaries, calibration evidence. Do not invent calibrated per-case trust percentage.
- Offline reliability experiments: missingness perturbation with explicit assumptions, hospital shift diagnostics, optional selective prediction tuned on development data; report risk/coverage and **number of withheld progression events** per cohort.
- Replay UI: display index-time features and original model probability, scrub subsequent observations, reveal Stage2/3 event vs adequate non-event vs unknown, never recompute original prediction from future values. Explicitly label outcomes as retrospective, synthetic vs real according to mode.
- Tests: advancing replay leaves original prediction hash unchanged; late results excluded; unknown outcomes not rendered non-events; withholding thresholds never fitted on external test; unavailable reliability artifact shows honest message.
- If insufficient data for calibration or selective prediction, implement honest unavailable state rather than unsupported status.

## Gate G8
Replay and reliability tests pass; verified real reliability metrics present only if generated and human-reviewed. No dynamic-prediction claims without separate validated model.
