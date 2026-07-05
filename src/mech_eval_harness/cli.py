"""Command-line interface for repository validation and evaluation."""

from __future__ import annotations

import argparse
from pathlib import Path

from mech_eval_harness.evaluation import (
    CheckConfigurationError,
    CheckResult,
    GateResult,
    run_deterministic_checks,
    run_mandatory_gates,
)
from mech_eval_harness.scoring import (
    ScoringConfigurationError,
    ScoringResult,
    score_evaluation,
)
from mech_eval_harness.validator import (
    RepositoryValidationError,
    load_case_by_id,
    load_candidate,
    load_json,
    validate_repository,
)


EXIT_PASS = 0
EXIT_EVALUATION_FAILED = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_INTERNAL_ERROR = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mech-eval",
        description=(
            "Validate, inspect, and execute mechanical evaluation cases."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate all cases and linked specifications.",
    )
    validate_parser.add_argument("root", type=Path)

    list_parser = subparsers.add_parser(
        "list",
        help="List validated cases.",
    )
    list_parser.add_argument("root", type=Path)

    inspect_parser = subparsers.add_parser(
        "inspect",
        help="Inspect one validated case.",
    )
    inspect_parser.add_argument("root", type=Path)
    inspect_parser.add_argument("case_id")

    evaluate_parser = subparsers.add_parser(
        "evaluate",
        help="Evaluate one candidate artifact against one case.",
    )
    evaluate_parser.add_argument("root", type=Path)
    evaluate_parser.add_argument("case_id")
    evaluate_parser.add_argument("candidate_path", type=Path)

    return parser


def _validate(root: Path) -> int:
    cases = validate_repository(root)

    for loaded in cases:
        print(
            f"PASS {loaded.case['case_id']} | "
            f"{loaded.case['workflow_id']} | {loaded.case['title']}"
        )

    print(f"{len(cases)} case(s) passed repository validation.")
    return EXIT_PASS


def _list(root: Path) -> int:
    cases = validate_repository(root)

    for loaded in cases:
        metadata = loaded.case["metadata"]
        print(
            f"{loaded.case['case_id']} | {loaded.case['workflow_id']} | "
            f"{metadata['difficulty']} | {metadata['dataset_split']} | "
            f"{loaded.case['title']}"
        )

    return EXIT_PASS


def _inspect(root: Path, case_id: str) -> int:
    loaded = load_case_by_id(root, case_id)

    print(f"Case:        {loaded.case['case_id']} - {loaded.case['title']}")
    print(f"Workflow:    {loaded.case['workflow_id']}")
    print(f"Task:        {loaded.task['task_id']}")
    print(f"Environment: {loaded.environment['environment_id']}")
    print(f"Evaluator:   {loaded.evaluator['evaluator_id']}")
    print(f"Deliverable: {loaded.task['deliverable']['filename']}")
    print(f"Inputs:      {len(loaded.task['input_assets'])}")
    print(f"Gates:       {len(loaded.evaluator['gates'])}")
    print(f"Checks:      {len(loaded.evaluator['checks'])}")
    print(
        "Failures:    "
        + ", ".join(loaded.case["metadata"]["failure_modes"])
    )

    return EXIT_PASS


def _evaluate(
    root: Path,
    case_id: str,
    candidate_path: Path,
) -> int:
    root = root.resolve()
    candidate_path = candidate_path.resolve()

    try:
        loaded_case = load_case_by_id(root, case_id)
    except RepositoryValidationError as exc:
        print(f"ERROR [CONFIGURATION]: {exc}")
        return EXIT_CONFIGURATION_ERROR

    try:
        gate_results = run_mandatory_gates(
            candidate_path,
            loaded_case.task,
            loaded_case.evaluator,
        )
    except (KeyError, TypeError, ValueError) as exc:
        print(f"ERROR [CONFIGURATION]: {exc}")
        return EXIT_CONFIGURATION_ERROR

    if not all(result.passed for result in gate_results):
        try:
            scoring_result = score_evaluation(
                loaded_case.evaluator,
                gate_results,
                [],
            )
        except ScoringConfigurationError as exc:
            print(f"ERROR [CONFIGURATION]: {exc}")
            return EXIT_CONFIGURATION_ERROR

        _render_evaluation(
            case_id,
            candidate_path,
            gate_results,
            [],
            scoring_result,
        )
        return EXIT_EVALUATION_FAILED

    try:
        loaded_candidate = load_candidate(
            root,
            candidate_path,
            expected_case_id=case_id,
        )
    except RepositoryValidationError as exc:
        _render_candidate_validation_failure(
            case_id,
            candidate_path,
            gate_results,
            float(loaded_case.evaluator["pass_threshold"]),
            str(exc),
        )
        return EXIT_EVALUATION_FAILED

    reference_path = (
        root
        / loaded_case.case["reference_dir"]
        / loaded_case.evaluator["reference_file"]
    )

    try:
        reference_payload = load_json(reference_path)
        check_results = run_deterministic_checks(
            loaded_candidate.payload,
            reference_payload,
            loaded_case.evaluator,
        )
        scoring_result = score_evaluation(
            loaded_case.evaluator,
            gate_results,
            check_results,
        )
    except (
        RepositoryValidationError,
        CheckConfigurationError,
        ScoringConfigurationError,
        KeyError,
        TypeError,
        ValueError,
        OSError,
    ) as exc:
        print(f"ERROR [CONFIGURATION]: {exc}")
        return EXIT_CONFIGURATION_ERROR

    _render_evaluation(
        case_id,
        candidate_path,
        gate_results,
        check_results,
        scoring_result,
    )

    if scoring_result.passed:
        return EXIT_PASS

    return EXIT_EVALUATION_FAILED


def _render_evaluation(
    case_id: str,
    candidate_path: Path,
    gate_results: list[GateResult],
    check_results: list[CheckResult],
    scoring_result: ScoringResult,
) -> None:
    status = "PASS" if scoring_result.passed else "FAIL"

    print(f"RESULT: {status}")
    print(f"CASE: {case_id}")
    print(f"CANDIDATE: {candidate_path}")
    print(
        f"SCORE: {scoring_result.score:.3f} "
        f"(threshold {scoring_result.pass_threshold:.3f})"
    )

    print("GATES:")
    for result in gate_results:
        result_status = "PASS" if result.passed else "FAIL"
        print(
            f"  {result_status} {result.gate_id} "
            f"[{result.kind}] | {result.evidence}"
        )

    print("CHECKS:")
    if not check_results:
        print("  NOT RUN")
    else:
        for result in check_results:
            result_status = "PASS" if result.passed else "FAIL"
            print(
                f"  {result_status} {result.check_id} "
                f"[{result.kind}] weight={result.weight:.3f} "
                f"| {result.evidence}"
            )

    print("FAILURES:")
    if not scoring_result.failures:
        print("  NONE")
    else:
        for failure in scoring_result.failures:
            weight = (
                ""
                if failure.weight is None
                else f" weight={failure.weight:.3f}"
            )
            print(
                f"  {failure.source.upper()} {failure.item_id} "
                f"| {failure.failure_mode}{weight} "
                f"| {failure.evidence}"
            )


def _render_candidate_validation_failure(
    case_id: str,
    candidate_path: Path,
    gate_results: list[GateResult],
    pass_threshold: float,
    evidence: str,
) -> None:
    print("RESULT: FAIL")
    print(f"CASE: {case_id}")
    print(f"CANDIDATE: {candidate_path}")
    print(f"SCORE: 0.000 (threshold {pass_threshold:.3f})")

    print("GATES:")
    for result in gate_results:
        result_status = "PASS" if result.passed else "FAIL"
        print(
            f"  {result_status} {result.gate_id} "
            f"[{result.kind}] | {result.evidence}"
        )

    print("CHECKS:")
    print("  NOT RUN")
    print("FAILURES:")
    print(
        "  CANDIDATE candidate_validation "
        f"| INVALID_FILE | {evidence}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "validate":
            return _validate(args.root)

        if args.command == "list":
            return _list(args.root)

        if args.command == "inspect":
            return _inspect(args.root, args.case_id)

        if args.command == "evaluate":
            return _evaluate(
                args.root,
                args.case_id,
                args.candidate_path,
            )

        parser.error(f"Unknown command: {args.command}")
        return EXIT_CONFIGURATION_ERROR

    except RepositoryValidationError as exc:
        print(f"ERROR: {exc}")
        return EXIT_EVALUATION_FAILED

    except Exception as exc:
        print(f"ERROR [INTERNAL]: {exc}")
        return EXIT_INTERNAL_ERROR
