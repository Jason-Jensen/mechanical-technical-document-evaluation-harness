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


def _read_only_result(runs_dir: Path) -> dict:
    run_dirs = [
        path
        for path in runs_dir.iterdir()
        if path.is_dir()
    ]

    assert len(run_dirs) == 1

    result_path = run_dirs[0] / "result.json"

    assert result_path.is_file()

    return json.loads(
        result_path.read_text(encoding="utf-8")
    )


def test_evaluate_command_returns_zero_and_persists_pass(
    tmp_path: Path,
    capsys,
) -> None:
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(VALID_CANDIDATE),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    output = capsys.readouterr().out
    document = _read_only_result(runs_dir)

    assert exit_code == 0
    assert "RESULT: PASS" in output
    assert "SCORE: 1.000 (threshold 0.950)" in output
    assert "PASS shaft_power" in output
    assert "FAILURES:\n  NONE" in output
    assert "RESULT RECORD:" in output
    assert document["passed"] is True
    assert document["score"] == 1.0


def test_evaluate_command_returns_one_and_persists_failed_checks(
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
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(candidate_path),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    output = capsys.readouterr().out
    document = _read_only_result(runs_dir)

    assert exit_code == 1
    assert "RESULT: FAIL" in output
    assert "SCORE: 0.650 (threshold 0.950)" in output
    assert "FAIL shaft_power" in output
    assert "WRONG_FORMULA" in output
    assert "RESULT RECORD:" in output
    assert document["passed"] is False
    assert document["score"] == 0.65
    assert document["failures"][0]["item_id"] == "shaft_power"


def test_evaluate_command_returns_one_and_persists_failed_gate(
    tmp_path: Path,
    capsys,
) -> None:
    missing_candidate = tmp_path / "missing.json"
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(missing_candidate),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    output = capsys.readouterr().out
    document = _read_only_result(runs_dir)

    assert exit_code == 1
    assert "RESULT: FAIL" in output
    assert "SCORE: 0.000 (threshold 0.950)" in output
    assert "FAIL output_exists" in output
    assert "INCOMPLETE_DELIVERABLE" in output
    assert "CHECKS:\n  NOT RUN" in output
    assert "RESULT RECORD:" in output
    assert document["gate_passed"] is False
    assert document["checks"] == []
    assert document["failures"][0]["source"] == "gate"


def test_evaluate_command_returns_two_without_result_for_unknown_case(
    tmp_path: Path,
    capsys,
) -> None:
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-999",
            str(VALID_CANDIDATE),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    output = capsys.readouterr().out

    assert exit_code == 2
    assert "ERROR [CONFIGURATION]" in output
    assert "Unknown case_id: MECH-999" in output
    assert not runs_dir.exists()


def test_invalid_candidate_schema_is_persisted_as_failed_gate(
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
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-002",
            str(candidate_path),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    output = capsys.readouterr().out
    document = _read_only_result(runs_dir)

    assert exit_code == 1
    assert "RESULT: FAIL" in output
    assert "FAIL candidate_schema" in output
    assert "INVALID_FILE" in output
    assert "CHECKS:\n  NOT RUN" in output
    assert "RESULT RECORD:" in output
    assert document["candidate_id"] is None
    assert document["failures"][0]["source"] == "gate"
    assert (
        document["failures"][0]["item_id"]
        == "candidate_schema"
    )
