from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance import load_package_manifest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "development"
    / "pump_skid_clean_v1"
)
PACKAGE_ROOT = FIXTURE_ROOT / "package"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _resolve_json_pointer(document: Any, pointer: str) -> Any:
    value = document
    for encoded_part in pointer.removeprefix("/").split("/"):
        part = encoded_part.replace("~1", "/").replace("~0", "~")
        value = value[int(part)] if isinstance(value, list) else value[part]
    return value


def _contains_value(document: Any, expected: Any) -> bool:
    if document == expected:
        return True
    if isinstance(document, dict):
        return any(_contains_value(value, expected) for value in document.values())
    if isinstance(document, list):
        return any(_contains_value(value, expected) for value in document)
    return False


def _relationship_semantics(relationship: dict[str, Any]) -> dict[str, Any]:
    return {
        key: relationship[key]
        for key in (
            "relationship_id",
            "relationship_type",
            "source",
            "target",
            "required_for_release",
        )
    }


def test_clean_fixture_manifest_paths_exist_and_oracles_are_hidden() -> None:
    loaded = load_package_manifest(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=PACKAGE_ROOT,
    )
    metadata = _load_json(FIXTURE_ROOT / "benchmark_metadata.json")

    assert loaded.package_id == "PKG-DEV-PUMP-SKID-001"
    assert all(path.is_file() for path in loaded.source_paths.values())
    assert all(path.is_file() for path in loaded.file_reference_paths.values())

    for document in loaded.manifest["document_inventory"]:
        artifact = loaded.file_reference_paths[document["file_ref_id"]].read_text(
            encoding="utf-8"
        )
        canonical_id = next(
            (
                document[key]
                for key in (
                    "drawing_number",
                    "datasheet_id",
                    "specification_id",
                    "title",
                )
                if key in document
            )
        )
        assert f"Document ID: {document['document_id']}" in artifact
        assert f"Canonical ID: {canonical_id}" in artifact
        assert f"Revision: {document['current_revision']['revision_id']}" in artifact

    declared_paths = {
        source["path"] for source in loaded.manifest["source_inventory"]
    } | {
        reference["path"] for reference in loaded.manifest["file_references"]
    }
    assert all(not path.startswith("expected/") for path in declared_paths)

    for relative_path in metadata["producer_hidden_paths"]:
        hidden_path = FIXTURE_ROOT / relative_path
        assert hidden_path.is_file()
        assert relative_path.removeprefix("package/") not in declared_paths

    for relative_path in metadata["producer_visible_paths"]:
        assert (FIXTURE_ROOT / relative_path).exists()


def test_clean_fixture_sources_are_internally_consistent() -> None:
    manifest = _load_json(PACKAGE_ROOT / "package_manifest.json")
    documents = {
        document["document_id"]: document
        for document in manifest["document_inventory"]
    }
    drawing_register = _load_csv(PACKAGE_ROOT / "inputs/drawing_register.csv")
    drawing_metadata = _load_json(
        PACKAGE_ROOT / "inputs/drawing_metadata.json"
    )["records"]
    equipment = _load_csv(PACKAGE_ROOT / "inputs/bom_or_equipment_list.csv")
    technical_metadata = _load_json(
        PACKAGE_ROOT / "inputs/datasheet_spec_metadata.json"
    )
    revision_history = _load_csv(PACKAGE_ROOT / "inputs/revision_history.csv")

    register_by_document = {row["document_id"]: row for row in drawing_register}
    metadata_by_document = {
        record["document_id"]: record for record in drawing_metadata
    }
    assert set(register_by_document) == set(metadata_by_document)
    for document_id, register_record in register_by_document.items():
        metadata_record = metadata_by_document[document_id]
        document = documents[document_id]
        assert register_record["drawing_number"] == metadata_record["drawing_number"]
        assert register_record["drawing_number"] == document["drawing_number"]
        assert register_record["revision_id"] == metadata_record["revision_id"]
        assert register_record["revision_id"] == document["current_revision"]["revision_id"]
        assert register_record["file_ref_id"] == metadata_record["file_ref_id"]
        assert register_record["file_ref_id"] == document["file_ref_id"]

    item_ids = [row["item_id"] for row in equipment]
    equipment_tags = [row["equipment_tag"] for row in equipment]
    assert len(item_ids) == len(set(item_ids))
    assert len(equipment_tags) == len(set(equipment_tags))

    drawing_numbers = {record["drawing_number"] for record in drawing_metadata}
    tags_on_drawings = {
        tag for record in drawing_metadata for tag in record["equipment_tags"]
    }
    datasheets = {
        record["datasheet_id"]: record
        for record in technical_metadata["datasheets"]
    }
    specifications = {
        record["specification_id"]: record
        for record in technical_metadata["specifications"]
    }
    for row in equipment:
        assert row["equipment_tag"] in tags_on_drawings
        assert row["drawing_number"] in drawing_numbers
        assert datasheets[row["datasheet_id"]]["equipment_tag"] == row["equipment_tag"]
        assert row["equipment_tag"] in specifications[row["specification_id"]][
            "equipment_tags"
        ]

    pump_values = datasheets["DS-P-101"]["controlled_values"]
    pump_requirements = specifications["SPEC-PUMP-001"]["requirement_summary"]
    assert pump_values["design_pressure"] == pump_requirements[
        "minimum_design_pressure"
    ]
    assert pump_values["casing_material"] == pump_requirements[
        "required_casing_material"
    ]
    motor_values = datasheets["DS-M-101"]["controlled_values"]
    motor_requirements = specifications["SPEC-MOTOR-001"]["requirement_summary"]
    for value_name, requirement_name in (
        ("rated_power", "minimum_rated_power"),
        ("rated_voltage", "required_voltage"),
        ("rated_frequency", "required_frequency"),
        ("enclosure", "required_enclosure"),
    ):
        assert motor_values[value_name] == motor_requirements[requirement_name]

    history_by_document: dict[str, list[dict[str, str]]] = defaultdict(list)
    for revision in revision_history:
        history_by_document[revision["document_id"]].append(revision)
    assert set(history_by_document) == set(documents)
    for document_id, history in history_by_document.items():
        current = [row for row in history if row["revision_status"] == "current"]
        sequence = [int(row["sequence_index"]) for row in history]
        assert len(current) == 1
        assert sequence == list(range(1, len(sequence) + 1))
        assert current[0]["revision_id"] == documents[document_id]["current_revision"][
            "revision_id"
        ]

    fixture_authority = _load_json(PACKAGE_ROOT / "authority/authority_map.json")
    accepted_authority = _load_json(
        ROOT / "docs/package_assurance/authority_map_example_v0.3.0.json"
    )
    metadata_keys = {"example_id", "review_status", "applies_to", "note"}
    assert {
        key: value
        for key, value in fixture_authority.items()
        if key not in metadata_keys
    } == {
        key: value
        for key, value in accepted_authority.items()
        if key not in metadata_keys
    }
    assert fixture_authority["applies_to"] == manifest["package_id"]


def test_clean_fixture_golden_relationships_and_locators_resolve() -> None:
    manifest = _load_json(PACKAGE_ROOT / "package_manifest.json")
    golden = _load_json(PACKAGE_ROOT / "expected/golden_relationships.json")
    expected_findings = _load_json(
        PACKAGE_ROOT / "expected/expected_findings.json"
    )
    expected_state = _load_json(
        PACKAGE_ROOT / "expected/expected_release_state.json"
    )
    source_by_type = {
        source["source_type"]: source["path"]
        for source in manifest["source_inventory"]
    }

    assert golden["relationship_count"] == len(golden["relationships"]) == 20
    assert [
        _relationship_semantics(relationship)
        for relationship in golden["relationships"]
    ] == manifest["relationship_declarations"]
    assert expected_findings["expected_findings"] == []
    assert expected_findings["allowed_incidental_findings"] == []
    assert expected_state["expected_package_state"] == "automatic_pass"
    assert expected_state["expected_cli_exit_code"] == 0
    assert expected_state["human_release_approval_required"] is True

    for relationship in golden["relationships"]:
        locator = relationship["evidence_locator"]
        assert locator["source_file"] == source_by_type[locator["source_type"]]
        source_path = PACKAGE_ROOT / locator["source_file"]
        if locator["format"] == "csv":
            assert locator["header_row_number"] == 1
            row = _load_csv(source_path)[locator["row_number"] - 2]
            row_key = locator["row_key"]
            assert row[row_key["column_name"]] == row_key["value"]
            actual = row[locator["column_name"]]
        else:
            source_document = _load_json(source_path)
            actual = _resolve_json_pointer(
                source_document,
                locator["json_pointer"],
            )
            assert _contains_value(source_document, locator["record_id"])
            assert locator["property_name"] in locator["json_pointer"]
        assert actual == locator["original_value"]
        assert str(actual).strip() == locator["normalized_value"]


def test_clean_fixture_inventory_matches_package_tree() -> None:
    inventory = _load_json(FIXTURE_ROOT / "fixture_inventory.json")
    metadata = _load_json(FIXTURE_ROOT / "benchmark_metadata.json")
    expected_entries = inventory["files"]
    actual_paths = sorted(
        path.relative_to(PACKAGE_ROOT).as_posix()
        for path in PACKAGE_ROOT.rglob("*")
        if path.is_file()
    )

    assert inventory["scope"] == "package_tree"
    assert inventory["file_count"] == len(expected_entries) == len(actual_paths)
    assert [entry["path"] for entry in expected_entries] == actual_paths

    tree_hash_input = bytearray()
    for entry in expected_entries:
        path = PACKAGE_ROOT / entry["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        assert entry["size_bytes"] == path.stat().st_size
        assert entry["sha256"] == digest
        tree_hash_input.extend(entry["path"].encode("utf-8"))
        tree_hash_input.extend(b"\0")
        tree_hash_input.extend(digest.encode("ascii"))
        tree_hash_input.extend(b"\n")

    tree_hash = hashlib.sha256(tree_hash_input).hexdigest()
    assert inventory["content_hash"] == tree_hash
    assert metadata["content_hash"]["value"] == tree_hash
