# RENAL-GUARD 0.2 — integrated synthetic workbench

Browser → React/Vite 127.0.0.1:5173 → same-origin `/api/v1` proxy → FastAPI
127.0.0.1:8000 → canonical creatinine engine and independent synthetic fixtures.
No patient-data connectors or artifact loaders run at application startup.

Pydantic contracts generate TypeScript types, runtime schemas and public synthetic
response fixtures. `make contract` detects drift. The browser validates response
shapes, renders only backend assessments, and cancels older requests on replay or
case changes. Failed requests hide stale data. The chart renders corrected,
available samples only; it does not calculate clinical stages or outcomes.

The API owns first-confirmed synthetic Stage 1 indexing and three-state outcomes.
The arithmetic requires an explicit earlier reference. Corrections replace a
sample only once available. A synthetic retraction invalidates that fixture's
Stage 1 episode. Only observations collected after index and within 48 hours may
form a progressed outcome. Adequate-negative ascertainment is an explicit fixture
assertion, not a clinical rule inferred from absence of events.

Inference returns explicit unavailable, with null probability. Research status
returns no metrics until genuine artifacts exist. Research mode fails closed.
No fake account layer, seeded credentials, mortality display or external AI
summaries are present. CORS is limited to explicit localhost origins; it is not
access control for a future research runtime.

Tests cover Python arithmetic, API/error contracts, React interactions, real
localhost proxy smoke and Chromium end-to-end desktop/mobile workflows. CI uses
synthetic data only. The source-only DuckDB audit stays outside normal runtime
and requires isolated authorized execution for any actual dataset.
