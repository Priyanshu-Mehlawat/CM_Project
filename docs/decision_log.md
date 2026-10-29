# Decision log

## 2026-10-30 — Stage 00 foundation increment

Scope: Prompt 00 only. Source repository cloned into `CM_Project/renal-guard`;
original LICENSE preserved. User explicitly requested a limited increment, updated
README, commit and push. No later implementation stages are included.

- Synthetic-only runtime; research mode unavailable at this stage.
- Model, clinical labels, probability, explanations and evaluation unavailable.
- G1 pending: dataset versions, eligibility, reference creatinine, outcome
  ascertainment/competing events, result availability and shared feature mappings.
- No restricted data locations configured or accessed. Runtime never scans paths.
- OS-level isolation of any credentialed datasets remains the researcher's
  responsibility before offline analysis; this session cannot certify isolation.
- React/Vite/Tailwind, accessible shadcn-style primitives; FastAPI/Pydantic.
- G0 checks and evidence recorded below after implementation.

## Validation evidence

- Python 3.14.4 / Node 22.22.1; project-local dependencies and lockfiles.
- 21 Python tests passed. Sandboxed FastAPI TestClient hung under socket
  restrictions; the same suite passed with permission outside that sandbox.
- 4 frontend interaction tests passed, including navigation, selection, retry,
  empty data, and rejecting incompatible numeric scores.
- Ruff lint/format, ESLint, TypeScript check and Vite production build passed.
- Worktree, staged-file and reachable-history heuristic checks passed.
- Localhost HTTP smoke: API health, both UI routes, and proxied synthetic cases
  returned 200. Owned servers stopped after checks.
- Updated Vitest to 5.0.5 after initial npm advisories; install audit reports
  zero known vulnerabilities in the resolved frontend dependency tree.
- Existing Starlette warning: HTTPX TestClient support is deprecated. Tests pass;
  client migration remains a future dependency-maintenance task.

Gate G0: automated acceptance checks passed; this is the software foundation only.
Manual visual/browser review and clean-machine setup have not been performed;
CI is configured but no remote run is claimed. G1 through G9 remain pending.

Assumptions requiring human approval: all G1 clinical/data policies listed in
`clinical_protocol.md`; no defaults have been invented for them.

Next part at that time: Prompt 01 source-only audit tooling. The user later
requested the next roughly 10% increment and authorized its commit and push.

## 2026-10-30 — Stage 01 source-only audit increment

Scope: Prompt 01's offline feasibility inventory and human decision templates.
The user asked for roughly one additional tenth of the project, a README update,
an appropriate commit, and a GitHub push. No real MIMIC-IV, eICU or SafeICU
data was read, enumerated, downloaded, or used by Codex. All tests use
independently authored temporary CSV fixtures.

- Explicit table-path manifest; no dataset path defaults or directory scanning.
- DuckDB inventory of candidate schema/types, count buckets, missingness,
  creatinine text/unit/numeric patterns, timestamps, linkage, ICU-admission
  observation patterns, dialysis text candidates and eICU hospital coverage.
- G1 templates and isolated researcher runbook provided. Source names and
  clinical concepts still require verification against actual versions.
- CLI report withholds raw paths, IDs, dates, free text and row values, suppresses
  cells below minimum 11, buckets larger counts and writes owner-only files
  outside the source checkout. This is a heuristic disclosure barrier; a human
  must review combined aggregates before any result is shared.
- No baseline method, Stage 1 index, negative follow-up rule, cohort flow,
  outcome label, conversion or cross-dataset comparability decision was inferred.

Validation: 28 Python tests passed; 4 frontend tests passed; Ruff and ESLint
passed; TypeScript check and Vite build passed; worktree and reachable-history
heuristic scans passed. `--help` and `--dry-run` worked without touching a
manifest. One pre-existing Starlette TestClient deprecation warning remains.
No private-data execution, independent browser review or remote CI result is
claimed. The staged-file scan runs before the commit.

**Gate G1: BLOCKED PENDING AUTHORIZED HUMAN-RUN AGGREGATE AUDIT.** Stage 01 code
is ready for isolated researcher use; G1 scientific acceptance is not achieved.
All policies in `G1_Decision_Template.md` require human review and approval.
Next engineering stage is Prompt 02 only after those decisions are frozen.
