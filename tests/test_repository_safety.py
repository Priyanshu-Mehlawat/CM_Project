import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "repository_safety", Path(__file__).parents[1] / "scripts/check_repository.py"
)
safety = importlib.util.module_from_spec(spec)
spec.loader.exec_module(safety)


@pytest.mark.parametrize(
    "name",
    [
        "exports/patients.csv",
        "exports/patients.csv.gz",
        ".env.local",
        "ml/private/records.json",
        "models/weights.json",
        "store.sqlite3",
        "private/report.md",
        "bundle.joblib",
        ".aws/config",
        "../elsewhere/file.txt",
    ],
)
def test_denies_sensitive_file_categories(name):
    assert safety.forbidden(name)


@pytest.mark.parametrize(
    "name", ["docs/architecture.md", ".env.example", "frontend/package-lock.json"]
)
def test_allows_source_files(name):
    assert not safety.forbidden(name)


def test_detects_secret_without_echoing_it():
    candidate = b"ghp_" + b"A" * 36
    issues = safety.inspect_blob("example.py", candidate, "100644")
    assert issues == ["possible secret"]
    assert candidate.decode() not in str(issues)


def test_rejects_symlink_and_binary_content():
    assert safety.inspect_blob("example.py", b"elsewhere", "120000")
    assert safety.inspect_blob("example.py", b"a\x00b", "100644")
