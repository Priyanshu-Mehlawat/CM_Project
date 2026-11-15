# CODEX PROMPT 04 — Reproducible training and model selection

Preconditions: G3 passed; authorized researcher has independently generated the approved private cohort/features outside agent access. Codex writes code and tests on synthetic data only. No patient rows/logs through Codex.

## Objective
Implement an offline, configurable tabular ML training/evaluation pipeline with a real Logistic Regression baseline and XGBoost/LightGBM candidates.

## Implement
- Grouped patient split (not ICU stay), reproducible seed, split manifests private. Distinct development train, tuning/calibration, internal test.
- Training-only imputation/scaling/feature transforms; consistent inference schema; class prevalence reporting.
- Logistic Regression baseline, two optional tree candidates, measured AUPRC (primary), AUROC, Brier score, calibration evaluation, confusion metrics at prespecified threshold/alert budget, sample/events and confidence intervals if defensible.
- Select model using predeclared development validation criteria only. Do not tune on internal test or external eICU.
- Calibration fit only on appropriate development partition and applied via versioned pipeline. If unsupported by data size, record `uncalibrated`.
- Artifact bundle: trusted model serialization, preprocessing, optional calibrator, validated schema, SHA-256 hashes, version metadata, run config. Keep bundle in private storage, never commit by default.
- Synthetic end-to-end test covering groups, reproducible refit, feature ordering, missing inputs, artifact roundtrip, metric calculations and invalid labels.
- Offline CLI commands for authorized execution with protected data run by HUMAN outside Codex access. Produce permitted aggregated metrics only after disclosure review.

## Gate G4
Synthetic tests pass. A real model training run is *not* claimed until user independently executes it and reviews safe aggregate results. Report exact required human steps; no invented AUPRC/AUROC or model selection. Gate is pending until verified real experiment artifacts exist.
