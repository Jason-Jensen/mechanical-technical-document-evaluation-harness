from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance import (
    BOM_EQUIPMENT_AUTHORITY_RULE_ID,
    DRAWING_REVISION_AUTHORITY_RULE_ID,
    EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
    EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE,
    EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
    EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    EQUIPMENT_DATASHEET_MISMATCH_CODE,
    EQUIPMENT_DATASHEET_RECIPROCITY_FAILED_CODE,
    run_package_relationships,
)
from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
from tests.package_relationship_support import (
    _check,
    _copy_package,
    _evaluate_gates,
    _load_json,
    _mutate_manifest,
    _rewrite_csv,
    _write_json,
)


def _datasheet_metadata_path(package_root: Path) -> Path:
    return package_root / "inputs" / "datasheet_spec_metadata.json"


def _remove_datasheet_record(package_root: Path, record_id: str) -> None:
    path = _datasheet_metadata_path(package_root)
    document = _load_json(path)
    document["datasheets"] = [
        record
        for record in document["datasheets"]
        if record["record_id"] != record_id
    ]
    _write_json(path, document)


def _make_competing_datasheet_mapping(package_root: Path) -> None:
    path = _datasheet_metadata_path(package_root)
    document = _load_json(path)
    record = next(
        item
        for item in document["datasheets"]
        if item["record_id"] == "DSMETA-002"
    )
    record["equipment_tag"] = "P-101A"
    _write_json(path, document)


def _set_bom_datasheet_ids(
    package_root: Path,
    values_by_item_id: dict[str, str],
) -> None:
    def update_selected(rows: list[dict[str, str]]) -> None:
        for row in rows:
            if row["item_id"] in values_by_item_id:
                row["datasheet_id"] = values_by_item_id[row["item_id"]]

    _rewrite_csv(
        package_root / "inputs" / "bom_or_equipment_list.csv",
        update_selected,
    )


def _set_manifest_datasheet_targets(
    package_root: Path,
    values_by_relationship_id: dict[str, str],
) -> None:
    def update_selected(manifest: dict[str, Any]) -> None:
        for relationship in manifest["relationship_declarations"]:
            relationship_id = relationship["relationship_id"]
            if relationship_id in values_by_relationship_id:
                relationship["target"]["identifier"] = values_by_relationship_id[
                    relationship_id
                ]

    _mutate_manifest(package_root, update_selected)


def _check_by_id(evaluation, check_id: str):
    return next(check for check in evaluation.checks if check.check_id == check_id)


def test_clean_equipment_datasheet_authority_presence_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(
        gates,
        EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    )
    second = _check(
        gates,
        EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 4
    assert first.to_dict() == second.to_dict()
    assert first.evidence[0].column_name == "equipment_tag"
    assert first.evidence[0].row_key_value == "ITEM-MOTOR-001"
    assert first.evidence[1].json_pointer == "/datasheets"
    assert first.evidence[1].property_name == "equipment_tag"
    assert first.evidence[1].normalized_value == {
        "equipment_tag": "M-101A",
        "matching_record_ids": ["DSMETA-002"],
        "matching_datasheet_ids": ["DS-M-101"],
        "authoritative_record_count": 1,
        "searched_record_count": 2,
    }
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_missing_equipment_datasheet_authority_emits_frozen_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _remove_datasheet_record(package_root, "DSMETA-001")
    gates = _evaluate_gates(package_root)

    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = _check_by_id(
        first,
        EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in first.checks[:7])
    assert check.status == "failed"
    assert len(check.findings) == 1
    assert first.to_dict() == second.to_dict()

    finding = check.findings[0]
    assert finding.code == EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE
    assert finding.result_state == "missing_authoritative_information"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID
    assert finding.review_owner == "mechanical_engineering"
    assert finding.affected_identifiers == ("ITEM-PUMP-001", "P-101A")
    assert finding.expected_value == "one authoritative datasheet"
    assert finding.actual_value == 0
    assert finding.evidence[0].column_name == "equipment_tag"
    assert finding.evidence[1].normalized_value == {
        "equipment_tag": "P-101A",
        "matching_record_ids": [],
        "matching_datasheet_ids": [],
        "authoritative_record_count": 0,
        "searched_record_count": 1,
    }

    association = _check_by_id(
        first,
        EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
    )
    assert association.status == "passed"
    assert association.findings == ()
    assert len(association.evidence) == 2
    assert "1 equipment tag(s) remained owned by check 8" in association.summary
    reciprocity = _check_by_id(
        first,
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    assert reciprocity.status == "passed"
    assert reciprocity.findings == ()
    assert len(reciprocity.evidence) == 3
    assert "1 equipment tag(s) remained owned by check 8" in reciprocity.summary


def test_missing_and_ambiguous_authority_are_sorted_and_order_independent(
    tmp_path: Path,
) -> None:
    original = _copy_package(tmp_path, "original")
    reordered = _copy_package(tmp_path, "reordered")
    for package_root in (original, reordered):
        _make_competing_datasheet_mapping(package_root)

    metadata_path = _datasheet_metadata_path(reordered)
    metadata = _load_json(metadata_path)
    metadata["datasheets"].reverse()
    _write_json(metadata_path, metadata)
    _rewrite_csv(
        reordered / "inputs" / "bom_or_equipment_list.csv",
        lambda rows: rows.reverse(),
    )

    first = _check(
        _evaluate_gates(original),
        EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    )
    second = _check(
        _evaluate_gates(reordered),
        EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    )

    assert first.status == second.status == "failed"
    assert [finding.affected_identifiers for finding in first.findings] == [
        ("ITEM-MOTOR-001", "M-101A"),
        ("ITEM-PUMP-001", "P-101A"),
    ]
    assert [finding.actual_value for finding in first.findings] == [0, 2]
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


def test_datasheet_presence_requires_exact_authority_rule(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    rule = next(
        item
        for item in authority["rules"]
        if item["rule_id"] == EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID
    )
    rule["agreement_rule"] = "similar but unreviewed wording"
    _write_json(authority_path, authority)

    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    check = _check_by_id(
        evaluation,
        EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    )

    assert gates.dependent_checks_allowed is True
    assert all(result.status == "passed" for result in evaluation.checks[:7])
    assert check.status == "skipped"
    assert check.blocked_by == (AUTHORITY_GATE_ID,)
    assert check.findings == ()
    assert check.evidence == ()
    assert EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID in check.summary
    association = _check_by_id(
        evaluation,
        EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
    )
    assert association.status == "skipped"
    assert association.blocked_by == (AUTHORITY_GATE_ID,)
    reciprocity = _check_by_id(
        evaluation,
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    assert reciprocity.status == "skipped"
    assert reciprocity.blocked_by == (AUTHORITY_GATE_ID,)


def test_datasheet_presence_is_independent_of_drawing_and_bom_authority(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    drawing_rule = next(
        item
        for item in authority["rules"]
        if item["rule_id"] == DRAWING_REVISION_AUTHORITY_RULE_ID
    )
    drawing_rule["rule_id"] = "AUTH-DWG-SUBSTITUTE"
    bom_rule = next(
        item
        for item in authority["rules"]
        if item["rule_id"] == BOM_EQUIPMENT_AUTHORITY_RULE_ID
    )
    bom_rule["agreement_rule"] = "similar but unreviewed wording"
    _write_json(authority_path, authority)

    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    statuses = {check.check_id: check.status for check in evaluation.checks}

    assert gates.dependent_checks_allowed is True
    assert all(result.status == "skipped" for result in evaluation.checks[:5])
    assert statuses["bom_item_equipment_manifest_reciprocity"] == "skipped"
    assert statuses["bom_equipment_drawing_presence"] == "skipped"
    assert statuses[EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID] == "passed"
    assert statuses[EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID] == "passed"
    assert statuses[EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID] == "passed"


def test_clean_equipment_datasheet_association_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(gates, EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID)
    second = _check(gates, EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID)

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 4
    assert first.to_dict() == second.to_dict()
    assert first.evidence[0].source_type == "datasheet_spec_metadata"
    assert first.evidence[0].record_id == "DSMETA-002"
    assert first.evidence[0].property_name == "datasheet_id"
    assert first.evidence[0].normalized_value == "DS-M-101"
    assert first.evidence[1].source_type == "bom_or_equipment_list"
    assert first.evidence[1].column_name == "datasheet_id"
    assert first.evidence[1].row_key_value == "ITEM-MOTOR-001"
    assert first.evidence[1].normalized_value == "DS-M-101"
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_wrong_valid_bom_datasheet_id_emits_one_frozen_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _set_bom_datasheet_ids(
        package_root,
        {"ITEM-PUMP-001": "DS-M-101"},
    )
    gates = _evaluate_gates(package_root)

    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = _check_by_id(first, EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID)

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in first.checks[:8])
    assert check.status == "failed"
    assert len(check.findings) == 1
    assert first.to_dict() == second.to_dict()

    finding = check.findings[0]
    assert finding.code == EQUIPMENT_DATASHEET_MISMATCH_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID
    assert finding.review_owner == "mechanical_engineering"
    assert finding.affected_identifiers == ("ITEM-PUMP-001", "P-101A")
    assert finding.expected_value == "DS-P-101"
    assert finding.actual_value == "DS-M-101"
    assert [locator.source_type for locator in finding.evidence] == [
        "datasheet_spec_metadata",
        "bom_or_equipment_list",
    ]
    assert [
        locator.to_dict().get("property_name")
        or locator.to_dict().get("column_name")
        for locator in finding.evidence
    ] == ["datasheet_id", "datasheet_id"]


def test_datasheet_association_findings_are_sorted_and_order_independent(
    tmp_path: Path,
) -> None:
    original = _copy_package(tmp_path, "original")
    reordered = _copy_package(tmp_path, "reordered")
    for package_root in (original, reordered):
        _set_bom_datasheet_ids(
            package_root,
            {
                "ITEM-MOTOR-001": "DS-P-101",
                "ITEM-PUMP-001": "DS-M-101",
            },
        )

    metadata_path = _datasheet_metadata_path(reordered)
    metadata = _load_json(metadata_path)
    metadata["datasheets"].reverse()
    _write_json(metadata_path, metadata)
    _rewrite_csv(
        reordered / "inputs" / "bom_or_equipment_list.csv",
        lambda rows: rows.reverse(),
    )

    first = _check(
        _evaluate_gates(original),
        EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
    )
    second = _check(
        _evaluate_gates(reordered),
        EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
    )

    assert first.status == second.status == "failed"
    assert [finding.affected_identifiers for finding in first.findings] == [
        ("ITEM-MOTOR-001", "M-101A"),
        ("ITEM-PUMP-001", "P-101A"),
    ]
    assert [
        (finding.expected_value, finding.actual_value)
        for finding in first.findings
    ] == [
        ("DS-M-101", "DS-P-101"),
        ("DS-P-101", "DS-M-101"),
    ]
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


def test_clean_equipment_datasheet_manifest_reciprocity_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(
        gates,
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        gates,
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 6
    assert first.to_dict() == second.to_dict()
    assert [locator.source_type for locator in first.evidence[:3]] == [
        "datasheet_spec_metadata",
        "datasheet_spec_metadata",
        "package_manifest",
    ]
    assert first.evidence[0].record_id == "DSMETA-002"
    assert first.evidence[0].property_name == "equipment_tag"
    assert first.evidence[0].normalized_value == "M-101A"
    assert first.evidence[1].property_name == "datasheet_id"
    assert first.evidence[1].normalized_value == "DS-M-101"
    assert first.evidence[2].record_id == "REL-EQ-DS-002"
    assert first.evidence[2].normalized_value == {
        "equipment_tag": "M-101A",
        "datasheet_id": "DS-M-101",
        "required_for_release": True,
    }
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_wrong_valid_manifest_datasheet_target_emits_one_frozen_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _set_manifest_datasheet_targets(
        package_root,
        {"REL-EQ-DS-001": "DS-M-101"},
    )
    gates = _evaluate_gates(package_root)

    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = _check_by_id(
        first,
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in first.checks[:9])
    assert check.status == "failed"
    assert len(check.findings) == 1
    assert first.to_dict() == second.to_dict()

    finding = check.findings[0]
    assert finding.code == EQUIPMENT_DATASHEET_RECIPROCITY_FAILED_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID
    assert finding.review_owner == "mechanical_engineering"
    assert finding.affected_identifiers == ("P-101A",)
    assert finding.expected_value == {
        "equipment_tag": "P-101A",
        "datasheet_id": "DS-P-101",
        "required_for_release": True,
    }
    assert finding.actual_value == {
        "equipment_tag": "P-101A",
        "datasheet_id": "DS-M-101",
        "required_for_release": True,
    }
    assert [locator.source_type for locator in finding.evidence] == [
        "datasheet_spec_metadata",
        "datasheet_spec_metadata",
        "package_manifest",
    ]
    assert finding.evidence[-1].record_id == "REL-EQ-DS-001"


def test_missing_and_multiple_manifest_datasheet_mappings_are_stable_when_reordered(
    tmp_path: Path,
) -> None:
    original = _copy_package(tmp_path, "original")
    reordered = _copy_package(tmp_path, "reordered")

    def replace_pump_mapping_with_motor_conflict(
        manifest: dict[str, Any],
    ) -> None:
        relationships = manifest["relationship_declarations"]
        relationships[:] = [
            item for item in relationships if item["relationship_id"] != "REL-EQ-DS-001"
        ]
        relationships.append(
            {
                "relationship_id": "REL-EQ-DS-000",
                "relationship_type": "equipment_to_datasheet",
                "source": {
                    "identifier_type": "equipment_tag",
                    "identifier": "M-101A",
                },
                "target": {
                    "identifier_type": "datasheet_id",
                    "identifier": "DS-P-101",
                },
                "required_for_release": True,
            }
        )

    for package_root in (original, reordered):
        _mutate_manifest(package_root, replace_pump_mapping_with_motor_conflict)

    metadata_path = _datasheet_metadata_path(reordered)
    metadata = _load_json(metadata_path)
    metadata["datasheets"].reverse()
    _write_json(metadata_path, metadata)

    def reverse_declarations(manifest: dict[str, Any]) -> None:
        manifest["relationship_declarations"].reverse()

    _mutate_manifest(reordered, reverse_declarations)

    first = _check(
        _evaluate_gates(original),
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        _evaluate_gates(reordered),
        EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
    )

    assert first.status == second.status == "failed"
    assert [finding.affected_identifiers for finding in first.findings] == [
        ("M-101A",),
        ("P-101A",),
    ]
    assert first.findings[1].actual_value == "missing"
    assert [mapping["datasheet_id"] for mapping in first.findings[0].actual_value] == [
        "DS-M-101",
        "DS-P-101",
    ]
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
