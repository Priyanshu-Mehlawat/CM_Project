# CODEX PROMPT 03 — Cross-dataset feature harmonization and leakage controls

Precondition: G2 passed and human-approved `docs/clinical_protocol.md` + audit-supported common feature dictionary exist. Do not open restricted files. Work from synthetic fixture datasets and schema mapping contracts.

## Objective
Implement MIMIC/eICU adapters and a single versioned, time-safe tabular feature-generation pipeline.

## Implement
- Pure mappings from dataset-specific concepts/units into canonical `Encounter` and `Observation` schemas; include provenance, timestamp semantics, duplicate reconciliation and invalid-value flags.
- A configurable, audited feature schema (age, sex, creatinine baseline/current/deltas, BUN, Na/K, MAP, HR, RR, temperature, SpO2, Hb/platelets and time-since-observed, only if documented as shared and available).
- Feature windows restricted to index information cutoff; no future values, final stage, ICU outcome, future treatment, LOS, or target-derived summaries. Version lookback window semantics explicitly.
- Missingness flags and transparent imputation interfaces; *fit* any learned imputation only on train folds in ML pipeline, never on aggregate source before splitting.
- Synthetic MIMIC/eICU fixtures producing identical ordered columns and validating units/availability as-of joins.
- Output private-local Parquet schema and data dictionary template; never output real rows to agent console or Git.

## Gate G3
Tests for unit conversions, availability cutoff (including late results), lookbacks, duplicate labs, missingness, deterministic schema and source equivalence; no real data requested or accessed. Updated `docs/data_dictionary.md`, mapped-source limitations and feature schema version. Stop for missing human-approved mappings.
