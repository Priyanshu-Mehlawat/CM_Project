# RENAL-GUARD

A local research prototype for **adult ICU Stage 1 AKI progression to Stage 2/3
within 48 hours**, version **0.3.0**.

The **Patient Assessment** page imports CSV/JSON measurements and evaluates current
creatinine stage, observed trend, timing and input coverage. A private trained
progression bundle enables actual model inference and linear influence inspection.
The offline trainer, shared feature schema and hash-checked JSON loader are now
implemented. No real-data model was trained in this agent session; prediction
quality cannot be claimed until the authorized private study is performed.

Start with [the local training and upload guide](docs/LOCAL_TRAINING.md). The app
opens at **http://127.0.0.1:5173/assess**. Existing synthetic replay is under
`/clinical`. Patient imports are opt-in in an authorized isolated environment;
synthetic template assessments work without private data or a model. This remains
a research prototype, not a patient-care tool.

Read the [project story](docs/WORKFLOW_HISTORY.md),
[review resolution](docs/review_resolution.md), and
[team contribution ledger](docs/team_contributions.md).

## Run on Linux

Tested with Python 3.14 and Node 22.22+. Source supports Python 3.11+; other Python
versions are not verified. Git and Make are required. Setup installs project-local
dependencies from lockfiles and needs network access.

```bash
git clone https://github.com/Priyanshu-Mehlawat/CM_Project.git
cd CM_Project
make setup
make hooks
```

Run in two terminals:

```bash
make dev-backend
```

```bash
make dev-frontend
```

Open **http://127.0.0.1:5173**. The API uses **http://127.0.0.1:8000**; API docs
are at `/docs`. Both services bind localhost. No accounts, seed passwords, data downloads or API keys are required.
Optional local patient imports and models are described in the training guide.

If using the existing Codex checkout, run these commands from `CM_Project/renal-guard`.

## What to demonstrate

1. Select Example A at hour 14: confirmed Stage 1, future outcome unknown.
2. Move to hour 32: the later Stage 2 observation is revealed; the index stays 14.
3. Select Example D and move from hour 14 to 20: a corrected sample removes the
   retracted abnormality and invalidates that synthetic Stage 1 episode.
4. Example C stays outcome-unknown without adequate follow-up. Example B has an
   explicit fixture-only ascertainment marker. Example E tests the Stage 3 boundary.
5. Open Research Console and Clinical Protocol to see evidence availability and
   the decisions needed before real clinical labeling or training.

Only the backend calculates stages/outcomes. The React client validates responses
against generated Pydantic schemas and never invents predictions or computes stages.
The diagram uses observed dots rather than a fabricated continuous physiologic curve.

## Verify

```bash
make lint
make test
make smoke
make contract
```

For browser checks, install Chromium once with
`cd frontend && npm exec playwright install chromium`, then run `make e2e`
from the repository root. Browser download is optional for ordinary demo use.

Tests use synthetic fixtures only. `make smoke` briefly starts owned localhost
servers and checks the real frontend proxy/API, then stops those servers. Ensure
ports 8000 and 5173 are free. `make contract` regenerates frontend contracts and
fixtures and fails if tracked output drifts. CI runs these checks without data or
research credentials. Frontend errors hide stale episode results and expose retry.

`make privacy` checks source, staged files through the hook, and reachable Git
history using heuristics. These do not certify PHI detection or replace disclosure
review. Restricted files and models must remain outside both the checkout and the
agent-readable filesystem.

## API contract

| Route | Purpose |
| --- | --- |
| `POST /api/v1/assessments` | Transient canonical patient assessment and optional model inference |
| `POST /api/v1/assessments/import` | Bounded JSON/CSV text import, unit/timing/schema validation |
| `GET /api/v1/model/status` | Installed progression model, private evaluation metrics and import status |
| `GET /api/v1/health` | Service liveness separate from model readiness |
| `GET /api/v1/system/info` | Mode, version and research gate |
| `GET /api/v1/episodes` | Five synthetic episode summaries |
| `GET /api/v1/episodes/{id}?cutoff_hour=14` | Available corrected observations, clinical stage, index and retrospective outcome |
| `POST /api/v1/predictions` | Explicit unavailable result for known episode; accepts only 48h horizon |
| `GET /api/v1/research/status` | Genuine absence of evaluation artifacts |

The development proxy gives the browser a same-origin `/api/v1` interface.
Contracts are exported with `python -m scripts.export_contract`; there is no
frontend/backend authentication or schema mismatch. Patient import is loopback-only and opt-in for authorized research records.
Model files are loaded only from an explicit trusted path plus pinned SHA256.
No dataset directories are scanned.

## Research path and limitations

**G1 remains pending.** [Clinical protocol](docs/clinical_protocol.md) and
[research plan](docs/research_plan.md) define the unresolved baseline, eligibility,
latency, negative-follow-up, competing-event and harmonization choices. The
synthetic reference and ascertainment assertions are not clinical defaults.
No real labels, training, independent evaluation or patient-care benefit is claimed.

The [offline audit runbook](docs/offline_audit_runbook.md) and
[G1 form](docs/G1_Decision_Template.md) support isolated, authorized researcher use.
The original dated stage prompts are retained under `docs/archive/2026-10-30/`.

The reviewed EliteAchievers project informed the repair priorities. Its patient
tables, onset models, exported predictions, disconnected account UI, mortality
views and external-AI summaries were not imported into the public source release.
See [migration decisions](docs/review_resolution.md) for exact scope and provenance.

## Presentation and fair attribution

The updated deck is generated separately from reviewed source under
`docs/presentation/`. [The contribution ledger](docs/team_contributions.md) gives
all nine members a concrete, equally defensible work package with evidence paths.
Proposed assignments are not represented as completed personal achievements.
Actual completed ownership requires team attestation. The 15 November workflow
entry records this software/presentation revision and its verification.


To regenerate the presentation outside the source checkout, install the optional
presentation extra in the project virtual environment and run:

```bash
.venv/bin/python -m pip install -e '.[presentation]'
.venv/bin/python scripts/build_presentation.py --output /tmp/renalguard-presentation
```

The script creates an editable PowerPoint and companion documents. PDF export
requires LibreOffice; the locally delivered PDF was rendered and visually checked.
See [release verification](docs/release_verification.md) for exact checks and limits.
