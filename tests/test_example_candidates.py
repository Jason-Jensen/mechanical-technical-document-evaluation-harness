from __future__ import annotations

import json
from pathlib import Path

from mech_eval_harness.cli import main


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DIR = (
    ROOT
    / "examples"
    / "candidates"
    / "MECH-002"
)


def _evaluate_example(
    *,
    candidate_name: str,
    runs_dir: Path,
) -> tuple[int, dict]:
    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
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
    document = json.loads(
        result_path.read_text(encoding="utf-8")
    )

    return exit_code, document


def test_valid_example_passes_end_to_end(
    tmp_path: Path,
) -> None:
    exit_code, document = _evaluate_example(
        candidate_name="valid.json",
        runs_dir=tmp_path / "valid-runs",
    )

    assert exit_code == 0
    assert document["candidate_id"] == "mech-002-valid-001"
    assert document["passed"] is True
    assert document["score"] == 1.0
    assert document["gate_passed"] is True
    assert document["failures"] == []


def test_unit_error_example_fails_expected_check(
    tmp_path: Path,
) -> None:
    exit_code, document = _evaluate_example(
        candidate_name="unit-error.json",
        runs_dir=tmp_path / "unit-error-runs",
    )

    assert exit_code == 1
    assert document["candidate_id"] == "mech-002-unit-error-001"
    assert document["passed"] is False
    assert document["score"] == 0.75
    assert document["gate_passed"] is True
    assert len(document["checks"]) == 5
    assert len(document["failures"]) == 1

    failure = document["failures"][0]

    assert failure["source"] == "check"
    assert failure["item_id"] == "angular_velocity"
    assert failure["failure_mode"] == "UNIT_ERROR"
    assert failure["weight"] == 0.25


def test_incomplete_example_fails_required_fields_gate(
    tmp_path: Path,
) -> None:
    exit_code, document = _evaluate_example(
        candidate_name="incomplete.json",
        runs_dir=tmp_path / "incomplete-runs",
    )

    assert exit_code == 1
    assert document["candidate_id"] is None
    assert document["passed"] is False
    assert document["score"] == 0.0
    assert document["gate_passed"] is False
    assert document["checks"] == []
    assert len(document["failures"]) == 1

    failure = document["failures"][0]

    assert failure["source"] == "gate"
    assert failure["item_id"] == "required_fields"
    assert failure["failure_mode"] == "INCOMPLETE_DELIVERABLE"
    assert failure["weight"] is None
