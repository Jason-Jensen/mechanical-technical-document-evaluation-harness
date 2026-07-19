from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Callable

from mech_eval_harness.package_assurance import (
    DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE,
    DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID,
    DRAWING_FILE_REFERENCE_MISMATCH_CODE,
    DRAWING_METADATA_MISSING_CODE,
    DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    DRAWING_REGISTER_AUTHORITY_MISSING_CODE,
    DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    DRAWING_REVISION_AUTHORITY_RULE_ID,
    DRAWING_REVISION_MISMATCH_CODE,
    RELATIONSHIP_CHECK_ORDER,
    RELATIONSHIP_CHECK_VERSION,
    run_package_gates,
    run_package_relationships,
)
from mech_eval_harness.package_assurance.gates import (
    AUTHORITY_GATE_ID,
    SOURCE_INVENTORY_GATE_ID,
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


def test_clean_drawing_revisions_pass_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = first.checks[0]

    assert gates.dependent_checks_allowed is True
    assert first.package_id == "PKG-DEV-PUMP-SKID-001"
    assert check.check_id == DRAWING_REGISTER_METADATA_REVISION_CHECK_ID
    assert check.check_version == RELATIONSHIP_CHECK_VERSION
    assert check.status == "passed"
    assert check.findings == ()
    assert check.blocked_by == ()
    assert len(check.evidence) == 4
    assert first.to_dict() == second.to_dict()

    register = check.evidence[0].to_dict()
    metadata = check.evidence[1].to_dict()
    assert register == {
        "source_type": "drawing_register",
        "source_file": "inputs/drawing_register.csv",
        "format": "csv",
        "row_number": 2,
        "header_row_number": 1,
        "column_name": "revision_id",
        "row_key": {
            "column_name": "drawing_number",
            "value": "DWG-PSK-1001",
        },
        "original_value": "C",
        "normalized_value": "C",
    }
    assert metadata == {
        "source_type": "drawing_metadata",
        "source_file": "inputs/drawing_metadata.json",
        "format": "json",
        "json_pointer": "/records/0/revision_id",
        "record_id": "DWMETA-001",
        "property_name": "revision_id",
        "original_value": "C",
        "normalized_value": "C",
    }

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_clean_drawing_metadata_presence_passes_with_membership_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(gates, DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID)
    second = _check(gates, DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID)

    assert gates.dependent_checks_allowed is True
    assert first.check_version == RELATIONSHIP_CHECK_VERSION
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 3
    assert first.to_dict() == second.to_dict()
    assert first.evidence[0].to_dict() == {
        "source_type": "drawing_register",
        "source_file": "inputs/drawing_register.csv",
        "format": "csv",
        "row_number": 2,
        "header_row_number": 1,
        "column_name": "drawing_number",
        "row_key": {
            "column_name": "drawing_number",
            "value": "DWG-PSK-1001",
        },
        "original_value": "DWG-PSK-1001",
        "normalized_value": "DWG-PSK-1001",
    }
    assert first.evidence[-1].to_dict() == {
        "source_type": "drawing_metadata",
        "source_file": "inputs/drawing_metadata.json",
        "format": "json",
        "json_pointer": "/records",
        "property_name": "records",
        "original_value": ["DWG-PSK-1001", "DWG-PSK-1002"],
        "normalized_value": ["DWG-PSK-1001", "DWG-PSK-1002"],
    }


def test_clean_drawing_metadata_authority_passes_with_membership_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(gates, DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID)
    second = _check(gates, DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID)

    assert gates.dependent_checks_allowed is True
    assert first.check_version == RELATIONSHIP_CHECK_VERSION
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 3
    assert first.to_dict() == second.to_dict()
    assert first.evidence[0].to_dict() == {
        "source_type": "drawing_metadata",
        "source_file": "inputs/drawing_metadata.json",
        "format": "json",
        "json_pointer": "/records/0/drawing_number",
        "record_id": "DWMETA-001",
        "property_name": "drawing_number",
        "original_value": "DWG-PSK-1001",
        "normalized_value": "DWG-PSK-1001",
    }
    assert first.evidence[-1].to_dict() == {
        "source_type": "drawing_register",
        "source_file": "inputs/drawing_register.csv",
        "format": "csv",
        "row_number": 1,
        "header_row_number": 1,
        "column_name": "drawing_number",
        "original_value": ["DWG-PSK-1001", "DWG-PSK-1002"],
        "normalized_value": ["DWG-PSK-1001", "DWG-PSK-1002"],
    }


def test_clean_drawing_file_references_pass_with_resolution_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(
        gates,
        DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    )
    second = _check(
        gates,
        DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    )

    assert gates.dependent_checks_allowed is True
    assert first.check_version == RELATIONSHIP_CHECK_VERSION
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 6
    assert first.to_dict() == second.to_dict()
    assert tuple(locator.to_dict() for locator in first.evidence[:3]) == (
        {
            "source_type": "drawing_register",
            "source_file": "inputs/drawing_register.csv",
            "format": "csv",
            "row_number": 2,
            "header_row_number": 1,
            "column_name": "file_ref_id",
            "row_key": {
                "column_name": "document_id",
                "value": "DOC-DWG-001",
            },
            "original_value": "FILE-DWG-001",
            "normalized_value": "FILE-DWG-001",
        },
        {
            "source_type": "drawing_metadata",
            "source_file": "inputs/drawing_metadata.json",
            "format": "json",
            "json_pointer": "/records/0/file_ref_id",
            "record_id": "DWMETA-001",
            "property_name": "file_ref_id",
            "original_value": "FILE-DWG-001",
            "normalized_value": "FILE-DWG-001",
        },
        {
            "source_type": "package_manifest",
            "source_file": "package_manifest.json",
            "format": "file_reference",
            "file_ref_id": "FILE-DWG-001",
            "declared_relative_path": (
                "files/drawings/DWG-PSK-1001_rev_C.txt"
            ),
            "resolved_package_relative_path": (
                "files/drawings/DWG-PSK-1001_rev_C.txt"
            ),
            "boundary_check": "inside_allowed_root",
        },
    )

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_clean_drawing_manifest_reciprocity_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(
        gates,
        DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        gates,
        DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 12
    assert first.to_dict() == second.to_dict()
    evidence = [locator.to_dict() for locator in first.evidence[:6]]
    assert [item["format"] for item in evidence] == [
        "csv",
        "csv",
        "csv",
        "json",
        "file_reference",
        "json",
    ]
    assert [item.get("column_name") for item in evidence[:3]] == [
        "document_id",
        "drawing_number",
        "file_ref_id",
    ]
    assert evidence[3]["json_pointer"] == "/document_inventory/0"
    assert evidence[3]["record_id"] == "DOC-DWG-001"
    assert evidence[4]["file_ref_id"] == "FILE-DWG-001"
    assert evidence[4]["boundary_check"] == "inside_allowed_root"
    assert evidence[5]["json_pointer"] == "/relationship_declarations/0"
    assert evidence[5]["record_id"] == "REL-DOC-FILE-001"
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_missing_required_document_file_mapping_emits_one_reciprocity_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def remove_mapping(document: dict[str, Any]) -> None:
        document["relationship_declarations"] = [
            item
            for item in document["relationship_declarations"]
            if item["relationship_id"] != "REL-DOC-FILE-001"
        ]

    _mutate_manifest(package_root, remove_mapping)
    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    *predecessors, check = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in predecessors)
    assert check.status == "failed"
    assert len(check.findings) == 1
    finding = check.findings[0]
    assert finding.finding_id == second.checks[4].findings[0].finding_id
    assert (
        finding.check_id
        == DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID
    )
    assert finding.code == DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID
    assert finding.affected_identifiers == (
        "DOC-DWG-001",
        "DWG-PSK-1001",
        "FILE-DWG-001",
    )
    assert finding.actual_value["failed_clauses"] == [
        "required_document_to_file_mapping"
    ]
    assert finding.actual_value["required_document_to_file"] == {
        "matching_relationship_ids": [],
        "conflicting_mappings": [],
    }
    assert any(
        locator.json_pointer == "/relationship_declarations"
        for locator in finding.evidence
    )
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized


def test_wrong_valid_manifest_target_reports_every_failed_clause(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def redirect_manifest(document: dict[str, Any]) -> None:
        inventory = next(
            item
            for item in document["document_inventory"]
            if item["document_id"] == "DOC-DWG-001"
        )
        inventory["file_ref_id"] = "FILE-DWG-002"
        relationship = next(
            item
            for item in document["relationship_declarations"]
            if item["relationship_id"] == "REL-DOC-FILE-001"
        )
        relationship["target"]["identifier"] = "FILE-DWG-002"

    _mutate_manifest(package_root, redirect_manifest)
    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    *predecessors, check = evaluation.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in predecessors)
    assert check.status == "failed"
    finding = check.findings[0]
    assert finding.actual_value["failed_clauses"] == [
        "manifest_inventory_file_reference",
        "required_document_to_file_mapping",
        "conflicting_required_document_to_file_mapping",
    ]
    assert finding.actual_value["document_inventory"] == {
        "match_count": 1,
        "file_ref_ids": ["FILE-DWG-002"],
    }
    assert finding.actual_value["required_document_to_file"][
        "conflicting_mappings"
    ] == [
        {
            "relationship_id": "REL-DOC-FILE-001",
            "document_id": "DOC-DWG-001",
            "file_ref_id": "FILE-DWG-002",
            "required_for_release": True,
        }
    ]


def test_conflicting_required_mapping_is_a_reciprocity_failure(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def add_conflict(document: dict[str, Any]) -> None:
        document["relationship_declarations"].append(
            {
                "relationship_id": "REL-DOC-FILE-CONFLICT",
                "relationship_type": "document_to_file",
                "source": {
                    "identifier_type": "document_id",
                    "identifier": "DOC-DWG-001",
                },
                "target": {
                    "identifier_type": "file_ref_id",
                    "identifier": "FILE-DWG-002",
                },
                "required_for_release": True,
            }
        )

    _mutate_manifest(package_root, add_conflict)
    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    *predecessors, check = evaluation.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in predecessors)
    assert check.status == "failed"
    finding = check.findings[0]
    assert finding.actual_value["failed_clauses"] == [
        "conflicting_required_document_to_file_mapping"
    ]
    mapping = finding.actual_value["required_document_to_file"]
    assert mapping["matching_relationship_ids"] == ["REL-DOC-FILE-001"]
    assert [
        item["relationship_id"] for item in mapping["conflicting_mappings"]
    ] == ["REL-DOC-FILE-CONFLICT"]


def test_shared_undeclared_drawing_reference_is_caught_by_reciprocity(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    undeclared = "FILE-DWG-UNDECLARED"
    _set_register_file_references(
        package_root,
        {"DOC-DWG-001": undeclared},
    )
    _set_metadata_file_references(
        package_root,
        {"DWMETA-001": undeclared},
    )

    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    *predecessors, check = evaluation.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in predecessors)
    assert check.status == "failed"
    finding = check.findings[0]
    assert finding.affected_identifiers[-1] == undeclared
    assert finding.actual_value["failed_clauses"] == [
        "manifest_inventory_file_reference",
        "manifest_file_reference_resolution",
        "required_document_to_file_mapping",
        "conflicting_required_document_to_file_mapping",
    ]
    assert finding.actual_value["file_reference"] == {
        "declared_count": 0,
        "resolved_inside_allowed_root": False,
    }
    assert any(
        locator.json_pointer == "/file_references"
        for locator in finding.evidence
    )


def test_two_missing_reciprocal_mappings_are_sorted_and_repeatable(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def remove_drawing_mappings(document: dict[str, Any]) -> None:
        document["relationship_declarations"] = [
            item
            for item in document["relationship_declarations"]
            if item["relationship_id"]
            not in {"REL-DOC-FILE-001", "REL-DOC-FILE-002"}
        ]

    _mutate_manifest(package_root, remove_drawing_mappings)
    gates = _evaluate_gates(package_root)
    first = _check(
        gates,
        DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        gates,
        DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    )

    assert first.status == "failed"
    assert [finding.affected_identifiers[1] for finding in first.findings] == [
        "DWG-PSK-1001",
        "DWG-PSK-1002",
    ]
    assert first.to_dict() == second.to_dict()


def test_metadata_revision_mismatch_emits_frozen_release_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["records"][0]["revision_id"] = "A"
    _write_json(metadata_path, metadata)

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = first.checks[0]

    assert all(gate.status == "passed" for gate in gates.gates)
    assert check.status == "failed"
    assert len(check.findings) == 1
    finding = check.findings[0]
    assert finding.finding_id == second.checks[0].findings[0].finding_id
    assert finding.check_id == DRAWING_REGISTER_METADATA_REVISION_CHECK_ID
    assert finding.check_version == RELATIONSHIP_CHECK_VERSION
    assert finding.package_id == "PKG-DEV-PUMP-SKID-001"
    assert finding.code == DRAWING_REVISION_MISMATCH_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == DRAWING_REVISION_AUTHORITY_RULE_ID
    assert finding.affected_identifiers == (
        "DOC-DWG-001",
        "DWG-PSK-1001",
    )
    assert finding.expected_value == "C"
    assert finding.actual_value == "A"
    assert finding.review_owner == "document_control"
    assert "metadata revision A" in finding.message
    assert "drawing-register revision C" in finding.message
    assert "DWG-PSK-1001" in finding.message
    assert tuple(locator.to_dict() for locator in finding.evidence) == (
        {
            "source_type": "drawing_register",
            "source_file": "inputs/drawing_register.csv",
            "format": "csv",
            "row_number": 2,
            "header_row_number": 1,
            "column_name": "revision_id",
            "row_key": {
                "column_name": "drawing_number",
                "value": "DWG-PSK-1001",
            },
            "original_value": "C",
            "normalized_value": "C",
        },
        {
            "source_type": "drawing_metadata",
            "source_file": "inputs/drawing_metadata.json",
            "format": "json",
            "json_pointer": "/records/0/revision_id",
            "record_id": "DWMETA-001",
            "property_name": "revision_id",
            "original_value": "A",
            "normalized_value": "A",
        },
    )


def test_metadata_file_reference_mismatch_emits_frozen_release_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _set_metadata_file_references(
        package_root,
        {"DWMETA-001": "FILE-DWG-002"},
    )

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        check,
        reciprocity_check,
    ) = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert revision_check.status == "passed"
    assert presence_check.status == "passed"
    assert authority_check.status == "passed"
    assert check.status == "failed"
    assert reciprocity_check.status == "passed"
    assert len(check.findings) == 1
    assert len(check.evidence) == 7
    finding = check.findings[0]
    assert finding.finding_id == second.checks[3].findings[0].finding_id
    assert (
        finding.check_id
        == DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID
    )
    assert finding.check_version == RELATIONSHIP_CHECK_VERSION
    assert finding.package_id == "PKG-DEV-PUMP-SKID-001"
    assert finding.code == DRAWING_FILE_REFERENCE_MISMATCH_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert (
        finding.authority_rule_id
        == DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID
    )
    assert finding.affected_identifiers == (
        "DOC-DWG-001",
        "DWG-PSK-1001",
        "FILE-DWG-001",
        "FILE-DWG-002",
    )
    assert finding.expected_value == "FILE-DWG-001"
    assert finding.actual_value == "FILE-DWG-002"
    assert finding.review_owner == "document_control"
    assert "metadata file reference FILE-DWG-002" in finding.message
    assert "drawing-register file reference FILE-DWG-001" in finding.message
    assert "DWG-PSK-1001" in finding.message
    assert tuple(locator.to_dict() for locator in finding.evidence) == (
        {
            "source_type": "drawing_register",
            "source_file": "inputs/drawing_register.csv",
            "format": "csv",
            "row_number": 2,
            "header_row_number": 1,
            "column_name": "file_ref_id",
            "row_key": {
                "column_name": "document_id",
                "value": "DOC-DWG-001",
            },
            "original_value": "FILE-DWG-001",
            "normalized_value": "FILE-DWG-001",
        },
        {
            "source_type": "drawing_metadata",
            "source_file": "inputs/drawing_metadata.json",
            "format": "json",
            "json_pointer": "/records/0/file_ref_id",
            "record_id": "DWMETA-001",
            "property_name": "file_ref_id",
            "original_value": "FILE-DWG-002",
            "normalized_value": "FILE-DWG-002",
        },
        {
            "source_type": "package_manifest",
            "source_file": "package_manifest.json",
            "format": "file_reference",
            "file_ref_id": "FILE-DWG-001",
            "declared_relative_path": (
                "files/drawings/DWG-PSK-1001_rev_C.txt"
            ),
            "resolved_package_relative_path": (
                "files/drawings/DWG-PSK-1001_rev_C.txt"
            ),
            "boundary_check": "inside_allowed_root",
        },
        {
            "source_type": "package_manifest",
            "source_file": "package_manifest.json",
            "format": "file_reference",
            "file_ref_id": "FILE-DWG-002",
            "declared_relative_path": (
                "files/drawings/DWG-PSK-1002_rev_B.txt"
            ),
            "resolved_package_relative_path": (
                "files/drawings/DWG-PSK-1002_rev_B.txt"
            ),
            "boundary_check": "inside_allowed_root",
        },
    )

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_swapped_metadata_file_references_emit_sorted_findings(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _set_metadata_file_references(
        package_root,
        {
            "DWMETA-001": "FILE-DWG-002",
            "DWMETA-002": "FILE-DWG-001",
        },
    )

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        check,
        reciprocity_check,
    ) = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert revision_check.status == "passed"
    assert presence_check.status == "passed"
    assert authority_check.status == "passed"
    assert check.status == "failed"
    assert reciprocity_check.status == "passed"
    assert [
        finding.affected_identifiers[1] for finding in check.findings
    ] == ["DWG-PSK-1001", "DWG-PSK-1002"]
    assert [
        (finding.expected_value, finding.actual_value)
        for finding in check.findings
    ] == [
        ("FILE-DWG-001", "FILE-DWG-002"),
        ("FILE-DWG-002", "FILE-DWG-001"),
    ]
    assert first.to_dict() == second.to_dict()


def test_file_reference_findings_ignore_metadata_record_order(
    tmp_path: Path,
) -> None:
    original_order = _copy_package(tmp_path, "original-file-ref-order")
    reordered = _copy_package(tmp_path, "reordered-file-ref")
    swapped_values = {
        "DWMETA-001": "FILE-DWG-002",
        "DWMETA-002": "FILE-DWG-001",
    }
    _set_metadata_file_references(original_order, swapped_values)
    _set_metadata_file_references(reordered, swapped_values)

    metadata_path = reordered / "inputs" / "drawing_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["records"].reverse()
    _write_json(metadata_path, metadata)

    original_gates = _evaluate_gates(original_order)
    reordered_gates = _evaluate_gates(reordered)
    original = _check(
        original_gates,
        DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    )
    changed_order = _check(
        reordered_gates,
        DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert original.status == changed_order.status == "failed"

    def semantic_findings(check: RelationshipCheckResult) -> list[tuple[Any, ...]]:
        return [
            (
                finding.finding_id,
                finding.code,
                finding.result_state,
                finding.affected_identifiers,
                finding.expected_value,
                finding.actual_value,
            )
            for finding in check.findings
        ]

    assert semantic_findings(original) == semantic_findings(changed_order)
    assert [
        finding.affected_identifiers[1] for finding in original.findings
    ] == ["DWG-PSK-1001", "DWG-PSK-1002"]
    assert [locator.normalized_value for locator in original.evidence] == [
        locator.normalized_value for locator in changed_order.evidence
    ]


def test_missing_drawing_metadata_emits_frozen_release_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _remove_metadata_records(package_root, "DWMETA-001")

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        file_reference_check,
        reciprocity_check,
    ) = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert revision_check.status == "passed"
    assert revision_check.findings == ()
    assert presence_check.status == "failed"
    assert authority_check.status == "passed"
    assert authority_check.findings == ()
    assert file_reference_check.status == "passed"
    assert file_reference_check.findings == ()
    assert reciprocity_check.status == "passed"
    assert len(presence_check.findings) == 1
    finding = presence_check.findings[0]
    assert finding.finding_id == second.checks[1].findings[0].finding_id
    assert finding.check_id == DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID
    assert finding.check_version == RELATIONSHIP_CHECK_VERSION
    assert finding.package_id == "PKG-DEV-PUMP-SKID-001"
    assert finding.code == DRAWING_METADATA_MISSING_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == DRAWING_REVISION_AUTHORITY_RULE_ID
    assert finding.affected_identifiers == (
        "DOC-DWG-001",
        "DWG-PSK-1001",
    )
    assert finding.expected_value == "drawing_metadata counterpart"
    assert finding.actual_value == "missing"
    assert finding.review_owner == "document_control"
    assert "Authoritative drawing-register drawing DWG-PSK-1001" in (
        finding.message
    )
    assert "no drawing-metadata counterpart" in finding.message
    assert tuple(locator.to_dict() for locator in finding.evidence) == (
        {
            "source_type": "drawing_register",
            "source_file": "inputs/drawing_register.csv",
            "format": "csv",
            "row_number": 2,
            "header_row_number": 1,
            "column_name": "drawing_number",
            "row_key": {
                "column_name": "drawing_number",
                "value": "DWG-PSK-1001",
            },
            "original_value": "DWG-PSK-1001",
            "normalized_value": "DWG-PSK-1001",
        },
        {
            "source_type": "drawing_metadata",
            "source_file": "inputs/drawing_metadata.json",
            "format": "json",
            "json_pointer": "/records",
            "property_name": "records",
            "original_value": ["DWG-PSK-1002"],
            "normalized_value": ["DWG-PSK-1002"],
        },
    )

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_all_missing_metadata_findings_are_sorted_and_repeatable(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _remove_metadata_records(package_root, "DWMETA-001", "DWMETA-002")

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        file_reference_check,
        reciprocity_check,
    ) = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert revision_check.status == "passed"
    assert presence_check.status == "failed"
    assert authority_check.status == "passed"
    assert authority_check.findings == ()
    assert file_reference_check.status == "passed"
    assert file_reference_check.findings == ()
    assert reciprocity_check.status == "passed"
    assert [
        finding.affected_identifiers[-1]
        for finding in presence_check.findings
    ] == ["DWG-PSK-1001", "DWG-PSK-1002"]
    assert first.to_dict() == second.to_dict()
    for finding in presence_check.findings:
        collection = finding.evidence[1].to_dict()
        assert collection["json_pointer"] == "/records"
        assert collection["original_value"] == []
        assert collection["normalized_value"] == []


def test_failed_p21_prerequisite_skips_relationship_check(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "inputs" / "drawing_metadata.json").unlink()

    gates = _evaluate_gates(package_root)
    relationship_evaluation = run_package_relationships(gates)

    assert gates.dependent_checks_allowed is False
    assert tuple(
        check.check_id for check in relationship_evaluation.checks
    ) == RELATIONSHIP_CHECK_ORDER
    for check in relationship_evaluation.checks:
        assert check.status == "skipped"
        assert check.findings == ()
        assert check.evidence == ()
        assert SOURCE_INVENTORY_GATE_ID in check.blocked_by


def test_file_reference_check_requires_exact_accepted_authority_rule(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    file_reference_rule = next(
        rule
        for rule in authority["rules"]
        if rule["rule_id"] == DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID
    )
    file_reference_rule["rule_id"] = "AUTH-DWG-SUBSTITUTE"
    _write_json(authority_path, authority)

    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        check,
        reciprocity_check,
    ) = evaluation.checks

    assert gates.dependent_checks_allowed is True
    assert revision_check.status == "passed"
    assert presence_check.status == "passed"
    assert authority_check.status == "passed"
    assert check.status == "skipped"
    assert reciprocity_check.status == "skipped"
    assert reciprocity_check.blocked_by == (AUTHORITY_GATE_ID,)
    assert check.blocked_by == (AUTHORITY_GATE_ID,)
    assert check.findings == ()
    assert check.evidence == ()
    assert "AUTH-DWG-002" in check.summary


def test_missing_register_authority_emits_frozen_release_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _remove_register_rows(package_root, "DOC-DWG-001")

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        file_reference_check,
        reciprocity_check,
    ) = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert revision_check.status == "passed"
    assert revision_check.findings == ()
    assert presence_check.status == "passed"
    assert presence_check.findings == ()
    assert authority_check.status == "failed"
    assert file_reference_check.status == "passed"
    assert file_reference_check.findings == ()
    assert reciprocity_check.status == "passed"
    assert len(authority_check.findings) == 1
    finding = authority_check.findings[0]
    assert finding.finding_id == second.checks[2].findings[0].finding_id
    assert finding.check_id == DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID
    assert finding.check_version == RELATIONSHIP_CHECK_VERSION
    assert finding.package_id == "PKG-DEV-PUMP-SKID-001"
    assert finding.code == DRAWING_REGISTER_AUTHORITY_MISSING_CODE
    assert finding.result_state == "missing_authoritative_information"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == DRAWING_REVISION_AUTHORITY_RULE_ID
    assert finding.affected_identifiers == (
        "DOC-DWG-001",
        "DWG-PSK-1001",
    )
    assert finding.expected_value == "authoritative drawing_register record"
    assert finding.actual_value == "missing"
    assert finding.review_owner == "document_control"
    assert "Drawing metadata DWG-PSK-1001" in finding.message
    assert "no authoritative drawing-register record" in finding.message
    assert tuple(locator.to_dict() for locator in finding.evidence) == (
        {
            "source_type": "drawing_metadata",
            "source_file": "inputs/drawing_metadata.json",
            "format": "json",
            "json_pointer": "/records/0/drawing_number",
            "record_id": "DWMETA-001",
            "property_name": "drawing_number",
            "original_value": "DWG-PSK-1001",
            "normalized_value": "DWG-PSK-1001",
        },
        {
            "source_type": "drawing_register",
            "source_file": "inputs/drawing_register.csv",
            "format": "csv",
            "row_number": 1,
            "header_row_number": 1,
            "column_name": "drawing_number",
            "original_value": ["DWG-PSK-1002"],
            "normalized_value": ["DWG-PSK-1002"],
        },
    )

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_all_missing_register_authority_findings_are_sorted_and_repeatable(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _remove_register_rows(package_root, "DOC-DWG-001", "DOC-DWG-002")

    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    (
        revision_check,
        presence_check,
        authority_check,
        file_reference_check,
        reciprocity_check,
    ) = first.checks

    assert all(gate.status == "passed" for gate in gates.gates)
    assert revision_check.status == "passed"
    assert presence_check.status == "passed"
    assert authority_check.status == "failed"
    assert file_reference_check.status == "passed"
    assert file_reference_check.findings == ()
    assert reciprocity_check.status == "passed"
    assert [
        finding.affected_identifiers[-1]
        for finding in authority_check.findings
    ] == ["DWG-PSK-1001", "DWG-PSK-1002"]
    assert first.to_dict() == second.to_dict()
    for finding in authority_check.findings:
        collection = finding.evidence[1].to_dict()
        assert collection["row_number"] == 1
        assert collection["header_row_number"] == 1
        assert "row_key" not in collection
        assert collection["original_value"] == []
        assert collection["normalized_value"] == []


def test_authority_finding_identity_ignores_metadata_record_order(
    tmp_path: Path,
) -> None:
    original_order = _copy_package(tmp_path, "original-authority-order")
    reordered = _copy_package(tmp_path, "reordered-authority")
    for package_root in (original_order, reordered):
        _remove_register_rows(
            package_root,
            "DOC-DWG-001",
            "DOC-DWG-002",
        )

    metadata_path = reordered / "inputs" / "drawing_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["records"].reverse()
    _write_json(metadata_path, metadata)

    original_gates = _evaluate_gates(original_order)
    reordered_gates = _evaluate_gates(reordered)
    original = _check(
        original_gates,
        DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    )
    changed_order = _check(
        reordered_gates,
        DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert original.status == changed_order.status == "failed"

    def semantic_findings(check: RelationshipCheckResult) -> list[tuple[Any, ...]]:
        return [
            (
                finding.finding_id,
                finding.code,
                finding.result_state,
                finding.affected_identifiers,
                finding.expected_value,
                finding.actual_value,
            )
            for finding in check.findings
        ]

    assert semantic_findings(original) == semantic_findings(changed_order)
    assert [
        finding.affected_identifiers[-1] for finding in original.findings
    ] == ["DWG-PSK-1001", "DWG-PSK-1002"]
    assert original.evidence[-1].normalized_value == (
        changed_order.evidence[-1].normalized_value
    )


def test_authority_membership_normalization_ignores_register_order(
    tmp_path: Path,
) -> None:
    original_order = _copy_package(tmp_path, "original-register-order")
    reordered = _copy_package(tmp_path, "reordered-register")

    register_path = reordered / "inputs" / "drawing_register.csv"
    _rewrite_csv(register_path, lambda rows: rows.reverse())

    original_gates = _evaluate_gates(original_order)
    reordered_gates = _evaluate_gates(reordered)
    original = _check(
        original_gates,
        DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    )
    changed_order = _check(
        reordered_gates,
        DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert original.status == changed_order.status == "passed"
    assert original.findings == changed_order.findings == ()
    assert original.evidence[-1].original_value == [
        "DWG-PSK-1001",
        "DWG-PSK-1002",
    ]
    assert changed_order.evidence[-1].original_value == [
        "DWG-PSK-1002",
        "DWG-PSK-1001",
    ]
    assert original.evidence[-1].normalized_value == (
        changed_order.evidence[-1].normalized_value
    )


def test_finding_identity_and_order_ignore_source_record_order(
    tmp_path: Path,
) -> None:
    original_order = _copy_package(tmp_path, "original-order")
    reordered = _copy_package(tmp_path, "reordered")
    _set_metadata_revisions(original_order, "A")
    _set_metadata_revisions(reordered, "A")

    register_path = reordered / "inputs" / "drawing_register.csv"
    _rewrite_csv(register_path, lambda rows: rows.reverse())
    metadata_path = reordered / "inputs" / "drawing_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["records"].reverse()
    _write_json(metadata_path, metadata)

    original_gates = _evaluate_gates(original_order)
    reordered_gates = _evaluate_gates(reordered)
    original = _check(original_gates)
    changed_order = _check(reordered_gates)

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert original.status == changed_order.status == "failed"

    def semantic_findings(check: RelationshipCheckResult) -> list[tuple[Any, ...]]:
        return [
            (
                finding.finding_id,
                finding.code,
                finding.result_state,
                finding.affected_identifiers,
                finding.expected_value,
                finding.actual_value,
            )
            for finding in check.findings
        ]

    assert semantic_findings(original) == semantic_findings(changed_order)
    assert [
        finding.affected_identifiers[-1] for finding in original.findings
    ] == ["DWG-PSK-1001", "DWG-PSK-1002"]


def test_presence_finding_identity_ignores_register_record_order(
    tmp_path: Path,
) -> None:
    original_order = _copy_package(tmp_path, "original-presence-order")
    reordered = _copy_package(tmp_path, "reordered-presence")
    _remove_metadata_records(original_order, "DWMETA-001")
    _remove_metadata_records(reordered, "DWMETA-001")

    register_path = reordered / "inputs" / "drawing_register.csv"
    _rewrite_csv(register_path, lambda rows: rows.reverse())

    original_gates = _evaluate_gates(original_order)
    reordered_gates = _evaluate_gates(reordered)
    original = _check(
        original_gates,
        DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    )
    changed_order = _check(
        reordered_gates,
        DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert original.status == changed_order.status == "failed"
    assert len(original.findings) == len(changed_order.findings) == 1

    original_finding = original.findings[0]
    reordered_finding = changed_order.findings[0]
    assert (
        original_finding.finding_id,
        original_finding.code,
        original_finding.result_state,
        original_finding.affected_identifiers,
        original_finding.expected_value,
        original_finding.actual_value,
    ) == (
        reordered_finding.finding_id,
        reordered_finding.code,
        reordered_finding.result_state,
        reordered_finding.affected_identifiers,
        reordered_finding.expected_value,
        reordered_finding.actual_value,
    )
    assert original.evidence[-1].normalized_value == (
        changed_order.evidence[-1].normalized_value
    )


def test_presence_membership_normalization_ignores_metadata_order(
    tmp_path: Path,
) -> None:
    original_order = _copy_package(tmp_path, "original-metadata-order")
    reordered = _copy_package(tmp_path, "reordered-metadata")

    metadata_path = reordered / "inputs" / "drawing_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["records"].reverse()
    _write_json(metadata_path, metadata)

    original_gates = _evaluate_gates(original_order)
    reordered_gates = _evaluate_gates(reordered)
    original = _check(
        original_gates,
        DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    )
    changed_order = _check(
        reordered_gates,
        DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert original.status == changed_order.status == "passed"
    assert original.findings == changed_order.findings == ()
    assert original.evidence[-1].original_value == [
        "DWG-PSK-1001",
        "DWG-PSK-1002",
    ]
    assert changed_order.evidence[-1].original_value == [
        "DWG-PSK-1002",
        "DWG-PSK-1001",
    ]
    assert original.evidence[-1].normalized_value == (
        changed_order.evidence[-1].normalized_value
    )
