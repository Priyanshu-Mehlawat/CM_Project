# RENAL-GUARD

A local research prototype for studying adult ICU **Stage 1 AKI progression to
Stage 2/3 within 48 hours**, with planned MIMIC-IV development and harmonized eICU
external evaluation. This is an educational research project, not a clinical tool.

**Current increment: Stage 01 — offline dataset audit tooling.** Stage 00's
synthetic application foundation remains available. No clinical labeling,
training, prediction, or evaluation has been performed. The API and UI explicitly
report **Model unavailable** and **Not yet evaluated**.

Start with the [project story and version history](docs/WORKFLOW_HISTORY.md)
for a readable account of every completed increment and why it was built.

## What works

- React/TypeScript/Vite frontend with Clinical Explorer and Research Console routes.
- Persistent Synthetic Demo / Research Prototype notices, selectable invented
  examples, provenance details, API connection/retry and empty states.
- FastAPI/Pydantic versioned health, system information and synthetic case APIs.
- Local-only defaults, restricted CORS, redacted structured errors, fail-closed
  research-mode configuration, and no data connectors or model loading.
- Python tests, UI interaction tests, frontend lint/type/build checks, synthetic-only
  CI, and source/staged/history file and secret safeguards.
- Modular `ml/` placeholders and the original implementation package under `docs/`.
- A DuckDB-based offline audit CLI for explicitly listed MIMIC-IV/eICU CSV or
  compressed CSV tables. It inventories candidate schemas, count buckets,
  missingness, creatinine/unit patterns, timestamps, linkage, pre-ICU and early
  post-admission observations, optional dialysis signals, and hospital coverage.
  It produces no clinical labels and has run only on invented temporary fixtures.

## Run locally

Requirements: Linux, Python **3.14** (the tested environment), Node **22.22+**,
`npm`, Git and Make. Dependency installation needs internet access. The source
allows Python 3.11+, but other Python versions have not been verified yet.

```bash
git clone https://github.com/Priyanshu-Mehlawat/CM_Project.git
cd CM_Project
make setup
make hooks
```

If using the checkout prepared by Codex, start in `CM_Project/renal-guard` instead
of cloning again. `make hooks` enables the included local pre-commit safeguard.

Run in separate terminals from the repository root:

```bash
make dev-backend
```

```bash
make dev-frontend
```

Open **http://127.0.0.1:5173**. The frontend proxies `/api` to
**http://127.0.0.1:8000**. The services bind to localhost. API docs are at
http://127.0.0.1:8000/docs. No environment file, dataset, GPU or model is required.
The `.env.example` documents the supported mode; `.env` loading is not enabled.

## Stage 01 audit handoff

**G1 BLOCKED PENDING AUTHORIZED HUMAN-RUN AGGREGATE AUDIT.** The audit requires
credentialed files and must run separately in an isolated research environment.
Codex has not inspected or processed those files. The [runbook](docs/offline_audit_runbook.md)
shows the private manifest format, setup, `--dry-run`, and actual offline command.
The [audit template](docs/dataset_audit_template.md) and
[G1 decision template](docs/G1_Decision_Template.md) list the evidence and
human-reviewed decisions needed before Stage 02. Do not put a private manifest,
audit output, patient data, or reviewed source paths in the repository.

The CLI writes aggregate JSON and Markdown to an explicitly supplied private
directory. Counts below the configured minimum are suppressed; larger counts
are bucketed. Its candidate mappings and text searches are **unverified**.
An authorized reviewer must still check every aggregate for disclosure risk
before sharing it.

## Check the increment

```bash
make lint
make test
```

`make test` runs Python tests, UI interaction tests, TypeScript checking, a
production frontend build, and worktree/history safeguards. CI runs the same
synthetic checks. Dependencies are pinned in `requirements-dev.lock` and
`frontend/package-lock.json`. The Python lock was captured on Linux/Python 3.14.
The production UI build is in ignored `frontend/dist/`; API integration is
configured for the Vite development server at this stage.

The included privacy scanner is a **heuristic**, not proof of de-identification.
It checks tracked/unignored source, staged blobs, and reachable Git history;
it does not traverse ignored private files. It rejects prohibited file categories
before reading their contents and never prints matching secrets. Human disclosure
review and filesystem isolation are still required.

## Layout

| Path | Purpose |
| --- | --- |
| `backend/app/` | FastAPI app, response contracts and invented demo cases |
| `frontend/` | React shell, Tailwind and locally owned UI primitive |
| `ml/ingestion/` | Offline source schema candidates and aggregate audit program |
| `ml/clinical/`, `ml/features/`, `ml/training/`, `ml/evaluation/` | Pending later gates |
| `tests/` | Synthetic API and repository safeguard tests |
| `scripts/` | Source-only repository checks and offline audit CLI |
| `docs/` | Specification, decisions, governance, architecture and staged prompts |

The shadcn configuration and a native accessible button are included; a full
component library and clinical dashboard belong to later stages.

## Research gates and next part

Stage 01 adds the source-only feasibility audit. See
[the decision log](docs/decision_log.md) for validation evidence and limitations.
The next engineering increment is [Prompt 02 — clinical engine](docs/prompts/02_kdigo_clinical_engine.md),
which requires the G1 decisions to be reviewed and frozen first.

**G1 remains pending.** Dataset versions, baseline creatinine, eligibility,
result-availability timing, adequate negative-outcome follow-up/competing events,
and shared cross-dataset features require human-reviewed audit decisions before
clinical labeling or training. Missing follow-up must remain unknown, not negative.

Keep credentialed datasets outside both the repository and the agent's readable
filesystem using OS/container isolation. Do not share patient rows, original IDs,
private model artifacts or unreviewed outputs with coding agents or CI. No private
data location is configured by this application.

Read [AGENTS.md](AGENTS.md), [the master specification](docs/MASTER_SPECIFICATION.md)
and [the clinical protocol](docs/clinical_protocol.md) before later implementation.
