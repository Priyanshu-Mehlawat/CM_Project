# RENAL-GUARD — Final Consistency Review (30 Oct 2026)

## Approved decisions
- Predict *progression*, not *onset*: creatinine-defined KDIGO Stage 1 at first valid ICU prediction point → creatinine-defined Stage 2/3 within 48h.
- Adult MIMIC-IV development; harmonized external eICU evaluation; SafeICU pediatric feasibility optional after access approval.
- Tabular models: Logistic Regression baseline, XGBoost/LightGBM candidates, chosen via validation. Report AUPRC, AUROC, calibration, prevalence, uncertainty where defensible.
- Reliability: missingness/data-quality checks, external population-shift assessment, calibration, optional validated selective prediction.
- Modular monorepo: Python/DuckDB/Polars + FastAPI, React/TypeScript/Vite, SQLite only for demo metadata; synthetic demonstration; clinical explorer + research console + timeline replay.
- Linux/RTX 4050, one main developer + Codex, public GitHub, local-first, deliver by November 15 with Nov 13 target feature freeze.

## Corrected ambiguities
1. **KDIGO Stage 3:** Stage 3 comprises more than a 3x creatinine ratio; clinical engine must implement all applicable creatinine criteria. New RRT/KRT is separately documented because the primary target is creatinine-only.
2. **Information latency:** MIMIC `labevents.storetime` availability; eICU offsets require inspection, do not treat revised timestamp as original availability proof.
3. **Missing outcomes:** Three-way labels (event, adequately observed non-event, unknown); observe competing events and outcome ascertainment bias.
4. **Index Stage 1:** Need decision on ICU-present vs newly developed Stage 1; not silently assumed.
5. **External label comparability:** Hospital-to-hospital scoring is invalid if baseline/outcome definitions diverge without disclosure and sensitivity checks.
6. **SafeICU:** Pediatric transfer may be scientifically unsound under adult reference definitions and must not be mandatory.
7. **Demo predictions:** Synthetic trajectories are for presentation; a numeric prediction is shown only when the real, validated pipeline can serve compatible synthetic features.
8. **Privacy:** Local Codex executable still may communicate with cloud models; filesystem isolation is mandatory, not only `.gitignore`.

## Mandatory G1 research decisions (human-reviewed, before G2)
- Exact dataset versions and schema mapping.
- Eligibility: first incident/present Stage 1 at ICU index, preexisting Stage 2/3, chronic KRT, repeated stays, uncertain age.
- Reference creatinine policy: lookback and adequate availability; handling unknown baseline; sensitivity plan.
- Timing: collection, publication, observation and clinical event index; eICU missing original availability timestamp latency policy.
- Follow-up: minimum post-index creatinine measurements and ascertainment window to label non-progressors; death/discharge/KRT competing events.
- Valid unit conversion and threshold boundaries.
- Primary cross-dataset feature dictionary and the minimum hospital size/event count for publication.
- Confirm sufficient positives and negatives and reasonable unknown-label proportion. If no, redesign with supervisor before implementation.

## Product and feasibility caveats
- Claim **retrospective research prototype**, not prospective clinical readiness or preventive benefit.
- No fake risk tiers; thresholds must be validated. No SHAP causal language.
- External poor performance is a legitimate research result, not reason to alter test splits.
- Under time pressure cut SafeICU, public hosting, extra architectures, animations, advanced shift detectors first.

## Next action
Begin `prompts/00_repository_foundation.md`. Follow with privacy-safe `prompts/01_dataset_audit.md`, then freeze G1 decisions before clinical labelling code and any real training.
