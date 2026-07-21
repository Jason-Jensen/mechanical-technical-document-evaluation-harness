from __future__ import annotations

import json
from pathlib import Path

from mech_eval_harness.package_assurance import (
    EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
    EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    SPECIFICATION_REVISION_AUTHORITY_RULE_ID,
    SPECIFICATION_REVISION_HISTORY_CHECK_ID,
    SPECIFICATION_REVISION_MISMATCH_CODE,
    run_package_relationships,
)
from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
from tests.package_relationship_support import (
    _check,
    _copy_package,
    _evaluate_gates,
    _load_json,
    _rewrite_csv,
    _write_json,
)


def _metadata_path(package_root: Path) -> Path:
    return package_root / "inputs" / "datasheet_spec_metadata.json"


def _history_path(package_root: Path) -> Path:
    return package_root / "inputs" / "revision_history.csv"


def _set_specification_revision(
    package_root: Path,
    record_id: str,
    revision_id: str,
) -> None:
    path = _metadata_path(package_root)
    document = _load_json(path)
    record = next(
        item
        for item in document["specifications"]
        if item["record_id"] == record_id
    )
    record["revision_id"] = revision_id
    _write_json(path, document)


def _change_authority_rule(
    package_root: Path,
    rule_id: str,
    field_name: str,
    value: str,
) -> None:
    path = package_root / "authority" / "authority_map.json"
    document = _load_json(path)
    rule = next(item for item in document["rules"] if item["rule_id"] == rule_id)
    rule[field_name] = value
    _write_json(path, document)


def test_clean_specification_revision_history_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(gates, SPECIFICATION_REVISION_HISTORY_CHECK_ID)
    second = _check(gates, SPECIFICATION_REVISION_HISTORY_CHECK_ID)

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 10
    assert first.to_dict() == second.to_dict()
    assert [locator.source_type for locator in first.evidence[:5]] == [
        "datasheet_spec_metadata",
        "datasheet_spec_metadata",
        "revision_history",
        "revision_history",
        "revision_history",
    ]
    assert first.evidence[0].record_id == "SPMETA-002"
    assert first.evidence[0].property_name == "specification_id"
    assert first.evidence[0].normalized_value == "SPEC-MOTOR-001"
    assert first.evidence[1].property_name == "revision_id"
    assert first.evidence[1].normalized_value == "A"
    assert first.evidence[2].row_key_value == "REVREC-SPEC-002-A"
    assert first.evidence[2].column_name == "owner_identifier"
    assert first.evidence[4].column_name == "revision_id"
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_wrong_valid_specification_revision_emits_one_frozen_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _set_specification_revision(package_root, "SPMETA-001", "B")
    gates = _evaluate_gates(package_root)

    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = first.checks[-1]

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in first.checks[:10])
    assert check.check_id == SPECIFICATION_REVISION_HISTORY_CHECK_ID
    assert check.status == "failed"
    assert len(check.findings) == 1
    assert first.to_dict() == second.to_dict()

    finding = check.findings[0]
    assert finding.code == SPECIFICATION_REVISION_MISMATCH_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == SPECIFICATION_REVISION_AUTHORITY_RULE_ID
    assert finding.review_owner == "document_control"
    assert finding.affected_identifiers == ("SPEC-PUMP-001",)
    assert finding.expected_value == "B"
    assert finding.actual_value == "A"
    assert [locator.source_type for locator in finding.evidence] == [
        "datasheet_spec_metadata",
        "datasheet_spec_metadata",
        "revision_history",
        "revision_history",
        "revision_history",
    ]
    assert finding.evidence[0].property_name == "specification_id"
    assert finding.evidence[1].property_name == "revision_id"
    assert finding.evidence[2].column_name == "owner_identifier"
    assert finding.evidence[3].column_name == "revision_status"
    assert finding.evidence[4].column_name == "revision_id"


def test_missing_and_multiple_current_history_are_stable_when_reordered(
    tmp_path: Path,
) -> None:
    original = _copy_package(tmp_path, "original")
    reordered = _copy_package(tmp_path, "reordered")

    def duplicate_pump_owner(rows: list[dict[str, str]]) -> None:
        record = next(
            item
            for item in rows
            if item["revision_record_id"] == "REVREC-SPEC-002-A"
        )
        record["owner_identifier"] = "SPEC-PUMP-001"

    for package_root in (original, reordered):
        _rewrite_csv(_history_path(package_root), duplicate_pump_owner)

    _rewrite_csv(_history_path(reordered), lambda rows: rows.reverse())
    metadata = _load_json(_metadata_path(reordered))
    metadata["specifications"].reverse()
    _write_json(_metadata_path(reordered), metadata)

    original_gates = _evaluate_gates(original)
    reordered_gates = _evaluate_gates(reordered)
    first = _check(original_gates, SPECIFICATION_REVISION_HISTORY_CHECK_ID)
    second = _check(reordered_gates, SPECIFICATION_REVISION_HISTORY_CHECK_ID)

    assert all(gate.status == "passed" for gate in original_gates.gates)
    assert all(gate.status == "passed" for gate in reordered_gates.gates)
    assert first.status == second.status == "failed"
    assert [finding.affected_identifiers for finding in first.findings] == [
        ("SPEC-MOTOR-001",),
        ("SPEC-PUMP-001",),
    ]
    assert first.findings[0].actual_value == "missing"
    assert [
        mapping["document_id"] for mapping in first.findings[1].actual_value
    ] == ["DOC-SPEC-001", "DOC-SPEC-002"]
    assert [
        (
            finding.finding_id,
            finding.code,
            finding.affected_identifiers,
            finding.expected_value,
            finding.actual_value,
        )
        for finding in first.findings
    ] == [
        (
            finding.finding_id,
            finding.code,
            finding.affected_identifiers,
            finding.expected_value,
            finding.actual_value,
        )
        for finding in second.findings
    ]
    missing_locator = first.findings[0].evidence[-1]
    assert missing_locator.source_type == "revision_history"
    assert missing_locator.row_number == 1
    assert missing_locator.normalized_value["current_record_count"] == 0


def test_specification_revision_requires_exact_authority_rule(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _change_authority_rule(
        package_root,
        SPECIFICATION_REVISION_AUTHORITY_RULE_ID,
        "agreement_rule",
        "specification revision agreement changed",
    )
    gates = _evaluate_gates(package_root)

    check = _check(gates, SPECIFICATION_REVISION_HISTORY_CHECK_ID)

    assert all(gate.status == "passed" for gate in gates.gates)
    assert check.status == "skipped"
    assert check.blocked_by == (AUTHORITY_GATE_ID,)
    assert check.findings == ()


def test_specification_revision_is_independent_of_datasheet_authority(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _change_authority_rule(
        package_root,
        "AUTH-SPEC-001",
        "review_owner",
        "document_control",
    )
    gates = _evaluate_gates(package_root)

    evaluation = run_package_relationships(gates)
    statuses = {check.check_id: check.status for check in evaluation.checks}

    assert all(gate.status == "passed" for gate in gates.gates)
    assert statuses[EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID] == "skipped"
    assert statuses[EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID] == "skipped"
    assert statuses[EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID] == "skipped"
    assert statuses[SPECIFICATION_REVISION_HISTORY_CHECK_ID] == "passed"
