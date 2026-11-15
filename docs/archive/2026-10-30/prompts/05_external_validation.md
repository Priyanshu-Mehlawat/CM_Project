# CODEX PROMPT 05 — Genuine external validation and transportability

Precondition: frozen MIMIC-developed model and G4 verification. DO NOT inspect restricted data. Implement offline evaluation tooling and synthetic tests only.

## Objective
Evaluate a *frozen* development model on a harmonized eICU adult Stage1 progression cohort and prepare research artifacts.

## Implement
- Validate external label protocol, feature schema, supported measurement-availability latency policy and cohort comparability before prediction.
- No refitting of scaler, imputer, feature selection, classifier, calibration or threshold with the external test cohort. Mismatch => block with documented reason.
- Report sample size, events, prevalence, unknown outcomes, exclusions, AUROC/AUPRC/Brier, calibration plots and slope/intercept, sensitivity/PPV at preselected thresholds/budgets, uncertainty where defensible. Never suppress poor performance.
- Hospital-level subsets only above human-approved minimum sample/event reporting thresholds; suppress small cells and unauthorized identities in public artifacts.
- Separate optional eICU-hospital holdout and **adaptation experiments** with distinct target adaptation/test partitions; no leakage from target test.
- Generate versioned metrics, calibration bins, cohort flow and manifest JSON with `not_yet_evaluated` support. Human must review before publishing even aggregate statistics.
- Synthetic unit tests for frozen parameter hashes, incompatible schemas, missing metrics, small-cell suppression, and mislabelled adaptation/test split.

## Gate G5
No claim of external generalization until a verified, authorized, frozen-model run was completed and cohort comparability established. A low score is a valid outcome, not a reason to retune test set. Share only non-disclosive aggregates.
