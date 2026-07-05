from __future__ import annotations

import csv
import json
from pathlib import Path

from mech_eval_harness.cli import main


ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = ROOT / "cases" / "MECH-005"
CANDIDATE_DIR = ROOT / "examples" / "candidates" / "MECH-005"


def _load_component_data() -> dict[str, str]:
    path = CASE_ROOT / "input" / "component_data.csv"

    with path.open(encoding="utf-8", newline="") as file:
        return next(csv.DictReader(file))


def _evaluate_candidate(
    *,
    candidate_name: str,
    runs_dir: Path,
) -> tuple[int, dict]:
    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-005",
            str(CANDIDATE_DIR / candidate_name),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    run_dirs = [
        path
        for path in runs_dir.iterdir()
        if path.is_dir()
    ]

    assert len(run_dirs) == 1

    result_path = run_dirs[0] / "result.json"
    result = json.loads(
        result_path.read_text(encoding="utf-8")
    )

    return exit_code, result


def test_mech_005_reference_matches_independent_calculation() -> None:
    row = _load_component_data()

    length_m = float(row["installed_length_m"])
    installation_temperature_c = float(
        row["installation_temperature_c"]
    )
    operating_temperature_c = float(
        row["operating_temperature_c"]
    )
    alpha_per_c = float(
        row["linear_expansion_coefficient_per_c"]
    )

    temperature_change_c = (
        operating_temperature_c
        - installation_temperature_c
    )

    primary_expansion_mm = (
        alpha_per_c
        * length_m
        * temperature_change_c
        * 1000.0
    )

    verification_expansion_mm = (
        alpha_per_c
        * (length_m * 1000.0)
        * temperature_change_c
    )

    relative_difference_percent = (
        abs(
            primary_expansion_mm
            - verification_expansion_mm
        )
        / verification_expansion_mm
        * 100.0
    )

    reference = json.loads(
        (
            CASE_ROOT
            / "reference"
            / "expected.json"
        ).read_text(encoding="utf-8")
    )

    assert abs(
        reference["temperature_change_c"]
        - temperature_change_c
    ) < 1e-12
    assert abs(
        reference["free_expansion_mm"]
        - primary_expansion_mm
    ) < 1e-12
    assert abs(
        reference["verification_expansion_mm"]
        - verification_expansion_mm
    ) < 1e-12
    assert abs(
        reference["relative_difference_percent"]
        - relative_difference_percent
    ) < 1e-12
    assert reference["expansion_direction"] == "increase"
    assert (
        reference["calculation_disposition"]
        == "requires_expansion_accommodation_review"
    )
    assert reference["verification"] is True


def test_mech_005_valid_candidate_passes_end_to_end(
    tmp_path: Path,
) -> None:
    exit_code, result = _evaluate_candidate(
        candidate_name="valid.json",
        runs_dir=tmp_path / "valid-runs",
    )

    assert exit_code == 0
    assert result["candidate_id"] == "mech-005-valid-001"
    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["gate_passed"] is True
    assert result["failures"] == []


def test_mech_005_unit_error_fails_expected_checks(
    tmp_path: Path,
) -> None:
    exit_code, result = _evaluate_candidate(
        candidate_name="unit-error.json",
        runs_dir=tmp_path / "unit-error-runs",
    )

    assert exit_code == 1
    assert result["candidate_id"] == "mech-005-unit-error-001"
    assert result["passed"] is False
    assert result["score"] == 0.65
    assert result["gate_passed"] is True
    assert len(result["checks"]) == 7
    assert len(result["failures"]) == 2

    failures = {
        (
            failure["item_id"],
            failure["failure_mode"],
            failure["weight"],
        )
        for failure in result["failures"]
    }

    assert failures == {
        ("free_expansion", "UNIT_ERROR", 0.25),
        (
            "relative_difference",
            "FAILURE_TO_VERIFY",
            0.1,
        ),
    }
