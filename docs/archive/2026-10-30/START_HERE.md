# Start here — RENAL-GUARD Codex handoff

This package is a **planning and agent-instruction package**, not a completed application. It is based on the decisions reached in conversation through 30 October 2026.

## Suggested use
1. Clone `https://github.com/Priyanshu-Mehlawat/CM_Project` on Linux.
2. **Before launching Codex, isolate credentialed datasets at OS/container level.** Put only public source code and synthetic fixtures within the accessible agent workspace. Never assume the working-directory boundary alone blocks reading.
3. Copy `AGENTS.md` into repository root and `MASTER_SPECIFICATION.md` into `docs/` (or repository root with adapted AGENTS path).
4. Add `docs/decision_log.md` identifying decisions that remain pending G1. Codex may create the initial file as part of Prompt 0.
5. Run `prompts/00_repository_foundation.md` in Codex and review changes/tests before committing/pushing.
6. Continue **one stage at a time**. Do **not** run training/real-data tasks via hosted Codex. When a prompt generates an offline script for credentialed datasets, have the authorized researcher execute it separately in an isolated environment; only share aggregate/approved results.
7. Stop after Prompt 1 until the clinical protocol ambiguity and label feasibility decisions are resolved by the responsible researcher/supervisor.
8. Record results from each gate in `docs/decision_log.md` and verify no restricted contents entered repo/history or hosted AI contexts.

## What the package contains
- `MASTER_SPECIFICATION.md`: requirements and research/engineering contract.
- `AGENTS.md`: mandatory Codex repo guardrails.
- `prompts/00` … `09`: sequential implementation tasks with acceptance gates.
- `FINAL_REVIEW.md`: consistency audit, unresolved decisions and submission priorities.

## Mandatory red lines
- No fabricated model output or clinical labels.
- No access to or upload of restricted patient data by cloud AI tools.
- No invalid assumption that no observed progression means non-progression.
- No Stage 1 index based on results not available at index time.
- No eICU external-validation claim if cohorts are not comparable.
- No silent bypass of tests, warnings, or incomplete research results.

## CLI usage (illustrative only)
Use your installed Codex interface and paste one prompt at a time. There is no assumed Codex command or authorization level. Confirm the active sandbox and filesystem access scope first.

## Dataset audit handoff
Codex creates source-only audit scripts using documented schemas and synthetic tests. The authorized researcher executes them without granting Codex access to protected files. Audit output must be screened for original IDs, patient rows, sparse/small-cell disclosures and accidental free text before being summarized back to the agent.

## Expected result
A functioning, source-reviewed and tested research prototype and a scientifically honest MIMIC-IV/eICU validation report, **conditional on actual data feasibility**. SafeICU remains optional and separately authorized.
