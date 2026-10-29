# Stage 00 architecture

Browser → React/Vite on 127.0.0.1:5173 → `/api` proxy → FastAPI on 127.0.0.1:8000.
The API responds from typed Python code with two independently invented examples.
No persistence, patient file access, clinical stage calculation, inference or
artifact loading exists. No external fonts, analytics or telemetry are configured.

- `GET /api/v1/health`: service alive separately from model availability.
- `GET /api/v1/system/info`: version, synthetic mode, pending protocol and evaluation.
- `GET /api/v1/demo/cases`: synthetic provenance, null stage/probability.

Contracts carry `schema_version: v1`. Unsupported routes/methods return redacted
structured errors. CORS accepts the two explicit localhost frontend origins only.
CORS is not authentication; research endpoints must acquire real access controls
in a later stage before any private use. Default dev commands bind localhost.

The frontend validates the synthetic response contract before displaying fixtures.
It makes no clinical calculations. Failure presents an actionable empty state.
Tailwind v4, shadcn component configuration/aliases and a locally owned native
button establish the UI foundation; larger components arrive with later work.

The `ml/` modules are placeholders. DuckDB/Polars, SQLite metadata, model pipelines,
trusted bundle verification and prediction/research APIs are deferred to their
respective prompts. Synthetic-only CI has read-only repository permission and no
research credentials or data download steps.
