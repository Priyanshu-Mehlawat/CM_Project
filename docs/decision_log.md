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

Next part: Prompt 01 source-only audit tooling, after review of this increment.
Stop here per the user's instruction to work and push in parts.
