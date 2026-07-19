from __future__ import annotations

import json
import shutil
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mech_eval_harness.package_assurance import (
    PACKAGE_GATE_ORDER,
    PACKAGE_STATE_PRECEDENCE,
    RELATIONSHIP_CHECK_ORDER,
    REQUIRED_EVALUATION_INCOMPLETE_CODE,
    build_package_input_fingerprint,
    build_package_result,
    route_package_state,
    run_package_gates,
    run_package_relationships,
)
from mech_eval_harness.package_assurance.models import (
    PackageRelationshipEvaluation,
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
STARTED_AT = datetime(2026, 7, 19, 18, 0, 0, tzinfo=timezone.utc)
COMPLETED_AT = STARTED_AT + timedelta(milliseconds=125)
RUN_ID = "RUN-20260719T180000000000Z-deadbeef"


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


def _build(package_root: Path, *, run_id: str = RUN_ID):
    gates, relationships = _evaluate(package_root)
    return build_package_result(
        run_id=run_id,
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships,
        host_metadata={"platform": "test"},
        output_location="runs/test",
    )


def test_clean_package_builds_complete_automatic_pass(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)

    result = _build(package_root)
    document = result.to_dict()

    assert result.package_state == "automatic_pass"
    assert result.release_hold is False
    assert result.blocking_states == ()
    assert result.findings == ()
    assert result.completeness.status == "complete"
    assert result.completeness.automatic_pass_eligible is True
    assert tuple(item["gate_id"] for item in result.gate_results) == PACKAGE_GATE_ORDER
    assert (
        tuple(item["check_id"] for item in result.relationship_results)
        == RELATIONSHIP_CHECK_ORDER
    )
    assert document["versions"] == {
        "package_result_schema": "0.3.0",
        "evaluator": "0.3.0",
        "router": "0.3.0",
        "workflow_contract": "0.3.0",
        "package_manifest": "0.3.0",
        "authority_map": "0.3.0",
    }
    assert document["engineering_review_limitation"].startswith(
        "This result supports qualified human review"
    )


def test_state_router_applies_precedence_for_every_ordered_pair() -> None:
    precedence = list(PACKAGE_STATE_PRECEDENCE)
    for left in precedence:
        for right in precedence:
            selected, blocking = route_package_state([left, right])
            non_pass = {left, right} - {"automatic_pass"}
            expected_blocking = tuple(
                state for state in precedence if state in non_pass
            )
            expected_selected = expected_blocking[0] if expected_blocking else "automatic_pass"
            assert selected == expected_selected
            assert blocking == expected_blocking

            reversed_selected, reversed_blocking = route_package_state([right, left])
            assert reversed_selected == selected
            assert reversed_blocking == blocking

    expected_blocking = tuple(
        state for state in PACKAGE_STATE_PRECEDENCE if state != "automatic_pass"
    )
    for permutation in (
        tuple(reversed(PACKAGE_STATE_PRECEDENCE)),
        (
            "engineering_review_required",
            "automatic_pass",
            "evaluator_uncertainty",
            "automatic_fail",
            "missing_authoritative_information",
            "extraction_or_tool_failure",
        ),
    ):
        selected, blocking = route_package_state(permutation)
        assert selected == "automatic_fail"
        assert blocking == expected_blocking


def test_relationship_failure_is_canonical_and_release_holding(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["records"][0]["revision_id"] = "A"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    result = _build(package_root)

    assert result.package_state == "automatic_fail"
    assert result.release_hold is True
    assert result.blocking_states == ("automatic_fail",)
    assert len(result.findings) == 1
    finding = result.findings[0]
    assert finding.control_type == "relationship_check"
    assert finding.authority_rule_id == "AUTH-DWG-001"
    assert finding.governing_control_id is None
    check = result.relationship_results[0]
    assert check["finding_ids"] == [finding.finding_id]
    assert "findings" not in check


def test_missing_required_check_routes_to_evaluator_uncertainty(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates, relationships = _evaluate(package_root)
    incomplete = PackageRelationshipEvaluation(
        package_id=relationships.package_id,
        checks=relationships.checks[:-1],
    )

    result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=incomplete,
    )

    assert result.package_state == "evaluator_uncertainty"
    assert result.release_hold is True
    assert result.completeness.status == "incomplete"
    assert any(
        issue.code == "missing_relationship_check"
        for issue in result.completeness.issues
    )
    assert result.findings[0].code == REQUIRED_EVALUATION_INCOMPLETE_CODE


def test_unexpected_skip_cannot_produce_pass(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    gates, relationships = _evaluate(package_root)
    skipped = replace(
        relationships.checks[0],
        status="skipped",
        summary="Synthetic unexpected skip.",
        findings=(),
        blocked_by=(PACKAGE_GATE_ORDER[0],),
    )
    altered = PackageRelationshipEvaluation(
        package_id=relationships.package_id,
        checks=(skipped, *relationships.checks[1:]),
    )

    result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=altered,
    )

    assert result.package_state == "evaluator_uncertainty"
    assert any(
        issue.code == "unexpected_relationship_check_skip"
        for issue in result.completeness.issues
    )


def test_duplicate_and_out_of_order_results_cannot_produce_pass(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates, relationships = _evaluate(package_root)
    duplicate = PackageRelationshipEvaluation(
        package_id=relationships.package_id,
        checks=(relationships.checks[0], *relationships.checks),
    )
    reordered_checks = list(relationships.checks)
    reordered_checks[0], reordered_checks[1] = (
        reordered_checks[1],
        reordered_checks[0],
    )
    reordered = PackageRelationshipEvaluation(
        package_id=relationships.package_id,
        checks=tuple(reordered_checks),
    )

    duplicate_result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=duplicate,
    )
    reordered_result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=COMPLETED_AT,
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=reordered,
    )

    assert duplicate_result.package_state == "evaluator_uncertainty"
    assert any(
        issue.code == "duplicate_relationship_check"
        for issue in duplicate_result.completeness.issues
    )
    assert reordered_result.package_state == "evaluator_uncertainty"
    assert any(
        issue.code == "out_of_order_relationship_check"
        for issue in reordered_result.completeness.issues
    )


def test_failed_gate_allows_dependency_skips_without_false_uncertainty(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")

    result = _build(package_root)

    assert result.package_id is None
    assert result.package_state == "extraction_or_tool_failure"
    assert result.blocking_states == ("extraction_or_tool_failure",)
    assert result.completeness.status == "complete"
    assert result.completeness.automatic_pass_eligible is False
    assert all(item["status"] == "skipped" for item in result.gate_results[1:])
    assert all(
        item["status"] == "skipped" for item in result.relationship_results
    )
    assert result.input_fingerprint.status == "partial"
    assert [artifact.path for artifact in result.input_fingerprint.artifacts] == [
        "package_manifest.json"
    ]


def test_fingerprint_includes_only_controlled_inputs(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)
    gates, _ = _evaluate(package_root)
    assert gates.manifest is not None
    (package_root / "expected").mkdir(exist_ok=True)
    (package_root / "expected" / "ignored.json").write_text("{}", encoding="utf-8")
    (package_root / "undeclared.txt").write_text("ignored", encoding="utf-8")

    first = build_package_input_fingerprint(
        package_root=package_root,
        manifest=gates.manifest,
    )
    (package_root / "undeclared.txt").write_text("changed", encoding="utf-8")
    second = build_package_input_fingerprint(
        package_root=package_root,
        manifest=gates.manifest,
    )

    expected_paths = {
        path.relative_to(package_root).as_posix()
        for path in (
            *gates.manifest.source_paths.values(),
            *gates.manifest.file_reference_paths.values(),
        )
    }
    assert first.status == "complete"
    assert {artifact.path for artifact in first.artifacts} == expected_paths
    assert first.sha256 == second.sha256
    assert all(artifact.sha256 is not None for artifact in first.artifacts)

    register_path = package_root / "inputs" / "drawing_register.csv"
    register_path.write_text(
        register_path.read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    third = build_package_input_fingerprint(
        package_root=package_root,
        manifest=gates.manifest,
    )
    assert third.sha256 != first.sha256


def test_substantive_result_is_stable_across_volatile_run_metadata(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    first = _build(package_root)
    gates, relationships = _evaluate(package_root)
    second = build_package_result(
        run_id="RUN-20260719T180001000000Z-feedface",
        started_at=STARTED_AT + timedelta(seconds=1),
        completed_at=COMPLETED_AT + timedelta(seconds=2),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships,
        host_metadata={"platform": "different-test-host"},
        output_location="different/runs/test",
    )

    first_document = first.to_dict()
    second_document = second.to_dict()
    for document in (first_document, second_document):
        document.pop("run_id")
        document.pop("run_metadata")
    assert first_document == second_document
