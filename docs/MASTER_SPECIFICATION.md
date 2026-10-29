# RENAL-GUARD — Master Specification

**Version:** 1.0 — 30 October 2026
**Status:** Implementation-ready requirements, with mandatory dataset-dependent research gates
**Project:** Group 31 course project
**Tentative submission:** 15 November 2026
**Repository:** `https://github.com/Priyanshu-Mehlawat/CM_Project`
**Environment:** Linux laptop, NVIDIA RTX 4050 laptop GPU; one primary developer, AI-assisted coding.

## 1. Project identity and boundaries

**Working name:** RENAL-GUARD — Generalizable and Reliability-Aware Prediction of Acute Kidney Injury Progression in Critical Care.

**Primary research question:** For adult ICU encounters with creatinine-defined KDIGO Stage 1 AKI identified at an index prediction time, can a model estimate the probability of observed progression to creatinine-defined KDIGO Stage 2 or 3 in the next 48 hours, and how do discrimination, calibration, robustness, and reliability change across hospitals?

This differs from predicting AKI *onset* in patients without AKI. Do not revert to onset prediction or silently alter the outcome.

**Intended use:** Retrospective clinical ML research and an educational clinical decision-support prototype; **not** patient care, triage, autonomous diagnosis, therapy guidance, or hospital deployment. Display a persistent research-use notice. No clinical benefit is claimed without prospective evidence.

**Primary dataset:** MIMIC-IV (exact downloaded version to be inventoried).
**External dataset:** eICU-CRD (version to be inventoried), held untouched for frozen-model external evaluation.
**SafeICU:** Pending DUA/authorization and feasibility: optional *pediatric* data audit and exploratory transfer experiment, not a blocker or equivalent adult validation dataset. Pediatric clinical criteria require a separate protocol.

**Fixed study design:** Adults >=18, one primary index prediction at the first *confirmed* Stage 1 assessment during an ICU stay, primary horizon 48 h, secondary horizon 24 h only if feasible. Creatinine-based staging and progression are the primary target; urine output / new renal replacement therapy are secondary or sensitivity analyses if reliably captured, not silently merged into the creatinine-only primary target.

**Key unconfirmed scientific details (cannot be guessed):** Baseline creatinine algorithm and lookback/reference requirements; whether index can include prevalent Stage 1 already present at ICU entry; eligibility when prior Stage 2/3 occurs; duration and sampling adequacy for a negative outcome; handling of discharge/death/dialysis as competing events; cross-dataset information-availability time; precise common feature list; whether eICU cohort is clinically comparable. These must be documented and approved at data-audit gate **before** cohort extraction/training. Use versioned `docs/clinical_protocol.md` with explicit decisions and sensitivity analyses.

## 2. Clinical definitions and temporal invariants

- Use published KDIGO 2012 definitions with clinical checks. Creatinine Stage 1: >=0.3 mg/dL absolute rise over 48h, or 1.5–1.9x eligible reference; Stage 2: 2–2.9x reference; Stage 3: >=3x reference, or qualifying rise to >=4.0 mg/dL; new kidney replacement therapy is KDIGO Stage 3 but **not** part of primary creatinine-only outcome unless the protocol is formally revised. Implement full logic carefully, including boundary rules and temporal reference criteria.
- Distinguish **measurement/acquisition time** from **result availability time**; information used in predictor features or to establish the index must have been available by the prediction cutoff. In MIMIC-IV `labevents`, `charttime` and `storetime` have different meanings. In eICU offsets, do not assume a *revised-result* time proves original-result availability. If unavailable, adopt a documented conservative latency policy and sensitivity analysis, not a pretend certainty.
- Stage must be knowable by index time. First eligible index time occurs when the Stage 1 diagnostic information becomes available; audit whether Stage 1 was present before ICU and the effect of this selection.
- Outcome labels: 1 = Stage 2/3 observed after index and by index+48h; 0 = no progression with **prespecified sufficient outcome ascertainment**; unknown = insufficient follow-up or ambiguous status. A missing measurement is never proof of non-progression. Report all unknown/excluded counts and investigate selection bias. Death and discharge are not automatically negatives; competing events must be accounted for.
- Exclude patients with previously established Stage 2/3 at index and apply a prespecified policy for chronic dialysis/prior kidney replacement therapy. One index episode per eligible ICU stay; keep all admissions from a patient in the same ML split. If patient IDs are not linkable across sites, document limitation.
- Use consistent mg/dL values (after verified unit conversion), clinically plausible value rules, documented window boundary inclusivity, and verified source concept mappings. Never use measurements, interventions, discharge outcomes, or final AKI stages from after index as model predictors.

## 3. Data architecture and provenance

Recommended: Python 3.11+, DuckDB for large CSV/Parquet querying, Polars/Pandas for transformations, private Parquet intermediates. Data connectors per source; no assumptions about data file layout until schema inventory.

Canonical entities:
1. `Encounter`: source, pseudonymous internal person/encounter IDs, source hospital when available, demographics, ICU bounds.
2. `Observation`: concept, numeric value/unit, measurement time, result-available time if credible, source table/source concept, quality flags.
3. `PredictionEpisode`: encounter, index time, reference creatinine + reference methodology version, stage, outcome state, event time, follow-up status, protocol version.
4. `FeatureRecord`: one validated, time-cutoff-feature vector per episode, feature-schema version, missingness flags, source/temporal provenance.
5. `ExperimentRecord`: data version, cohort version, split hashes/IDs (private), seed, training config, model version, evaluation outputs.

Use a common feature dictionary. Candidate features, subject to harmonization: age, sex, reference and current creatinine, pre-index creatinine deltas/ratios, BUN, Na/K, hemoglobin, platelets, heart rate, MAP, respiratory rate, temperature, SpO2, historical temporal summaries, missingness and observation-age indicators. Only retain consistently defined features in the primary cross-dataset model.

No raw/restricted CSVs, person-level Parquet files, IDs, logs, model artifacts of unresolved disclosure status, or credentials in the Git repository. Store private research data and model artifacts **outside repository and outside Codex-accessible sandbox**. Code, schemas, synthetic fixtures, and permitted aggregate metrics are public-safe only after review.

## 4. Data audit — required before model development

Locally inventory exact versions, table/column names, compression/file formats, schema variants, patient/stay joins, creatinine item mappings, unit distributions, timestamps, missingness, outcome follow-up, pre-ICU historical values, chronic KRT capture, candidate features, and eICU hospital counts. Produce an **aggregate-only, disclosure-reviewed** audit report. No row dumps or free-text notes to coding agents.

Explicit gate: if equivalent Stage 1 and progression labels cannot be defined on both adult datasets, stop and redesign a scientifically honest protocol rather than manufacture external validation. Audit may uncover too few events. Record cohort flow and unknown-label rates.

## 5. ML and evaluation protocol

- Patient-grouped MIMIC train, validation, internal test. Freeze group assignments, hyperparameter selection, preprocessing, threshold policies, and calibration using development data only. Model candidate baseline: Logistic Regression; candidates: XGBoost and LightGBM. Choose final model based on prespecified validation criteria, not prestige.
- Primary ranking metric AUPRC with event prevalence; also AUROC, Brier score, calibration intercept/slope and plots, sensitivity/PPV at prespecified alert budgets, sample and event counts, and 95% intervals when defensible. Report missing outcomes and censoring selection limitations. Where intervals unavailable, state why.
- Frozen model evaluated **once** on harmonized eICU external test cohort. No fitting on target test. Optional hospital-held-out analyses and target-hospital recalibration require separate development/adaptation splits distinct from final tests.
- Reliability: input checks (schema/unit/range/missingness/time availability), population-shift summaries, calibration and selective prediction. Abstention policy/thresholds selected on development only. Report coverage, performance on retained predictions, and number/event rate of withheld progressed cases. Do **not** describe distribution shift as calibrated prediction confidence.
- Explanations: SHAP where supported, matched to transformed features and clearly labeled log-odds vs probability explanation space; model influence is **not** causality.
- Reproducibility: seeded experiments, versioned protocol/features/model, training software versions, artifact manifests, source-validated, read-only evaluation JSON served to UI. Never fabricate performance, model outputs, p-values, or confidence estimates.

## 6. System architecture

**Modular monorepo:**

```text
CM_Project/
  AGENTS.md README.md .gitignore .env.example Makefile docker-compose.yml
  frontend/        # React + TypeScript + Vite + Tailwind + shadcn/ui
  backend/         # FastAPI, Pydantic, services, repositories, API contracts
  ml/              # ingestion, clinical, harmonization, features, train, eval, reliability
  demo/synthetic/  # fully synthetic, conspicuously labeled
  experiments/configs/
  docs/            # protocols, dictionary, audit, decisions, model card, AI use, viva
  scripts/         # safe public setup/audit scaffolds, repository safety checks
  tests/           # clinical unit, synthetic integration, security
  .github/workflows/ # synthetic-only CI
```

**Runtime:** Frontend talks to backend through typed JSON HTTP APIs. Backend loads a vetted model + preprocessing + optional calibrator from a **trusted local** directory. Offline research scripts do not execute on normal API startup. SQLite for synthetic demo/app metadata; DuckDB/private Parquet for authorized experiments. Docker Compose optional after local startup works. Default bind `127.0.0.1`; research mode disabled unless explicitly configured. No auth theater: never expose research endpoints on a public interface without actual access controls.

**Prediction API contract:** `POST /api/v1/predictions` with episode ID + model ID + horizon; returns probability (or null), state (`available`, `review_required`, `withheld`, `unavailable`), machine-readable reason, provenance, validated data-quality warnings, index time, model version and feature-schema version. Do not serve arbitrary uploaded patient data from public endpoints. Return structured errors. Prediction score only from actual pipeline—not static demo JSON masquerading as inference.

**Other APIs:** `/api/v1/health`, `/api/v1/system/info`, `/api/v1/patients`, `/api/v1/patients/{id}`, `/api/v1/patients/{id}/timeline`, `/api/v1/predictions/{id}/explanation`, and read-only `/api/v1/research/{models,experiments,metrics,calibration,hospitals,reliability}`. Pydantic contracts + generated TypeScript types where practical.

**Demo mode:** synthetic encounters and trajectories; available without restricted datasets. If a validated local model is absent, prediction says unavailable. Synthetic case outcomes may illustrate workflow but are never external-validation results. **Research mode:** authorized local-only retrospective data and approved aggregate evaluation artifacts, secure by default.

## 7. Product and UX specification

Two connected modes, with persistent Research Prototype / Demo / Research badges:

**Clinical Explorer:**
- Command Center: retrospective *review* queue, counts from selected source, filters/search/sort, source/status/missingness indicators; **not** a live ICU census.
- Patient Workspace: pseudonymous demographics, index time and creatinine, key measurements, interactive kidney-function timeline, cutoff line separating available-from-future observations.
- Prediction Inspector: actual predicted probability, model/target/horizon, applicable reliability warnings, feature completeness, SHAP if valid, provenance.
- Historical Replay: at the one *validated index time*, reveal subsequent observed 48h trajectory/outcome without changing original index-time feature vector. Do not imply repeatedly validated dynamic predictions.

**Research Console:** Model comparison, internal vs external metrics, calibration, event prevalence, eligible hospital differences with minimum-cell-size policy, missingness experiments, selective prediction risk/coverage, reproducibility/limitations. Every card must read from actual artifact metadata or show `Not yet evaluated`.

Design: refined medical SaaS, accessible light UI, navy/teal neutrals, tasteful motion, Recharts/Plotly as needed, shadcn/ui, careful responsive behavior. No red/yellow/green risk tiers or medical alarm states without defined thresholds and validation. No color-only signals. No therapy recommendations.

## 8. Quality gates and schedule

| Gate | Deliverable | Required pass condition | Target |
|---|---|---|---|
| G0 | Repo/tooling/synthetic app shell | API and UI smoke tests; privacy checks | Oct 30 |
| G1 | Dataset feasibility audit | Cohort and label feasibility; clinical decisions frozen | Oct 31–Nov 1 |
| G2 | Clinical labeling | Synthetic boundary/availability/follow-up tests + cohort flow | Nov 2–3 |
| G3 | Harmonization/features | Shared schema, time-safe features, missingness report | Nov 4 |
| G4 | Baseline + candidates | Genuine held-out results; reproducible bundle | Nov 5–6 |
| G5 | External validation | Frozen MIMIC → eICU evaluation with calibration | Nov 7 |
| G6 | Real inference API | Exact saved pipeline; Pydantic tests | Nov 8 |
| G7 | React integration | End-to-end synthetic flow and model-backed inference | Nov 9–10 |
| G8 | Replay/reliability | No temporal leakage; measured reliability and honest states | Nov 11–12 |
| G9 | Release | Fresh clone demo, tests, docs, safe GitHub, viva preparation | Nov 13–14 |

Nov 15 submission tentative. The calendar is aggressive for one person; **freeze major features by Nov 13**, cut public hosting/SafeICU/extra models/fancy animation first. Do not sacrifice cohort validity, external-validation honesty, a working integrated demo, or repository security.

## 9. Mandatory safety and QA rules

- No restricted record, original ID, row-level output, sensitive log, credential, or possibly disclosive derived model/weights in Git, CI, Codex requests, screenshots, browser telemetry, or hosted services without specific approval under applicable DUAs. A `.gitignore` does **not** prevent leaks from already-tracked files; add staged-file and git-history checks.
- Do not allow Codex to read protected directories merely because it is running locally. Use OS/container filesystem isolation; do not share patient-level terminal output with cloud LLMs.
- No invented clinical constants beyond explicit reviewed KDIGO implementation. Never silently assume unmeasured outcomes negative or use all-stay minimum creatinine as known pre-index baseline.
- No test-set leakage, guessed metrics, fake model explanations, silent skip of failing tests, or fake `success` statuses.
- All stages require tests, failure reports, doc updates, small understandable commits, and a concise viva-oriented explanation of what was implemented.
- Model artifacts loaded only from trusted local paths, never untrusted uploads; package hashes/metadata validated.

## 10. Definition of done

Successful demo can launch from fresh clone with synthetic inputs; authorized local analysis can reproduce Stage 1 cohort labels, model training, internal and external evaluation; API serves **real** selected model with versioned preprocessing; React shows a working patient review/clinical timeline and genuine validation artifacts; confidentiality and disclosure review pass; methodology and model limitations are documented; developer can explain clinical definitions, leakage controls, training, generalization, inference, and UX. If scientific feasibility gate fails, document the limitation and agree to a revised outcome—do not pretend project is validated.

## 11. Approved source references (not substitutes for local dataset audit)

- KDIGO AKI guideline page: https://kdigo.org/guidelines/acute-kidney-injury/
- MIMIC-IV labevents: https://mimic.mit.edu/docs/iv/modules/hosp/labevents.html
- eICU table docs: https://eicu.mit.edu/
- SafeICU documentation: https://safeicu.aiims.edu.in/safeicu/v1.0/
- PhysioNet LLM / restricted data guidance: https://physionet.org/news/post/llm-responsible-use/
- PhysioNet credentialed data FAQ: https://physionet.org/about/faqs/

**Decision status:** Research objective and system architecture APPROVED; baseline/follow-up/timestamp ascertainment and exact common features REQUIRE G1 REVIEW. No agent may assert G1–G9 have passed without evidence.
