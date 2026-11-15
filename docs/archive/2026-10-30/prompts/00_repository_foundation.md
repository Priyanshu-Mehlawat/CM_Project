# CODEX PROMPT 00 — Repository foundation and safe synthetic scaffold

Read `AGENTS.md` and `docs/MASTER_SPECIFICATION.md` (or `MASTER_SPECIFICATION.md` if copied at root). Treat their prohibitions as binding. Work only inside the source-code repository. **Do not access, enumerate, or read restricted datasets or directories; do not attempt network downloads of datasets.** Do not push commits without my approval.

## Objective
Prepare a reproducible Linux monorepo for RENAL-GUARD while keeping the existing README/LICENSE intact unless improvements are necessary.

## Implement
1. Inventory public repository state and create a concise plan without inspecting protected paths.
2. Create skeleton `frontend/` using React + TypeScript + Vite, Tailwind, shadcn/ui setup; initialize accessible header/sidebar and two route placeholders `Clinical Explorer` and `Research Console`, conspicuous `SYNTHETIC DEMO / RESEARCH PROTOTYPE` badge. Do **not** invent risk scores.
3. Create `backend/` using FastAPI + Pydantic with `/api/v1/health`, `/api/v1/system/info`, Pydantic versioned responses, CORS restricted to local origin, uvicorn localhost default, and structured errors. Provide a health endpoint that distinguishes service alive from model available.
4. Add Python package skeleton `ml/` with `clinical`, `ingestion`, `features`, `training`, `evaluation`, `reliability`, and synthetic testing fixtures. No real data yet.
5. Add `.env.example` with safe placeholders (NOT any secrets), `.gitignore` for credentials/model artifacts/CSV/Parquet/sqlite/logs/private folders, `Makefile` with `setup`, `test`, `dev-backend`, `dev-frontend`, `lint` targets when available; minimal Docker skeleton optional.
6. Create `docs/decision_log.md`, `docs/clinical_protocol.md` with **pending** baseline/outcome policies, `docs/data_governance.md`, `docs/architecture.md`, `docs/viva_preparation.md`, and `README.md` that honestly states implementation status.
7. Create synthetic-only CI for Python tests, frontend lint/type/build, secret checks; add a staged-file denylist or safeguards for data file extensions and generic secrets. `gitignore` alone is not enough. Never claim fully automated PHI detection.
8. Add small working synthetic UI fixture with no patient resemblance and no output fabricated as actual model inference. If model absent, show explicit `Model unavailable`.

## Constraints
- Avoid overengineering (Kubernetes, Redis, queues, cloud DBs). No public remote dataset access, no external telemetry.
- Tests must not require protected data. Do not access any directory outside agent-approved source scope. If tooling requires network approval, ask before proceeding.
- Keep root README helpful and repository clean.

## Acceptance / Gate G0
- Backend health and frontend dev server start using documented commands.
- Backend tests pass; frontend typecheck/build pass, or clearly report blockers.
- Synthetic UI opens without model or private data.
- `git status` and `git diff --stat` reviewed; no secrets/restricted files staged.
- Explain exactly how I can repeat setup and checks. End with `Files changed`, `Commands/tests`, `Gate G0 status`, `Blockers`, `Next prompt`.
