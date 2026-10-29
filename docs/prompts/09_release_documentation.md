# CODEX PROMPT 09 — Release verification, GitHub security, documentation and viva

Precondition: G0–G8 statuses documented, failures/omissions explicit. No protected data access by agent.

## Objective
Prepare Nov 13–14 release candidate and a strong reproducible demonstration.

## Implement
- Run backend/unit/integration/frontend/typecheck/build/synthetic E2E checks. Do not skip tests to get a green result. Audit API and UI behavior with/without model/evaluation artifacts.
- Threat review: no patient IDs, raw data, credentials, private paths, model artifacts of unapproved disclosure status, logs, browser telemetry, restricted files in repo or Git history. Stage/commit scan; explain limits of automated scans. Do not push changes without explicit approval.
- README with project research question, Group 31, scientific novelty vs onset, local-first setup, synthetic demo, external validation reproducibility for authorized users, CLI recipes with placeholders only, UI screenshots **from synthetic demo only**, limitations, intended use, references.
- `docs/clinical_protocol.md`, `docs/research_methodology.md`, `docs/data_dictionary.md`, `docs/data_governance.md`, `docs/decision_log.md`, `docs/architecture.md`, `docs/api_contracts.md`, `docs/model_card.md`, `docs/reproducibility.md`, `docs/ai_assistance.md`, `docs/viva_preparation.md` updated to reflect actual code/results, not imagined completion.
- Final model card explicitly lists development/test sources and versions, eligibility, feature definitions, metrics/event prevalence, calibration and transportability limitations, deployment prohibition, known biases, unmeasured outcomes.
- Prepare deterministic 5–7 minute demo script: overview → patient → index-time prediction → retrospective outcome reveal → explanation/reliability → genuine external validation. If real model unavailable, say so explicitly and demonstrate synthetic UI honestly.
- Define release checklist and outstanding issues, tag suggestion only (don't push/tag until permission), final `git diff` summary and run commands.

## Gate G9
Fresh clone starts synthetic demo, all feasible tests pass or limitations documented, no known privacy leak, real experiment results present only if independently verified, research limitations clear, and developer can explain end-to-end methodology. Return status report with `PASS / BLOCKED / DEFERRED` per gate; never misstate readiness.
