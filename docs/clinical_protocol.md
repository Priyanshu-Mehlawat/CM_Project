# Clinical protocol — draft, pending G1

Version: draft-1 (15 November 2026). No clinical labels or training authorized by this document.

Stage 01 provides offline inventory code only. Its ICU-admission timing patterns
are descriptive and cannot establish a Stage 1 index, negative follow-up adequacy,
or comparable external labels. See `G1_Decision_Template.md` for the reviewer form.

Approved study objective: adult ICU, first confirmed creatinine-based Stage 1
assessment, progression to creatinine-based Stage 2/3 within 48 hours. The clinical
engine now tests KDIGO 2012 creatinine arithmetic with an explicit synthetic
reference and synthetic follow-up assertions. It does not select research baselines
or generate real labels. The boundary criteria were checked against the official
2012 guideline, chapter 2.1; these tests do not constitute clinical protocol approval.

| Decision | Status |
| --- | --- |
| Dataset versions and verified source mappings | Pending audit |
| Baseline/reference creatinine, lookback and available history | Pending human review |
| Present vs incident Stage 1, prior Stage 2/3, chronic KRT and eligibility | Pending human review |
| Measurement time vs result availability; eICU latency sensitivity policy | Pending audit and review |
| Adequate follow-up for negatives; death/discharge/KRT handling | Pending human review |
| Unit conversions and precise boundary tests | Pending independent verification |
| Common features and comparable cohort definitions | Pending harmonization review |
| Disclosure thresholds for released aggregates | Pending governance review |

Outcome unknown is distinct from negative. No all-stay minimum baseline, clinical
latency, or follow-up rule has been selected. Record reviewer, date, rationale,
version and sensitivity plan for each decision before G2 begins.

Synthetic regressions cover delayed results, retracted corrections, ≥4.0 mg/dL
after ratio-defined AKI, expired reference windows and exact 48-hour endpoints.
Real-data availability latency and negative ascertainment remain unresolved.
