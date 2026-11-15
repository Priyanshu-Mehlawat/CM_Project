# RENAL-GUARD 0.2.0 — release verification

Generated 15 November 2026. Evidence applies to the current source release, not
clinical model validity. Tests used synthetic data only.

| Check | Result |
| --- | --- |
| Python clinical/API/audit/privacy tests | 42 passed |
| React interaction/contract/replay tests | 7 passed |
| Real Chromium desktop/mobile E2E tests | 2 passed |
| Ruff lint/format and ESLint | Passed |
| TypeScript and production Vite build | Passed |
| Localhost API + real Vite proxy smoke | 4 endpoint checks passed; owned processes stopped |
| Worktree/history heuristic privacy scans | Passed; staged scan runs before commit |
| Dependency install/audit | 0 known npm advisories after a targeted dev-tool minimatch override |
| Desktop/mobile visual inspection | Synthetic screenshots inspected; no horizontal overflow in mobile E2E |
| Presentation | 12 slides rendered and visually inspected; 7 main + 5 backup |
| Speaker script | 562 spoken words excluding name cues; 290-second plan, actual rehearsal required |
| Contribution attribution | Nine design workstreams explicitly supplied by user, equal cards, no ranking |
| Real clinical data, model training or independent validation | Not performed; not claimed |

Environment: Linux, Python 3.14.4, Node 22.22.1. Existing Starlette TestClient
HTTPX deprecation warning remains. Playwright emits harmless console color/path
warnings in this environment; browser checks pass. The backend requirements were
not changed. Frontend lockfile includes a targeted patched minimatch override for
lint tooling; lint and application gates were repeated successfully after it.

The committed CI workflow repeats contracts, lint, tests/build/privacy, localhost
smoke and Chromium E2E on synthetic inputs. No remote CI run is claimed here.
`make contract` checks that Pydantic-generated types/runtime schemas and synthetic
fixtures match the tracked frontend outputs.

Research gate: G1 remains pending actual isolated audit and dataset-dependent
clinical policy decisions. This release is an integrated synthetic workbench.
It does not claim a trained or clinically validated progression predictor.
