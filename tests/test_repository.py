from __future__ import annotations

import copy
import json
import subprocess
import sys
import shutil
from pathlib import Path

import pytest

from mech_eval_harness.validator import (
    RepositoryValidationError,
    discover_case_files,
    load_case,
    load_case_by_id,
    load_json,
    validate_repository,
)


ROOT = Path(__file__).resolve().parents[1]



def test_repository_has_five_cases() -> None:
    case_files = discover_case_files(ROOT)

    assert [
        case_file.parent.name
        for case_file in case_files
    ] == [
        "MECH-001",
        "MECH-002",
        "MECH-003",
        "MECH-004",
        "MECH-005",
    ]


def test_repository_validates() -> None:
    loaded = validate_repository(ROOT)

    assert [
        item.case["case_id"]
        for item in loaded
    ] == [
        "MECH-001",
        "MECH-002",
        "MECH-003",
        "MECH-004",
        "MECH-005",
    ]

@pytest.mark.parametrize(
    "case_id",
    [
        "MECH-001",
        "MECH-002",
        "MECH-003",
        "MECH-004",
        "MECH-005",
    ],
)
def test_each_case_loads(case_id: str) -> None:
    loaded = load_case(ROOT, ROOT / "cases" / case_id / "case.json")
    assert loaded.case["case_id"] == case_id

def test_load_case_by_id_loads_requested_case() -> None:
    loaded = load_case_by_id(ROOT, "MECH-002")

    assert loaded.case["case_id"] == "MECH-002"
    assert loaded.case_path == ROOT / "cases" / "MECH-002" / "case.json"


def test_load_case_by_id_rejects_unknown_case() -> None:
    with pytest.raises(
        RepositoryValidationError,
        match="Unknown case_id: MECH-999",
    ):
        load_case_by_id(ROOT, "MECH-999")

def test_all_cases_are_synthetic() -> None:
    assert all(
        item.case["metadata"]["synthetic"]
        for item in validate_repository(ROOT)
    )


def test_all_seed_cases_are_reviewed() -> None:
    assert all(
        item.case["metadata"]["review_status"] == "reviewed"
        for item in validate_repository(ROOT)
    )


def test_reference_is_evaluator_only() -> None:
    assert all(
        item.environment["reference_access"] == "evaluator_only"
        for item in validate_repository(ROOT)
    )


def test_external_access_is_disabled() -> None:
    assert all(
        item.environment["external_access"] == "disabled"
        for item in validate_repository(ROOT)
    )


def test_evaluator_weights_sum_to_one() -> None:
    for item in validate_repository(ROOT):
        assert sum(check["weight"] for check in item.evaluator["checks"]) == pytest.approx(1.0)


def test_all_evaluators_are_deterministic() -> None:
    assert all(
        item.evaluator["mode"] == "deterministic"
        for item in validate_repository(ROOT)
    )


def test_all_evaluators_use_gates_before_checks() -> None:
    assert all(
        item.evaluator["composition"] == "gate_then_weighted_checks"
        for item in validate_repository(ROOT)
    )


def test_each_task_requires_human_review() -> None:
    assert all(
        item.task["human_review_required"] is True
        for item in validate_repository(ROOT)
    )


def test_each_case_has_failure_modes() -> None:
    assert all(
        item.case["metadata"]["failure_modes"]
        for item in validate_repository(ROOT)
    )


def test_power_reference_is_numerically_consistent() -> None:
    expected = load_json(ROOT / "cases/MECH-002/reference/expected.json")
    assert expected["shaft_power_kw"] == pytest.approx(21.9911, abs=0.0001)
    assert expected["verification"] is True


def test_fit_reference_is_diametral() -> None:
    expected = load_json(ROOT / "cases/MECH-001/reference/expected.json")
    assert expected["minimum_clearance_mm"] == pytest.approx(0.010)
    assert expected["maximum_clearance_mm"] == pytest.approx(0.046)


def test_revision_case_rejects_instruction() -> None:
    expected = load_json(ROOT / "cases/MECH-003/reference/expected.json")
    assert expected["release_disposition"] == "reject_for_correction"
    assert "WRONG_REVISION" in expected["issue_codes"]


def test_load_json_rejects_array_top_level(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("[]", encoding="utf-8")
    with pytest.raises(RepositoryValidationError, match="Top-level"):
        load_json(path)


def test_load_json_rejects_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not json}", encoding="utf-8")
    with pytest.raises(RepositoryValidationError, match="Invalid JSON"):
        load_json(path)

def test_cli_inspect_rejects_unknown_case() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mech_eval_harness",
            "inspect",
            str(ROOT),
            "MECH-999",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 1
    assert "ERROR: Unknown case_id: MECH-999" in output

def test_cli_inspect_ignores_invalid_unrelated_case(tmp_path: Path) -> None:
    temp_root = tmp_path / "repository"

    shutil.copytree(ROOT / "schemas", temp_root / "schemas")
    shutil.copytree(ROOT / "specs", temp_root / "specs")
    shutil.copytree(
        ROOT / "cases" / "MECH-002",
        temp_root / "cases" / "MECH-002",
    )

    unrelated_case_dir = temp_root / "cases" / "MECH-003"
    unrelated_case_dir.mkdir(parents=True)
    (unrelated_case_dir / "case.json").write_text(
        "{not valid json}",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "mech_eval_harness",
            "inspect",
            str(temp_root),
            "MECH-002",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr

    assert result.returncode == 0
    assert "Case:        MECH-002" in output
    assert "Invalid JSON" not in output

def test_load_case_rejects_evaluator_weights_not_summing_to_one(
    tmp_path: Path,
) -> None:
    temp_root = tmp_path / "repository"

    shutil.copytree(ROOT / "schemas", temp_root / "schemas")
    shutil.copytree(ROOT / "specs", temp_root / "specs")
    shutil.copytree(
        ROOT / "cases" / "MECH-002",
        temp_root / "cases" / "MECH-002",
    )

    evaluator_path = (
        temp_root / "specs" / "evaluators" / "shaft_power_v1.json"
    )
    evaluator = load_json(evaluator_path)
    evaluator["checks"][0]["weight"] += 0.1

    evaluator_path.write_text(
        json.dumps(evaluator, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        RepositoryValidationError,
        match="evaluator check weights must sum to 1.0",
    ):
        load_case(
            temp_root,
            temp_root / "cases" / "MECH-002" / "case.json",
        )

def test_load_case_rejects_missing_input_asset(tmp_path: Path) -> None:
    temp_root = tmp_path / "repository"

    shutil.copytree(ROOT / "schemas", temp_root / "schemas")
    shutil.copytree(ROOT / "specs", temp_root / "specs")
    shutil.copytree(
        ROOT / "cases" / "MECH-002",
        temp_root / "cases" / "MECH-002",
    )

    missing_asset = (
        temp_root
        / "cases"
        / "MECH-002"
        / "input"
        / "equipment_data.csv"
    )
    missing_asset.unlink()

    with pytest.raises(
        RepositoryValidationError,
        match="MECH-002: missing input asset: equipment_data.csv",
    ):
        load_case(
            temp_root,
            temp_root / "cases" / "MECH-002" / "case.json",
        )