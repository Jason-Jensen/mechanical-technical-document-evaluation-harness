"""Shared fixtures and mutators for package relationship tests."""

from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Callable

from mech_eval_harness.package_assurance import (
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    RELATIONSHIP_CHECK_ORDER,
    run_package_gates,
    run_package_relationships,
)
from mech_eval_harness.package_assurance.models import (
    PackageGateEvaluation,
    RelationshipCheckResult,
)


ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PACKAGE = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "development"
    / "pump_skid_clean_v1"
    / "package"
)

def _copy_package(tmp_path: Path, name: str = "package") -> Path:
    package_root = tmp_path / name
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    return package_root


def _evaluate_gates(package_root: Path) -> PackageGateEvaluation:
    return run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )


def _check(
    evaluation: PackageGateEvaluation,
    check_id: str = DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
) -> RelationshipCheckResult:
    relationship_evaluation = run_package_relationships(evaluation)
    assert tuple(
        check.check_id for check in relationship_evaluation.checks
    ) == RELATIONSHIP_CHECK_ORDER
    return next(
        check
        for check in relationship_evaluation.checks
        if check.check_id == check_id
    )


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _rewrite_csv(
    path: Path,
    mutate: Callable[[list[dict[str, str]]], None],
) -> None:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    assert fieldnames is not None
    mutate(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fieldnames,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def _set_metadata_revisions(package_root: Path, revision: str) -> None:
    path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(path)
    for record in document["records"]:
        record["revision_id"] = revision
    _write_json(path, document)


def _set_metadata_file_references(
    package_root: Path,
    values_by_record_id: dict[str, str],
) -> None:
    path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(path)
    for record in document["records"]:
        if record["record_id"] in values_by_record_id:
            record["file_ref_id"] = values_by_record_id[record["record_id"]]
    _write_json(path, document)


def _set_metadata_equipment_tags(
    package_root: Path,
    values_by_record_id: dict[str, list[str]],
) -> None:
    path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(path)
    for record in document["records"]:
        if record["record_id"] in values_by_record_id:
            record["equipment_tags"] = values_by_record_id[record["record_id"]]
    _write_json(path, document)


def _set_register_file_references(
    package_root: Path,
    values_by_document_id: dict[str, str],
) -> None:
    path = package_root / "inputs" / "drawing_register.csv"

    def update_selected(rows: list[dict[str, str]]) -> None:
        for row in rows:
            if row["document_id"] in values_by_document_id:
                row["file_ref_id"] = values_by_document_id[
                    row["document_id"]
                ]

    _rewrite_csv(path, update_selected)


def _mutate_manifest(
    package_root: Path,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    path = package_root / "package_manifest.json"
    document = _load_json(path)
    mutate(document)
    _write_json(path, document)


def _remove_metadata_records(
    package_root: Path,
    *record_ids: str,
) -> None:
    path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(path)
    document["records"] = [
        record
        for record in document["records"]
        if record["record_id"] not in record_ids
    ]
    _write_json(path, document)


def _remove_register_rows(
    package_root: Path,
    *document_ids: str,
) -> None:
    path = package_root / "inputs" / "drawing_register.csv"

    def remove_selected(rows: list[dict[str, str]]) -> None:
        rows[:] = [
            row for row in rows if row["document_id"] not in document_ids
        ]

    _rewrite_csv(path, remove_selected)
