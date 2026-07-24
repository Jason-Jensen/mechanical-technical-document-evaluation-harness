from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

import pytest

from mech_eval_harness.ai_governance import (
    AIManagementSystemValidationError,
    main as ai_governance_main,
    referenced_document_paths,
    validate_ai_management_system,
)


ROOT = Path(__file__).resolve().parents[1]


def _load_system(root: Path = ROOT) -> dict[str, Any]:
    with (root / "governance/ai_management_system.json").open(
        encoding="utf-8"
    ) as handle:
        return json.load(handle)


def _copy_system(
    tmp_path: Path,
    mutate: Callable[[dict[str, Any]], None] | None = None,
) -> Path:
    temp_root = tmp_path / "repository"
    (temp_root / "governance").mkdir(parents=True)
    (temp_root / "schemas").mkdir(parents=True)
    shutil.copy2(
        ROOT / "schemas/ai_management_system.schema.json",
        temp_root / "schemas/ai_management_system.schema.json",
    )
    system = _load_system()
    if mutate is not None:
        mutate(system)
    for reference in referenced_document_paths(system):
        target = temp_root.joinpath(*Path(reference).parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("test evidence\n", encoding="utf-8")
    (temp_root / "governance/ai_management_system.json").write_text(
        json.dumps(system, indent=2) + "\n",
        encoding="utf-8",
    )
    return temp_root


def _remove_risk_and_nonconformity_holds(system: dict[str, Any]) -> None:
    for risk in system["risks"]:
        if risk["release_hold"]:
            risk["owner_role_id"] = "ROLE-OWNER"
            risk["status"] = "accepted"
            risk["release_hold"] = False
    for item in system["nonconformities"]:
        item["status"] = "closed"
        item["release_hold"] = False
    system["release_status"]["hold_risk_ids"] = []
    system["release_status"]["hold_nonconformity_ids"] = []


def test_repository_ai_management_system_is_valid_and_release_held() -> None:
    summary = validate_ai_management_system(ROOT)

    assert summary.management_system_id == "AIMS-MEWA-001"
    assert summary.system_count == 3
    assert summary.risk_count == 13
    assert summary.control_count == 20
    assert summary.gate_count == 8
    assert summary.release_authorized is False
    assert summary.release_state == "held"
    assert summary.hold_risk_ids == ("AIR-003", "AIR-008", "AIR-011")
    assert summary.hold_nonconformity_ids == ("NC-002",)
    assert summary.pending_decision_ids == ("D-120",)
    assert summary.release_ready is False


def test_governance_cli_reports_valid_held_state() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mech_eval_harness.ai_governance",
            str(ROOT),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "PASS AIMS-MEWA-001" in result.stdout
    assert "RELEASE: HELD" in result.stdout
    assert "risks=AIR-003,AIR-008,AIR-011" in result.stdout
    assert "nonconformities=NC-002" in result.stdout
    assert "pending=D-120" in result.stdout


def test_release_ready_mode_fails_while_mandatory_holds_remain() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mech_eval_harness.ai_governance",
            str(ROOT),
            "--require-release-ready",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2
    assert "Mandatory AI management-system release holds remain open" in result.stderr


def test_governance_main_reports_valid_and_strict_states(capsys: Any) -> None:
    assert ai_governance_main([str(ROOT)]) == 0
    normal = capsys.readouterr()
    assert "PASS AIMS-MEWA-001" in normal.out
    assert "RELEASE: HELD" in normal.out

    assert ai_governance_main([str(ROOT), "--require-release-ready"]) == 2
    strict = capsys.readouterr()
    assert "Mandatory AI management-system release holds remain open" in strict.err


def test_duplicate_governance_identifier_fails(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        duplicate = dict(system["roles"][0])
        system["roles"].append(duplicate)

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Duplicate role identifier: ROLE-OWNER",
    ):
        validate_ai_management_system(root)


def test_risk_score_must_equal_likelihood_times_impact(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["risks"][0]["residual_score"] = 7

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="AIR-001 residual score must equal likelihood times impact",
    ):
        validate_ai_management_system(root)


def test_unknown_control_reference_fails(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["risks"][0]["control_ids"] = ["AIC-999"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Risk AIR-001 controls references unknown identifiers: AIC-999",
    ):
        validate_ai_management_system(root)


def test_missing_evidence_path_fails(tmp_path: Path) -> None:
    root = _copy_system(tmp_path)
    missing = root / "docs/governance/ai_impact_assessment_v0.3.0.md"
    missing.unlink()

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Governance evidence path does not exist",
    ):
        validate_ai_management_system(root)


def test_release_hold_list_must_match_risk_register(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["release_status"]["hold_risk_ids"] = ["AIR-010"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="hold_risk_ids must exactly match",
    ):
        validate_ai_management_system(root)


def test_pending_decision_alone_keeps_release_held(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        _remove_risk_and_nonconformity_holds(system)

    root = _copy_system(tmp_path, mutate)
    summary = validate_ai_management_system(root)

    assert summary.hold_risk_ids == ()
    assert summary.hold_nonconformity_ids == ()
    assert summary.pending_decision_ids == ("D-120",)
    assert summary.release_ready is False


def test_release_authorization_must_match_release_state(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        _remove_risk_and_nonconformity_holds(system)
        system["release_status"]["pending_decision_ids"] = []
        system["release_status"]["release_state"] = "ready_for_owner_decision"
        system["release_status"]["release_authorized"] = True
        system["status"] = "operational_release_ready"

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="release_authorized must be true exactly when release_state is",
    ):
        validate_ai_management_system(root)


def test_unapproved_governance_source_host_fails(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["sources"][0]["url"] = "https://example.com/standard"

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="is not on an approved authoritative host",
    ):
        validate_ai_management_system(root)


def test_exactly_one_role_may_authorize_release(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["roles"][1]["may_authorize_release"] = True

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Exactly one governance role must have release authority",
    ):
        validate_ai_management_system(root)


def test_future_ai_capability_must_remain_blocked(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        future = next(
            item for item in system["systems"] if item["system_id"] == "AIS-003"
        )
        future["lifecycle_status"] = "active"
        future["data_classes"] = ["public", "synthetic"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Future AI system AIS-003 must remain blocked",
    ):
        validate_ai_management_system(root)


def test_minimum_control_cannot_be_deferred(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        control = next(
            item for item in system["controls"] if item["control_id"] == "AIC-001"
        )
        control["implementation_status"] = "deferred_not_triggered"

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Minimum control AIC-001 cannot be deferred",
    ):
        validate_ai_management_system(root)


def test_control_risk_reference_must_exist(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["controls"][0]["risk_ids"] = ["AIR-999"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Control AIC-001 risks references unknown identifiers: AIR-999",
    ):
        validate_ai_management_system(root)


def test_gate_control_reference_must_exist(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["mandatory_gates"][0]["required_control_ids"] = ["AIC-999"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Gate AIG-01 controls references unknown identifiers: AIC-999",
    ):
        validate_ai_management_system(root)


def test_controlled_risk_cannot_remain_high(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        risk = next(item for item in system["risks"] if item["risk_id"] == "AIR-003")
        risk["status"] = "controlled"

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="AIR-003 cannot be controlled while residual risk remains high",
    ):
        validate_ai_management_system(root)


def test_next_review_date_must_follow_effective_date(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["next_review_date"] = system["effective_date"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="next_review_date must be later than effective_date",
    ):
        validate_ai_management_system(root)


def test_high_residual_risk_requires_hold_or_authorized_acceptance(
    tmp_path: Path,
) -> None:
    def mutate(system: dict[str, Any]) -> None:
        risk = next(item for item in system["risks"] if item["risk_id"] == "AIR-003")
        risk["release_hold"] = False
        system["release_status"]["hold_risk_ids"] = ["AIR-008", "AIR-011"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="AIR-003 has high residual risk without a release hold",
    ):
        validate_ai_management_system(root)


def test_partial_control_requires_gap_and_action(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        control = next(
            item for item in system["controls"] if item["control_id"] == "AIC-013"
        )
        del control["gap"]

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Partial control AIC-013 requires a gap and action_ref",
    ):
        validate_ai_management_system(root)


def test_active_system_cannot_use_restricted_data_class(tmp_path: Path) -> None:
    def mutate(system: dict[str, Any]) -> None:
        system["systems"][0]["data_classes"].append("restricted_not_authorized")

    root = _copy_system(tmp_path, mutate)

    with pytest.raises(
        AIManagementSystemValidationError,
        match="Active system AIS-001 cannot use",
    ):
        validate_ai_management_system(root)
