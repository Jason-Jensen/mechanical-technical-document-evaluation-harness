from __future__ import annotations

import json
import shutil
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mech_eval_harness.package_assurance import (
    PackageResultCollisionError,
    PackageResultPersistenceError,
    PackageResultSchemaValidationError,
    build_package_result,
    run_package_gates,
    run_package_relationships,
    validate_package_result_document,
    write_package_result,
)
from mech_eval_harness.package_assurance.models import PackageRelationshipEvaluation


ROOT = Path(__file__).resolve().parents[1]
RESULT_SCHEMA = ROOT / "schemas" / "package_result.schema.json"
DEVELOPMENT_PACKAGE = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "development"
    / "pump_skid_clean_v1"
    / "package"
)
STARTED_AT = datetime(2026, 7, 19, 18, 0, 0, tzinfo=timezone.utc)
RUN_ID = "RUN-20260719T180000000000Z-deadbeef"


def _build_result(tmp_path: Path, *, run_id: str = RUN_ID):
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    gates = run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )
    relationships = run_package_relationships(gates)
    return build_package_result(
        run_id=run_id,
        started_at=STARTED_AT,
        completed_at=STARTED_AT + timedelta(milliseconds=25),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships,
    )


def test_package_result_is_schema_valid_and_written_immutably(
    tmp_path: Path,
) -> None:
    result = _build_result(tmp_path)

    result_path = write_package_result(
        result=result,
        runs_dir=tmp_path / "runs",
        schema_path=RESULT_SCHEMA,
    )

    assert result_path == tmp_path / "runs" / RUN_ID / "package_result.json"
    raw = result_path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    document = json.loads(raw.decode("utf-8"))
    validate_package_result_document(document, RESULT_SCHEMA)
    assert document["package_state"] == "automatic_pass"
    assert document["release_hold"] is False


def test_existing_package_run_is_never_overwritten(tmp_path: Path) -> None:
    result = _build_result(tmp_path)
    runs_dir = tmp_path / "runs"
    result_path = write_package_result(
        result=result,
        runs_dir=runs_dir,
        schema_path=RESULT_SCHEMA,
    )
    original_bytes = result_path.read_bytes()

    with pytest.raises(PackageResultCollisionError, match="not be overwritten"):
        write_package_result(
            result=result,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )
    assert result_path.read_bytes() == original_bytes


def test_unsafe_package_run_id_is_rejected_before_writing(tmp_path: Path) -> None:
    result = replace(_build_result(tmp_path), run_id="../escape")
    runs_dir = tmp_path / "runs"

    with pytest.raises(PackageResultPersistenceError, match="run_id must use"):
        write_package_result(
            result=result,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )
    assert not runs_dir.exists()
    assert not (tmp_path / "escape").exists()


def test_schema_invalid_package_result_is_rejected_before_writing(
    tmp_path: Path,
) -> None:
    result = _build_result(tmp_path)
    invalid = replace(result, versions={**result.versions, "router": "wrong"})
    runs_dir = tmp_path / "runs"

    with pytest.raises(
        PackageResultSchemaValidationError,
        match="failed schema validation",
    ):
        write_package_result(
            result=invalid,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )
    assert not runs_dir.exists()


def test_controlled_manifest_failure_remains_a_schema_valid_result(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")
    gates = run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )
    relationships = run_package_relationships(gates)
    result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=STARTED_AT + timedelta(milliseconds=25),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships,
    )

    validate_package_result_document(result.to_dict(), RESULT_SCHEMA)
    assert result.package_state == "extraction_or_tool_failure"
    assert result.package_id is None


def test_incomplete_evaluator_result_can_be_preserved(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    gates = run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )
    relationships = run_package_relationships(gates)
    incomplete = PackageRelationshipEvaluation(
        package_id=relationships.package_id,
        checks=relationships.checks[:-1],
    )
    result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=STARTED_AT + timedelta(milliseconds=25),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=incomplete,
    )

    result_path = write_package_result(
        result=result,
        runs_dir=tmp_path / "runs",
        schema_path=RESULT_SCHEMA,
    )

    assert result_path.is_file()
    assert result.package_state == "evaluator_uncertainty"
    assert result.completeness.status == "incomplete"
