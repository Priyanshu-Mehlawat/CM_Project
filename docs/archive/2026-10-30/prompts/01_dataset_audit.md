# CODEX PROMPT 01 — Privacy-safe adult dataset audit, source code only

Read the master spec and `AGENTS.md`. G0 must pass. **DO NOT read, list, inspect, or process real patient-level MIMIC, eICU, or SafeICU files yourself or via agent tools.** Generate a reusable local offline audit CLI and synthetic tests only. The authorized researcher will execute it separately outside Codex's accessible environment.

## Objective
Build an auditable data inventory and clinical-feasibility program for exact locally installed MIMIC-IV and eICU files, whose versions/formats are not yet confirmed.

## Implement
1. Command-line audit executable taking explicitly supplied **external private** dataset paths from environment or CLI at *human runtime*, with no path defaults pointing to protected locations and no execution by Codex against real data. Support CSV and compressed CSV; where possible DuckDB schema/projection queries without full memory load.
2. Adapter-based table/column discovery; source mapping stubs for MIMIC: `patients`, `admissions`, `icustays`, `labevents`, `d_labitems`, `chartevents`, `d_items`; eICU: `patient`, `hospital`, `lab`, `vitalPeriodic`, `vitalAperiodic` (verify actual names/version on future local audit). No unsupported assumptions.
3. Schema/dtype/count/unit/missingness audit; creatinine concept candidate extraction, timestamp/offset inventory, patient/stay linkage checks, pre-index historical observation availability, follow-up measurement patterns, hospital-level feasibility, dialysis signal inventory, potential cohort flow.
4. **Aggregate-only output:** local JSON/Markdown summary with no patient rows or IDs and small-cell suppression/configurable minimum-cell count. Store any other output only in designated private location with human approval. Do not print patient values, IDs, original dates, free text, or file paths to agent-visible logs.
5. Add synthetic sample inputs for MIMIC-like/eICU-like schema and tests of tables missing, dtype variants, unit conversion errors, offsets, and suppressed counts. Make user-facing `--help` and `--dry-run` safe; explain that `--dry-run` must not probe protected folders under agent control.
6. Generate `docs/dataset_audit_template.md` and clinical `G1_Decision_Template.md` listing baseline, availability cutoff, ICU-present Stage1, dialysis, competing death/discharge, negative-label adequacy, hospital minimum counts, and cross-dataset compatibility decisions requiring human review.

## Gate G1
Codex tests audit code with **synthetic fixtures only**; do not claim real cohort feasibility. Clearly mark `G1 BLOCKED PENDING AUTHORIZED HUMAN-RUN AGGREGATE AUDIT`. Show command templates with private paths represented only as placeholders and an isolated execution method. Ask for only disclosure-reviewed, sufficiently aggregated output summaries. No real labeling/training before G1 research decisions are approved.
