from __future__ import annotations

import csv
import json
from pathlib import Path

from mech_eval_harness.cli import main


ROOT = Path(__file__).resolve().parents[1]
CASE_ROOT = ROOT / "cases" / "MECH-004"
CANDIDATE_DIR = ROOT / "examples" / "candidates" / "MECH-004"


def _load_parts(path: Path) -> dict[str, dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as file:
        return {
            row["part_number"]: row
            for row in csv.DictReader(file)
        }


def _evaluate_candidate(
    *,
    candidate_name: str,
    runs_dir: Path,
) -> tuple[int, dict]:
    exit_code = main(
        [
            "evaluate",
            str(ROOT),
            "MECH-004",
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


def test_mech_004_reference_matches_independent_reconciliation() -> None:
    drawing = _load_parts(
        CASE_ROOT / "input" / "drawing_parts_list.csv"
    )
    procurement = _load_parts(
        CASE_ROOT / "input" / "procurement_bom.csv"
    )

    drawing_parts = set(drawing)
    procurement_parts = set(procurement)
    common_parts = drawing_parts & procurement_parts

    derived = {
        "missing_part_numbers": sorted(
            drawing_parts - procurement_parts
        ),
        "extra_part_numbers": sorted(
            procurement_parts - drawing_parts
        ),
        "quantity_mismatch_part_numbers": sorted(
            part_number
            for part_number in common_parts
            if int(drawing[part_number]["quantity"])
            != int(procurement[part_number]["quantity"])
        ),
        "revision_mismatch_part_numbers": sorted(
            part_number
            for part_number in common_parts
            if drawing[part_number]["revision"]
            != procurement[part_number]["revision"]
        ),
        "reconciliation_disposition": "reject_for_correction",
        "verification": True,
    }

    reference = json.loads(
        (
            CASE_ROOT
            / "reference"
            / "expected.json"
        ).read_text(encoding="utf-8")
    )

    assert derived == reference


def test_mech_004_valid_candidate_passes_end_to_end(
    tmp_path: Path,
) -> None:
    exit_code, result = _evaluate_candidate(
        candidate_name="valid.json",
        runs_dir=tmp_path / "valid-runs",
    )

    assert exit_code == 0
    assert result["candidate_id"] == "mech-004-valid-001"
    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["gate_passed"] is True
    assert result["failures"] == []


def test_mech_004_revision_error_fails_expected_check(
    tmp_path: Path,
) -> None:
    exit_code, result = _evaluate_candidate(
        candidate_name="revision-error.json",
        runs_dir=tmp_path / "revision-error-runs",
    )

    assert exit_code == 1
    assert (
        result["candidate_id"]
        == "mech-004-revision-error-001"
    )
    assert result["passed"] is False
    assert result["score"] == 0.8
    assert result["gate_passed"] is True
    assert len(result["checks"]) == 6
    assert len(result["failures"]) == 1

    failure = result["failures"][0]

    assert failure["source"] == "check"
    assert failure["item_id"] == "revision_mismatches"
    assert failure["failure_mode"] == "WRONG_REVISION"
    assert failure["weight"] == 0.2
