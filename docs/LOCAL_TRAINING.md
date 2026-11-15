# From measurements to a real progression forecast

Generated 15 November 2026 · software increment 0.3.0.

The new Patient Assessment page accepts one adult ICU encounter as JSON or CSV.
It evaluates the observations, rather than selecting a canned example. Current
creatinine stage and rising/falling direction are computed from submitted values.
A separate model estimates progression from the first eligible Stage 1 index to
Stage 2/3 within 48 hours. It does not forecast all causes of clinical deterioration.
A rising creatinine is an observation, not a forecast or a clinical alarm.

The model implementation is executable, but no clinical model has been fitted in
this agent session. The authorized researcher must run the private steps below.
Do not upload private datasets, patient rows, predictions or model weights into
this chat or the source checkout. Work in an OS-isolated environment outside the
agent's readable filesystem. Source-only test fixtures do not establish clinical
performance, and a retrospective model is not ready for patient care.

## 1. Freeze the protocol and prepare the feature table

Use the existing offline audit and `G1_Decision_Template.md`. Resolve and document
baseline/reference selection, prevalent versus incident Stage 1, prior Stage 2/3,
chronic KRT eligibility, measurement/result latency, negative follow-up sufficiency,
death/discharge/KRT handling and shared feature mappings. Confirm adult ICU use.
Do not fill in approval fields just to bypass the checks. The trainer consumes
approved feature rows; it does not invent raw MIMIC/eICU mappings or outcome labels.

Create a private protocol JSON, with a real version and reviewer:

```json
{
  "version": "YOUR-APPROVED-PROTOCOL-VERSION",
  "reviewer": "YOUR-REVIEWER",
  "baseline": true,
  "eligibility": true,
  "followup": true,
  "competing_events": true,
  "availability": true,
  "harmonization": true
}
```

Create one private CSV row per eligible index episode, with these exact columns:

```text
patient_group,outcome,index_stage,features_available_by_index,age,reference_creatinine,creatinine,creatinine_ratio,creatinine_delta,heart_rate,map,respiratory_rate,spo2,temperature,bun,potassium
```

`patient_group` links every admission of the same person. Use a private pseudonym.
`outcome` is 1 for observed creatinine Stage 2/3 after index through index + 48h,
0 only with protocol-approved sufficient follow-up. Unknown is neither class:
exclude it from fitting and report its count and selection consequences in the
private cohort report. `index_stage` must be 1 and
`features_available_by_index` must literally be `true`, after a real provenance
audit. The boolean does not replace that audit.

The feature dictionary is `ml/features/patient.py`. Creatinine/reference/BUN use
mg/dL, MAP mmHg, heart rate bpm, respiratory rate /min, SpO2 %, temperature C and
potassium mmol/L. Ratio = index creatinine / reference; delta = index creatinine
minus reference. Current creatinine is the latest available at the index, not the
largest value later in the stay. For optional measurements choose the latest
measurement in the preceding 24h whose result was available by index; ties use
latest availability. Empty optional CSV fields mean missing. Five core renal/age
features must be present; at most four optional features may be missing. This
coverage cutoff is an engineering restriction, not a clinically validated rule.
Only use the first eligible Stage 1 index. Audit comparable eICU timing separately.

## 2. Fit privately

In the isolated authorized copy of the source, using its project environment:

```bash
.venv/bin/python -m scripts.train_progression \
  --features /PRIVATE/approved-index-features.csv \
  --approved-protocol /PRIVATE/approved-protocol.json \
  --data-version YOUR-COHORT-VERSION \
  --output /PRIVATE/progression-bundle.json
```

Replace `/PRIVATE` with a location outside the source checkout and agent access.
No private path is configured by default. The command needs only normal project
dependencies. It will not overwrite an existing bundle. Output files are owner-only.

A seeded 60/20/20 split is made at patient-group level, keeping admissions together.
The run requires at least 30 groups and 10 records plus both classes per split;
these are executable minimums, not a research sample-size justification. With
small or rare-event cohorts it stops rather than reporting meaningless metrics.
Medians, means, scaling and missingness indicators are fitted on training only.
The baseline is deterministic L2 logistic regression using full-batch gradients;
nonconvergence fails the run. No calibration or threshold tuning is claimed.
Validation/test data are scored without fitting preprocessing or coefficients.
The bundle contains actual split AUROC, average precision, prevalence and Brier
score; these remain private until disclosure review. Repeated model selection on
test results invalidates the test: freeze the development protocol before running.

This baseline does not complete the planned LR/XGBoost/LightGBM comparison,
external eICU study, calibration analysis, confidence intervals or prospective
validation. Do not label its internal test results external validation.

## 3. Connect the model in the authorized local app

Use the exact SHA256 printed by training. A digest verifies integrity, not scientific
validity. Review the model, clinical protocol, cohort report and actual held-out
results before enabling research use. Keep all artifacts private.

```bash
export RENAL_GUARD_MODEL_PATH=/PRIVATE/progression-bundle.json
export RENAL_GUARD_MODEL_SHA256=THE_64_CHARACTER_SHA256_FROM_TRAINING
export RENAL_GUARD_ENABLE_PATIENT_IMPORT=1
make dev-backend
```

Start `make dev-frontend` separately. The backend loads one explicitly configured
JSON bundle, never scans a model folder and never deserializes pickle/joblib.
Incorrect hashes, incompatible feature order/shapes, or synthetic-test model
provenance fail startup. `GET /api/v1/model/status` exposes installed model
metadata and actual bundle metrics. Research Console reads these instead of
repeated empty metric cards. Restart the backend to change the installed model.
Do not expose this local app on a public or shared network; it has no multiuser
authentication. Do not use external request-body logging or telemetry.

## 4. Upload and inspect

Open `http://127.0.0.1:5173/assess`. Download JSON/CSV templates there. The template
is independently synthetic, uses source `synthetic`, and illustrates the contract.
For authorized retrospective records set `source` to `authorized_research`, enter
the actual approved `protocol_version`, verified reference timing, and set the two
confirmation booleans only after checking reference/eligibility. No names, record
numbers, free text or birth dates are supported. Hours are relative to ICU entry;
negative reference/measurement times are supported within the preceding week.
CSV repeats consistent metadata for each measurement. One encounter per upload.

Measurements require concept, value, unit, measured_hour and available_hour. Only
supported units/ranges are accepted; creatinine umol/L converts by dividing 88.4.
Range checks detect unsupported inputs, not complete clinical plausibility. Resolve
corrected/duplicate samples before import; duplicate concept/measurement times are
rejected. Measurements unavailable at cutoff are excluded; baseline must already
be known. Assessment requires serial creatinine and an eligible reference window;
vitals alone cannot establish creatinine-defined AKI progression.

The application shows current creatinine stage, last-measurement change, Stage 1
index, missing inputs, warnings and index-time model inputs. If a compatible real
bundle is installed it returns an actual computed probability and exact linear
log-odds contributions, which are influences rather than causal explanations.
The estimate is explicitly uncalibrated. There is no arbitrary high/low risk tier.
If current status is outside Stage 1, progression was already observed, the 48h
window has expired, protocol differs or input coverage fails, the forecast is
withheld with a concrete reason. A forecast is frozen at index; uploading later
vitals does not imply a separately validated dynamic model.

Uploads use bounded POST bodies and memory-only processing. The API rejects
non-loopback patient-import clients and unapproved browser origins, uses no-store
responses, redacts validation errors and does not log bodies. The app does not
save uploads in a database, browser storage or third-party service. The operating
system/browser may still retain memory; clear the session when finished.

## What to share back

Share only disclosure-reviewed aggregates and protocol decisions: cohort/exclusion
counts (suppress small cells), unknown-label rates, grouped split counts, actual
held-out metrics/calibration findings, dataset versions, approved protocol version
and model-loading success/failure. Do not share patient-level rows, private paths,
weights or individual predictions. This is the next evidence needed to evaluate
whether the prototype's real-data predictions are useful.

Criteria reference: [KDIGO 2012 AKI guideline, chapter 2.1](https://kdigo.org/wp-content/uploads/2016/10/KDIGO-2012-AKI-Guideline-English.pdf).
The creatinine branch is implemented; urine output and KRT criteria are outside
this primary outcome. Clinical review and real-data evaluation remain required.
