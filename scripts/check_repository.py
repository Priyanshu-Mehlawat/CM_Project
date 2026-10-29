"""Heuristic source-only safeguards. Never claims to detect all PHI/secrets.

Use only in an isolated source checkout. Ignored files are never traversed.
Forbidden paths are rejected before reading their contents; diagnostics omit contents.
"""

import argparse
import re
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DENIED_PARTS = {
    "private",
    "restricted",
    "data",
    "artifacts",
    "models",
    ".aws",
    ".ssh",
    ".venv",
    "node_modules",
    "__pycache__",
}
DENIED_SUFFIXES = {
    ".csv",
    ".tsv",
    ".parquet",
    ".arrow",
    ".feather",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".duckdb",
    ".log",
    ".pkl",
    ".pickle",
    ".joblib",
    ".onnx",
    ".pt",
    ".pth",
    ".h5",
    ".pem",
    ".key",
    ".zip",
    ".gz",
    ".tgz",
    ".tar",
    ".pdf",
    ".xlsx",
    ".xls",
    ".dta",
}
SECRET_PATTERNS = [
    re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(rb"(?:AKIA|ASIA)[A-Z0-9]{16}"),
    re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    re.compile(rb"sk-[A-Za-z0-9_-]{24,}"),
    re.compile(
        rb"(?i)(?:api[_-]?key|password|secret|token)\s*[:=]\s*[\"']"
        rb"(?!placeholder|example|changeme)[^\"'\r\n]{12,}[\"']"
    ),
]


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", *args], cwd=ROOT)


def forbidden(path: str) -> bool:
    value = PurePosixPath(path)
    return (
        value.is_absolute()
        or ".." in value.parts
        or bool(set(value.parts) & DENIED_PARTS)
        or bool(set(value.suffixes) & DENIED_SUFFIXES)
        or (value.name.startswith(".env") and value.name != ".env.example")
        or value.name.startswith("credentials")
    )


def inspect_blob(path: str, blob: bytes, mode: str) -> list[str]:
    if forbidden(path):
        return ["forbidden file category"]
    if mode in {"120000", "160000"}:
        return ["symlinks and submodules require manual review"]
    if len(blob) > 1_000_000:
        return ["large file requires manual review"]
    if b"\x00" in blob:
        return ["binary file requires manual review"]
    return ["possible secret" for pattern in SECRET_PATTERNS if pattern.search(blob)]


def scan(scope: str) -> list[str]:
    issues = []
    if scope == "history":
        # Examine every reachable revision, including files later removed.
        revisions = git("rev-list", "--all").decode().splitlines()
        seen = set()
        for revision in revisions:
            for entry in git("ls-tree", "-r", "-z", revision).split(b"\x00"):
                if not entry:
                    continue
                metadata, raw_path = entry.split(b"\t", 1)
                mode, _, oid = metadata.decode().split()
                path = raw_path.decode("utf-8", "surrogateescape")
                key = (path, oid)
                if key in seen:
                    continue
                seen.add(key)
                if forbidden(path):
                    issues.append("history: forbidden file category (contents not read)")
                elif mode in {"120000", "160000"}:
                    issues.append("history: symlink/submodule requires review")
                elif int(git("cat-file", "-s", oid)) > 1_000_000:
                    issues.append("history: large file requires review")
                else:
                    issues.extend(inspect_blob(path, git("cat-file", "blob", oid), mode))
        return issues
    args = (
        ("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
        if scope == "staged"
        else ("ls-files", "--cached", "--others", "--exclude-standard", "-z")
    )
    paths = set(git(*args).decode("utf-8", "surrogateescape").split("\x00")) - {""}
    for path in paths:
        if forbidden(path):
            issues.append("forbidden file category (contents not read)")
            continue
        if scope == "staged":
            metadata = git("ls-files", "--stage", "--", path).decode().split()
            mode = metadata[0]
            if mode in {"120000", "160000"}:
                issues.append("symlink/submodule requires review")
                continue
            if int(git("cat-file", "-s", f":{path}")) > 1_000_000:
                issues.append("large file requires review")
                continue
            blob = git("show", f":{path}")
        else:
            file = ROOT / path
            if file.is_symlink():
                issues.append("symlink requires review (target not read)")
                continue
            if not file.exists():
                continue  # tracked file deleted in working tree
            if file.stat().st_size > 1_000_000:
                issues.append("large file requires review")
                continue
            mode = "100644"
            blob = file.read_bytes()
        issues.extend(inspect_blob(path, blob, mode))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for scope in ("staged", "worktree", "history"):
        group.add_argument(f"--{scope}", action="store_true")
    args = parser.parse_args()
    scope = next(name for name in ("staged", "worktree", "history") if getattr(args, name))
    issues = scan(scope)
    for issue in issues:
        print(f"REVIEW REQUIRED: {issue}; contents withheld")
    print(
        f"{scope}: {'FAILED' if issues else 'PASS'} (heuristic checks; disclosure review required)"
    )
    return bool(issues)


if __name__ == "__main__":
    raise SystemExit(main())
