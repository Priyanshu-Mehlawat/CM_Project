"""Offline, aggregate-only feasibility inventory for an isolated research runtime.

Never run this module on credentialed files in an agent-accessible environment.
It does not assign AKI stages, select a baseline, or mark outcomes negative.
"""

import re
from pathlib import Path
from typing import Any

from ml.ingestion.audit_catalog import (
    CATALOG,
    DIALYSIS_TERMS,
    REQUIRED_TABLES,
    TableSpec,
)

REPORT_VERSION = "v1"


def bucket(value: int | None, minimum: int) -> str:
    """Suppress small cells and release coarse intervals for larger counts."""
    if value is None:
        return "unavailable"
    if value == 0:
        return "0"
    if value < minimum:
        return "suppressed"
    lower = (value // minimum) * minimum
    return f"{lower}–{lower + minimum - 1}"


def safe_identifier(name: str) -> str:
    # All callers use hard-coded catalog fields, never headers from private files.
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
        raise ValueError("Unsupported public schema identifier")
    return f'"{name}"'


def path_literal(path: str) -> str:
    # Data source paths are SQL string literals; never return them in reports/errors.
    return "'" + path.replace("'", "''") + "'"


def validate_manifest(raw: Any, repository: Path) -> dict[str, dict[str, Path]]:
    if not isinstance(raw, dict) or raw.get("format_version") != 1:
        raise ValueError("Invalid manifest format version")
    tables = raw.get("tables")
    if not isinstance(tables, dict) or not tables:
        raise ValueError("Manifest must declare tables")
    result: dict[str, dict[str, Path]] = {}
    for source, source_tables in tables.items():
        if source not in CATALOG or not isinstance(source_tables, dict):
            raise ValueError("Unsupported manifest source")
        result[source] = {}
        for table, supplied_path in source_tables.items():
            if table not in CATALOG[source] or not isinstance(supplied_path, str):
                raise ValueError("Unsupported manifest table or path")
            path = Path(supplied_path)
            if not path.is_absolute() or not (
                supplied_path.lower().endswith(".csv") or supplied_path.lower().endswith(".csv.gz")
            ):
                raise ValueError("Each table needs an absolute CSV or CSV.GZ path")
            resolved = path.resolve(strict=False)
            if resolved.is_relative_to(repository.resolve()):
                raise ValueError("Dataset paths must remain outside the source checkout")
            if path.is_symlink():
                raise ValueError("Symlinked dataset paths are not supported")
            result[source][table] = path
    return result


def _sql_count(connection: Any, sql: str) -> int:
    result = connection.execute(sql).fetchone()
    return int(result[0] or 0)


def _group_counts(connection: Any, sql: str, minimum: int) -> dict[str, str]:
    """SQL must select a fixed, non-identifying category and a count."""
    return {
        str(category): bucket(int(count), minimum)
        for category, count in connection.execute(sql).fetchall()
    }


def _table_inventory(
    connection: Any, view: str, path: Path, spec: TableSpec, minimum: int
) -> dict[str, Any]:
    connection.execute(
        f"CREATE TEMP VIEW {safe_identifier(view)} AS "
        f"SELECT * FROM read_csv_auto({path_literal(str(path))}, header=true, "
        "all_varchar=true, sample_size=10000)"
    )
    observed = {
        description[0].lower()
        for description in connection.execute(
            f"SELECT * FROM {safe_identifier(view)} LIMIT 0"
        ).description
    }
    present = [column for column in spec.columns if column.lower() in observed]
    inferred: dict[str, str] = {}
    try:
        rows = connection.execute(
            "DESCRIBE SELECT * FROM read_csv_auto("
            f"{path_literal(str(path))}, header=true, sample_size=10000)"
        ).fetchall()
        inferred = {str(row[0]).lower(): str(row[1]) for row in rows}
    except Exception:
        # File formats and mixed types vary. Never echo DuckDB's path-bearing error.
        pass
    query = ["count(*)"]
    query.extend(
        f"sum(CASE WHEN NULLIF(TRIM({safe_identifier(col)}), '') IS NULL THEN 1 ELSE 0 END)"
        for col in present
    )
    counts = connection.execute(
        f"SELECT {', '.join(query)} FROM {safe_identifier(view)}"
    ).fetchone()
    return {
        "status": "audited",
        "rows": bucket(int(counts[0]), minimum),
        "columns": {
            column: {
                "present": column in present,
                "inferred_type": inferred.get(column.lower(), "unavailable")
                if column in present
                else None,
                "missing_cells": bucket(int(counts[index + 1]), minimum)
                if column in present
                else "unavailable",
            }
            for column in spec.columns
            for index in [present.index(column) if column in present else -1]
        },
        "unlisted_column_names": "withheld",
    }


def _has(inventory: dict[str, Any], source: str, table: str, *columns: str) -> bool:
    table_info = inventory.get(source, {}).get(table, {})
    return table_info.get("status") == "audited" and all(
        table_info["columns"].get(column, {}).get("present") for column in columns
    )


def _creatinine_predicate(source: str, inventory: dict[str, Any]) -> str | None:
    if (
        source == "mimic"
        and _has(inventory, source, "labevents", "itemid")
        and _has(inventory, source, "d_labitems", "itemid", "label")
    ):
        return (
            "EXISTS (SELECT 1 FROM mimic_d_labitems AS d WHERE "
            "d.itemid = l.itemid AND lower(d.label) LIKE '%creatinine%')"
        )
    if source == "eicu" and _has(inventory, source, "lab", "labname"):
        return "lower(l.labname) LIKE '%creatinine%'"
    return None


def _candidate_lab_inventory(
    connection: Any, source: str, inventory: dict[str, Any], minimum: int
) -> dict[str, Any]:
    table = "labevents" if source == "mimic" else "lab"
    value = "valuenum" if source == "mimic" else "labresult"
    unit = "valueuom" if source == "mimic" else "labmeasurenamesystem"
    result: dict[str, Any] = {
        "method": "case-insensitive creatinine text candidate; mapping unverified",
        "candidate_rows": "unavailable",
        "unit_categories": "unavailable",
        "numeric_parse_failures": "unavailable",
        "unit_conversion": "not_performed",
    }
    predicate = _creatinine_predicate(source, inventory)
    if predicate is None:
        return result
    view = f"{source}_{table}"
    result["candidate_rows"] = bucket(
        _sql_count(connection, f"SELECT count(*) FROM {view} AS l WHERE {predicate}"), minimum
    )
    if _has(inventory, source, table, value):
        result["numeric_parse_failures"] = bucket(
            _sql_count(
                connection,
                f"SELECT count(*) FROM {view} AS l WHERE {predicate} "
                f"AND nullif(trim(l.{value}), '') IS NOT NULL "
                f"AND try_cast(l.{value} AS DOUBLE) IS NULL",
            ),
            minimum,
        )
    if _has(inventory, source, table, unit):
        unit_expr = f"lower(replace(replace(trim(l.{unit}), ' ', ''), 'μ', 'u'))"
        category = (
            f"CASE WHEN nullif(trim(l.{unit}), '') IS NULL THEN 'missing' "
            f"WHEN {unit_expr} IN ('mg/dl', 'mg/dl.') THEN 'mg_per_dL' "
            f"WHEN {unit_expr} IN ('umol/l', 'µmol/l') THEN 'micromol_per_L' "
            f"WHEN {unit_expr} = 'mg/l' THEN 'mg_per_L' ELSE 'other_unverified' END"
        )
        result["unit_categories"] = _group_counts(
            connection,
            f"SELECT {category} AS category, count(*) FROM {view} AS l "
            f"WHERE {predicate} GROUP BY 1",
            minimum,
        )
    return result


def _time_inventory(
    connection: Any, source: str, inventory: dict[str, Any], minimum: int
) -> dict[str, Any]:
    result: dict[str, Any] = {}
    table = "labevents" if source == "mimic" else "lab"
    measure = "charttime" if source == "mimic" else "labresultoffset"
    available = "storetime" if source == "mimic" else "labresultrevisedoffset"
    if not _has(inventory, source, table, measure, available):
        return {"status": "unavailable"}
    cast_type = "TIMESTAMP" if source == "mimic" else "DOUBLE"
    view = f"{source}_{table}"
    for name, condition in {
        "measurement_time_unparseable": f"try_cast({measure} AS {cast_type}) IS NULL",
        "availability_time_unparseable": f"try_cast({available} AS {cast_type}) IS NULL",
        "availability_precedes_measurement": (
            f"try_cast({available} AS {cast_type}) < try_cast({measure} AS {cast_type})"
        ),
    }.items():
        result[name] = bucket(
            _sql_count(connection, f"SELECT count(*) FROM {view} WHERE {condition}"), minimum
        )
    result["interpretation"] = (
        "storetime candidate; verify documentation and latency policy"
        if source == "mimic"
        else "revised offset is not proof of original result availability"
    )
    return result


def _linkage_inventory(
    connection: Any, source: str, inventory: dict[str, Any], minimum: int
) -> dict[str, Any]:
    pairs = (
        [
            ("icustays", "patients", "subject_id"),
            ("labevents", "patients", "subject_id"),
            ("labevents", "admissions", "hadm_id"),
        ]
        if source == "mimic"
        else [("lab", "patient", "patientunitstayid"), ("patient", "hospital", "hospitalid")]
    )
    result = {}
    for child, parent, key in pairs:
        name = f"{child}_to_{parent}"
        if not _has(inventory, source, child, key) or not _has(inventory, source, parent, key):
            result[name] = "unavailable"
            continue
        result[name] = bucket(
            _sql_count(
                connection,
                f"SELECT count(*) FROM {source}_{child} AS c WHERE nullif(trim(c.{key}), '') "
                f"IS NOT NULL AND NOT EXISTS (SELECT 1 FROM {source}_{parent} AS p "
                f"WHERE p.{key} = c.{key})",
            ),
            minimum,
        )
    return result


def _timing_feasibility(
    connection: Any, source: str, inventory: dict[str, Any], minimum: int
) -> dict[str, Any]:
    """Descriptive timing around ICU admission, never Stage 1 or outcome labels."""
    result: dict[str, Any] = {
        "anchor": "ICU admission, not Stage 1 index",
        "pre_icu_candidate_creatinine_rows": "unavailable",
        "candidate_measurements_0_to_48h_after_icu_admission": "unavailable",
        "icu_stays_by_0_1_2plus_candidate_measurements": "unavailable",
        "negative_outcome_adequacy": "undetermined",
    }
    predicate = _creatinine_predicate(source, inventory)
    if predicate is None:
        return result
    if source == "mimic":
        if not (
            _has(inventory, source, "icustays", "hadm_id", "intime")
            and _has(inventory, source, "labevents", "hadm_id", "charttime")
        ):
            return result
        condition = (
            "l.hadm_id = i.hadm_id AND "
            "try_cast(l.charttime AS TIMESTAMP) IS NOT NULL AND "
            "try_cast(i.intime AS TIMESTAMP) IS NOT NULL"
        )
        joined = f"mimic_labevents AS l JOIN mimic_icustays AS i ON {condition}"
        before = "try_cast(l.charttime AS TIMESTAMP) < try_cast(i.intime AS TIMESTAMP)"
        after = (
            "try_cast(l.charttime AS TIMESTAMP) >= try_cast(i.intime AS TIMESTAMP) "
            "AND try_cast(l.charttime AS TIMESTAMP) <= "
            "try_cast(i.intime AS TIMESTAMP) + INTERVAL 48 HOUR"
        )
        result["pre_icu_candidate_creatinine_rows"] = bucket(
            _sql_count(connection, f"SELECT count(*) FROM {joined} WHERE {predicate} AND {before}"),
            minimum,
        )
        result["candidate_measurements_0_to_48h_after_icu_admission"] = bucket(
            _sql_count(connection, f"SELECT count(*) FROM {joined} WHERE {predicate} AND {after}"),
            minimum,
        )
        if _has(inventory, source, "icustays", "stay_id"):
            categories = (
                "SELECT CASE WHEN n = 0 THEN 'zero' WHEN n = 1 THEN 'one' "
                "ELSE 'two_or_more' END AS category, count(*) FROM "
                "(SELECT i.stay_id, count(l.itemid) AS n FROM mimic_icustays AS i "
                "LEFT JOIN mimic_labevents AS l ON l.hadm_id = i.hadm_id "
                f"AND {predicate} AND {after} GROUP BY i.stay_id) AS q GROUP BY 1"
            )
            result["icu_stays_by_0_1_2plus_candidate_measurements"] = _group_counts(
                connection, categories, minimum
            )
    elif _has(inventory, source, "lab", "labresultoffset"):
        result["pre_icu_candidate_creatinine_rows"] = bucket(
            _sql_count(
                connection,
                f"SELECT count(*) FROM eicu_lab AS l WHERE {predicate} "
                "AND try_cast(l.labresultoffset AS DOUBLE) < 0",
            ),
            minimum,
        )
        result["candidate_measurements_0_to_48h_after_icu_admission"] = bucket(
            _sql_count(
                connection,
                f"SELECT count(*) FROM eicu_lab AS l WHERE {predicate} "
                "AND try_cast(l.labresultoffset AS DOUBLE) BETWEEN 0 AND 2880",
            ),
            minimum,
        )
        if _has(inventory, source, "patient", "patientunitstayid") and _has(
            inventory, source, "lab", "patientunitstayid"
        ):
            categories = (
                "SELECT CASE WHEN n = 0 THEN 'zero' WHEN n = 1 THEN 'one' "
                "ELSE 'two_or_more' END AS category, count(*) FROM "
                "(SELECT p.patientunitstayid, count(l.labname) AS n FROM eicu_patient AS p "
                "LEFT JOIN eicu_lab AS l ON l.patientunitstayid = p.patientunitstayid "
                f"AND {predicate} AND try_cast(l.labresultoffset AS DOUBLE) "
                "BETWEEN 0 AND 2880 GROUP BY p.patientunitstayid) AS q GROUP BY 1"
            )
            result["icu_stays_by_0_1_2plus_candidate_measurements"] = _group_counts(
                connection, categories, minimum
            )
    return result


def _dialysis_signals(
    connection: Any, source: str, inventory: dict[str, Any], minimum: int
) -> dict[str, Any]:
    table, column = ("d_items", "label") if source == "mimic" else ("treatment", "treatmentstring")
    if not _has(inventory, source, table, column):
        return {"status": "unavailable; optional source not supplied or column absent"}
    predicate = " OR ".join(f"lower({column}) LIKE '%{term}%'" for term in DIALYSIS_TERMS)
    return {
        "candidate_dictionary_or_treatment_rows": bucket(
            _sql_count(connection, f"SELECT count(*) FROM {source}_{table} WHERE {predicate}"),
            minimum,
        ),
        "status": "text candidates only; chronic/new KRT classification unverified",
    }


def _hospital_feasibility(
    connection: Any, inventory: dict[str, Any], minimum: int
) -> dict[str, Any]:
    if not _has(inventory, "eicu", "patient", "hospitalid"):
        return {"status": "unavailable"}
    counts = connection.execute(
        "SELECT count(*) AS stays FROM eicu_patient "
        "WHERE nullif(trim(hospitalid), '') IS NOT NULL GROUP BY hospitalid"
    ).fetchall()
    sizes = [int(row[0]) for row in counts]
    return {
        "hospital_ids": "withheld",
        "hospitals_with_at_least_minimum_stays": bucket(sum(n >= minimum for n in sizes), minimum),
        "hospitals_below_minimum_stays": bucket(sum(n < minimum for n in sizes), minimum),
        "minimum_stays_used": minimum,
        "event_counts": "unavailable; labels not defined",
    }


def audit_manifest(manifest: dict[str, dict[str, Path]], minimum: int = 11) -> dict[str, Any]:
    if minimum < 11:
        raise ValueError("Minimum cell count must be at least 11")
    import duckdb

    connection = duckdb.connect(database=":memory:")
    inventory: dict[str, dict[str, Any]] = {}
    try:
        for source, tables in manifest.items():
            inventory[source] = {}
            for table, spec in CATALOG[source].items():
                path = tables.get(table)
                if path is None:
                    inventory[source][table] = {
                        "status": "not_supplied",
                        "columns": {
                            col: {
                                "present": False,
                                "inferred_type": None,
                                "missing_cells": "unavailable",
                            }
                            for col in spec.columns
                        },
                    }
                    continue
                try:
                    inventory[source][table] = _table_inventory(
                        connection, f"{source}_{table}", path, spec, minimum
                    )
                except Exception:
                    # Never include private filename, CSV row, or DuckDB error text.
                    inventory[source][table] = {
                        "status": "read_error",
                        "columns": {
                            col: {
                                "present": False,
                                "inferred_type": None,
                                "missing_cells": "unavailable",
                            }
                            for col in spec.columns
                        },
                    }
        analyses: dict[str, Any] = {}
        for source in manifest:
            analyses[source] = {}
            for key, analysis in (
                ("creatinine_candidates", _candidate_lab_inventory),
                ("timing", _time_inventory),
                ("linkage", _linkage_inventory),
                ("icu_admission_observation_patterns", _timing_feasibility),
                ("dialysis_signal_candidates", _dialysis_signals),
            ):
                try:
                    analyses[source][key] = analysis(connection, source, inventory, minimum)
                except Exception:
                    analyses[source][key] = {"status": "unavailable; query failed"}
            if source == "eicu":
                try:
                    analyses[source]["hospital_feasibility"] = _hospital_feasibility(
                        connection, inventory, minimum
                    )
                except Exception:
                    analyses[source]["hospital_feasibility"] = {
                        "status": "unavailable; query failed"
                    }
        completeness = {
            source: all(
                inventory[source][name]["status"] == "audited" for name in REQUIRED_TABLES[source]
            )
            for source in manifest
        }
        return {
            "report_version": REPORT_VERSION,
            "aggregate_only": True,
            "minimum_cell_count": minimum,
            "count_policy": (
                "zero exact; 1 through minimum-1 suppressed; larger counts interval-bucketed"
            ),
            "schema_mapping_status": "candidates_not_verified",
            "clinical_feasibility": "undetermined_pending_human_review",
            "cohort_flow": "unavailable_until_clinical_protocol_approved",
            "dataset_version": "not_verified_by_audit",
            "required_table_inventory_complete": completeness,
            "tables": inventory,
            "analyses": analyses,
            "review_required": [
                "confirm source versions and public schema mappings",
                "review concept and unit candidates; no conversion performed",
                "establish original result availability, especially eICU revised offsets",
                "decide reference creatinine, Stage 1 index, eligibility and adequate follow-up",
                "verify comparable adult cohorts before external evaluation",
                "review all aggregates and small-cell policy before sharing",
            ],
        }
    finally:
        connection.close()


def report_markdown(report: dict[str, Any]) -> str:
    """Use only fixed report keys and public table names; no raw CSV values."""
    lines = [
        "# RENAL-GUARD offline dataset audit",
        "",
        "**Disclosure review required before sharing this output.**",
        "Clinical feasibility: undetermined; no labels or cohort flow calculated.",
        f"Minimum cell count: {report['minimum_cell_count']}.",
        "Counts: zero exact, small cells suppressed, larger cells interval-bucketed.",
        "",
        "| Source | Public table candidate | Status | Row count bucket |",
        "| --- | --- | --- | --- |",
    ]
    for source, tables in report["tables"].items():
        for table, info in tables.items():
            lines.append(
                f"| {source} | {table} | {info['status']} | {info.get('rows', 'unavailable')} |"
            )
    lines.extend(
        [
            "",
            "Further aggregate details are in the companion JSON file.",
            "No table or concept candidate is clinically verified by this audit.",
            "",
        ]
    )
    return "\n".join(lines)
