# RENAL-GUARD progression study — protocol decisions and experiment plan

Version 0.2 · 15 November 2026. Source-only plan, not a completed experiment.

The primary question remains adult ICU first confirmed creatinine-based Stage 1
→ creatinine-based Stage 2/3 in (index, index + 48 hours]. The 24-hour onset models
in EliteAchievers cannot be repurposed by changing their label or display text.

## Required gate before extraction and training

G1 is pending. A researcher must approve dataset releases, eligibility, reference
creatinine, observation/result availability, adequate negative ascertainment,
death/discharge/KRT handling, shared features and disclosure thresholds. The
synthetic engine requires an explicit fixture reference; it does not choose a
patient's baseline. Synthetic negative ascertainment is an explicit assertion
inside one fixture and must never become a default clinical follow-up rule.

## Feature dictionary — candidates only

| Group | Candidate information available by index | Verification needed |
| --- | --- | --- |
| Demographics | Adult age, recorded sex | Source definitions, linkage and age uncertainty |
| Renal labs | Reference/current creatinine, prior changes, BUN | Reference policy, units and collection/result times |
| General labs | Potassium, bicarbonate, hemoglobin, platelets | Source concepts, units and missingness |
| Physiology | MAP, heart rate, respiratory rate, temperature, SpO2 | Measurement definition and credible availability |
| Observation process | Age of last measurement and missingness | Comparable observation practice; selection bias |

Interventions, urine output and KRT are conditional secondary analyses, not silently
combined with the primary creatinine outcome. No unverified exposure is active.

## Reproducible comparison

Freeze patient-level train/validation/internal-test assignments. All stays of a
patient stay together. Fit imputation/scaling on training only. Establish an
intercept/prevalence benchmark and Logistic Regression; compare XGBoost under a
prespecified development budget. LightGBM is optional, not an achieved result.
Choose hyperparameters, calibrator and any threshold on development/validation
only, with reasons recorded before opening the test set.

Primary ranking metric: AUPRC with event prevalence. Also report AUROC, Brier,
calibration plot/intercept/slope, eligible samples/events and unknown outcomes.
Use patient-block uncertainty intervals when defensible. State the dependence
and remaining uncertainty. A nonlinear model is not automatically superior.

## External evaluation

Check that a common feature schema and equivalent labels are feasible. Freeze the
MIMIC pipeline before one eICU external test. Never train or tune on that test.
A separately prespecified adaptation cohort is needed for target recalibration.
Do not call previously inspected audit patients independent fresh validation.
Hospital holdouts of a different baseline do not validate the selected model.

## Reliability and release

Availability and missingness checks are separate from confidence. Input sensitivity
is not a probability confidence interval. SHAP is optional and non-causal. No
probability is served without a trusted, versioned progression pipeline and reviewed
evaluation. Real artifacts and restricted rows remain outside the source checkout
and agent-readable filesystem. Current API inference explicitly returns unavailable.

## Practical decisions made for the prototype

The user authorized engineering choices without waiting for supervisor review.
We therefore implement only source-level, synthetic mechanics with explicit
reference and ascertainment inputs. The fixed 48-hour target, mg/dL units,
measurement/result-time separation and correction semantics are testable now.
They do not require pretending that unobserved measurements are known.

Candidate clinical policies remain draft until the offline feasibility audit can
establish usable historical references and repeat testing. We do not resolve an
unknown baseline by using future recovery; we do not resolve insufficient
follow-up by assigning zero. These are substantive scientific limits rather
than a conversational approval step that can be skipped to make a demo look done.
