"""Run the controlled P4.1 structured-package development benchmark."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from mech_eval_harness.package_assurance.development_benchmark import (
    DEVELOPMENT_BENCHMARK_DEFINITION,
    DEVELOPMENT_BENCHMARK_OUTPUT_ROOT,
    DevelopmentBenchmarkError,
    development_benchmark_exit_code,
    run_development_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]


def _parse_args() -> argparse.Namespace:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    parser = argparse.ArgumentParser(
        description=(
            "Generate and run the P4.1 development package scenarios twice, "
            "preserve all outputs, and compare exact normalized publications."
        )
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root. Defaults to the script's repository.",
    )
    parser.add_argument(
        "--definition",
        type=Path,
        default=DEVELOPMENT_BENCHMARK_DEFINITION,
        help="Development benchmark definition path, relative to --root.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / DEVELOPMENT_BENCHMARK_OUTPUT_ROOT / timestamp,
        help="New output directory. Existing directories are never overwritten.",
    )
    parser.add_argument(
        "--scenario",
        action="append",
        default=None,
        help="Run one scenario ID. Repeat to select more than one.",
    )
    parser.add_argument(
        "--observe-only",
        action="store_true",
        help=(
            "Record observed outcomes without making a benchmark pass claim. "
            "This cannot update the versioned oracle."
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    try:
        report = run_development_benchmark(
            repository_root=args.root,
            output_root=args.output,
            definition_path=args.definition,
            compare_oracles=not args.observe_only,
            selected_scenario_ids=args.scenario,
        )
    except DevelopmentBenchmarkError as exc:
        print(f"ERROR: {exc}")
        return 2

    print(f"BENCHMARK: {report['benchmark_id']}")
    print(f"REVISION: {report['benchmark_revision']}")
    print(f"MODE: {report['mode']}")
    print(f"STATUS: {report['status']}")
    print(
        "SCENARIOS: "
        f"{report['scenario_pass_count']}/{report['scenario_count']} passed"
    )
    print(f"REPORT: {args.output.resolve() / 'benchmark_report.json'}")
    return development_benchmark_exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
