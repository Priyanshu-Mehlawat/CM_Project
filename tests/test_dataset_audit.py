"""Only independently authored, temporary CSV fixtures are read in these tests."""

import json
from pathlib import Path

import pytest

from ml.ingestion.audit import audit_manifest, bucket, report_markdown, validate_manifest
from scripts.dataset_audit import main


def write_table(directory: Path, filename: str, header: str, rows: list[str]) -> Path:
    path = directory / filename
    path.write_text(header + "\n" + "\n".join(rows) + "\n")
    return path


def synthetic_mimic(directory: Path) -> dict:
    dictionary = write_table(
        directory,
        "dictionary.csv",
        "itemid,label,fluid",
        ["c1,Creatinine,Blood", "d1,Dialysis,Blood"],
    )
    labs = write_table(
        directory,
        "labs.csv",
        "itemid,charttime,storetime,valuenum,valueuom,subject_id,hadm_id",
        [f"c1,2020-01-01 01:00:00,2020-01-01 02:00:00,1.{i},mg/dL,s{i},h{i}" for i in range(12)]
        + ["c1,2020-01-01 03:00:00,2019-12-31 23:00:00,bad,odd-unit,private-row-marker,hx"],
    )
    return {
        "format_version": 1,
        "tables": {
            "mimic": {
                "d_labitems": str(dictionary),
                "labevents": str(labs),
            }
        },
    }


def test_bucket_suppresses_small_cells_and_buckets_larger_counts():
    assert bucket(0, 11) == "0"
    assert bucket(1, 11) == "suppressed"
    assert bucket(10, 11) == "suppressed"
    assert bucket(11, 11) == "11–21"
    assert bucket(22, 11) == "22–32"
    with pytest.raises(ValueError):
        audit_manifest({}, minimum=10)


def test_mimic_inventory_handles_missing_tables_mixed_types_and_unverified_units(tmp_path):
    report = audit_manifest(validate_manifest(synthetic_mimic(tmp_path), Path.cwd()), 11)
    info = report["tables"]["mimic"]
    assert info["patients"]["status"] == "not_supplied"
    assert info["labevents"]["columns"]["valuenum"]["present"] is True
    assert info["labevents"]["columns"]["valuenum"]["inferred_type"]
    assert info["labevents"]["rows"] == "11–21"
    analysis = report["analyses"]["mimic"]
    assert analysis["creatinine_candidates"]["candidate_rows"] == "11–21"
    assert analysis["creatinine_candidates"]["numeric_parse_failures"] == "suppressed"
    assert analysis["creatinine_candidates"]["unit_categories"]["other_unverified"] == "suppressed"
    assert analysis["timing"]["availability_precedes_measurement"] == "suppressed"
    assert report["required_table_inventory_complete"]["mimic"] is False
    serialized = json.dumps(report) + report_markdown(report)
    assert "private-row-marker" not in serialized
    assert "odd-unit" not in serialized
    assert str(tmp_path) not in serialized
    assert "2020-01-01" not in serialized


def test_eicu_offsets_linkage_and_hospital_counts_remain_aggregate(tmp_path):
    patient = write_table(
        tmp_path,
        "patient.csv",
        "patientunitstayid,hospitalid,age",
        [f"x{i},H1,{50 + i}" for i in range(12)],
    )
    hospital = write_table(tmp_path, "hospital.csv", "hospitalid,region", ["H1,fiction"])
    lab = write_table(
        tmp_path,
        "lab.csv",
        "patientunitstayid,labresultoffset,labresultrevisedoffset,labname,labresult,labmeasurenamesystem",
        [f"x{i},{i * 10},{i * 10 + 5},creatinine,1.0,mg/dL" for i in range(12)]
        + ["missing,-3,-8,creatinine,not-a-number,unverified-unit"],
    )
    manifest = validate_manifest(
        {
            "format_version": 1,
            "tables": {
                "eicu": {
                    "patient": str(patient),
                    "hospital": str(hospital),
                    "lab": str(lab),
                }
            },
        },
        Path.cwd(),
    )
    report = audit_manifest(manifest)
    eicu = report["analyses"]["eicu"]
    assert eicu["linkage"]["lab_to_patient"] == "suppressed"
    assert eicu["timing"]["availability_precedes_measurement"] == "suppressed"
    assert (
        eicu["icu_admission_observation_patterns"]["pre_icu_candidate_creatinine_rows"]
        == "suppressed"
    )
    assert (
        eicu["icu_admission_observation_patterns"]["icu_stays_by_0_1_2plus_candidate_measurements"][
            "one"
        ]
        == "11–21"
    )
    assert eicu["hospital_feasibility"]["hospital_ids"] == "withheld"
    assert report["clinical_feasibility"] == "undetermined_pending_human_review"
    assert "H1" not in json.dumps(report)


def test_csv_gz_supported_without_committing_csv_fixture(tmp_path):
    import gzip

    path = tmp_path / "lab.csv.gz"
    with gzip.open(path, "wt") as output:
        output.write("patientunitstayid,labname,labresultoffset\nabc,creatinine,10\n")
    manifest = validate_manifest(
        {"format_version": 1, "tables": {"eicu": {"lab": str(path)}}}, Path.cwd()
    )
    report = audit_manifest(manifest)
    assert report["tables"]["eicu"]["lab"]["status"] == "audited"
    assert report["tables"]["eicu"]["lab"]["rows"] == "suppressed"


def test_manifest_rejects_source_checkout_paths_and_unknown_tables(tmp_path):
    fake = Path.cwd() / "private.csv"
    with pytest.raises(ValueError):
        validate_manifest(
            {"format_version": 1, "tables": {"mimic": {"labevents": str(fake)}}}, Path.cwd()
        )
    with pytest.raises(ValueError):
        validate_manifest(
            {"format_version": 1, "tables": {"eicu": {"unknown": str(tmp_path / "x.csv")}}},
            Path.cwd(),
        )


def test_dry_run_does_not_probe_supplied_manifest(tmp_path, capsys):
    result = main(["--dry-run", "--manifest", str(tmp_path / "does-not-exist.json")])
    output = capsys.readouterr()
    assert result == 0
    assert "mimic:" in output.out
    assert str(tmp_path) not in output.out + output.err


def test_cli_writes_private_aggregate_files_without_printing_paths(tmp_path, capsys):
    fixture_dir = tmp_path / "fixture"
    fixture_dir.mkdir()
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps(synthetic_mimic(fixture_dir)))
    output = tmp_path / "private-output"
    output.mkdir()
    result = main(
        ["--manifest", str(manifest), "--output-dir", str(output), "--confirm-isolated-run"]
    )
    display = capsys.readouterr()
    assert result == 0
    assert str(tmp_path) not in display.out + display.err
    payload = json.loads((output / "renal_guard_audit.json").read_text())
    assert payload["aggregate_only"] is True
    assert not ((output / "renal_guard_audit.json").stat().st_mode & 0o077)
    assert (
        main(["--manifest", str(manifest), "--output-dir", str(output), "--confirm-isolated-run"])
        == 1
    )
