from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance import (
    BOM_EQUIPMENT_AUTHORITY_RULE_ID,
    BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE,
    BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE,
    DRAWING_REVISION_AUTHORITY_RULE_ID,
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
    _set_metadata_equipment_tags,
    _write_json,
)


def test_clean_bom_item_equipment_reciprocity_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(
        gates,
        BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        gates,
        BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 6
    assert first.to_dict() == second.to_dict()
    assert tuple(locator.to_dict() for locator in first.evidence[:3]) == (
        {
            "source_type": "bom_or_equipment_list",
            "source_file": "inputs/bom_or_equipment_list.csv",
            "format": "csv",
            "row_number": 3,
            "header_row_number": 1,
            "column_name": "item_id",
            "row_key": {
                "column_name": "item_id",
                "value": "ITEM-MOTOR-001",
            },
            "original_value": "ITEM-MOTOR-001",
            "normalized_value": "ITEM-MOTOR-001",
        },
        {
            "source_type": "bom_or_equipment_list",
            "source_file": "inputs/bom_or_equipment_list.csv",
            "format": "csv",
            "row_number": 3,
            "header_row_number": 1,
            "column_name": "equipment_tag",
            "row_key": {
                "column_name": "item_id",
                "value": "ITEM-MOTOR-001",
            },
            "original_value": "M-101A",
            "normalized_value": "M-101A",
        },
        {
            "source_type": "package_manifest",
            "source_file": "package_manifest.json",
            "format": "json",
            "json_pointer": "/relationship_declarations/13",
            "record_id": "REL-ITEM-EQ-002",
            "property_name": "relationship_declarations",
            "original_value": {
                "relationship_id": "REL-ITEM-EQ-002",
                "relationship_type": "item_to_equipment",
                "source": {
                    "identifier_type": "item_id",
                    "identifier": "ITEM-MOTOR-001",
                },
                "target": {
                    "identifier_type": "equipment_tag",
                    "identifier": "M-101A",
                },
                "required_for_release": True,
            },
            "normalized_value": {
                "item_id": "ITEM-MOTOR-001",
                "equipment_tag": "M-101A",
                "required_for_release": True,
            },
        },
    )

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "package_state" not in serialized


def test_wrong_valid_bom_manifest_target_emits_one_frozen_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def use_wrong_valid_target(manifest: dict[str, Any]) -> None:
        relationship = next(
            item
            for item in manifest["relationship_declarations"]
            if item["relationship_id"] == "REL-ITEM-EQ-001"
        )
        relationship["target"]["identifier"] = "M-101A"

    _mutate_manifest(package_root, use_wrong_valid_target)
    gates = _evaluate_gates(package_root)
    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = next(
        result
        for result in first.checks
        if result.check_id == BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in first.checks[:5])
    assert check.check_id == BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID
    assert check.status == "failed"
    assert len(check.findings) == 1
    assert first.to_dict() == second.to_dict()

    finding = check.findings[0]
    assert finding.code == BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == BOM_EQUIPMENT_AUTHORITY_RULE_ID
    assert finding.review_owner == "mechanical_engineering"
    assert finding.affected_identifiers == ("ITEM-PUMP-001",)
    assert finding.expected_value == {
        "item_id": "ITEM-PUMP-001",
        "equipment_tag": "P-101A",
        "required_for_release": True,
    }
    assert finding.actual_value == {
        "item_id": "ITEM-PUMP-001",
        "equipment_tag": "M-101A",
        "required_for_release": True,
    }
    assert [locator.to_dict().get("column_name") for locator in finding.evidence] == [
        "item_id",
        "equipment_tag",
        None,
    ]
    assert finding.evidence[-1].json_pointer == "/relationship_declarations/12"


def test_missing_and_extra_bom_manifest_mappings_are_sorted_and_repeatable(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def replace_mapping_with_extra(manifest: dict[str, Any]) -> None:
        relationships = manifest["relationship_declarations"]
        relationships[:] = [
            item
            for item in relationships
            if item["relationship_id"] != "REL-ITEM-EQ-001"
        ]
        relationships.append(
            {
                "relationship_id": "REL-ITEM-EQ-999",
                "relationship_type": "item_to_equipment",
                "source": {
                    "identifier_type": "item_id",
                    "identifier": "ITEM-EXTRA-001",
                },
                "target": {
                    "identifier_type": "equipment_tag",
                    "identifier": "P-101A",
                },
                "required_for_release": True,
            }
        )

    _mutate_manifest(package_root, replace_mapping_with_extra)
    gates = _evaluate_gates(package_root)
    first = _check(
        gates,
        BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        gates,
        BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "failed"
    assert [finding.affected_identifiers[0] for finding in first.findings] == [
        "ITEM-EXTRA-001",
        "ITEM-PUMP-001",
    ]
    assert first.findings[0].expected_value == (
        "authoritative release-required BOM item"
    )
    assert first.findings[1].actual_value == "missing"
    assert first.to_dict() == second.to_dict()


def test_bom_reciprocity_requires_exact_accepted_authority_rule(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    bom_rule = next(
        rule
        for rule in authority["rules"]
        if rule["rule_id"] == BOM_EQUIPMENT_AUTHORITY_RULE_ID
    )
    bom_rule["agreement_rule"] = "similar but unreviewed wording"
    _write_json(authority_path, authority)

    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)
    check = next(
        result
        for result in evaluation.checks
        if result.check_id == BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID
    )

    assert gates.dependent_checks_allowed is True
    assert all(result.status == "passed" for result in evaluation.checks[:5])
    assert check.status == "skipped"
    assert check.blocked_by == (AUTHORITY_GATE_ID,)
    assert check.findings == ()
    assert check.evidence == ()
    assert "AUTH-BOM-002" in check.summary


def test_bom_reciprocity_does_not_depend_on_drawing_authority_rule(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    drawing_rule = next(
        rule
        for rule in authority["rules"]
        if rule["rule_id"] == DRAWING_REVISION_AUTHORITY_RULE_ID
    )
    drawing_rule["rule_id"] = "AUTH-DWG-SUBSTITUTE"
    _write_json(authority_path, authority)

    gates = _evaluate_gates(package_root)
    evaluation = run_package_relationships(gates)

    assert gates.dependent_checks_allowed is True
    assert all(result.status == "skipped" for result in evaluation.checks[:5])
    assert all(
        next(
            result
            for result in evaluation.checks
            if result.check_id == check_id
        ).status
        == "passed"
        for check_id in (
            BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
            BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
        )
    )


def test_multiple_bom_manifest_mappings_emit_one_stable_item_finding(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)

    def add_conflicting_mapping(manifest: dict[str, Any]) -> None:
        manifest["relationship_declarations"].append(
            {
                "relationship_id": "REL-ITEM-EQ-CONFLICT",
                "relationship_type": "item_to_equipment",
                "source": {
                    "identifier_type": "item_id",
                    "identifier": "ITEM-PUMP-001",
                },
                "target": {
                    "identifier_type": "equipment_tag",
                    "identifier": "M-101A",
                },
                "required_for_release": True,
            }
        )

    _mutate_manifest(package_root, add_conflicting_mapping)
    gates = _evaluate_gates(package_root)
    first = _check(
        gates,
        BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    )
    second = _check(
        gates,
        BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "failed"
    assert len(first.findings) == 1
    assert first.findings[0].affected_identifiers == ("ITEM-PUMP-001",)
    assert [
        mapping["equipment_tag"]
        for mapping in first.findings[0].actual_value
    ] == ["P-101A", "M-101A"]
    assert first.to_dict() == second.to_dict()


def test_clean_bom_equipment_drawing_presence_passes_with_exact_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates = _evaluate_gates(package_root)

    first = _check(gates, BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID)
    second = _check(gates, BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID)

    assert all(gate.status == "passed" for gate in gates.gates)
    assert first.status == "passed"
    assert first.findings == ()
    assert first.blocked_by == ()
    assert len(first.evidence) == 4
    assert first.to_dict() == second.to_dict()
    assert first.evidence[0].column_name == "equipment_tag"
    assert first.evidence[0].row_key_value == "ITEM-MOTOR-001"
    assert first.evidence[1].json_pointer == "/records"
    assert first.evidence[1].property_name == "equipment_tags"
    assert first.evidence[1].normalized_value == {
        "equipment_tag": "M-101A",
        "matching_record_ids": ["DWMETA-001"],
        "searched_record_count": 2,
    }
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized


def test_missing_bom_equipment_drawing_reference_emits_frozen_hold(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    _set_metadata_equipment_tags(
        package_root,
        {"DWMETA-001": ["P-101A"]},
    )
    gates = _evaluate_gates(package_root)

    first = run_package_relationships(gates)
    second = run_package_relationships(gates)
    check = next(
        result
        for result in first.checks
        if result.check_id == BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID
    )

    assert all(gate.status == "passed" for gate in gates.gates)
    assert all(result.status == "passed" for result in first.checks[:6])
    assert check.check_id == BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID
    assert check.status == "failed"
    assert len(check.findings) == 1
    assert first.to_dict() == second.to_dict()

    finding = check.findings[0]
    assert finding.code == BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE
    assert finding.result_state == "automatic_fail"
    assert finding.severity == "high"
    assert finding.release_hold is True
    assert finding.authority_rule_id == BOM_EQUIPMENT_AUTHORITY_RULE_ID
    assert finding.review_owner == "mechanical_engineering"
    assert finding.affected_identifiers == ("ITEM-MOTOR-001", "M-101A")
    assert finding.expected_value == (
        "at least one drawing_metadata equipment_tags reference"
    )
    assert finding.actual_value == "missing"
    assert finding.evidence[0].column_name == "equipment_tag"
    assert finding.evidence[1].normalized_value == {
        "equipment_tag": "M-101A",
        "matching_record_ids": [],
        "searched_record_count": 2,
    }


def test_bom_drawing_presence_uses_exact_authority_and_stable_item_order(
    tmp_path: Path,
) -> None:
    missing_package = _copy_package(tmp_path, "missing")
    _set_metadata_equipment_tags(
        missing_package,
        {"DWMETA-001": [], "DWMETA-002": []},
    )
    first = _check(
        _evaluate_gates(missing_package),
        BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    )
    second = _check(
        _evaluate_gates(missing_package),
        BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    )
    assert [finding.affected_identifiers for finding in first.findings] == [
        ("ITEM-MOTOR-001", "M-101A"),
        ("ITEM-PUMP-001", "P-101A"),
    ]
    assert first.to_dict() == second.to_dict()

    authority_package = _copy_package(tmp_path, "authority")
    authority_path = authority_package / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    bom_rule = next(
        rule
        for rule in authority["rules"]
        if rule["rule_id"] == BOM_EQUIPMENT_AUTHORITY_RULE_ID
    )
    bom_rule["secondary_sources"] = ["drawing_metadata"]
    _write_json(authority_path, authority)
    evaluation = run_package_relationships(_evaluate_gates(authority_package))
    reciprocity = next(
        result
        for result in evaluation.checks
        if result.check_id == BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID
    )
    drawing_presence = next(
        result
        for result in evaluation.checks
        if result.check_id == BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID
    )
    assert reciprocity.status == "skipped"
    assert drawing_presence.status == "skipped"
    assert drawing_presence.blocked_by == (AUTHORITY_GATE_ID,)


def test_bom_drawing_presence_finding_ignores_source_record_order(
    tmp_path: Path,
) -> None:
    original = _copy_package(tmp_path, "original")
    reordered = _copy_package(tmp_path, "reordered")
    for package_root in (original, reordered):
        _set_metadata_equipment_tags(
            package_root,
            {"DWMETA-001": ["P-101A"]},
        )

    metadata_path = reordered / "inputs" / "drawing_metadata.json"
    metadata = _load_json(metadata_path)
    metadata["records"].reverse()
    _write_json(metadata_path, metadata)
    _rewrite_csv(
        reordered / "inputs" / "bom_or_equipment_list.csv",
        lambda rows: rows.reverse(),
    )

    first = _check(
        _evaluate_gates(original),
        BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    )
    second = _check(
        _evaluate_gates(reordered),
        BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    )

    assert first.status == second.status == "failed"
    assert len(first.findings) == len(second.findings) == 1
    original_finding = first.findings[0]
    reordered_finding = second.findings[0]
    assert (
        original_finding.finding_id,
        original_finding.code,
        original_finding.affected_identifiers,
        original_finding.expected_value,
        original_finding.actual_value,
    ) == (
        reordered_finding.finding_id,
        reordered_finding.code,
        reordered_finding.affected_identifiers,
        reordered_finding.expected_value,
        reordered_finding.actual_value,
    )
