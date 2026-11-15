# Review resolution and migration decisions

Version 0.2 · 15 November 2026.

Reviewed upstream: RishiSrivastava2310/EliteAchievers at
`75718c28d14a09402d034d7937c6c7430ee98108`. Its clinical tests, availability/revision
handling and explicit scientific limits informed this repair. Its repository is
preserved unchanged as a local reference. No upstream patient files, serialized
models, credentials, generated predictions, test-temp folders or web-AI calls were
copied into this repository. The source implementation here is independently
written; the original repository's attribution and authorship are not rewritten.

| Review issue | Resolution in this repository | Evidence |
| --- | --- | --- |
| Incompatible login/data routes | One `/api/v1` contract, same-origin Vite proxy, no demo-account auth theater | `scripts/export_contract.py`, API/React tests, smoke command |
| 24h onset vs 48h progression | Source and UI explicitly use first Stage 1 → Stage 2/3 over 48h | `backend/app/episodes.py`, `docs/research_plan.md` |
| Browser duplicates clinical engine | Browser renders backend-computed assessments only | `frontend/src/App.tsx`; no browser staging module |
| Wrong ≥4.0 Stage 3 branch | AKI first; ratio can establish AKI before 4.0 branch | `tests/test_progression.py` |
| Retracted abnormal lab retained | Collapse samples by identity and latest available revision | `ml/clinical/creatinine.py` |
| Expired reference treated as adequate | Explicit earlier reference within seven days required; unknown otherwise | Clinical boundary tests |
| Missing UI tests | Committed interaction and generated-contract tests | `frontend/src/App.test.tsx` |
| Hidden API/schema drift | Generated response types/runtime schemas; drift checked in CI | `make contract` |
| Temporal validation overclaim | Research metrics absent until genuine evaluation; no temporal-holdout claim | Research Console |
| Uncertain eICU latency | Remains explicit G1 decision with sensitivity requirement | Clinical protocol and audit handoff |
| Current dependency advisory upstream | This frontend's lockfile uses Vite 6.4.5; audit rechecked for release | Frontend lockfile |
| Vague/unfair contribution log | Nine equal, specific accountable deliverables; completed credit requires evidence | `docs/team_contributions.md` and revised deck |

The current release is an integrated **synthetic research workbench**, not the
completed clinical model study. It fixes source/application issues that can be
resolved without inventing missing protocol decisions or experiments. Training,
independent validation and prospective benefit are explicitly unfinished.

Removed/superseded: the two unused Stage 00 placeholder cases and `/demo/cases`
endpoint; disconnected account conventions, onset scores, mortality graphs and
external AI summaries were not migrated. We retained the research specification,
source-only audit tools, license, privacy checks, Linux setup and decision history.
