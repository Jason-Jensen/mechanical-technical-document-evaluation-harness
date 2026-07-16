from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance import load_package_manifest


ROOT = Path(__file__).resolve().parents[1]
FAMILY_ROOT = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "held_out"
    / "instrument_air_module_v1"
)
SCENARIOS_ROOT = FAMILY_ROOT / "scenarios"
DEVELOPMENT_ROOT = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "development"
    / "pump_skid_clean_v1"
    / "package"
)


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_hash(package_root: Path, entries: list[dict[str, Any]]) -> str:
    canonical = bytearray()
    for entry in entries:
        digest = _sha256(package_root / entry["path"])
        canonical.extend(entry["path"].encode("utf-8"))
        canonical.extend(b"\0")
        canonical.extend(digest.encode("ascii"))
        canonical.extend(b"\n")
    return hashlib.sha256(canonical).hexdigest()


def _assert_locator(package_root: Path, locator: dict[str, Any]) -> Any:
    source_path = package_root / locator["source_file"]
    source_format = locator["format"]

    if source_format == "csv":
        assert locator["header_row_number"] == 1
        row = _load_csv(source_path)[locator["row_number"] - 2]
        row_key = locator["row_key"]
        assert row[row_key["column_name"]] == row_key["value"]
        actual = row[locator["column_name"]]
    elif source_format == "json":
        source_document = _load_json(source_path)
        actual = _resolve_json_pointer(source_document, locator["json_pointer"])
        assert _contains_value(source_document, locator["record_id"])
        assert locator["property_name"] in locator["json_pointer"]
    else:
        assert source_format == "file_reference"
        assert locator["declared_relative_path"] == locator["source_file"]
        assert locator["resolved_package_relative_path"] == locator["source_file"]
        assert locator["boundary_check"] == "inside_allowed_root"
        if locator["existence_check"] == "missing":
            assert not source_path.exists()
        else:
            assert locator["existence_check"] == "exists"
            assert source_path.is_file()
        return None

    assert actual == locator["original_value"]
    assert str(actual).strip() == str(locator["normalized_value"])
    return actual


def _scenario_catalog() -> dict[str, Any]:
    return _load_json(FAMILY_ROOT / "protected/scenario_catalog.json")


def _fault_matrix() -> dict[str, Any]:
    return _load_json(FAMILY_ROOT / "protected/fault_matrix.json")


def _canonical_identifiers(manifest: dict[str, Any]) -> set[str]:
    identifiers: set[str] = set()
    for document in manifest["document_inventory"]:
        for key in (
            "document_id",
            "drawing_number",
            "datasheet_id",
            "specification_id",
            "file_ref_id",
        ):
            if key in document:
                identifiers.add(document[key])
    for relationship in manifest["relationship_declarations"]:
        identifiers.add(relationship["source"]["identifier"])
        identifiers.add(relationship["target"]["identifier"])
    return identifiers


def test_held_out_family_meets_the_p13_scenario_contract() -> None:
    family = _load_json(FAMILY_ROOT / "family_metadata.json")
    catalog = _scenario_catalog()
    fault_matrix = _fault_matrix()
    oracle = _load_json(FAMILY_ROOT / "protected/oracle_contract.json")
    scenarios = catalog["scenarios"]
    faults = fault_matrix["records"]

    assert family["package_family_id"] == "FAM-HO-INSTRUMENT-AIR-001"
    assert family["split"] == catalog["split"] == fault_matrix["split"] == "held_out"
    assert family["synthetic"] is True
    assert catalog["producer_hidden"] is True
    assert fault_matrix["producer_hidden"] is True
    assert family["scenario_count"] == catalog["scenario_count"] == len(scenarios) == 8
    assert catalog["clean_scenario_count"] == 1
    assert catalog["single_fault_scenario_count"] == 6
    assert catalog["compound_fault_scenario_count"] == 1
    assert Counter(item["scenario_type"] for item in scenarios) == {
        "clean": 1,
        "single_fault": 6,
        "compound_fault": 1,
    }
    assert len({item["scenario_id"] for item in scenarios}) == 8
    assert len({item["package_id"] for item in scenarios}) == 8

    assert fault_matrix["fault_count"] == len(faults) == 8
    assert fault_matrix["release_blocking_fault_count"] == 7
    assert sum(fault["expected_release_hold"] for fault in faults) == 7
    release_blocking_scenarios = {
        fault["scenario_id"]
        for fault in faults
        if fault["expected_release_hold"]
    }
    assert len(release_blocking_scenarios) == 7
    assert len(release_blocking_scenarios) >= 4
    assert "evaluator_uncertainty" in {
        scenario["expected_package_state"] for scenario in scenarios
    }

    expected_check_ids = {check["check_id"] for check in oracle["checks"]}
    required_check_ids = {
        check_id for fault in faults for check_id in fault["required_check_ids"]
    }
    assert expected_check_ids == required_check_ids
    assert oracle["check_version"] == "0.3.0"
    assert {item["value"] for item in oracle["severity_values"]} == {
        "critical",
        "high",
        "medium",
    }
    assert oracle["implementation_status"] == (
        "benchmark_expectation_only_no_evaluator_implementation"
    )

    faults_by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fault in faults:
        faults_by_scenario[fault["scenario_id"]].append(fault)
        assert fault["expected_package_state"] in {
            scenario["expected_package_state"] for scenario in scenarios
        }
        assert fault["required_findings"]
        assert fault["allowed_incidental_findings"] == []

    for scenario in scenarios:
        scenario_root = SCENARIOS_ROOT / scenario["scenario_slug"]
        expected_findings = _load_json(
            scenario_root / "package/expected/expected_findings.json"
        )
        expected_state = _load_json(
            scenario_root / "package/expected/expected_release_state.json"
        )
        scenario_faults = faults_by_scenario[scenario["scenario_id"]]
        required_findings = [
            finding
            for fault in scenario_faults
            for finding in fault["required_findings"]
        ]

        assert expected_findings["seeded_fault_ids"] == scenario["seeded_fault_ids"]
        assert expected_findings["expected_findings"] == required_findings
        assert expected_findings["allowed_incidental_findings"] == []
        assert expected_state["expected_package_state"] == scenario[
            "expected_package_state"
        ]
        assert expected_state["expected_cli_exit_code"] == scenario[
            "expected_cli_exit_code"
        ]
        assert expected_state["expected_finding_ids"] == [
            finding["finding_id"] for finding in required_findings
        ]
        assert expected_state["expected_release_hold"] is any(
            finding["release_hold"] for finding in required_findings
        )
        assert all(
            finding["check_version"] == oracle["check_version"]
            for finding in required_findings
        )

    compound_state = _load_json(
        SCENARIOS_ROOT
        / "compound_revision_and_title/package/expected/expected_release_state.json"
    )
    assert compound_state["expected_blocking_states"] == [
        "automatic_fail",
        "engineering_review_required",
    ]
    assert compound_state["expected_package_state"] == "automatic_fail"
    assert compound_state["expected_cli_exit_code"] == 1


def test_held_out_packages_load_and_keep_oracles_outside_the_manifest() -> None:
    for scenario in _scenario_catalog()["scenarios"]:
        scenario_root = SCENARIOS_ROOT / scenario["scenario_slug"]
        package_root = scenario_root / "package"
        metadata = _load_json(scenario_root / "benchmark_metadata.json")
        loaded = load_package_manifest(
            ROOT,
            Path("package_manifest.json"),
            allowed_package_root=package_root,
        )

        assert loaded.package_id == scenario["package_id"] == metadata["package_id"]
        assert metadata["scenario_id"] == scenario["scenario_id"]
        assert metadata["scenario_type"] == scenario["scenario_type"]
        assert metadata["package_family_id"] == "FAM-HO-INSTRUMENT-AIR-001"
        assert metadata["split"] == "held_out"
        assert len(loaded.manifest["source_inventory"]) == 7
        assert len(loaded.manifest["document_inventory"]) == 11
        assert len(loaded.manifest["file_references"]) == 11
        assert len(loaded.manifest["relationship_declarations"]) == 31
        assert all(path.is_file() for path in loaded.source_paths.values())

        missing_references = {
            path.relative_to(package_root).as_posix()
            for path in loaded.file_reference_paths.values()
            if not path.is_file()
        }
        expected_missing = (
            {"files/issued_drawings/AIR-MOD-2300_CONNECTION__r02.ref"}
            if scenario["scenario_slug"] == "missing_drawing_file"
            else set()
        )
        assert missing_references == expected_missing

        declared_paths = {
            source["path"] for source in loaded.manifest["source_inventory"]
        } | {
            reference["path"] for reference in loaded.manifest["file_references"]
        }
        assert all(not path.startswith("expected/") for path in declared_paths)
        for hidden_path in metadata["producer_hidden_paths"]:
            if hidden_path.startswith("family:"):
                resolved = FAMILY_ROOT / hidden_path.removeprefix("family:")
            else:
                resolved = scenario_root / hidden_path
            assert resolved.is_file()
        for visible_path in metadata["producer_visible_paths"]:
            assert (scenario_root / visible_path).exists()

        authority = _load_json(package_root / "authority/authority_map.json")
        assert authority["applies_to"] == "FAM-HO-INSTRUMENT-AIR-001"
        assert authority["review_status"] == (
            "author_reviewed_pending_user_acceptance"
        )


def test_clean_held_out_sources_and_relationship_goldens_are_consistent() -> None:
    package_root = SCENARIOS_ROOT / "clean/package"
    manifest = _load_json(package_root / "package_manifest.json")
    documents = {
        document["document_id"]: document
        for document in manifest["document_inventory"]
    }
    register = _load_csv(package_root / "inputs/drawing_register.csv")
    drawing_metadata = _load_json(
        package_root / "inputs/drawing_metadata.json"
    )["records"]
    equipment = _load_csv(package_root / "inputs/bom_or_equipment_list.csv")
    technical = _load_json(
        package_root / "inputs/datasheet_spec_metadata.json"
    )
    revision_history = _load_csv(package_root / "inputs/revision_history.csv")

    register_by_document = {row["document_id"]: row for row in register}
    metadata_by_document = {
        record["document_id"]: record for record in drawing_metadata
    }
    assert set(register_by_document) == set(metadata_by_document)
    for document_id, register_record in register_by_document.items():
        metadata_record = metadata_by_document[document_id]
        document = documents[document_id]
        for field in ("drawing_number", "revision_id", "file_ref_id", "title"):
            manifest_field = (
                document["current_revision"]["revision_id"]
                if field == "revision_id"
                else document[field]
            )
            assert register_record[field] == metadata_record[field] == manifest_field

    datasheets = {
        record["datasheet_id"]: record for record in technical["datasheets"]
    }
    specifications = {
        record["specification_id"]: record
        for record in technical["specifications"]
    }
    tags_on_drawings = {
        tag for record in drawing_metadata for tag in record["equipment_tags"]
    }
    assert len({row["item_id"] for row in equipment}) == len(equipment)
    assert len({row["equipment_tag"] for row in equipment}) == len(equipment)
    for row in equipment:
        assert row["equipment_tag"] in tags_on_drawings
        assert datasheets[row["datasheet_id"]]["equipment_tag"] == row[
            "equipment_tag"
        ]
        assert int(row["quantity"]) == datasheets[row["datasheet_id"]][
            "package_quantity"
        ]
        assert row["equipment_tag"] in specifications[row["specification_id"]][
            "equipment_tags"
        ]

    history_by_document: dict[str, list[dict[str, str]]] = defaultdict(list)
    for revision in revision_history:
        history_by_document[revision["document_id"]].append(revision)
    assert set(history_by_document) == set(documents)
    for document_id, history in history_by_document.items():
        current = [row for row in history if row["revision_status"] == "current"]
        sequence = sorted(int(row["sequence_index"]) for row in history)
        assert len(current) == 1
        assert sequence == list(range(1, len(sequence) + 1))
        assert current[0]["revision_id"] == documents[document_id][
            "current_revision"
        ]["revision_id"]

    authority = _load_json(package_root / "authority/authority_map.json")
    revision_schemes = {scheme["id"]: scheme for scheme in authority["revision_schemes"]}
    assert revision_schemes["drawing_numeric_zero_padded_v1"]["width"] == 2
    assert revision_schemes["technical_explicit_sequence_v1"][
        "allowed_values"
    ] == ["P0", "P1", "C0"]
    quantity_rule = next(
        rule for rule in authority["rules"] if rule["rule_id"] == "AUTH-BOM-001"
    )
    assert quantity_rule["secondary_sources"] == ["datasheet_spec_metadata"]

    golden = _load_json(FAMILY_ROOT / "protected/golden_relationships.json")
    assert golden["relationship_count"] == len(golden["relationships"]) == 31
    assert [
        _relationship_semantics(relationship)
        for relationship in golden["relationships"]
    ] == manifest["relationship_declarations"]
    for relationship in golden["relationships"]:
        _assert_locator(package_root, relationship["evidence_locator"])


def test_fault_variants_have_only_the_declared_controlled_mutations() -> None:
    clean_root = SCENARIOS_ROOT / "clean/package"
    clean_manifest = _load_json(clean_root / "package_manifest.json")
    clean_paths = {
        path.relative_to(clean_root).as_posix(): path
        for path in clean_root.rglob("*")
        if path.is_file()
    }
    faults_by_scenario: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fault in _fault_matrix()["records"]:
        faults_by_scenario[fault["scenario_id"]].append(fault)

    for scenario in _scenario_catalog()["scenarios"]:
        if scenario["scenario_type"] == "clean":
            continue
        package_root = SCENARIOS_ROOT / scenario["scenario_slug"] / "package"
        variant_paths = {
            path.relative_to(package_root).as_posix(): path
            for path in package_root.rglob("*")
            if path.is_file()
        }
        changed_paths = {
            relative_path
            for relative_path in clean_paths.keys() | variant_paths.keys()
            if relative_path not in clean_paths
            or relative_path not in variant_paths
            or clean_paths[relative_path].read_bytes()
            != variant_paths[relative_path].read_bytes()
        }
        scenario_faults = faults_by_scenario[scenario["scenario_id"]]
        mutation_paths = {fault["source_file"] for fault in scenario_faults}
        assert changed_paths == mutation_paths | {
            "package_manifest.json",
            "expected/expected_findings.json",
            "expected/expected_release_state.json",
        }

        variant_manifest = _load_json(package_root / "package_manifest.json")
        normalized_manifest = deepcopy(variant_manifest)
        normalized_manifest["package_id"] = clean_manifest["package_id"]
        assert normalized_manifest == clean_manifest

        expected_findings = _load_json(
            package_root / "expected/expected_findings.json"
        )
        assert expected_findings["seeded_fault_ids"] == scenario[
            "seeded_fault_ids"
        ]
        for fault in scenario_faults:
            for finding in fault["required_findings"]:
                assert finding in expected_findings["expected_findings"]
                assert finding["check_id"] in fault["required_check_ids"]
                assert finding["result_state"] == fault["expected_finding_state"]
                assert finding["severity"] == fault["expected_severity"]
                assert finding["release_hold"] == fault["expected_release_hold"]
                assert finding["evidence_locators"] == fault[
                    "required_evidence_locators"
                ]
                for locator in finding["evidence_locators"]:
                    _assert_locator(package_root, locator)


def test_held_out_hashes_and_freeze_set_are_reproducible() -> None:
    freeze = _load_json(FAMILY_ROOT / "freeze_record.json")
    family = _load_json(FAMILY_ROOT / "family_metadata.json")
    freeze_entries: list[tuple[str, str]] = []

    assert freeze["scenario_count"] == len(freeze["scenario_records"]) == 8
    for record in freeze["scenario_records"]:
        scenario_root = SCENARIOS_ROOT / record["scenario_slug"]
        package_root = scenario_root / "package"
        inventory_path = scenario_root / "fixture_inventory.json"
        metadata_path = scenario_root / "benchmark_metadata.json"
        inventory = _load_json(inventory_path)
        metadata = _load_json(metadata_path)
        actual_paths = sorted(
            path.relative_to(package_root).as_posix()
            for path in package_root.rglob("*")
            if path.is_file()
        )

        assert inventory["scope"] == "package_tree"
        assert inventory["file_count"] == len(inventory["files"]) == len(actual_paths)
        assert [entry["path"] for entry in inventory["files"]] == actual_paths
        for entry in inventory["files"]:
            path = package_root / entry["path"]
            assert entry["size_bytes"] == path.stat().st_size
            assert entry["sha256"] == _sha256(path)
        content_hash = _tree_hash(package_root, inventory["files"])
        assert inventory["content_hash"] == content_hash
        assert metadata["content_hash"]["value"] == content_hash
        assert record["package_content_hash"] == content_hash
        assert record["benchmark_metadata_sha256"] == _sha256(metadata_path)
        assert record["fixture_inventory_sha256"] == _sha256(inventory_path)

        scenario_id = record["scenario_id"]
        freeze_entries.extend(
            [
                (f"scenario/{scenario_id}/package", content_hash),
                (
                    f"scenario/{scenario_id}/benchmark_metadata.json",
                    record["benchmark_metadata_sha256"],
                ),
                (
                    f"scenario/{scenario_id}/fixture_inventory.json",
                    record["fixture_inventory_sha256"],
                ),
            ]
        )

    for asset in freeze["protected_assets"]:
        path = FAMILY_ROOT / asset["path"]
        assert asset["size_bytes"] == path.stat().st_size
        assert asset["sha256"] == _sha256(path)
        freeze_entries.append((f"control/{asset['path']}", asset["sha256"]))

    canonical = "".join(
        f"{entry_path}\0{digest}\n"
        for entry_path, digest in sorted(freeze_entries)
    ).encode("utf-8")
    freeze_hash = hashlib.sha256(canonical).hexdigest()
    assert freeze["freeze_set_hash"]["value"] == freeze_hash
    assert family["freeze_set_hash"] == freeze_hash
    assert freeze["split_commit"] is None
    assert freeze["first_execution_status"] == "not_executed"
    assert all(not record["producer_visible"] for record in freeze["scenario_records"])


def test_held_out_family_is_materially_distinct_from_development() -> None:
    held_out_root = SCENARIOS_ROOT / "clean/package"
    held_out = _load_json(held_out_root / "package_manifest.json")
    development = _load_json(DEVELOPMENT_ROOT / "package_manifest.json")

    assert held_out["package_id"] != development["package_id"]
    assert _canonical_identifiers(held_out).isdisjoint(
        _canonical_identifiers(development)
    )
    assert len(held_out["document_inventory"]) == 11
    assert len(development["document_inventory"]) == 9
    assert len(held_out["relationship_declarations"]) == 31
    assert len(development["relationship_declarations"]) == 20
    assert {
        reference["path"] for reference in held_out["file_references"]
    }.isdisjoint(
        reference["path"] for reference in development["file_references"]
    )

    held_drawing_schemes = {
        document["current_revision"]["scheme"]
        for document in held_out["document_inventory"]
        if document["document_type"] == "drawing"
    }
    development_drawing_schemes = {
        document["current_revision"]["scheme"]
        for document in development["document_inventory"]
        if document["document_type"] == "drawing"
    }
    assert held_drawing_schemes == {"numeric_zero_padded"}
    assert development_drawing_schemes == {"alpha_upper"}

    assert [
        row["document_id"]
        for row in _load_csv(held_out_root / "inputs/drawing_register.csv")
    ] == ["DOC-AIR-DWG-003", "DOC-AIR-DWG-001", "DOC-AIR-DWG-002"]
    assert [
        record["document_id"]
        for record in _load_json(
            held_out_root / "inputs/drawing_metadata.json"
        )["records"]
    ] == ["DOC-AIR-DWG-002", "DOC-AIR-DWG-003", "DOC-AIR-DWG-001"]
    assert [
        row["equipment_tag"]
        for row in _load_csv(held_out_root / "inputs/bom_or_equipment_list.csv")
    ] == ["DR-230A", "C-210A", "V-220A"]

    held_relationship_types = Counter(
        relationship["relationship_type"]
        for relationship in held_out["relationship_declarations"]
    )
    development_relationship_types = Counter(
        relationship["relationship_type"]
        for relationship in development["relationship_declarations"]
    )
    assert held_relationship_types != development_relationship_types
    assert held_relationship_types["document_to_file"] == 11
    assert development_relationship_types["document_to_file"] == 9

    development_ids = _canonical_identifiers(development)
    for fault in _fault_matrix()["records"]:
        assert development_ids.isdisjoint(fault["affected_canonical_identifiers"])

    material_review = (FAMILY_ROOT / "material_distinction.md").read_text(
        encoding="utf-8"
    )
    access_control = (FAMILY_ROOT / "ACCESS_CONTROL.md").read_text(
        encoding="utf-8"
    )
    assert "This is not a renamed development copy." in material_review
    assert "not independently blind" in access_control
    assert "must not inspect this directory" in access_control
