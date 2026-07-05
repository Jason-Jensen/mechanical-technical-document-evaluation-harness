from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = (
    ROOT / "evidence" / "mvp_v1_baseline" / "summary.json"
)
REPORT_PATH = (
    ROOT / "evidence" / "mvp_v1_baseline" / "report.md"
)
RUNNER_PATH = ROOT / "scripts" / "run_mvp_baseline.py"

EXPECTED_METRICS = {
    "oracle_development_total": 4,
    "oracle_development_passed": 4,
    "oracle_held_out_total": 1,
    "oracle_held_out_passed": 1,
    "fault_scenarios_total": 4,
    "fault_scenarios_detected": 4,
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_committed_baseline_summary_has_expected_claims() -> None:
    summary = _load_json(SUMMARY_PATH)

    assert summary["benchmark_id"] == "MECHANICAL-MVP-V1"
    assert summary["baseline_type"] == "harness_verification"
    assert summary["metrics"] == EXPECTED_METRICS
    assert summary["claims"] == {
        "model_performance_evidence": False,
        "agent_performance_evidence": False,
        "oracle_evaluator_integrity_check": True,
        "curated_fault_detection_check": True,
    }


def test_committed_baseline_scenarios_are_complete() -> None:
    summary = _load_json(SUMMARY_PATH)
    scenarios = summary["scenarios"]

    assert len(scenarios) == 9
    assert len(
        {
            scenario["scenario_id"]
            for scenario in scenarios
        }
    ) == 9
    assert all(
        scenario["expectation_met"]
        for scenario in scenarios
    )

    oracle_development = [
        scenario
        for scenario in scenarios
        if scenario["suite"] == "oracle"
        and scenario["split"] == "development"
    ]
    oracle_held_out = [
        scenario
        for scenario in scenarios
        if scenario["suite"] == "oracle"
        and scenario["split"] == "held_out"
    ]
    fault_scenarios = [
        scenario
        for scenario in scenarios
        if scenario["suite"] == "fault_injection"
    ]

    assert {
        scenario["case_id"]
        for scenario in oracle_development
    } == {
        "MECH-001",
        "MECH-002",
        "MECH-004",
        "MECH-005",
    }
    assert [
        scenario["case_id"]
        for scenario in oracle_held_out
    ] == ["MECH-003"]
    assert len(fault_scenarios) == 4

    actual_failure_modes = {
        scenario["scenario_id"]: [
            failure["failure_mode"]
            for failure in scenario["actual"]["failures"]
        ]
        for scenario in fault_scenarios
    }

    assert actual_failure_modes == {
        "mech-002-unit-error": ["UNIT_ERROR"],
        "mech-002-incomplete": [
            "INCOMPLETE_DELIVERABLE"
        ],
        "mech-004-revision-error": ["WRONG_REVISION"],
        "mech-005-unit-error": [
            "UNIT_ERROR",
            "FAILURE_TO_VERIFY",
        ],
    }


def test_committed_report_preserves_claim_boundaries() -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")

    assert "harness-verification baseline" in report
    assert (
        "not evidence of AI-model or agent performance"
        in report
    )
    assert "Development cases: 4/4" in report
    assert "Held-out cases: 1/1" in report
    assert "historically seen during case authoring" in report
    assert "not claimed to be a pristine blind test case" in report
    assert "UNIT_ERROR" in report
    assert "INCOMPLETE_DELIVERABLE" in report
    assert "WRONG_REVISION" in report
    assert "FAILURE_TO_VERIFY" in report


def test_baseline_runner_reexecutes_in_isolated_directories(
    tmp_path: Path,
) -> None:
    runs_root = tmp_path / "runs"
    evidence_dir = tmp_path / "evidence"

    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--root",
            str(ROOT),
            "--runs-root",
            str(runs_root),
            "--evidence-dir",
            str(evidence_dir),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    output = completed.stdout + completed.stderr

    assert completed.returncode == 0, output
    assert "Baseline completed successfully." in output

    summary = _load_json(evidence_dir / "summary.json")

    assert summary["metrics"] == EXPECTED_METRICS
    assert len(summary["scenarios"]) == 9
    assert all(
        scenario["expectation_met"]
        for scenario in summary["scenarios"]
    )

    result_paths = list(runs_root.rglob("result.json"))

    assert len(result_paths) == 9
    assert not (
        ROOT
        / "examples"
        / "candidates"
        / "MECH-003"
    ).exists()
