from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_portfolio_demo_verifies_pass_failure_and_persistence(
    tmp_path: Path,
) -> None:
    runs_dir = tmp_path / "runs"
    report_path = tmp_path / "report.md"

    completed = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "run_portfolio_demo.py"),
            "--runs-dir",
            str(runs_dir),
            "--report-path",
            str(report_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, (
        completed.stdout + "\n" + completed.stderr
    )
    assert "DEMO VERIFIED: 2/2 scenarios" in completed.stdout
    assert "RESULT: PASS" in completed.stdout
    assert "RESULT: FAIL" in completed.stdout
    assert "UNIT_ERROR" in completed.stdout

    result_paths = sorted(runs_dir.rglob("result.json"))
    assert len(result_paths) == 2

    documents = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in result_paths
    ]

    passing = next(
        document for document in documents if document["passed"]
    )
    failing = next(
        document for document in documents if not document["passed"]
    )

    assert passing["candidate_id"] == "mech-002-valid-001"
    assert passing["score"] == 1.0
    assert passing["failures"] == []

    assert failing["candidate_id"] == "mech-002-unit-error-001"
    assert failing["score"] == 0.75
    assert [
        failure["failure_mode"]
        for failure in failing["failures"]
    ] == ["UNIT_ERROR"]

    report = report_path.read_text(encoding="utf-8")
    assert "# Portfolio Demo Evidence" in report
    assert "`mech-002-pass`" in report
    assert "`mech-002-unit-error`" in report
    assert "This is evidence of harness behaviour." in report
