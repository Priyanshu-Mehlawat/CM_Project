# Run Stage 01 audit in an isolated private environment

The code is ready for an authorized researcher to use **outside any agent-readable
filesystem**. The developer must use OS/container permissions to ensure Codex
cannot read credentialed files, the private manifest, logs, or outputs. No real
data audit has been run by Codex.

1. In the isolated research environment, install the project and audit extra with
   a local Python environment: `python -m pip install -e '.[audit]'`.
2. Prepare a private JSON manifest with absolute paths. Example structure only:

```json
{
  "format_version": 1,
  "tables": {
    "mimic": {
      "patients": "/PRIVATE/PLACEHOLDER/patients.csv.gz",
      "admissions": "/PRIVATE/PLACEHOLDER/admissions.csv.gz",
      "icustays": "/PRIVATE/PLACEHOLDER/icustays.csv.gz",
      "labevents": "/PRIVATE/PLACEHOLDER/labevents.csv.gz",
      "d_labitems": "/PRIVATE/PLACEHOLDER/d_labitems.csv.gz",
      "chartevents": "/PRIVATE/PLACEHOLDER/chartevents.csv.gz",
      "d_items": "/PRIVATE/PLACEHOLDER/d_items.csv.gz"
    },
    "eicu": {
      "patient": "/PRIVATE/PLACEHOLDER/patient.csv.gz",
      "hospital": "/PRIVATE/PLACEHOLDER/hospital.csv.gz",
      "lab": "/PRIVATE/PLACEHOLDER/lab.csv.gz",
      "vitalPeriodic": "/PRIVATE/PLACEHOLDER/vitalPeriodic.csv.gz",
      "vitalAperiodic": "/PRIVATE/PLACEHOLDER/vitalAperiodic.csv.gz"
    }
  }
}
```

All names are **candidates**; verify exact installed files and concepts. The
manifest must itself remain private. Supplying fewer tables is allowed; reports
mark the rest `not_supplied`. There is no automatic directory scan or private-path
default. Optional eICU `treatment` can be supplied to inventory dialysis text
candidates. The code does not identify chronic dialysis status.

3. `python scripts/dataset_audit.py --dry-run` prints only public table names and
   does not read the manifest or probe protected folders. Do not use dry-run as
   permission to expose protected paths to an agent.
4. In the isolated environment, run with a pre-existing **private output directory**:

```bash
python scripts/dataset_audit.py \
  --manifest /PRIVATE/PLACEHOLDER/audit_manifest.json \
  --output-dir /PRIVATE/PLACEHOLDER/reviewed_outputs \
  --min-cell 11 \
  --confirm-isolated-run
```

The CLI writes `renal_guard_audit.json` and `.md` with owner-only permissions and
refuses to overwrite. It prints no private path or row. Parse or I/O failures are
reported without raw exception text. The output includes public schema names,
inferred types, missingness, candidate creatinine/unit patterns, timestamp order,
linkage and ICU-admission timing patterns, dialysis text candidates and broad
hospital feasibility. Larger count cells are interval-bucketed. This policy does
not replace a disclosure review; combined aggregates may still disclose details.

A CSV with inconsistent types may fail an audit table; `read_error` is explicit.
The CLI uses DuckDB streaming queries, but the largest MIMIC tables and joins may
take substantial time and disk/memory resources. It performs no baseline
creatinine selection, Stage 1 detection, outcome classification or model training.
MIMIC `storetime` and eICU revised offsets are inventoried, not treated as a
verified common original-result timestamp.

5. Review and redact outputs locally. Share only the approved aggregate findings
and signed policy decisions from the templates. Do not commit the private report,
manifest, restricted model artifacts, IDs or record-level examples.
