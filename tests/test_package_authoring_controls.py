from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import pytest

from mech_eval_harness.cli import main
from mech_eval_harness.package_assurance import (
    PACKAGE_RESULT_FILENAME,
    PACKAGE_RESULT_READY_STATUS,
    PROTECTED_REACHABILITY_FILENAME,
    PUBLIC_REACHABILITY_FILENAME,
    RELATIONSHIP_CHECK_ORDER,
    TargetReachabilityError,
    build_package_result,
    run_package_gates,
    run_package_relationships,
    validate_package_contract,
    verify_custodian_target_reachability,
    write_custodian_reachability_reports,
)
from mech_eval_harness.package_assurance.gates import (
    AUTHORITY_GATE_ID,
    IDENTIFIER_GATE_ID,
    MANIFEST_GATE_ID,
    REVISION_GATE_ID,
    SOURCE_INVENTORY_GATE_ID,
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
REVISION_CHECK_ID = RELATIONSHIP_CHECK_ORDER[0]
FIXED_TIME = datetime(2026, 7, 24, tzinfo=timezone.utc)


def _copy_package(tmp_path: Path, name: str) -> Path:
    package_root = tmp_path / name
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    return package_root


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _mutate_json(
    path: Path,
    mutate: Callable[[dict[str, Any]], None],
) -> None:
    document = _load_json(path)
    mutate(document)
    _write_json(path, document)


def _rewrite_register_identifier(package_root: Path, value: str) -> None:
    path = package_root / "inputs" / "drawing_register.csv"
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    assert fieldnames is not None
    rows[0]["document_id"] = value
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _scope_authority_to_family(package_root: Path) -> None:
    _mutate_json(
        package_root / "authority" / "authority_map.json",
        lambda authority: authority.__setitem__("applies_to", "FAMILY-NOT-PACKAGE"),
    )


def _set_relationship_revision_fault(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        current = document["records"][0]["revision_id"]
        document["records"][0]["revision_id"] = "B" if current != "B" else "A"

    _mutate_json(
        package_root / "inputs" / "drawing_metadata.json",
        mutate,
    )


def _package_result_document(package_root: Path, suffix: int) -> dict[str, Any]:
    gates = run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )
    relationships = run_package_relationships(gates)
    result = build_package_result(
        run_id=f"RUN-20260724T000000000000Z-{suffix:08x}",
        started_at=FIXED_TIME,
        completed_at=FIXED_TIME,
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships,
        output_location=f"synthetic-proof/{suffix}",
        output_generation_status=PACKAGE_RESULT_READY_STATUS,
        output_names=(PACKAGE_RESULT_FILENAME,),
    )
    return result.to_dict()


def _write_custody_inputs(
    custody_root: Path,
    *,
    documents: dict[str, dict[str, Any]],
    plan_rows: list[dict[str, Any]],
) -> tuple[Path, Path]:
    scenario_results: list[dict[str, str]] = []
    for token, document in documents.items():
        path = custody_root / "results" / token / PACKAGE_RESULT_FILENAME
        path.parent.mkdir(parents=True)
        _write_json(path, document)
        scenario_results.append(
            {
                "scenario_token": token,
                "package_result_path": path.relative_to(custody_root).as_posix(),
            }
        )

    public_index = {
        "schema_version": "0.3.0",
        "family_id": "FAM-SYNTHETIC-D118",
        "scenario_results": scenario_results,
    }
    protected_plan = {
        "schema_version": "0.3.0",
        "family_id": "FAM-SYNTHETIC-D118",
        "commitment_nonce": "a" * 64,
        "scenarios": plan_rows,
    }
    public_index_path = custody_root / "public_index.json"
    protected_plan_path = custody_root / "protected" / "target_plan.json"
    protected_plan_path.parent.mkdir(parents=True)
    _write_json(public_index_path, public_index)
    _write_json(protected_plan_path, protected_plan)
    return public_index_path, protected_plan_path


def test_public_contract_validator_accepts_clean_development_package(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path, "clean")

    first = validate_package_contract(
        repository_root=ROOT,
        package_root=package_root,
    )
    second = validate_package_contract(
        repository_root=ROOT,
        package_root=package_root,
    )

    assert first.public_contract_complete is True
    assert first.failed_gate_ids == ()
    assert first.to_dict() == second.to_dict()
    assert first.to_dict()["relationships_executed"] is False
    serialized = json.dumps(first.to_dict(), sort_keys=True)
    assert str(package_root) not in serialized


def test_public_contract_validator_rejects_exact_d117_scope_defect(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path, "scope-defect")
    _scope_authority_to_family(package_root)

    validation = validate_package_contract(
        repository_root=ROOT,
        package_root=package_root,
    )

    assert validation.public_contract_complete is False
    assert validation.failed_gate_ids == (AUTHORITY_GATE_ID,)
    authority = next(
        gate for gate in validation.gates if gate.gate_id == AUTHORITY_GATE_ID
    )
    assert authority.finding_codes == ("AUTHORITY_SCOPE_CONFLICT",)


@pytest.mark.parametrize(
    ("mutate", "expected_gate", "expected_code"),
    [
        (
            lambda package: _mutate_json(
                package / "authority" / "authority_map.json",
                lambda authority: authority["rules"][0].__setitem__(
                    "authoritative_source",
                    "unknown_source",
                ),
            ),
            AUTHORITY_GATE_ID,
            "AUTHORITY_SOURCE_UNKNOWN",
        ),
        (
            lambda package: (
                package / "inputs" / "drawing_register.csv"
            ).unlink(),
            SOURCE_INVENTORY_GATE_ID,
            "SOURCE_FILE_MISSING",
        ),
        (
            lambda package: _mutate_json(
                package / "package_manifest.json",
                lambda manifest: manifest["relationship_declarations"][0][
                    "target"
                ].__setitem__("identifier", "UNDECLARED-FILE-REFERENCE"),
            ),
            MANIFEST_GATE_ID,
            "MANIFEST_INVALID",
        ),
        (
            lambda package: _rewrite_register_identifier(package, " bad identifier "),
            IDENTIFIER_GATE_ID,
            "CANONICAL_IDENTIFIER_INVALID",
        ),
        (
            lambda package: _mutate_json(
                package / "inputs" / "drawing_metadata.json",
                lambda document: document["records"][0].__setitem__(
                    "revision_id",
                    "a",
                ),
            ),
            REVISION_GATE_ID,
            "REVISION_FORMAT_INVALID",
        ),
    ],
)
def test_public_contract_validator_exposes_each_authoring_invariant_class(
    tmp_path: Path,
    mutate: Callable[[Path], None],
    expected_gate: str,
    expected_code: str,
) -> None:
    package_root = _copy_package(tmp_path, "invalid")
    mutate(package_root)

    validation = validate_package_contract(
        repository_root=ROOT,
        package_root=package_root,
    )

    gate = next(item for item in validation.gates if item.gate_id == expected_gate)
    assert gate.status == "failed"
    assert expected_code in gate.finding_codes


def test_public_contract_cli_returns_machine_readable_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path, "scope-defect")
    _scope_authority_to_family(package_root)

    exit_code = main(
        [
            "validate-package-contract",
            str(ROOT),
            str(package_root),
        ]
    )

    captured = capsys.readouterr()
    document = json.loads(captured.out)
    assert exit_code == 1
    assert captured.err == ""
    assert document["status"] == "failed"
    assert document["failed_gate_ids"] == [AUTHORITY_GATE_ID]
    assert document["relationships_executed"] is False


def test_custodian_reachability_passes_clean_and_relationship_target(
    tmp_path: Path,
) -> None:
    clean = _copy_package(tmp_path, "clean")
    relationship_fault = _copy_package(tmp_path, "relationship-fault")
    _set_relationship_revision_fault(relationship_fault)
    custody_root = tmp_path / "custody"
    custody_root.mkdir()
    public_index, protected_plan = _write_custody_inputs(
        custody_root,
        documents={
            "S01": _package_result_document(clean, 1),
            "S02": _package_result_document(relationship_fault, 2),
        },
        plan_rows=[
            {
                "scenario_token": "S01",
                "scenario_role": "clean",
                "targets": [],
            },
            {
                "scenario_token": "S02",
                "scenario_role": "fault",
                "targets": [
                    {
                        "kind": "relationship_check",
                        "control_id": REVISION_CHECK_ID,
                    }
                ],
            },
        ],
    )

    outcome = verify_custodian_target_reachability(
        repository_root=ROOT,
        custody_root=custody_root,
        public_index_path=public_index,
        protected_plan_path=protected_plan,
    )

    assert outcome.passed is True
    assert outcome.public_attestation["reachable_target_count"] == 1
    assert outcome.public_attestation["unplanned_blocker_count"] == 0
    public_text = json.dumps(outcome.public_attestation, sort_keys=True)
    assert "S01" not in public_text
    assert "S02" not in public_text
    assert REVISION_CHECK_ID not in public_text
    assert "scenario_token" not in public_text
    assert "a" * 64 not in public_text
    assert outcome.public_attestation["protected_values_published"] is False

    public_path, protected_path = write_custodian_reachability_reports(
        outcome=outcome,
        output_directory=custody_root / "verification",
    )
    assert public_path.name == PUBLIC_REACHABILITY_FILENAME
    assert protected_path.name == PROTECTED_REACHABILITY_FILENAME
    assert hashlib.sha256(protected_path.read_bytes()).hexdigest() == (
        outcome.public_attestation["protected_detail_sha256"]
    )
    with pytest.raises(TargetReachabilityError, match="will not be overwritten"):
        write_custodian_reachability_reports(
            outcome=outcome,
            output_directory=custody_root / "verification",
        )


def test_custodian_reachability_rejects_unplanned_authority_blocker(
    tmp_path: Path,
) -> None:
    clean = _copy_package(tmp_path, "clean")
    scope_defect = _copy_package(tmp_path, "scope-defect")
    _scope_authority_to_family(scope_defect)
    custody_root = tmp_path / "custody"
    custody_root.mkdir()
    public_index, protected_plan = _write_custody_inputs(
        custody_root,
        documents={
            "S01": _package_result_document(clean, 3),
            "S02": _package_result_document(scope_defect, 4),
        },
        plan_rows=[
            {
                "scenario_token": "S01",
                "scenario_role": "clean",
                "targets": [],
            },
            {
                "scenario_token": "S02",
                "scenario_role": "fault",
                "targets": [
                    {
                        "kind": "relationship_check",
                        "control_id": REVISION_CHECK_ID,
                    }
                ],
            },
        ],
    )

    outcome = verify_custodian_target_reachability(
        repository_root=ROOT,
        custody_root=custody_root,
        public_index_path=public_index,
        protected_plan_path=protected_plan,
    )

    assert outcome.passed is False
    assert outcome.public_attestation["reachable_target_count"] == 0
    assert outcome.public_attestation["unplanned_blocker_count"] == 1
    fault = next(
        row
        for row in outcome.protected_detail["scenarios"]
        if row["scenario_role"] == "fault"
    )
    assert fault["targets"][0]["reachable"] is False
    assert fault["targets"][0]["unplanned_blockers"] == [AUTHORITY_GATE_ID]


def test_custodian_reachability_allows_an_intended_gate_target(
    tmp_path: Path,
) -> None:
    clean = _copy_package(tmp_path, "clean")
    authority_fault = _copy_package(tmp_path, "authority-fault")
    _scope_authority_to_family(authority_fault)
    custody_root = tmp_path / "custody"
    custody_root.mkdir()
    public_index, protected_plan = _write_custody_inputs(
        custody_root,
        documents={
            "S01": _package_result_document(clean, 5),
            "S02": _package_result_document(authority_fault, 6),
        },
        plan_rows=[
            {
                "scenario_token": "S01",
                "scenario_role": "clean",
                "targets": [],
            },
            {
                "scenario_token": "S02",
                "scenario_role": "fault",
                "targets": [
                    {
                        "kind": "gate",
                        "control_id": AUTHORITY_GATE_ID,
                    }
                ],
            },
        ],
    )

    outcome = verify_custodian_target_reachability(
        repository_root=ROOT,
        custody_root=custody_root,
        public_index_path=public_index,
        protected_plan_path=protected_plan,
    )

    assert outcome.passed is True
    target = outcome.protected_detail["scenarios"][1]["targets"][0]
    assert target["status"] == "failed"
    assert target["reachable"] is True
    assert target["unplanned_blockers"] == []


def test_custodian_reachability_rejects_path_escape(tmp_path: Path) -> None:
    clean = _copy_package(tmp_path, "clean")
    fault = _copy_package(tmp_path, "fault")
    _set_relationship_revision_fault(fault)
    custody_root = tmp_path / "custody"
    custody_root.mkdir()
    public_index, protected_plan = _write_custody_inputs(
        custody_root,
        documents={
            "S01": _package_result_document(clean, 7),
            "S02": _package_result_document(fault, 8),
        },
        plan_rows=[
            {
                "scenario_token": "S01",
                "scenario_role": "clean",
                "targets": [],
            },
            {
                "scenario_token": "S02",
                "scenario_role": "fault",
                "targets": [
                    {
                        "kind": "relationship_check",
                        "control_id": REVISION_CHECK_ID,
                    }
                ],
            },
        ],
    )
    index_document = _load_json(public_index)
    index_document["scenario_results"][0]["package_result_path"] = "../escape.json"
    _write_json(public_index, index_document)

    with pytest.raises(TargetReachabilityError, match="POSIX-relative"):
        verify_custodian_target_reachability(
            repository_root=ROOT,
            custody_root=custody_root,
            public_index_path=public_index,
            protected_plan_path=protected_plan,
        )


def test_custodian_reachability_requires_protected_commitment_nonce(
    tmp_path: Path,
) -> None:
    clean = _copy_package(tmp_path, "clean")
    fault = _copy_package(tmp_path, "fault")
    _set_relationship_revision_fault(fault)
    custody_root = tmp_path / "custody"
    custody_root.mkdir()
    public_index, protected_plan = _write_custody_inputs(
        custody_root,
        documents={
            "S01": _package_result_document(clean, 11),
            "S02": _package_result_document(fault, 12),
        },
        plan_rows=[
            {
                "scenario_token": "S01",
                "scenario_role": "clean",
                "targets": [],
            },
            {
                "scenario_token": "S02",
                "scenario_role": "fault",
                "targets": [
                    {
                        "kind": "relationship_check",
                        "control_id": REVISION_CHECK_ID,
                    }
                ],
            },
        ],
    )
    plan = _load_json(protected_plan)
    plan["commitment_nonce"] = "predictable"
    _write_json(protected_plan, plan)

    with pytest.raises(TargetReachabilityError, match="64 lowercase hexadecimal"):
        verify_custodian_target_reachability(
            repository_root=ROOT,
            custody_root=custody_root,
            public_index_path=public_index,
            protected_plan_path=protected_plan,
        )


def test_custodian_reachability_cli_writes_redacted_and_protected_outputs(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    clean = _copy_package(tmp_path, "clean")
    fault = _copy_package(tmp_path, "fault")
    _set_relationship_revision_fault(fault)
    custody_root = tmp_path / "custody"
    custody_root.mkdir()
    public_index, protected_plan = _write_custody_inputs(
        custody_root,
        documents={
            "S01": _package_result_document(clean, 9),
            "S02": _package_result_document(fault, 10),
        },
        plan_rows=[
            {
                "scenario_token": "S01",
                "scenario_role": "clean",
                "targets": [],
            },
            {
                "scenario_token": "S02",
                "scenario_role": "fault",
                "targets": [
                    {
                        "kind": "relationship_check",
                        "control_id": REVISION_CHECK_ID,
                    }
                ],
            },
        ],
    )
    output_directory = custody_root / "verification"

    exit_code = main(
        [
            "verify-target-reachability",
            str(ROOT),
            str(custody_root),
            str(public_index),
            str(protected_plan),
            str(output_directory),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "TARGET REACHABILITY: PASSED" in captured.out
    public_document = _load_json(output_directory / PUBLIC_REACHABILITY_FILENAME)
    protected_document = _load_json(
        output_directory / PROTECTED_REACHABILITY_FILENAME
    )
    assert public_document["protected_values_published"] is False
    assert "scenarios" not in public_document
    assert protected_document["scenarios"][1]["targets"][0]["control_id"] == (
        REVISION_CHECK_ID
    )
