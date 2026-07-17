from __future__ import annotations

import csv
import json
import shutil
from pathlib import Path
from typing import Any, Callable

import pytest

from mech_eval_harness.package_assurance import run_package_gates
from mech_eval_harness.package_assurance.gates import (
    AUTHORITY_GATE_ID,
    BOUNDARY_GATE_ID,
    DUPLICATE_GATE_ID,
    EVIDENCE_GATE_ID,
    IDENTIFIER_GATE_ID,
    MANIFEST_GATE_ID,
    PACKAGE_GATE_ORDER,
    REVISION_GATE_ID,
    SOURCE_INVENTORY_GATE_ID,
)
from mech_eval_harness.package_assurance.models import (
    PackageGateEvaluation,
    PackageGateResult,
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


def _copy_package(tmp_path: Path) -> Path:
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    return package_root


def _evaluate(package_root: Path) -> PackageGateEvaluation:
    return run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )


def _gate(
    evaluation: PackageGateEvaluation,
    gate_id: str,
) -> PackageGateResult:
    return next(gate for gate in evaluation.gates if gate.gate_id == gate_id)


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
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_clean_development_package_passes_all_p21_gates(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)

    first = _evaluate(package_root)
    second = _evaluate(package_root)

    assert tuple(gate.gate_id for gate in first.gates) == PACKAGE_GATE_ORDER
    assert all(gate.status == "passed" for gate in first.gates)
    assert first.dependent_checks_allowed is True
    assert first.package_id == "PKG-DEV-PUMP-SKID-001"
    assert first.sources is not None
    assert len(first.sources.records) == 23
    assert first.to_dict() == second.to_dict()

    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "C:\\" not in serialized


def test_missing_manifest_fails_before_package_evaluation(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").unlink()

    evaluation = _evaluate(package_root)

    manifest_gate = _gate(evaluation, MANIFEST_GATE_ID)
    assert manifest_gate.status == "failed"
    assert manifest_gate.findings[0].code == "MANIFEST_UNREADABLE"
    assert manifest_gate.findings[0].state == "extraction_or_tool_failure"
    assert all(gate.status == "skipped" for gate in evaluation.gates[1:])
    assert all(gate.blocked_by == (MANIFEST_GATE_ID,) for gate in evaluation.gates[1:])
    assert evaluation.dependent_checks_allowed is False
    serialized = json.dumps(evaluation.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized
    assert "C:\\" not in serialized


def test_malformed_manifest_fails_as_extraction_error(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")

    evaluation = _evaluate(package_root)

    manifest_gate = _gate(evaluation, MANIFEST_GATE_ID)
    assert manifest_gate.status == "failed"
    assert manifest_gate.findings[0].code == "MANIFEST_UNREADABLE"
    assert manifest_gate.findings[0].state == "extraction_or_tool_failure"
    assert all(gate.status == "skipped" for gate in evaluation.gates[1:])


def test_manifest_declaration_failure_is_automatic_fail(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    manifest_path = package_root / "package_manifest.json"
    manifest = _load_json(manifest_path)
    manifest["document_inventory"][1]["document_id"] = manifest[
        "document_inventory"
    ][0]["document_id"]
    _write_json(manifest_path, manifest)

    evaluation = _evaluate(package_root)

    manifest_gate = _gate(evaluation, MANIFEST_GATE_ID)
    assert manifest_gate.status == "failed"
    assert manifest_gate.findings[0].code == "MANIFEST_INVALID"
    assert manifest_gate.findings[0].state == "automatic_fail"
    assert all(gate.status == "skipped" for gate in evaluation.gates[1:])
    serialized = json.dumps(evaluation.to_dict(), sort_keys=True)
    assert str(package_root.resolve()) not in serialized


@pytest.mark.parametrize("mutation", ["missing", "malformed"])
def test_source_inventory_failures_are_controlled_and_skip_dependents(
    tmp_path: Path,
    mutation: str,
) -> None:
    package_root = _copy_package(tmp_path)
    source_path = package_root / "inputs" / "drawing_metadata.json"
    if mutation == "missing":
        source_path.unlink()
        expected_code = "SOURCE_FILE_MISSING"
    else:
        source_path.write_text("{\n", encoding="utf-8")
        expected_code = "SOURCE_PARSE_FAILED"

    evaluation = _evaluate(package_root)

    source_gate = _gate(evaluation, SOURCE_INVENTORY_GATE_ID)
    assert source_gate.status == "failed"
    assert [finding.code for finding in source_gate.findings] == [expected_code]
    assert source_gate.findings[0].state == "extraction_or_tool_failure"
    assert _gate(evaluation, AUTHORITY_GATE_ID).status == "passed"
    assert _gate(evaluation, BOUNDARY_GATE_ID).status == "passed"
    assert _gate(evaluation, IDENTIFIER_GATE_ID).status == "skipped"
    assert _gate(evaluation, DUPLICATE_GATE_ID).status == "skipped"
    assert _gate(evaluation, REVISION_GATE_ID).status == "skipped"
    assert _gate(evaluation, EVIDENCE_GATE_ID).status == "skipped"


def test_invalid_csv_value_is_a_source_parse_failure(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    source_path = package_root / "inputs" / "bom_or_equipment_list.csv"
    _rewrite_csv(source_path, lambda rows: rows[0].__setitem__("quantity", "one"))

    evaluation = _evaluate(package_root)

    source_gate = _gate(evaluation, SOURCE_INVENTORY_GATE_ID)
    assert source_gate.status == "failed"
    finding = source_gate.findings[0]
    assert finding.code == "SOURCE_VALUE_INVALID"
    assert finding.evidence[0].row_number == 2
    assert finding.evidence[0].column_name == "quantity"


def test_unsupported_json_source_version_fails_closed(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    source_path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(source_path)
    document["schema_version"] = "0.4.0"
    _write_json(source_path, document)

    evaluation = _evaluate(package_root)

    source_gate = _gate(evaluation, SOURCE_INVENTORY_GATE_ID)
    assert source_gate.status == "failed"
    assert [finding.code for finding in source_gate.findings] == [
        "SOURCE_SCHEMA_VERSION_UNSUPPORTED"
    ]
    assert source_gate.findings[0].evidence[0].json_pointer == "/schema_version"
    assert _gate(evaluation, IDENTIFIER_GATE_ID).status == "skipped"
    assert _gate(evaluation, DUPLICATE_GATE_ID).status == "skipped"
    assert evaluation.dependent_checks_allowed is False


def test_missing_controlled_file_is_a_boundary_hold(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    manifest = _load_json(package_root / "package_manifest.json")
    reference = manifest["file_references"][0]
    (package_root / reference["path"]).unlink()

    first = _evaluate(package_root)
    second = _evaluate(package_root)

    boundary_gate = _gate(first, BOUNDARY_GATE_ID)
    assert boundary_gate.status == "failed"
    assert len(boundary_gate.findings) == 1
    finding = boundary_gate.findings[0]
    assert finding.code == "BROKEN_FILE_REFERENCE"
    assert finding.state == "automatic_fail"
    assert finding.affected_identifiers == (reference["file_ref_id"],)
    assert finding.evidence[0].boundary_check == "inside_allowed_root"
    assert first.to_dict() == second.to_dict()
    assert first.dependent_checks_allowed is False


def test_duplicate_source_document_id_fails_duplicate_gate(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    source_path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(source_path)
    document["records"][1]["document_id"] = document["records"][0]["document_id"]
    _write_json(source_path, document)

    evaluation = _evaluate(package_root)

    assert _gate(evaluation, SOURCE_INVENTORY_GATE_ID).status == "passed"
    assert _gate(evaluation, IDENTIFIER_GATE_ID).status == "passed"
    duplicate_gate = _gate(evaluation, DUPLICATE_GATE_ID)
    assert duplicate_gate.status == "failed"
    assert [finding.code for finding in duplicate_gate.findings] == [
        "DUPLICATE_CANONICAL_IDENTIFIER"
    ]
    assert duplicate_gate.findings[0].affected_identifiers == ("DOC-DWG-001",)


def test_invalid_revision_format_fails_revision_gate(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    source_path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(source_path)
    document["records"][0]["revision_id"] = "c"
    _write_json(source_path, document)

    evaluation = _evaluate(package_root)

    revision_gate = _gate(evaluation, REVISION_GATE_ID)
    assert revision_gate.status == "failed"
    finding = next(
        item
        for item in revision_gate.findings
        if item.code == "REVISION_FORMAT_INVALID"
    )
    assert finding.state == "automatic_fail"
    assert finding.evidence[0].json_pointer == "/records/0/revision_id"


def test_invalid_revision_progression_fails_revision_gate(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    source_path = package_root / "inputs" / "revision_history.csv"

    def mutate(rows: list[dict[str, str]]) -> None:
        rows[1]["sequence_index"] = "5"

    _rewrite_csv(source_path, mutate)

    evaluation = _evaluate(package_root)

    revision_gate = _gate(evaluation, REVISION_GATE_ID)
    assert revision_gate.status == "failed"
    codes = {finding.code for finding in revision_gate.findings}
    assert "REVISION_SEQUENCE_INDEX_INVALID" in codes


def test_missing_required_authority_rule_blocks_policy_dependent_gates(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    authority["rules"] = [
        rule
        for rule in authority["rules"]
        if rule["field"] != "drawing.current_revision"
    ]
    _write_json(authority_path, authority)

    evaluation = _evaluate(package_root)

    authority_gate = _gate(evaluation, AUTHORITY_GATE_ID)
    assert authority_gate.status == "failed"
    finding = next(
        item
        for item in authority_gate.findings
        if item.code == "AUTHORITY_REQUIRED_RULE_MISSING"
    )
    assert finding.state == "missing_authoritative_information"
    assert _gate(evaluation, IDENTIFIER_GATE_ID).status == "passed"
    assert _gate(evaluation, DUPLICATE_GATE_ID).blocked_by == (AUTHORITY_GATE_ID,)
    assert _gate(evaluation, REVISION_GATE_ID).status == "skipped"
    assert _gate(evaluation, EVIDENCE_GATE_ID).status == "skipped"


def test_contradictory_authority_source_fails_closed(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    rule = next(
        item for item in authority["rules"] if item["rule_id"] == "AUTH-DWG-001"
    )
    rule["secondary_sources"].append(rule["authoritative_source"])
    _write_json(authority_path, authority)

    evaluation = _evaluate(package_root)

    authority_gate = _gate(evaluation, AUTHORITY_GATE_ID)
    assert authority_gate.status == "failed"
    finding = next(
        item
        for item in authority_gate.findings
        if item.code == "AUTHORITY_SOURCE_CONTRADICTION"
    )
    assert finding.state == "automatic_fail"
    assert finding.affected_identifiers == ("AUTH-DWG-001",)


def test_malformed_authority_value_types_fail_closed(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    authority["normalization_profiles"][0]["on_ambiguous_normalization"] = {
        "invalid": True
    }
    authority["revision_schemes"][0]["scheme"] = {"invalid": True}
    rule = authority["rules"][0]
    rule["authoritative_source"] = {"invalid": True}
    rule["on_conflict"] = ["automatic_fail"]
    rule["agreement_rule"] = None
    rule["review_owner"] = []
    drawing_rule = next(
        item for item in authority["rules"] if item["rule_id"] == "AUTH-DWG-001"
    )
    drawing_rule["normalization_profile"] = {"invalid": True}
    _write_json(authority_path, authority)

    evaluation = _evaluate(package_root)

    authority_gate = _gate(evaluation, AUTHORITY_GATE_ID)
    assert authority_gate.status == "failed"
    codes = {finding.code for finding in authority_gate.findings}
    assert {
        "AUTHORITY_NORMALIZATION_ROUTE_INVALID",
        "AUTHORITY_REVISION_SCHEME_INVALID",
        "AUTHORITY_SOURCE_UNKNOWN",
        "AUTHORITY_ROUTE_INVALID",
        "AUTHORITY_NORMALIZATION_PROFILE_UNRESOLVED",
        "AUTHORITY_RULE_TEXT_INVALID",
    } <= codes
    assert _gate(evaluation, DUPLICATE_GATE_ID).status == "skipped"


def test_incomplete_duplicate_policy_blocks_duplicate_evaluation(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    policy = next(
        item
        for item in authority["duplicate_policies"]
        if item["controlled_identifier"] == "equipment_tag"
    )
    representation = policy["intentional_duplicate_representation"]
    representation["required_fields"].remove("duplicate_instance_id")
    representation["on_missing_disambiguation"] = "engineering_review_required"
    _write_json(authority_path, authority)

    evaluation = _evaluate(package_root)

    authority_gate = _gate(evaluation, AUTHORITY_GATE_ID)
    assert authority_gate.status == "failed"
    codes = {finding.code for finding in authority_gate.findings}
    assert "AUTHORITY_DUPLICATE_DISAMBIGUATION_INCOMPLETE" in codes
    assert "AUTHORITY_DUPLICATE_MISSING_ROUTE_INVALID" in codes
    duplicate_gate = _gate(evaluation, DUPLICATE_GATE_ID)
    assert duplicate_gate.status == "skipped"
    assert duplicate_gate.blocked_by == (AUTHORITY_GATE_ID,)


def test_incomplete_evidence_requirements_fail_evidence_gate(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = _load_json(authority_path)
    authority["evidence_locator_requirements"]["csv"]["required_fields"].remove(
        "row_key"
    )
    _write_json(authority_path, authority)

    evaluation = _evaluate(package_root)

    assert _gate(evaluation, AUTHORITY_GATE_ID).status == "passed"
    evidence_gate = _gate(evaluation, EVIDENCE_GATE_ID)
    assert evidence_gate.status == "failed"
    finding = next(
        item
        for item in evidence_gate.findings
        if item.code == "EVIDENCE_REQUIREMENT_INCOMPLETE"
    )
    assert finding.affected_identifiers == ("csv", "row_key")
