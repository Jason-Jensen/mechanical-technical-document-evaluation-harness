from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path
from typing import Callable

import pytest

from mech_eval_harness.cli import main
from mech_eval_harness.package_assurance import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
    PACKAGE_STATE_EXIT_CODES,
    package_state_exit_code,
)
from mech_eval_harness.package_assurance.gates import IDENTIFIER_GATE_ID


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


def _only_run_directory(runs_dir: Path) -> Path:
    run_directories = [
        path
        for path in runs_dir.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ]
    assert len(run_directories) == 1
    return run_directories[0]


def _run_cli(package_root: Path, runs_dir: Path) -> int:
    return main(
        [
            "audit-package",
            str(ROOT),
            str(package_root),
            "--runs-dir",
            str(runs_dir),
        ]
    )


def _rewrite_bom(
    package_root: Path,
    mutate: Callable[[list[dict[str, str]]], None],
) -> None:
    source_path = package_root / "inputs" / "bom_or_equipment_list.csv"
    with source_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    assert fieldnames is not None
    mutate(rows)
    with source_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def test_clean_package_cli_publishes_complete_non_approving_audit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    assert exit_code == 0
    assert captured.err == ""
    assert "PACKAGE STATE: automatic_pass" in captured.out
    assert "RELEASE HOLD: false" in captured.out
    assert "ISSUE COUNT: 0" in captured.out
    assert "RESULT PATH:" in captured.out
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )

    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    assert document["package_state"] == "automatic_pass"
    assert document["release_hold"] is False
    assert document["output_generation"]["output_names"] == list(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    issue_rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )
    assert issue_rows == []
    readiness = (run_directory / "release_readiness.md").read_text(
        encoding="utf-8"
    )
    assert "qualified human must decide" in readiness
    assert "does not approve release" in readiness


def test_blank_optional_bom_references_publish_missing_authority_result(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)

    def blank_optional_references(rows: list[dict[str, str]]) -> None:
        for row in rows:
            row["drawing_number"] = ""
            row["datasheet_id"] = ""
            row["specification_id"] = ""

    _rewrite_bom(package_root, blank_optional_references)
    authority_path = package_root / "authority" / "authority_map.json"
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    authority["rules"] = [
        rule
        for rule in authority["rules"]
        if rule["field"] != "equipment.datasheet_id"
    ]
    authority_path.write_text(
        json.dumps(authority, indent=2) + "\n",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    assert exit_code == 3
    assert captured.err == ""
    assert "PACKAGE STATE: missing_authoritative_information" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    assert document["package_state"] == "missing_authoritative_information"
    assert document["release_hold"] is True
    identifier_gate = next(
        gate
        for gate in document["gate_results"]
        if gate["gate_id"] == IDENTIFIER_GATE_ID
    )
    assert identifier_gate["status"] == "passed"
    assert [finding["code"] for finding in document["findings"]] == [
        "AUTHORITY_REQUIRED_RULE_MISSING"
    ]


def test_malformed_optional_bom_identifier_publishes_schema_valid_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    _rewrite_bom(
        package_root,
        lambda rows: rows[0].__setitem__("datasheet_id", " DS-P-101 "),
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    assert exit_code == 1
    assert captured.err == ""
    assert "PACKAGE STATE: automatic_fail" in captured.out
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    finding = document["findings"][0]
    assert finding["code"] == "CANONICAL_IDENTIFIER_INVALID"
    assert finding["affected_identifiers"] == ["ITEM-PUMP-001"]
    assert finding["evidence"][0]["original_value"] == " DS-P-101 "
    assert finding["evidence"][0]["normalized_value"] == "DS-P-101"


def test_removed_required_mapping_cli_preserves_exact_fault(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    manifest_path = package_root / "package_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["relationship_declarations"] = [
        relationship
        for relationship in manifest["relationship_declarations"]
        if relationship["relationship_id"] != "REL-DOC-FILE-001"
    ]
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )
    assert exit_code == 1
    assert "PACKAGE STATE: automatic_fail" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert document["package_state"] == "automatic_fail"
    assert document["release_hold"] is True
    assert [item["status"] for item in document["relationship_results"]] == [
        "passed",
        "passed",
        "passed",
        "passed",
        "failed",
        "passed",
        "passed",
        "passed",
        "passed",
    ]
    assert len(rows) == 1
    assert rows[0]["code"] == "DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED"
    for report_name in (
        "issue_register.csv",
        "issue_register.md",
        "release_readiness.md",
    ):
        report = (run_directory / report_name).read_text(encoding="utf-8")
        assert str(package_root) not in report


def test_wrong_valid_bom_mapping_cli_preserves_exact_fault(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    manifest_path = package_root / "package_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    relationship = next(
        item
        for item in manifest["relationship_declarations"]
        if item["relationship_id"] == "REL-ITEM-EQ-001"
    )
    relationship["target"]["identifier"] = "M-101A"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )

    assert exit_code == 1
    assert "PACKAGE STATE: automatic_fail" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert document["package_state"] == "automatic_fail"
    assert document["release_hold"] is True
    assert [item["status"] for item in document["relationship_results"]] == [
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "failed",
        "passed",
        "passed",
        "passed",
    ]
    assert len(rows) == 1
    assert rows[0]["code"] == "BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED"
    assert json.loads(rows[0]["affected_identifiers_json"]) == [
        "ITEM-PUMP-001"
    ]
    assert (
        json.loads(rows[0]["expected_value_json"])["equipment_tag"]
        == "P-101A"
    )
    assert (
        json.loads(rows[0]["actual_value_json"])["equipment_tag"]
        == "M-101A"
    )
    readiness = (run_directory / "release_readiness.md").read_text(
        encoding="utf-8"
    )
    assert "| Relationship checks | 8 | 1 | 0 |" in readiness
    for output_name in AUDIT_PACKAGE_OUTPUT_FILENAMES:
        output = (run_directory / output_name).read_text(encoding="utf-8")
        assert str(package_root) not in output


def test_missing_bom_equipment_drawing_reference_reaches_all_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["records"][0]["equipment_tags"] = ["P-101A"]
    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )

    assert exit_code == 1
    assert "PACKAGE STATE: automatic_fail" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert document["package_state"] == "automatic_fail"
    assert document["release_hold"] is True
    assert [item["status"] for item in document["relationship_results"]] == [
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "failed",
        "passed",
        "passed",
    ]
    assert len(rows) == 1
    assert rows[0]["code"] == "BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING"
    assert json.loads(rows[0]["affected_identifiers_json"]) == [
        "ITEM-MOTOR-001",
        "M-101A",
    ]
    assert json.loads(rows[0]["evidence_json"])[1]["json_pointer"] == "/records"
    readiness = (run_directory / "release_readiness.md").read_text(
        encoding="utf-8"
    )
    assert "| Relationship checks | 8 | 1 | 0 |" in readiness
    for output_name in AUDIT_PACKAGE_OUTPUT_FILENAMES:
        output = (run_directory / output_name).read_text(encoding="utf-8")
        assert str(package_root) not in output


def test_missing_equipment_datasheet_authority_reaches_all_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "datasheet_spec_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["datasheets"] = [
        record
        for record in metadata["datasheets"]
        if record["record_id"] != "DSMETA-001"
    ]
    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )

    assert exit_code == 3
    assert "PACKAGE STATE: missing_authoritative_information" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    assert document["package_state"] == "missing_authoritative_information"
    assert document["release_hold"] is True
    assert [item["status"] for item in document["relationship_results"]] == [
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "failed",
        "passed",
    ]
    assert len(rows) == 1
    assert rows[0]["code"] == "EQUIPMENT_DATASHEET_AUTHORITY_MISSING"
    assert json.loads(rows[0]["affected_identifiers_json"]) == [
        "ITEM-PUMP-001",
        "P-101A",
    ]
    assert json.loads(rows[0]["expected_value_json"]) == (
        "one authoritative datasheet"
    )
    assert json.loads(rows[0]["actual_value_json"]) == 0
    assert json.loads(rows[0]["evidence_json"])[1]["json_pointer"] == (
        "/datasheets"
    )
    readiness = (run_directory / "release_readiness.md").read_text(
        encoding="utf-8"
    )
    assert "| Relationship checks | 8 | 1 | 0 |" in readiness
    for output_name in AUDIT_PACKAGE_OUTPUT_FILENAMES:
        output = (run_directory / output_name).read_text(encoding="utf-8")
        assert str(package_root) not in output


def test_wrong_valid_equipment_datasheet_association_reaches_all_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)

    def use_wrong_valid_datasheet(rows: list[dict[str, str]]) -> None:
        pump = next(row for row in rows if row["item_id"] == "ITEM-PUMP-001")
        pump["datasheet_id"] = "DS-M-101"

    _rewrite_bom(package_root, use_wrong_valid_datasheet)
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )

    assert exit_code == 1
    assert "PACKAGE STATE: automatic_fail" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    assert document["package_state"] == "automatic_fail"
    assert document["release_hold"] is True
    assert [item["status"] for item in document["relationship_results"]] == [
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "passed",
        "failed",
    ]
    assert len(rows) == 1
    assert rows[0]["code"] == "EQUIPMENT_DATASHEET_MISMATCH"
    assert json.loads(rows[0]["affected_identifiers_json"]) == [
        "ITEM-PUMP-001",
        "P-101A",
    ]
    assert json.loads(rows[0]["expected_value_json"]) == "DS-P-101"
    assert json.loads(rows[0]["actual_value_json"]) == "DS-M-101"
    evidence = json.loads(rows[0]["evidence_json"])
    assert [item["source_type"] for item in evidence] == [
        "datasheet_spec_metadata",
        "bom_or_equipment_list",
    ]
    readiness = (run_directory / "release_readiness.md").read_text(
        encoding="utf-8"
    )
    assert "| Relationship checks | 8 | 1 | 0 |" in readiness
    for output_name in AUDIT_PACKAGE_OUTPUT_FILENAMES:
        output = (run_directory / output_name).read_text(encoding="utf-8")
        assert str(package_root) not in output


def test_malformed_manifest_cli_persists_controlled_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    assert exit_code == 4
    assert "PACKAGE ID: not established" in captured.out
    assert "PACKAGE STATE: extraction_or_tool_failure" in captured.out
    assert document["package_id"] is None
    assert document["package_state"] == "extraction_or_tool_failure"
    assert document["input_fingerprint"]["status"] == "partial"
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )


def test_unchanged_repeated_runs_preserve_substantive_outputs(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    runs_dir = tmp_path / "runs"

    assert _run_cli(package_root, runs_dir) == 0
    assert _run_cli(package_root, runs_dir) == 0

    run_directories = sorted(
        path for path in runs_dir.iterdir() if not path.name.startswith(".")
    )
    assert len(run_directories) == 2
    documents = [
        json.loads(
            (run_directory / "package_result.json").read_text(encoding="utf-8")
        )
        for run_directory in run_directories
    ]
    for document in documents:
        document.pop("run_id")
        document.pop("run_metadata")
    assert documents[0] == documents[1]
    assert (run_directories[0] / "issue_register.csv").read_bytes() == (
        run_directories[1] / "issue_register.csv"
    ).read_bytes()


@pytest.mark.parametrize(
    "argv",
    [
        ["audit-package"],
        ["audit-package", "missing-repository", "missing-package"],
    ],
)
def test_audit_package_usage_errors_return_64_without_result(
    argv: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(argv) == 64
    assert not (tmp_path / "runs").exists()


def test_output_inside_package_is_a_usage_error(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)

    exit_code = main(
        [
            "audit-package",
            str(ROOT),
            str(package_root),
            "--runs-dir",
            str(package_root / "generated"),
        ]
    )

    assert exit_code == 64
    assert not (package_root / "generated").exists()


def test_pre_result_internal_failure_returns_70_without_result(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    incomplete_repository = tmp_path / "incomplete-repository"
    incomplete_repository.mkdir()
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "audit-package",
            str(incomplete_repository),
            str(package_root),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    assert exit_code == 70
    assert not runs_dir.exists()


def test_every_package_state_has_the_accepted_stable_exit() -> None:
    assert PACKAGE_STATE_EXIT_CODES == {
        "automatic_pass": 0,
        "automatic_fail": 1,
        "engineering_review_required": 2,
        "missing_authoritative_information": 3,
        "extraction_or_tool_failure": 4,
        "evaluator_uncertainty": 5,
    }
    for state, expected_exit in PACKAGE_STATE_EXIT_CODES.items():
        assert package_state_exit_code(state) == expected_exit
