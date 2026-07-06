"""Run the deterministic portfolio demonstration for the MVP harness."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class DemoScenario:
    scenario_id: str
    title: str
    candidate_path: Path
    expected_exit_code: int
    expected_passed: bool
    expected_score: float
    expected_failure_modes: tuple[str, ...]


@dataclass(frozen=True)
class DemoOutcome:
    scenario: DemoScenario
    command: tuple[str, ...]
    stdout: str
    stderr: str
    result_path: Path
    result: dict[str, Any]


SCENARIOS = (
    DemoScenario(
        scenario_id="mech-002-pass",
        title="Passing shaft-power artifact",
        candidate_path=(
            ROOT / "examples" / "candidates" / "MECH-002" / "valid.json"
        ),
        expected_exit_code=0,
        expected_passed=True,
        expected_score=1.0,
        expected_failure_modes=(),
    ),
    DemoScenario(
        scenario_id="mech-002-unit-error",
        title="Shaft-power artifact with an angular-velocity unit error",
        candidate_path=(
            ROOT
            / "examples"
            / "candidates"
            / "MECH-002"
            / "unit-error.json"
        ),
        expected_exit_code=1,
        expected_passed=False,
        expected_score=0.75,
        expected_failure_modes=("UNIT_ERROR",),
    ),
)


class DemoVerificationError(RuntimeError):
    """Raised when the portfolio demonstration does not meet expectations."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run a passing and failing MECH-002 evaluation, verify the "
            "expected CLI/result contracts, and optionally write a Markdown "
            "evidence report."
        )
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=ROOT / "runs" / "portfolio-demo",
        help=(
            "Parent directory for generated immutable run records. "
            "Defaults to runs/portfolio-demo."
        ),
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=None,
        help="Optional Markdown report path.",
    )
    return parser.parse_args(argv)


def _new_result_path(
    *,
    scenario_runs_dir: Path,
    before: set[Path],
) -> Path:
    after = {
        path.resolve()
        for path in scenario_runs_dir.iterdir()
        if path.is_dir()
    }
    created = sorted(after - before)

    if len(created) != 1:
        raise DemoVerificationError(
            f"Expected exactly one new run directory under "
            f"{scenario_runs_dir}, found {len(created)}."
        )

    result_path = created[0] / "result.json"
    if not result_path.is_file():
        raise DemoVerificationError(
            f"Expected result record was not created: {result_path}"
        )

    return result_path


def _verify_outcome(
    *,
    scenario: DemoScenario,
    completed: subprocess.CompletedProcess[str],
    result: dict[str, Any],
) -> None:
    if completed.returncode != scenario.expected_exit_code:
        raise DemoVerificationError(
            f"{scenario.scenario_id}: expected exit code "
            f"{scenario.expected_exit_code}, got {completed.returncode}."
        )

    if result.get("passed") is not scenario.expected_passed:
        raise DemoVerificationError(
            f"{scenario.scenario_id}: expected passed="
            f"{scenario.expected_passed}, got {result.get('passed')}."
        )

    score = result.get("score")
    if not isinstance(score, (int, float)) or not math.isclose(
        float(score),
        scenario.expected_score,
        rel_tol=0.0,
        abs_tol=1e-9,
    ):
        raise DemoVerificationError(
            f"{scenario.scenario_id}: expected score "
            f"{scenario.expected_score}, got {score}."
        )

    failures = result.get("failures")
    if not isinstance(failures, list):
        raise DemoVerificationError(
            f"{scenario.scenario_id}: result failures must be a list."
        )

    actual_modes = tuple(
        sorted(
            failure.get("failure_mode")
            for failure in failures
            if isinstance(failure, dict)
            and isinstance(failure.get("failure_mode"), str)
        )
    )
    expected_modes = tuple(sorted(scenario.expected_failure_modes))

    if actual_modes != expected_modes:
        raise DemoVerificationError(
            f"{scenario.scenario_id}: expected failure modes "
            f"{expected_modes}, got {actual_modes}."
        )

    if "RESULT RECORD:" not in completed.stdout:
        raise DemoVerificationError(
            f"{scenario.scenario_id}: CLI output did not report the "
            "persisted result path."
        )


def run_scenario(
    scenario: DemoScenario,
    *,
    runs_dir: Path,
) -> DemoOutcome:
    scenario_runs_dir = (runs_dir / scenario.scenario_id).resolve()
    scenario_runs_dir.mkdir(parents=True, exist_ok=True)

    before = {
        path.resolve()
        for path in scenario_runs_dir.iterdir()
        if path.is_dir()
    }

    command = (
        sys.executable,
        "-m",
        "mech_eval_harness",
        "evaluate",
        str(ROOT),
        "MECH-002",
        str(scenario.candidate_path),
        "--runs-dir",
        str(scenario_runs_dir),
    )

    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    result_path = _new_result_path(
        scenario_runs_dir=scenario_runs_dir,
        before=before,
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))

    _verify_outcome(
        scenario=scenario,
        completed=completed,
        result=result,
    )

    return DemoOutcome(
        scenario=scenario,
        command=command,
        stdout=completed.stdout,
        stderr=completed.stderr,
        result_path=result_path,
        result=result,
    )


def _relative_or_absolute(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path.resolve())


def render_report(outcomes: list[DemoOutcome]) -> str:
    created_at = datetime.now(timezone.utc).isoformat()

    lines = [
        "# Portfolio Demo Evidence",
        "",
        "## Purpose",
        "",
        (
            "This report verifies the implemented MVP harness using one "
            "passing and one technically defective MECH-002 candidate."
        ),
        "",
        f"- Executed at: `{created_at}`",
        "- Case: `MECH-002`",
        "- Workflow: `WF-SHAFT-POWER`",
        "- Scenarios verified: `2/2`",
        "",
        "## Results",
        "",
        "| Scenario | Expected exit | Score | Result | Failure modes |",
        "|---|---:|---:|---|---|",
    ]

    for outcome in outcomes:
        failures = outcome.result["failures"]
        modes = sorted(
            failure["failure_mode"]
            for failure in failures
        )
        mode_text = ", ".join(modes) if modes else "None"
        result_text = "PASS" if outcome.result["passed"] else "FAIL"

        lines.append(
            f"| `{outcome.scenario.scenario_id}` "
            f"| {outcome.scenario.expected_exit_code} "
            f"| {outcome.result['score']:.2f} "
            f"| {result_text} "
            f"| {mode_text} |"
        )

    lines.extend(
        [
            "",
            "## Immutable result records",
            "",
        ]
    )

    for outcome in outcomes:
        lines.append(
            f"- `{outcome.scenario.scenario_id}`: "
            f"`{_relative_or_absolute(outcome.result_path)}`"
        )

    lines.extend(
        [
            "",
            "## Captured CLI output",
            "",
        ]
    )

    for outcome in outcomes:
        lines.extend(
            [
                f"### {outcome.scenario.title}",
                "",
                "```text",
                outcome.stdout.rstrip(),
            ]
        )
        if outcome.stderr.strip():
            lines.extend(
                [
                    "",
                    "STDERR:",
                    outcome.stderr.rstrip(),
                ]
            )
        lines.extend(["```", ""])

    lines.extend(
        [
            "## Interpretation",
            "",
            (
                "The passing artifact traversed mandatory gates, deterministic "
                "checks, weighted scoring, and immutable result persistence "
                "with exit code 0 and score 1.00."
            ),
            "",
            (
                "The defective artifact remained structurally valid, passed "
                "the mandatory gates, failed the angular-velocity check with "
                "`UNIT_ERROR`, returned exit code 1, scored 0.75, and still "
                "produced an immutable result record."
            ),
            "",
            (
                "This is evidence of harness behaviour. It is not evidence of "
                "AI-model or agent performance, and it does not provide "
                "engineering sign-off."
            ),
            "",
        ]
    )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    runs_dir = args.runs_dir.resolve()

    try:
        outcomes = [
            run_scenario(scenario, runs_dir=runs_dir)
            for scenario in SCENARIOS
        ]
    except (
        DemoVerificationError,
        json.JSONDecodeError,
        OSError,
        KeyError,
        TypeError,
    ) as exc:
        print(f"DEMO ERROR: {exc}")
        return 1

    for outcome in outcomes:
        print("=" * 72)
        print(outcome.scenario.title)
        print("=" * 72)
        print(outcome.stdout.rstrip())
        if outcome.stderr.strip():
            print("STDERR:")
            print(outcome.stderr.rstrip())
        print(
            "VERIFIED RESULT RECORD: "
            f"{outcome.result_path}"
        )
        print()

    if args.report_path is not None:
        report_path = args.report_path.resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            render_report(outcomes),
            encoding="utf-8",
        )
        print(f"DEMO REPORT: {report_path}")

    print("DEMO VERIFIED: 2/2 scenarios")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
