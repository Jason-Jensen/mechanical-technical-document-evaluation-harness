"""Command-line interface for repository validation and evaluation."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from mech_eval_harness.evaluation import (
    CheckConfigurationError,
    CheckResult,
    GateResult,
    run_deterministic_checks,
    run_mandatory_gates,
)
from mech_eval_harness.persistence import (
    ResultPersistenceError,
    ResultSchemaValidationError,
    generate_run_id,
    write_result_record,
)
from mech_eval_harness.results import build_evaluation_result
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

try:
    HARNESS_VERSION = version(
        "mechanical-technical-document-evaluation-harness"
    )
except PackageNotFoundError:
    HARNESS_VERSION = "0.2.0"


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
    evaluate_parser.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help=(
            "Directory for immutable run records. "
            "Defaults to <root>/runs."
        ),
    )

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
    runs_dir: Path | None,
) -> int:
    root = root.resolve()
    candidate_path = candidate_path.resolve()
    resolved_runs_dir = (
        runs_dir.resolve()
        if runs_dir is not None
        else (root / "runs").resolve()
    )
    result_schema_path = (
        root / "schemas" / "result.schema.json"
    )

    try:
        loaded_case = load_case_by_id(root, case_id)
    except RepositoryValidationError as exc:
        print(f"ERROR [CONFIGURATION]: {exc}")
        return EXIT_CONFIGURATION_ERROR

    reference_path = (
        root
        / loaded_case.case["reference_dir"]
        / loaded_case.evaluator["reference_file"]
    )

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

        return _complete_evaluation(
            loaded_case=loaded_case,
            candidate_id=None,
            candidate_schema_version=None,
            candidate_path=candidate_path,
            reference_path=reference_path,
            gate_results=gate_results,
            check_results=[],
            scoring_result=scoring_result,
            runs_dir=resolved_runs_dir,
            result_schema_path=result_schema_path,
        )

    try:
        loaded_candidate = load_candidate(
            root,
            candidate_path,
            expected_case_id=case_id,
        )
    except RepositoryValidationError as exc:
        candidate_id, candidate_schema_version = (
            _read_candidate_identity(candidate_path)
        )

        failed_gate_results = [
            *gate_results,
            GateResult(
                gate_id="candidate_schema",
                kind="candidate_schema_valid",
                passed=False,
                failure_mode="INVALID_FILE",
                evidence=str(exc),
            ),
        ]

        try:
            scoring_result = score_evaluation(
                loaded_case.evaluator,
                failed_gate_results,
                [],
            )
        except ScoringConfigurationError as scoring_exc:
            print(f"ERROR [CONFIGURATION]: {scoring_exc}")
            return EXIT_CONFIGURATION_ERROR

        return _complete_evaluation(
            loaded_case=loaded_case,
            candidate_id=candidate_id,
            candidate_schema_version=candidate_schema_version,
            candidate_path=candidate_path,
            reference_path=reference_path,
            gate_results=failed_gate_results,
            check_results=[],
            scoring_result=scoring_result,
            runs_dir=resolved_runs_dir,
            result_schema_path=result_schema_path,
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

    return _complete_evaluation(
        loaded_case=loaded_case,
        candidate_id=(
            loaded_candidate.candidate["candidate_id"]
        ),
        candidate_schema_version=(
            loaded_candidate.candidate["schema_version"]
        ),
        candidate_path=candidate_path,
        reference_path=reference_path,
        gate_results=gate_results,
        check_results=check_results,
        scoring_result=scoring_result,
        runs_dir=resolved_runs_dir,
        result_schema_path=result_schema_path,
    )


def _complete_evaluation(
    *,
    loaded_case,
    candidate_id: str | None,
    candidate_schema_version: str | None,
    candidate_path: Path,
    reference_path: Path,
    gate_results: list[GateResult],
    check_results: list[CheckResult],
    scoring_result: ScoringResult,
    runs_dir: Path,
    result_schema_path: Path,
) -> int:
    created_at = datetime.now(timezone.utc)

    try:
        result = build_evaluation_result(
            run_id=generate_run_id(created_at),
            created_at=created_at,
            harness_version=HARNESS_VERSION,
            loaded_case=loaded_case,
            candidate_id=candidate_id,
            candidate_schema_version=candidate_schema_version,
            candidate_path=candidate_path,
            reference_path=reference_path,
            gate_results=gate_results,
            check_results=check_results,
            scoring_result=scoring_result,
        )

        result_path = write_result_record(
            result=result,
            runs_dir=runs_dir,
            schema_path=result_schema_path,
        )
    except ResultSchemaValidationError as exc:
        print(f"ERROR [CONFIGURATION]: {exc}")
        return EXIT_CONFIGURATION_ERROR
    except ResultPersistenceError as exc:
        print(f"ERROR [INTERNAL]: {exc}")
        return EXIT_INTERNAL_ERROR

    _render_evaluation(
        loaded_case.case["case_id"],
        candidate_path,
        gate_results,
        check_results,
        scoring_result,
    )
    print(f"RESULT RECORD: {result_path}")

    if scoring_result.passed:
        return EXIT_PASS

    return EXIT_EVALUATION_FAILED


def _read_candidate_identity(
    candidate_path: Path,
) -> tuple[str | None, str | None]:
    try:
        candidate = load_json(candidate_path)
    except (RepositoryValidationError, OSError):
        return None, None

    candidate_id = candidate.get("candidate_id")
    schema_version = candidate.get("schema_version")

    if not isinstance(candidate_id, str) or not candidate_id:
        candidate_id = None

    if (
        not isinstance(schema_version, str)
        or not schema_version
    ):
        schema_version = None

    return candidate_id, schema_version


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
                args.runs_dir,
            )

        parser.error(f"Unknown command: {args.command}")
        return EXIT_CONFIGURATION_ERROR

    except RepositoryValidationError as exc:
        print(f"ERROR: {exc}")
        return EXIT_EVALUATION_FAILED

    except Exception as exc:
        print(f"ERROR [INTERNAL]: {exc}")
        return EXIT_INTERNAL_ERROR
