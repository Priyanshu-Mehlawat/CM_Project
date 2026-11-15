# Team contribution and evidence ledger

Version 3.1 · Generated 15 November 2026 (Asia/Kolkata).

The user supplied the nine individual deliverables below on 15 November 2026.
These are **team-confirmed proposal/design contributions**, not inferred from Git
ownership and not claims of completed clinical experiments. No ranking is used:
each member receives equal presentation space and a substantive oral-defense topic.

| Member | Confirmed proposal/design deliverable | Specific reasoning to explain | Corresponding project material |
| --- | --- | --- | --- |
| Priyanshu Mehlawat · 2024443 | Research methodology, end-to-end system architecture, prediction framework and hypothesis | Explain the Stage 1 index, 48-hour progression question and complete research-to-application flow | `docs/research_plan.md`, `docs/architecture.md` |
| Rishi Srivastava · 2024467 | Proposed KDIGO staging algorithm, cohort inclusion criteria and 48-hour progression-labeling logic | Defend reference requirements, Stage 3 boundaries and unknown follow-up handling | `docs/clinical_protocol.md`, `ml/clinical/creatinine.py` |
| Shaurya Tyagi · 2024525 | Clinical feature selection, missing-data strategy and temporal leakage-prevention plan | Explain pre-index feature availability and training-only missingness handling | Feature dictionary and split/preprocessing plan in `docs/research_plan.md` |
| Ayan Ahmed · 2024143 | Evaluation framework: AUROC, AUPRC, calibration and external validation | Explain prevalence, probability calibration and a frozen external test | Evaluation plan in `docs/research_plan.md` |
| Hemendra Pahwa · 2024258 | Comparison of Logistic Regression, XGBoost and LightGBM with selection rationale | Defend baseline-first comparison and development-only model selection | Model-comparison plan in `docs/research_plan.md` |
| Tejas Singh Bidhuri · 2024590 | Clinical dashboard wireframe, risk visualization and interaction workflow | Trace a case through selection, availability-aware replay and evidence states | `frontend/src/App.tsx`, `docs/architecture.md` |
| Harshit Kumar · 2024248 | Literature review: AKI significance, existing prediction approaches and research gaps | Position progression relative to onset and prior progression studies | Verified references in `docs/presentation/content.json` |
| Shourya Swami · 2024537 | MIMIC-IV/eICU dataset analysis: tables, variables and access requirements | Compare documented source schemas and access; distinguish documentation analysis from data extraction | `ml/ingestion/audit_catalog.py`, `docs/offline_audit_runbook.md` |
| Priyanshu · 2024441 | Backend architecture, proposed API endpoints and inference workflow | Explain the canonical API, schema generation and honest unavailable-model response | `backend/app/main.py`, `scripts/export_contract.py` |

## Evidence interpretation

The attribution source is the team's explicit statement, not independent authorship
verification. The material column points to where the workstream is represented
in the integrated project; it does **not** claim each member authored every line
in that file. Software repair was AI-assisted under the user's instructions.

Dataset analysis here means documentation/schema/access analysis. The team has
not supplied an authorized extracted cohort, clinically approved labels, trained
progression model or independent evaluation. Model comparison is a rationale and
plan; no winning algorithm or measured superiority is claimed.

## Per-member assessment preparation

Each member should bring their own notes, diagram, draft or dated design review,
explain one design choice and one limitation, and identify their current next step.
Add original individual artifact links or dated team attestation as available;
no commit chronology or document date should be invented retrospectively.

| Version | Date | Change |
| --- | --- | --- |
| 2.0 | 14 November 2026 | Ownership confirmation fields; initial roster inference later superseded. |
| 2.1 | 14 November 2026 | User-confirmed nine-member roster, provisional speaking responsibilities. |
| 3.0 | 15 November 2026 | Specific accountable work packages and evidence requirements. |
| 3.1 | 15 November 2026 | Replaced provisional roles with the user's nine confirmed proposal/design deliverables; removed ranking and unverified implementation credit. |
