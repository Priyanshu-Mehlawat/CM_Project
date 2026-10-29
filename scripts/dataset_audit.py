#!/usr/bin/env python3
"""Run only by an authorized researcher in an isolated, private environment."""

import argparse
import json
import os
import sys
from pathlib import Path

# Allow direct execution from the source checkout, without package installation.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.ingestion.audit import audit_manifest, report_markdown, validate_manifest  # noqa: E402
from ml.ingestion.audit_catalog import CATALOG  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Offline aggregate schema/feasibility inventory. "
            "Never run on real data in an agent environment."
        )
    )
    parser.add_argument(
        "--manifest", help="Private JSON manifest with explicit absolute paths for named tables"
    )
    parser.add_argument(
        "--output-dir", help="Existing private directory for reviewed JSON/Markdown outputs"
    )
    parser.add_argument(
        "--min-cell", type=int, default=11, help="Minimum count for release; must be at least 11"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show public expected table names without reading any manifest or data path",
    )
    parser.add_argument(
        "--confirm-isolated-run",
        action="store_true",
        help="Confirm authorized isolated local execution outside agent access",
    )
    args = parser.parse_args(argv)
    if args.dry_run:
        print("No manifest or dataset path was read. Public table candidates:")
        for source, tables in CATALOG.items():
            print(f"{source}: {', '.join(tables)}")
        print("Real runs require an isolated private environment and disclosure review.")
        return 0
    if not args.confirm_isolated_run:
        print("Audit refused: explicit isolated-run confirmation required.", file=sys.stderr)
        return 2
    if args.min_cell < 11:
        print("Audit refused: minimum cell count must be at least 11.", file=sys.stderr)
        return 2
    manifest_name = args.manifest or os.environ.get("RENAL_GUARD_AUDIT_MANIFEST")
    if not manifest_name or not args.output_dir:
        print("Audit refused: private manifest and output directory required.", file=sys.stderr)
        return 2
    repository = Path(__file__).resolve().parents[1]
    try:
        manifest_path = Path(manifest_name)
        output_dir = Path(args.output_dir)
        if not manifest_path.is_absolute() or not output_dir.is_absolute():
            raise ValueError("Private paths must be absolute")
        if manifest_path.resolve().is_relative_to(
            repository
        ) or output_dir.resolve().is_relative_to(repository):
            raise ValueError("Private paths must be outside the source checkout")
        if not output_dir.is_dir() or output_dir.is_symlink():
            raise ValueError("Private output directory must exist and must not be a symlink")
        raw = json.loads(manifest_path.read_text())
        manifest = validate_manifest(raw, repository)
        report = audit_manifest(manifest, args.min_cell)
        payloads = {
            "renal_guard_audit.json": json.dumps(report, indent=2, sort_keys=True) + "\n",
            "renal_guard_audit.md": report_markdown(report),
        }
        # Refuse to replace a prior report. Both outputs remain private by default.
        if any((output_dir / name).exists() for name in payloads):
            raise ValueError("Output files already exist")
        for name, contents in payloads.items():
            descriptor = os.open(output_dir / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(descriptor, "w") as stream:
                stream.write(contents)
        print("Aggregate audit files written to private output directory. Review before sharing.")
        return 0
    except Exception:
        # DuckDB/OS exceptions can include sensitive paths or input snippets.
        print(
            "Audit failed; inspect the private environment locally. No path or row shown.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
