from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mech_eval_harness.cli import main


BENCHMARK_ID = "MECHANICAL-MVP-V1"

FAULT_SCENARIOS = (
    {
        "scenario_id": "mech-002-unit-error",
        "case_id": "MECH-002",
        "candidate_path": "examples/candidates/MECH-002/unit-error.json",
        "expected_exit_code": 1,
        "expected_score": 0.75,
        "expected_failure_modes": ["UNIT_ERROR"],
    },
    {
        "scenario_id": "mech-002-incomplete",
        "case_id": "MECH-002",
        "candidate_path": "examples/candidates/MECH-002/incomplete.json",
        "expected_exit_code": 1,
        "expected_score": 0.0,
        "expected_failure_modes": ["INCOMPLETE_DELIVERABLE"],
    },
    {
        "scenario_id": "mech-004-revision-error",
        "case_id": "MECH-004",
        "candidate_path": "examples/candidates/MECH-004/revision-error.json",
        "expected_exit_code": 1,
        "expected_score": 0.8,
        "expected_failure_modes": ["WRONG_REVISION"],
    },
    {
        "scenario_id": "mech-005-unit-error",
        "case_id": "MECH-005",
        "candidate_path": "examples/candidates/MECH-005/unit-error.json",
        "expected_exit_code": 1,
        "expected_score": 0.65,
        "expected_failure_modes": [
            "UNIT_ERROR",
            "FAILURE_TO_VERIFY",
        ],
    },
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the Mechanical MVP v1 harness-verification baseline."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Repository root. Defaults to the current directory.",
    )
    parser.add_argument(
        "--runs-root",
        type=Path,
        default=Path("runs/baseline-mvp-v1"),
        help=(
            "Root for immutable raw result records. Relative paths are "
            "resolved under the repository root."
        ),
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("evidence/mvp_v1_baseline"),
        help=(
            "Directory for the normalized summary and Markdown report. "
            "Relative paths are resolved under the repository root."
        ),
    )
    return parser.parse_args()


def _resolve_under_root(root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return root / path


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def _build_oracle_candidate(
    *,
    root: Path,
    case_id: str,
    destination: Path,
) -> dict[str, Any]:
    reference_path = (
        root
        / "cases"
        / case_id
        / "reference"
        / "expected.json"
    )
    payload = _load_json(reference_path)

    candidate = {
        "schema_version": "1.0",
        "case_id": case_id,
        "candidate_id": f"oracle-{case_id.lower()}-001",
        "artifact_type": "structured_engineering_response",
        "artifacts": [],
        "payload": payload,
        "provenance": {
            "producer_type": "human_authored_example",
        },
    }

    _write_json(destination, candidate)
    return candidate


def _find_single_result(runs_dir: Path) -> Path:
    result_paths = sorted(runs_dir.glob("*/result.json"))

    if len(result_paths) != 1:
        raise RuntimeError(
            f"Expected exactly one result.json under {runs_dir}; "
            f"found {len(result_paths)}."
        )

    return result_paths[0]


def _execute_scenario(
    *,
    root: Path,
    run_root: Path,
    scenario_id: str,
    suite: str,
    split: str,
    case_id: str,
    candidate_path: Path,
    candidate_source: str,
    expected_exit_code: int,
    expected_score: float,
    expected_failure_modes: list[str],
) -> dict[str, Any]:
    scenario_runs_dir = run_root / scenario_id

    captured_stdout = io.StringIO()
    with contextlib.redirect_stdout(captured_stdout):
        exit_code = main(
            [
                "evaluate",
                str(root),
                case_id,
                str(candidate_path),
                "--runs-dir",
                str(scenario_runs_dir),
            ]
        )

    result_path = _find_single_result(scenario_runs_dir)
    result = _load_json(result_path)

    actual_failure_modes = [
        failure["failure_mode"]
        for failure in result["failures"]
    ]

    score_matches = abs(
        float(result["score"]) - expected_score
    ) < 1e-12

    expectation_met = (
        exit_code == expected_exit_code
        and score_matches
        and sorted(actual_failure_modes)
        == sorted(expected_failure_modes)
    )

    record = {
        "scenario_id": scenario_id,
        "suite": suite,
        "split": split,
        "case_id": case_id,
        "candidate_id": result["candidate_id"],
        "candidate_source": candidate_source,
        "candidate_sha256": _sha256(candidate_path),
        "expected": {
            "exit_code": expected_exit_code,
            "score": expected_score,
            "failure_modes": expected_failure_modes,
        },
        "actual": {
            "exit_code": exit_code,
            "evaluation_passed": result["passed"],
            "score": result["score"],
            "gate_passed": result.get("gate_passed"),
            "failures": result["failures"],
        },
        "expectation_met": expectation_met,
        "raw_result_record": _relative_or_absolute(
            result_path,
            root,
        ),
    }

    status = "PASS" if expectation_met else "FAIL"
    print(
        f"{status} {scenario_id} | "
        f"case={case_id} | score={result['score']:.3f} | "
        f"evaluation_passed={result['passed']}"
    )

    if not expectation_met:
        print(captured_stdout.getvalue())
        raise RuntimeError(
            f"Baseline expectation failed for {scenario_id}."
        )

    return record


def _build_report(summary: dict[str, Any]) -> str:
    metrics = summary["metrics"]
    scenarios = summary["scenarios"]

    lines = [
        "# Mechanical MVP v1 Baseline Report",
        "",
        "## Purpose",
        "",
        (
            "This is a harness-verification baseline. It demonstrates that "
            "the deterministic evaluators accept reference-equivalent "
            "structured artifacts and reject a small curated set of known "
            "defects. It is not evidence of AI-model or agent performance."
        ),
        "",
        "## Benchmark controls",
        "",
        (
            f"- Benchmark: `{summary['benchmark_id']}`"
        ),
        (
            f"- Executed at: `{summary['executed_at_utc']}`"
        ),
        (
            f"- Development cases: "
            f"{metrics['oracle_development_passed']}/"
            f"{metrics['oracle_development_total']} oracle checks passed"
        ),
        (
            f"- Held-out cases: "
            f"{metrics['oracle_held_out_passed']}/"
            f"{metrics['oracle_held_out_total']} oracle checks passed"
        ),
        (
            f"- Fault injections detected as expected: "
            f"{metrics['fault_scenarios_detected']}/"
            f"{metrics['fault_scenarios_total']}"
        ),
        (
            f"- Raw result records: "
            f"`{summary['raw_runs_root']}`"
        ),
        "",
        "MECH-003 is reported separately as held-out. It was historically "
        "seen during case authoring and is not claimed to be a pristine "
        "blind test case.",
        "",
        "## Oracle verification suite",
        "",
        "| Scenario | Split | Case | Score | Evaluator result |",
        "|---|---|---|---:|---|",
    ]

    for scenario in scenarios:
        if scenario["suite"] != "oracle":
            continue

        actual = scenario["actual"]
        lines.append(
            "| "
            f"`{scenario['scenario_id']}` | "
            f"{scenario['split']} | "
            f"{scenario['case_id']} | "
            f"{float(actual['score']):.2f} | "
            f"{'pass' if actual['evaluation_passed'] else 'fail'} |"
        )

    lines.extend(
        [
            "",
            "## Fault-injection suite",
            "",
            "| Scenario | Case | Score | Failure modes | Expectation |",
            "|---|---|---:|---|---|",
        ]
    )

    for scenario in scenarios:
        if scenario["suite"] != "fault_injection":
            continue

        actual = scenario["actual"]
        failure_modes = ", ".join(
            failure["failure_mode"]
            for failure in actual["failures"]
        )

        lines.append(
            "| "
            f"`{scenario['scenario_id']}` | "
            f"{scenario['case_id']} | "
            f"{float(actual['score']):.2f} | "
            f"{failure_modes} | "
            f"{'met' if scenario['expectation_met'] else 'not met'} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The oracle suite establishes an evaluator-integrity upper "
                "bound: reference-equivalent artifacts can traverse the "
                "candidate contract, deterministic gates, weighted checks, "
                "and immutable result-record path successfully."
            ),
            "",
            (
                "The fault-injection suite demonstrates intended detection "
                "for unit conversion, incomplete deliverable, revision, and "
                "verification failures. The sample is deliberately small "
                "and curated; no statistical generalization is claimed."
            ),
            "",
            "## Limitations",
            "",
            "- No model or agent generated the oracle artifacts.",
            "- Fault coverage is representative, not exhaustive.",
            "- MECH-003 was frozen only after initial authoring and review.",
            "- Engineering outputs still require qualified human review.",
            "",
        ]
    )

    return "\n".join(lines)


def main_entry() -> int:
    args = _parse_args()
    root = args.root.resolve()
    runs_root = _resolve_under_root(root, args.runs_root)
    evidence_dir = _resolve_under_root(root, args.evidence_dir)

    manifest_path = (
        root / "benchmarks" / "mvp_v1" / "split.json"
    )
    manifest = _load_json(manifest_path)

    executed_at = datetime.now(timezone.utc)
    run_id = executed_at.strftime(
        "BASELINE-%Y%m%dT%H%M%SZ"
    )
    run_root = runs_root / run_id
    run_root.mkdir(parents=True, exist_ok=False)

    scenarios: list[dict[str, Any]] = []

    with tempfile.TemporaryDirectory(
        prefix="mvp-v1-oracle-"
    ) as temp_dir_name:
        temp_dir = Path(temp_dir_name)

        for split_name, case_ids in (
            (
                "development",
                manifest["development_case_ids"],
            ),
            (
                "held_out",
                manifest["held_out_case_ids"],
            ),
        ):
            for case_id in case_ids:
                scenario_id = (
                    f"oracle-{split_name}-{case_id.lower()}"
                )
                candidate_path = (
                    temp_dir / f"{scenario_id}.json"
                )
                _build_oracle_candidate(
                    root=root,
                    case_id=case_id,
                    destination=candidate_path,
                )

                scenarios.append(
                    _execute_scenario(
                        root=root,
                        run_root=run_root,
                        scenario_id=scenario_id,
                        suite="oracle",
                        split=split_name,
                        case_id=case_id,
                        candidate_path=candidate_path,
                        candidate_source=(
                            f"cases/{case_id}/reference/expected.json"
                        ),
                        expected_exit_code=0,
                        expected_score=1.0,
                        expected_failure_modes=[],
                    )
                )

    for definition in FAULT_SCENARIOS:
        candidate_path = (
            root / definition["candidate_path"]
        )

        scenarios.append(
            _execute_scenario(
                root=root,
                run_root=run_root,
                scenario_id=definition["scenario_id"],
                suite="fault_injection",
                split="development",
                case_id=definition["case_id"],
                candidate_path=candidate_path,
                candidate_source=definition["candidate_path"],
                expected_exit_code=definition[
                    "expected_exit_code"
                ],
                expected_score=definition["expected_score"],
                expected_failure_modes=definition[
                    "expected_failure_modes"
                ],
            )
        )

    oracle_development = [
        item
        for item in scenarios
        if item["suite"] == "oracle"
        and item["split"] == "development"
    ]
    oracle_held_out = [
        item
        for item in scenarios
        if item["suite"] == "oracle"
        and item["split"] == "held_out"
    ]
    fault_scenarios = [
        item
        for item in scenarios
        if item["suite"] == "fault_injection"
    ]

    summary = {
        "schema_version": "1.0",
        "benchmark_id": BENCHMARK_ID,
        "baseline_type": "harness_verification",
        "executed_at_utc": executed_at.isoformat(),
        "run_id": run_id,
        "split_manifest": _relative_or_absolute(
            manifest_path,
            root,
        ),
        "raw_runs_root": _relative_or_absolute(
            run_root,
            root,
        ),
        "claims": {
            "model_performance_evidence": False,
            "agent_performance_evidence": False,
            "oracle_evaluator_integrity_check": True,
            "curated_fault_detection_check": True,
        },
        "metrics": {
            "oracle_development_total": len(
                oracle_development
            ),
            "oracle_development_passed": sum(
                item["expectation_met"]
                for item in oracle_development
            ),
            "oracle_held_out_total": len(
                oracle_held_out
            ),
            "oracle_held_out_passed": sum(
                item["expectation_met"]
                for item in oracle_held_out
            ),
            "fault_scenarios_total": len(
                fault_scenarios
            ),
            "fault_scenarios_detected": sum(
                item["expectation_met"]
                for item in fault_scenarios
            ),
        },
        "scenarios": scenarios,
    }

    summary_path = evidence_dir / "summary.json"
    report_path = evidence_dir / "report.md"

    _write_json(summary_path, summary)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        _build_report(summary),
        encoding="utf-8",
        newline="\n",
    )

    print()
    print(f"Summary: {summary_path}")
    print(f"Report:  {report_path}")
    print(f"Runs:    {run_root}")
    print("Baseline completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main_entry())
