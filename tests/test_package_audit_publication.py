from __future__ import annotations

import json
import shutil
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import mech_eval_harness.package_assurance.publication as publication_module
from mech_eval_harness.package_assurance import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
    AUDIT_PACKAGE_READY_STATUS,
    PUBLICATION_FAILURE_FILENAME,
    PackageAuditCollisionError,
    PackageAuditPublicationError,
    build_package_result,
    publish_package_audit,
    run_package_gates,
    run_package_relationships,
)


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
RUN_ID = "RUN-20260719T230000000000Z-deadbeef"
STARTED_AT = datetime(2026, 7, 19, 23, 0, 0, tzinfo=timezone.utc)


def _build_audit_result(tmp_path: Path):
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
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
        output_location=f"runs/{RUN_ID}",
        output_generation_status=AUDIT_PACKAGE_READY_STATUS,
        output_names=AUDIT_PACKAGE_OUTPUT_FILENAMES,
    )
    return package_root, result


def _failed_publications(runs_dir: Path) -> list[Path]:
    return [
        path
        for path in runs_dir.iterdir()
        if path.name.startswith(f".{RUN_ID}.publication-failed-")
    ]


def test_complete_audit_outputs_publish_together(tmp_path: Path) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"

    published = publish_package_audit(
        result=result,
        package_root=package_root,
        runs_dir=runs_dir,
        schema_path=RESULT_SCHEMA,
    )

    assert published.run_directory == runs_dir / RUN_ID
    assert {
        path.name for path in published.run_directory.iterdir()
    } == set(AUDIT_PACKAGE_OUTPUT_FILENAMES)
    document = json.loads(published.result_path.read_text(encoding="utf-8"))
    assert document["output_generation"] == {
        "status": AUDIT_PACKAGE_READY_STATUS,
        "output_names": list(AUDIT_PACKAGE_OUTPUT_FILENAMES),
    }
    assert published.issue_register_csv_path.read_text(encoding="utf-8").count(
        "\n"
    ) == 1
    readiness = published.release_readiness_path.read_text(encoding="utf-8")
    for filename in AUDIT_PACKAGE_OUTPUT_FILENAMES:
        assert f"[{filename}]({filename})" in readiness


def test_existing_complete_run_is_never_overwritten(tmp_path: Path) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"
    published = publish_package_audit(
        result=result,
        package_root=package_root,
        runs_dir=runs_dir,
        schema_path=RESULT_SCHEMA,
    )
    original = {
        path.name: path.read_bytes()
        for path in published.run_directory.iterdir()
    }

    with pytest.raises(PackageAuditCollisionError, match="not be overwritten"):
        publish_package_audit(
            result=result,
            package_root=package_root,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert {
        path.name: path.read_bytes()
        for path in published.run_directory.iterdir()
    } == original


def test_partial_publication_is_preserved_as_incomplete_evidence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"

    def fail_readiness(**_kwargs) -> str:
        raise RuntimeError("synthetic readiness failure")

    monkeypatch.setattr(
        publication_module,
        "render_release_readiness_summary",
        fail_readiness,
    )

    with pytest.raises(PackageAuditPublicationError, match="Could not publish"):
        publish_package_audit(
            result=result,
            package_root=package_root,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert not (runs_dir / RUN_ID).exists()
    failed = _failed_publications(runs_dir)
    assert len(failed) == 1
    assert (failed[0] / "package_result.json").is_file()
    assert (failed[0] / PUBLICATION_FAILURE_FILENAME).read_text(
        encoding="utf-8"
    ) == "complete=false\nphase=publication\nerror_type=RuntimeError\n"


def test_transient_final_rename_permission_error_is_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"
    actual_replace = publication_module._replace_directory
    attempts: list[tuple[Path, Path]] = []
    delays: list[float] = []

    def fail_twice_then_replace(source: Path, target: Path) -> None:
        attempts.append((source, target))
        if len(attempts) <= 2:
            raise PermissionError("synthetic transient sharing violation")
        actual_replace(source, target)

    monkeypatch.setattr(
        publication_module,
        "_replace_directory",
        fail_twice_then_replace,
    )
    monkeypatch.setattr(publication_module.time, "sleep", delays.append)

    published = publish_package_audit(
        result=result,
        package_root=package_root,
        runs_dir=runs_dir,
        schema_path=RESULT_SCHEMA,
    )

    assert published.run_directory == runs_dir / RUN_ID
    assert len(attempts) == 3
    assert delays == list(
        publication_module.FINAL_RENAME_RETRY_DELAYS_SECONDS[:2]
    )
    assert _failed_publications(runs_dir) == []


def test_final_rename_permission_retry_exhaustion_preserves_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"
    attempts: list[tuple[Path, Path]] = []
    delays: list[float] = []

    def always_fail(source: Path, target: Path) -> None:
        attempts.append((source, target))
        raise PermissionError("synthetic persistent sharing violation")

    monkeypatch.setattr(publication_module, "_replace_directory", always_fail)
    monkeypatch.setattr(publication_module.time, "sleep", delays.append)

    with pytest.raises(PackageAuditPublicationError, match="Could not publish"):
        publish_package_audit(
            result=result,
            package_root=package_root,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert len(attempts) == (
        len(publication_module.FINAL_RENAME_RETRY_DELAYS_SECONDS) + 1
    )
    assert delays == list(publication_module.FINAL_RENAME_RETRY_DELAYS_SECONDS)
    assert not (runs_dir / RUN_ID).exists()
    failed = _failed_publications(runs_dir)
    assert len(failed) == 1
    assert (failed[0] / PUBLICATION_FAILURE_FILENAME).read_text(
        encoding="utf-8"
    ) == "complete=false\nphase=publication\nerror_type=PermissionError\n"


def test_final_rename_collision_is_never_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"
    attempts: list[tuple[Path, Path]] = []
    delays: list[float] = []

    def create_collision(source: Path, target: Path) -> None:
        attempts.append((source, target))
        target.mkdir()
        raise PermissionError("synthetic collision during rename")

    monkeypatch.setattr(
        publication_module,
        "_replace_directory",
        create_collision,
    )
    monkeypatch.setattr(publication_module.time, "sleep", delays.append)

    with pytest.raises(PackageAuditCollisionError, match="not be overwritten"):
        publish_package_audit(
            result=result,
            package_root=package_root,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert len(attempts) == 1
    assert delays == []
    assert (runs_dir / RUN_ID).is_dir()
    assert list((runs_dir / RUN_ID).iterdir()) == []
    failed = _failed_publications(runs_dir)
    assert len(failed) == 1
    assert (failed[0] / PUBLICATION_FAILURE_FILENAME).read_text(
        encoding="utf-8"
    ) == (
        "complete=false\n"
        "phase=publication\n"
        "error_type=PackageAuditCollisionError\n"
    )


def test_non_permission_final_rename_error_is_never_retried(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    package_root, result = _build_audit_result(tmp_path)
    runs_dir = tmp_path / "runs"
    attempts: list[tuple[Path, Path]] = []
    delays: list[float] = []

    def fail_once(source: Path, target: Path) -> None:
        attempts.append((source, target))
        raise OSError("synthetic non-permission failure")

    monkeypatch.setattr(publication_module, "_replace_directory", fail_once)
    monkeypatch.setattr(publication_module.time, "sleep", delays.append)

    with pytest.raises(PackageAuditPublicationError, match="Could not publish"):
        publish_package_audit(
            result=result,
            package_root=package_root,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert len(attempts) == 1
    assert delays == []
    assert not (runs_dir / RUN_ID).exists()
    failed = _failed_publications(runs_dir)
    assert len(failed) == 1
    assert (failed[0] / PUBLICATION_FAILURE_FILENAME).read_text(
        encoding="utf-8"
    ) == "complete=false\nphase=publication\nerror_type=OSError\n"


def test_publication_rejects_incomplete_output_declaration(
    tmp_path: Path,
) -> None:
    package_root, result = _build_audit_result(tmp_path)
    incomplete = replace(
        result,
        output_generation={
            "status": "package_result_ready",
            "output_names": ["package_result.json"],
        },
    )

    with pytest.raises(
        PackageAuditPublicationError,
        match="complete audit output set",
    ):
        publish_package_audit(
            result=incomplete,
            package_root=package_root,
            runs_dir=tmp_path / "runs",
            schema_path=RESULT_SCHEMA,
        )
    assert not (tmp_path / "runs").exists()
