# AGENTS.md — RENAL-GUARD Repository Rules for Codex

Read `MASTER_SPECIFICATION.md` (copy into `docs/` or place at repo root) and `docs/decision_log.md` before modifying code.

## Mission
Build a reproducible, privacy-respecting, full-stack *research prototype* for predicting Stage 1 AKI progression to Stage 2/3 within 48 hours, using adult MIMIC-IV development and harmonized eICU external evaluation. Do not turn it into AKI-onset prediction, live clinical monitoring, treatment guidance, or unvalidated pediatric care.

## Hard safety boundary
- Codex works on **source code, public schemas, synthetic fixtures, tests and reviewed aggregate outputs ONLY**. Do not read, enumerate, search, index, print, upload or otherwise access restricted patient-level data or any protected files/directories. This includes background tools and shell commands, logs, caches, and file search. If project tasks require restricted data, generate an offline command/script for the authorized developer to run **outside Codex's accessible environment**, then STOP and ask for disclosure-reviewed aggregate results/decisions.
- Do not create symlinks into restricted directories or mount protected data into the agent workspace. Keep private data paths outside the repository and agent's readable filesystem by OS permissions/isolation. Never use GitHub Actions or cloud runners for restricted datasets.
- Never commit CSV/Parquet/database files that might originate from real patients, restricted models, sensitive metrics, original identifiers, secrets or API keys. Public demo data must be synthetic, clearly labeled, and generated independently from protected records.
- Do not suggest turning off safeguards to get tasks working; document blockers.

## Scientific invariants
- Prediction is at **first confirmed creatinine-based Stage 1** time within ICU; use only features available by that time. Primary target is *creatinine-based* Stage 2/3 progression within 48 hours. Urine output/KRT are separate conditional analyses.
- KDIGO 2012 staging must be tested. **Do not invent baseline creatinine, eligibility, censoring/adequate follow-up or eICU latency rules.** Clinical protocol must be signed off after local audit; if absent, stop before making real labels/training.
- Outcome unknown is distinct from negative. Death/discharge and missing repeat tests are not automatically negatives.
- Group by patient in all MIMIC train/validation/test partitions. Test data may not fit preprocessing, calibration or thresholds. External eICU is a frozen-model test unless distinct adaptation/test cohorts are prespecified.
- Do not fabricate performance metrics, predictions, SHAP explanations, statistical uncertainty or completed experiments. All API metrics must reference actual versioned artifacts; absent artifacts => explicit unavailable state.
- SHAP influence is not causality. Do not label uncalibrated scores calibrated. No clinical treatment advice.

## Engineering
- Linux; Python/FastAPI/Pydantic, DuckDB/Polars for data pipeline, scikit-learn + XGBoost/LightGBM, React/TypeScript/Vite/Tailwind/shadcn/ui, SQLite for synthetic app metadata.
- Modular monorepo. Frontend never independently calculates canonical AKI stage/outcome, feature windows, or model probability. Backend inference uses saved, versioned, **trusted** preprocessing + model + optional calibrator.
- Use types, linting, unit tests, synthetic E2E tests, strict schema validation, meaningful error codes, predictable empty states. Default bind localhost. Demo mode safe without model or private data; research mode opt-in and access controlled.
- Never delete/skip tests merely to hide failures. Prefer minimal dependencies. Keep application buildable between stages.
- Model bundles include model/protocol/feature-schema/data-version metadata and validated hashes; never load untrusted joblib/pickle.

## Required working style
1. Inspect repository state and current gate; state concise plan.
2. Implement **only** the requested phase. Don't proceed across failed gates.
3. Use synthetic test fixtures only.
4. Run relevant checks (Python tests, frontend tests/build, lints, privacy scan); accurately report commands/results and unrun checks.
5. Update `docs/decision_log.md`, `docs/clinical_protocol.md` where relevant, and code documentation.
6. End each task with: `Files changed`, `Tests run/results`, `Gate status`, `Assumptions requiring human approval`, `Next step`.
7. Do not modify Git remotes, publish, push, install global packages, perform destructive operations, or access protected folders without explicit user approval.

## UI requirements
Research Prototype banner; permanent synthetic/research mode distinction; no fabricated risk badges, live-census claims or unvalidated trust scores. Clinical Explorer, Patient Timeline/Replay, Prediction Inspector, Research Console. Accessible responsive medical UI with graceful missing-evaluation/model states.

## Definition of success
Reproducible cohort methodology; no leakage; genuine internal and external evaluation; model-backed API; end-to-end React demo using safe synthetic cases; tested reliability warnings; public repository free of restricted data; explainable research limitations.
