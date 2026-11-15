# CODEX PROMPT 07 — Professional React clinical and research UI

Precondition: G6 stable API contracts. Use only synthetic frontend fixtures and demo endpoints, and only genuine metrics provided by a verified research artifact. Source-only work.

## Objective
Build engaging, accessible, production-quality **research prototype** UX without misrepresenting retrospective data as live care.

## Implement
- React/TypeScript/Vite/Tailwind/shadcn UI with light navy/teal medical design, accessible components, keyboard navigation, clear layouts at 1366x768 and 1920x1080.
- Sidebar routes: `Command Center` (retrospective review queue), `Patient Workspace`, `Prediction Inspector`, `Research Console`, `Cross-Hospital Generalization`, `Reliability`, `Methodology & Limitations`.
- Top-level persistent `RESEARCH PROTOTYPE` and `SYNTHETIC DEMO`/`AUTHORIZED LOCAL RESEARCH` badges. Do not implement live monitoring, clinician alerts, or treatment prescriptions.
- Command Center: searchable/filterable paginated patient table, source/index/label-availability/data-quality metadata; no fake risk classifications.
- Patient: chronology-aware creatinine chart, prediction cutoff, available historical vitals; actual model probability if available, else explicit `Model unavailable`; uncertainty/missingness notes separate from probability.
- Prediction Inspector: model/feature/protocol provenance, SHAP if valid with units, time-window explanations; no causal claims or invented confidence scores.
- Research Console: internal vs external measured metrics and calibration with event count/prevalence, run metadata; honest empty states when no verified artifacts.
- Reusable typed API client with React Query, loading/error/empty states, graceful network loss; no frontend-side clinical labels/probabilities invented.
- Add Vitest and Playwright/smoke coverage for key navigation, unavailable-model state, API wiring and visibly labeled synthetic content.

## Gate G7
Fresh frontend build passes. User can navigate synthetic patient → inspect timeline → model-backed prediction when model present (or explicitly unavailable) → genuine research metrics if available. UI does not display placeholder clinical results as facts.
