# Offline adult dataset audit template — G1

**This document is a blank review form.** It is not a completed feasibility report.
The authorized researcher fills it after executing the source-only CLI in an
isolated private environment and screening the resulting aggregate report.
Never paste patient rows, original IDs, dates, file paths, free text or unreviewed
small cells here or into an agent context.

## Execution record

- Researcher and supervisor/reviewer: **PENDING**
- Execution date, exact MIMIC-IV version and eICU-CRD version: **PENDING**
- File formats, compression and source schema variants: **PENDING**
- Private run environment and output disclosure approval: **PENDING**
- Audit code commit hash and minimum cell suppression threshold: **PENDING**
- Tables missing or failed to read: **PENDING**

## Source inventory

| Question | MIMIC-IV | eICU-CRD | Reviewed conclusion |
| --- | --- | --- | --- |
| Patient/stay/hospital join keys and coverage | PENDING | PENDING | PENDING |
| Candidate creatinine concept identifiers verified against dictionaries | PENDING | PENDING | PENDING |
| Numeric and unit distributions; conversion policy | PENDING | PENDING | PENDING |
| Measurement vs result availability fields | PENDING | PENDING | PENDING |
| Plausibility and parse failures | PENDING | PENDING | PENDING |
| Pre-ICU historical values and linkability | PENDING | PENDING | PENDING |
| Repeat creatinine patterns after candidate Stage 1 | PENDING | PENDING | PENDING |
| Chronic and new dialysis/KRT signal feasibility | PENDING | PENDING | PENDING |
| Adult eligibility and unclear ages | PENDING | PENDING | PENDING |
| Hospital counts and adequate sample/event sizes | PENDING | PENDING | PENDING |
| Death/discharge timing and follow-up | PENDING | PENDING | PENDING |

The CLI reports descriptive observations relative to ICU admission. It does **not**
produce Stage 1 index times, progression labels, negative-outcome adequacy,
unit conversions, or a clinical cohort flow. These require signed decisions and
later offline calculations; no inference should be drawn from absence of a row.

## Feasibility and disclosure review

- Are label definitions genuinely comparable across datasets? **PENDING**
- Are required signals and availability times credible? **PENDING**
- Can a reviewed baseline and adequate-negative-follow-up policy be applied? **PENDING**
- Are event rates, unknown-label rates and hospital sizes sufficient? **PENDING**
- Small-cell suppression, complementary disclosure and redaction reviewed by: **PENDING**
- Permitted aggregate summary for source repository (if any): **PENDING**
- Decision: **G1 BLOCKED PENDING AUTHORIZED HUMAN-RUN AGGREGATE AUDIT**
