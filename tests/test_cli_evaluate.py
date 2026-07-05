from __future__ import annotations

import json
from pathlib import Path

from mech_eval_harness.cli import main


ROOT = Path(__file__).resolve().parents[1]
VALID_CANDIDATE = (
    ROOT
    / "examples"
    / "candidates"
    / "MECH-002"
    / "valid.json"
)


def test_evaluate_command_returns_zero_for_passing_candidate(
    capsys,
) -> None:
    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(VALID_CANDIDATE),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 0
    assert "RESULT: PASS" in output
    assert "SCORE: 1.000 (threshold 0.950)" in output
    assert "PASS shaft_power" in output
    assert "FAILURES:\n  NONE" in output


def test_evaluate_command_returns_one_for_failed_checks(
    tmp_path: Path,
    capsys,
) -> None:
    candidate = json.loads(
        VALID_CANDIDATE.read_text(encoding="utf-8")
    )
    candidate["candidate_id"] = "mech-002-wrong-power"
    candidate["payload"]["shaft_power_kw"] = 999.0

    candidate_path = tmp_path / "wrong-power.json"
    candidate_path.write_text(
        json.dumps(candidate),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(candidate_path),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 1
    assert "RESULT: FAIL" in output
    assert "SCORE: 0.650 (threshold 0.950)" in output
    assert "FAIL shaft_power" in output
    assert "WRONG_FORMULA" in output


def test_evaluate_command_returns_one_for_failed_gate(
    tmp_path: Path,
    capsys,
) -> None:
    missing_candidate = tmp_path / "missing.json"

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(missing_candidate),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 1
    assert "RESULT: FAIL" in output
    assert "SCORE: 0.000 (threshold 0.950)" in output
    assert "FAIL output_exists" in output
    assert "INCOMPLETE_DELIVERABLE" in output
    assert "CHECKS:\n  NOT RUN" in output


def test_evaluate_command_returns_two_for_unknown_case(
    capsys,
) -> None:
    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-999",
            str(VALID_CANDIDATE),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 2
    assert "ERROR [CONFIGURATION]" in output
    assert "Unknown case_id: MECH-999" in output


def test_evaluate_command_returns_one_for_invalid_candidate_schema(
    tmp_path: Path,
    capsys,
) -> None:
    candidate = json.loads(
        VALID_CANDIDATE.read_text(encoding="utf-8")
    )
    del candidate["candidate_id"]

    candidate_path = tmp_path / "invalid-schema.json"
    candidate_path.write_text(
        json.dumps(candidate),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(candidate_path),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 1
    assert "RESULT: FAIL" in output
    assert "candidate_validation" in output
    assert "INVALID_FILE" in output
    assert "CHECKS:\n  NOT RUN" in output
