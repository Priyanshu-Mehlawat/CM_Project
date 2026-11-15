# RENAL-GUARD — Project story and version history

**Document version 1.2 · Updated 15 November 2026 (Asia/Kolkata)**

This document is the readable record of how RENAL-GUARD was built. Read it first
if you want to understand the project as a sequence of decisions rather than a
list of files. Each new increment should add a plain-language account of what
changed, why it changed, how it was checked, what remains uncertain, and when
the account was written. The compact scientific decisions live separately in
[the decision log](decision_log.md); this file tells the full development story.

## Where the project began

RENAL-GUARD was specified as a research prototype for estimating whether an adult
ICU encounter with a confirmed creatinine-based Stage 1 acute kidney injury later
shows creatinine-based Stage 2 or 3 within 48 hours. The intended research route
is MIMIC-IV for model development and eICU for external evaluation. Before code
was written, the planning package identified several choices that must come from
real dataset inspection and clinical review: the reference creatinine, when a
result became available, who is eligible at ICU entry, how much follow-up makes
a non-progression label credible, and whether the two datasets can support the
same definitions. Treating any of these as already settled would make later
performance claims unreliable. The implementation therefore proceeds through
stages with an explicit gate before clinical labeling or training.

## Increment 00 — the synthetic application foundation

**Generated 30 October 2026 · Code commit `6d17cae` · Documented project stage 00**

The GitHub repository initially held only a short README and a license. We
cloned it into a dedicated checkout, preserved the license, copied the approved
requirements and stage prompts into the repository, and built the first working
application shell. The frontend uses React, TypeScript, Vite and Tailwind. It
provides Clinical Explorer and Research Console routes and shows invented
examples with a persistent Synthetic Demo / Research Prototype notice. Its
research panels say “Not yet evaluated,” and its prediction panel says “Model
unavailable.” That matters because a polished interface can otherwise imply a
model or scientific result that does not yet exist.

The backend uses FastAPI and Pydantic and exposes versioned health, system and
synthetic-case endpoints. Health reports whether the service is alive separately
from whether a model exists. The UI reads the API contract, rejects an unexpected
numeric score, and handles a missing backend with a retry state. Research mode
fails closed. These choices give later stages a place to attach validated
artifacts while keeping the present demo honest.

We also created empty modules for the later clinical, ingestion, feature,
training, evaluation and reliability work; repository ignore rules; a staged
file hook; a heuristic scan of source files and reachable Git history; and
synthetic-only CI. The initial README explains setup and limits. None of these
safeguards is proof that sensitive data are safe to release, so the governance
notes still require OS-level isolation and human disclosure review.

At this increment, 21 Python tests and 4 frontend tests passed. Lint, TypeScript
checking, the production frontend build, source/history scans, and localhost
HTTP smoke checks passed. A visual browser review and a fresh-machine setup were
not completed. The changes were committed as `feat: add Stage 00 synthetic
research foundation` and pushed to `main`. The project then had a usable
software foundation, while clinical feasibility remained completely open.

## Increment 01 — source-only dataset audit tooling

**Generated 30 October 2026 · Code commit `29b59af` · Documented project stage 01**

The next increment addresses the first research gate without bringing restricted
records into the coding environment. We added an offline DuckDB audit program
that accepts an explicit private manifest of MIMIC-IV and eICU table paths.
There are no default data locations or directory searches. A safe `--dry-run`
prints only public table candidates. A real run requires an explicit isolated-run
flag and writes JSON and Markdown to a private directory outside the source
checkout, with owner-only permissions and no overwrite of prior reports.

The audit inventories candidate table columns and types, coarse row counts and
missingness, possible creatinine concepts and unit categories, numeric parse
failures, measurement and availability time fields, linkage coverage, candidate
observations around ICU admission, optional dialysis text signals, and broad
hospital coverage. It intentionally reports only fixed public schema names and
suppressed or interval-bucketed counts. It does not reveal source paths, patient
identifiers, rows, original dates, arbitrary labels or free text. Its concept
searches are candidates for human verification, and its timing summaries use ICU
admission as a descriptive anchor because the Stage 1 index has not been
specified. Thus the program is a feasibility inventory, not a clinical labeling
engine or a model evaluation.

We added a runbook for the authorized researcher, a blank audit report template,
and a G1 decision form. The README, governance notes, clinical protocol and
decision log now point to those materials and state clearly that G1 cannot pass
until an isolated human-run audit is reviewed. No real MIMIC-IV, eICU or SafeICU
files were read, listed, downloaded or processed during this increment. All audit
tests created invented CSV files temporarily for the test run and removed them
through the test fixture lifecycle; no CSV fixture was committed.

At this increment, 28 Python tests and 4 frontend tests passed. Ruff and ESLint
passed, TypeScript checked, Vite built, and the worktree/history heuristic scans
passed. The new tests cover missing tables, mixed numeric data, unsupported
units, offset ordering, compressed CSV, linkage, small-cell suppression, redacted
output, and `--dry-run` without path probing. The local Python run still emits a
pre-existing Starlette TestClient deprecation warning. No real cohort feasibility
or clinical performance is claimed. The remaining step is for an authorized
researcher to perform the private audit and for responsible reviewers to approve
the G1 clinical policies before Stage 02 can start.

## Version history

| Document version | Generated (Asia/Kolkata) | Project increment | What changed |
| --- | --- | --- | --- |
| 1.0 | 30 October 2026 | Stage 00, commit `6d17cae` | First synthetic app, local API, tests, repository safeguards and README. |
| 1.1 | 30 October 2026 | Stage 01, commit `29b59af` | Offline aggregate audit CLI, synthetic tests, human G1 templates, runbook and updated README. |

For each future increment, add a new narrative section and a dated row here.
Explain the reason for any changed design, cite the tests actually run, and
state the next research or engineering gate. Record its commit hash once known
in a subsequent document update. Do not treat an implementation
stage as scientific validation merely because its code is complete.

## Increment 02 — repairing the reviewed implementation and integrating progression

**Generated 15 November 2026 · Software version 0.2.0 · Presentation version 3.1**

The team supplied a friend's completed-project repository and asked for a careful
review. We found meaningful backend work, but also a different scientific target:
24-hour first-AKI prediction rather than RENAL-GUARD's Stage 1 progression within
48 hours. The separately authored frontend could not connect to that backend,
recomputed clinical stages incorrectly and lacked the tests its README advertised.
The user then asked us to repair the project, publish the improvements into their
own repository, remove unnecessary material and improve the contribution slide.

We retained the target repository's useful source-only audit, specification,
privacy safeguards, Linux setup and license. We did not copy patient files,
serialized onset models, private exports or temporary test folders. Instead, we
implemented one coherent progression workbench with an API contract shared by the
frontend and backend. Response types and runtime schemas are generated from
Pydantic, so route/schema drift becomes testable. The frontend no longer attempts
to compute canonical clinical stages, and unused starter cases were removed.
The original dated prompts are archived rather than mistaken for current status.

The new workbench contains five independently authored synthetic histories. They
show progression, an explicit fixture-only adequately observed negative, unknown
follow-up, a retracted result and a Stage 3 boundary. The arithmetic requires an
explicit earlier reference and respects sample collection and availability times.
Corrected samples replace older versions only when available. Replay reveals
observations and retrospective outcomes while keeping predictions unavailable
until a validated progression pipeline exists. This solves the software mechanics
without guessing real baseline selection or a clinical follow-up policy.

We wrote regression tests for the review's failures and checked a real API-to-UI
workflow in Chromium on desktop and mobile. All 42 Python, 7 React and 2 browser
tests passed, as did lint, build, contract generation, localhost smoke and
heuristic privacy checks. Screenshots were inspected. A newly reported lint-tool
dependency advisory was repaired with a targeted override; the final npm audit
reported zero known advisories. One pre-existing Python test-client deprecation
warning remains, with harmless browser-runner path/color warnings. These results
are software evidence, not independent model performance.

During the work the user supplied nine individual contributions. We replaced the
old vague placeholders with those team-confirmed proposal/design deliverables,
equal cards, concrete supporting material and specific oral-defense topics. We
removed the ranking and did not turn design ownership into claims of completed
experiments or sole code authorship. The 12-slide deck has seven timed main slides,
five backups, a 562-word script and a dated evidence ledger. All slides were
rendered and visually inspected, with tight cards/banners refined. The editable
source and companion notes are committed; generated PowerPoint/PDF files are
kept separately from source safeguards and older versions are preserved.

The resulting release is a working synthetic research workbench. The next
scientific milestone is still an authorized isolated dataset audit and reviewed
baseline, follow-up, eligibility and timing decisions. No actual cohort extraction,
training, independent clinical validation or demonstrated patient benefit is
claimed. Those limits are explicit in the application, README and presentation.

| Document entry | Generated | What changed |
| --- | --- | --- |
| 1.2 | 15 November 2026 | Repaired integrated software 0.2.0; canonical progression contract, replay, tests and cleanup; presentation 3.1 with nine confirmed design contributions. |

The feature release was pushed as `0dc7e04`. GitHub Actions run 43682902343
failed before starting any step because GitHub reported an account billing lock.
The code was verified locally; no remote success is claimed. A documentation-only
follow-up records that external blocker and the feature commit for traceability.
