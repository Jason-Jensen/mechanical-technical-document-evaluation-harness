from __future__ import annotations

import json
import shutil
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mech_eval_harness.package_assurance import (
    ENGINEERING_REVIEW_LIMITATION,
    RELEASE_READINESS_MARKDOWN_FILENAME,
    ReleaseReadinessRenderError,
    build_package_result,
    render_release_readiness_summary,
    run_package_gates,
    run_package_relationships,
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
STARTED_AT = datetime(2026, 7, 19, 19, 0, 0, tzinfo=timezone.utc)
RUN_ID = "RUN-20260719T190000000000Z-feedface"


def _copy_package(tmp_path: Path) -> Path:
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    return package_root


def _evaluate(package_root: Path):
    gates = run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )
    return gates, run_package_relationships(gates)


def _build_result(
    package_root: Path,
    *,
    relationships: PackageRelationshipEvaluation | None = None,
):
    gates, evaluated_relationships = _evaluate(package_root)
    return build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=STARTED_AT + timedelta(milliseconds=25),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships or evaluated_relationships,
    )


def _write_result(tmp_path: Path, result) -> Path:
    return write_package_result(
        result=result,
        runs_dir=tmp_path / "runs",
        schema_path=RESULT_SCHEMA,
    )


def _render(result_path: Path) -> str:
    return render_release_readiness_summary(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )


def test_clean_result_reports_stored_counts_and_human_boundary(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    result_path = _write_result(tmp_path, _build_result(package_root))

    first = _render(result_path)
    second = _render(result_path)

    assert first == second
    assert RELEASE_READINESS_MARKDOWN_FILENAME == "release_readiness.md"
    assert "# Package Release-Readiness Summary" in first
    assert "<code>PKG-DEV-PUMP-SKID-001</code>" in first
    assert f"<code>{RUN_ID}</code>" in first
    assert "| Package state | <code>automatic_pass</code> |" in first
    assert "| Release hold | <code>false</code> |" in first
    assert "| Blocking states | none observed |" in first
    assert "| Mandatory gates | 8 | 0 | 0 |" in first
    assert "| Relationship checks | 5 | 0 | 0 |" in first
    assert "| **Total** | **0** |" in first
    assert "[package_result.json](package_result.json)" in first
    assert "release_readiness.md" not in first
    assert ENGINEERING_REVIEW_LIMITATION in first
    assert "A qualified human must decide" in first
    assert "This summary does not approve release" in first
    assert "ready for release" not in first.lower()
    assert "approved for release" not in first.lower()
    assert "\r" not in first
    assert str(tmp_path) not in first


def test_relationship_failure_reports_hold_blocking_state_and_finding_count(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["records"][0]["revision_id"] = "A"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    result_path = _write_result(tmp_path, _build_result(package_root))

    summary = _render(result_path)

    assert "| Package state | <code>automatic_fail</code> |" in summary
    assert "| Release hold | <code>true</code> |" in summary
    assert "| Blocking states | <code>automatic_fail</code> |" in summary
    assert "| Mandatory gates | 8 | 0 | 0 |" in summary
    assert "| Relationship checks | 4 | 1 | 0 |" in summary
    assert "| <code>automatic_fail</code> | 1 |" in summary
    assert "| **Total** | **1** |" in summary


def test_gate_failure_reports_missing_package_identity_and_stored_skips(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")
    result = _build_result(package_root)
    result_path = _write_result(tmp_path, result)
    gate_counts = Counter(item["status"] for item in result.gate_results)
    relationship_counts = Counter(
        item["status"] for item in result.relationship_results
    )

    summary = _render(result_path)

    assert "- Package ID: not established" in summary
    assert (
        "| Mandatory gates | "
        f"{gate_counts['passed']} | {gate_counts['failed']} | {gate_counts['skipped']} |"
    ) in summary
    assert (
        "| Relationship checks | "
        f"{relationship_counts['passed']} | {relationship_counts['failed']} | "
        f"{relationship_counts['skipped']} |"
    ) in summary
    assert "<code>extraction_or_tool_failure</code>" in summary


def test_evaluator_uncertainty_remains_visible_in_summary(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    gates, relationships = _evaluate(package_root)
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

    summary = _render(_write_result(tmp_path, result))

    assert "| Package state | <code>evaluator_uncertainty</code> |" in summary
    assert "| Release hold | <code>true</code> |" in summary
    assert "| <code>evaluator_uncertainty</code> | 1 |" in summary


def test_summary_uses_stored_result_values_without_recomputing(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    document = _build_result(package_root).to_dict()
    document["package_state"] = "engineering_review_required"
    document["release_hold"] = True
    document["blocking_states"] = ["engineering_review_required"]
    document["gate_results"][0]["status"] = "failed"
    document["gate_results"][1]["status"] = "skipped"
    document["relationship_results"][0]["status"] = "failed"
    result_path = tmp_path / "package_result.json"
    result_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")

    summary = _render(result_path)

    assert "| Package state | <code>engineering_review_required</code> |" in summary
    assert "| Release hold | <code>true</code> |" in summary
    assert "| Blocking states | <code>engineering_review_required</code> |" in summary
    assert "| Mandatory gates | 6 | 1 | 1 |" in summary
    assert "| Relationship checks | 4 | 1 | 0 |" in summary
    assert "| **Total** | **0** |" in summary


@pytest.mark.parametrize(
    "raw",
    [
        "{\n",
        '{"schema_version":"0.3.0","schema_version":"0.3.0"}',
        '{"schema_version":"0.3.0"}',
        '{"schema_version":NaN}',
    ],
)
def test_malformed_or_schema_invalid_result_fails_closed(
    tmp_path: Path,
    raw: str,
) -> None:
    result_path = tmp_path / "package_result.json"
    result_path.write_text(raw, encoding="utf-8")

    with pytest.raises(ReleaseReadinessRenderError):
        _render(result_path)


def test_unreadable_result_path_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(ReleaseReadinessRenderError, match="Could not read"):
        _render(tmp_path / "missing.json")
