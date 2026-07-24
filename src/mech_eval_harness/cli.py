"""Command-line interface for repository validation and evaluation."""

from __future__ import annotations

import argparse
import json
import sys
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
from mech_eval_harness.package_assurance.audit import (
    execute_package_audit,
    package_state_exit_code,
)
from mech_eval_harness.package_assurance.public_contract import (
    validate_package_contract,
)
from mech_eval_harness.package_assurance.target_reachability import (
    TargetReachabilityError,
    verify_custodian_target_reachability,
    write_custodian_reachability_reports,
)


EXIT_PASS = 0
EXIT_EVALUATION_FAILED = 1
EXIT_CONFIGURATION_ERROR = 2
EXIT_INTERNAL_ERROR = 3
EXIT_AUDIT_USAGE_ERROR = 64
EXIT_AUDIT_INTERNAL_ERROR = 70

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

    audit_parser = subparsers.add_parser(
        "audit-package",
        help="Run the accepted structured package audit.",
    )
    _configure_audit_package_parser(audit_parser)

    contract_parser = subparsers.add_parser(
        "validate-package-contract",
        help="Validate producer-visible package authoring invariants.",
    )
    contract_parser.add_argument("repository_root", type=Path)
    contract_parser.add_argument("package_directory", type=Path)

    reachability_parser = subparsers.add_parser(
        "verify-target-reachability",
        help="Custodian-only verification of protected target reachability.",
    )
    reachability_parser.add_argument("repository_root", type=Path)
    reachability_parser.add_argument("custody_root", type=Path)
    reachability_parser.add_argument("public_index", type=Path)
    reachability_parser.add_argument("protected_plan", type=Path)
    reachability_parser.add_argument("output_directory", type=Path)

    return parser


class _AuditPackageUsageError(ValueError):
    """Raised instead of exiting for invalid audit-package arguments."""


class _AuditPackageParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise _AuditPackageUsageError(message)


def _configure_audit_package_parser(
    parser: argparse.ArgumentParser,
) -> None:
    parser.add_argument("repository_root", type=Path)
    parser.add_argument("package_directory", type=Path)
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help=(
            "Directory for immutable package audit runs. "
            "Defaults to <repository-root>/runs."
        ),
    )


def _audit_package_main(argv: list[str]) -> int:
    parser = _AuditPackageParser(
        prog="mech-eval audit-package",
        description="Run and atomically publish one structured package audit.",
    )
    _configure_audit_package_parser(parser)
    try:
        args = parser.parse_args(argv)
    except _AuditPackageUsageError as exc:
        parser.print_usage(sys.stderr)
        print(f"ERROR [USAGE]: {exc}", file=sys.stderr)
        return EXIT_AUDIT_USAGE_ERROR

    repository_root = args.repository_root.resolve()
    package_root = args.package_directory.resolve()
    runs_dir = (
        args.runs_dir.resolve()
        if args.runs_dir is not None
        else (repository_root / "runs").resolve()
    )
    usage_error = _audit_path_usage_error(
        repository_root=repository_root,
        package_root=package_root,
        runs_dir=runs_dir,
    )
    if usage_error is not None:
        print(f"ERROR [USAGE]: {usage_error}", file=sys.stderr)
        return EXIT_AUDIT_USAGE_ERROR

    try:
        outcome = execute_package_audit(
            repository_root=repository_root,
            package_root=package_root,
            runs_dir=runs_dir,
            schema_path=(
                repository_root / "schemas" / "package_result.schema.json"
            ),
        )
    except Exception as exc:
        print(f"ERROR [INTERNAL]: {exc}", file=sys.stderr)
        return EXIT_AUDIT_INTERNAL_ERROR

    result = outcome.result
    print(f"RUN ID: {result.run_id}")
    print(f"PACKAGE ID: {result.package_id or 'not established'}")
    print(f"PACKAGE STATE: {result.package_state}")
    print(f"RELEASE HOLD: {'true' if result.release_hold else 'false'}")
    print(f"ISSUE COUNT: {len(result.findings)}")
    print(f"RESULT PATH: {outcome.publication.result_path}")
    return package_state_exit_code(result.package_state)


def _validate_package_contract(
    repository_root: Path,
    package_root: Path,
) -> int:
    repository_root = repository_root.resolve()
    package_root = package_root.resolve()
    if not repository_root.is_dir():
        print(
            f"ERROR [USAGE]: Repository root is not a directory: {repository_root}",
            file=sys.stderr,
        )
        return EXIT_AUDIT_USAGE_ERROR
    if not package_root.is_dir():
        print(
            f"ERROR [USAGE]: Package path is not a directory: {package_root}",
            file=sys.stderr,
        )
        return EXIT_AUDIT_USAGE_ERROR

    validation = validate_package_contract(
        repository_root=repository_root,
        package_root=package_root,
    )
    print(
        json.dumps(
            validation.to_dict(),
            indent=2,
            ensure_ascii=True,
            allow_nan=False,
            sort_keys=True,
        )
    )
    return EXIT_PASS if validation.public_contract_complete else EXIT_EVALUATION_FAILED


def _verify_target_reachability(
    repository_root: Path,
    custody_root: Path,
    public_index_path: Path,
    protected_plan_path: Path,
    output_directory: Path,
) -> int:
    custody_root = custody_root.resolve()
    output_directory = output_directory.resolve()
    if not _path_is_within(output_directory, custody_root):
        print(
            "ERROR [USAGE]: Reachability outputs must stay inside the custody root.",
            file=sys.stderr,
        )
        return EXIT_AUDIT_USAGE_ERROR

    try:
        outcome = verify_custodian_target_reachability(
            repository_root=repository_root,
            custody_root=custody_root,
            public_index_path=public_index_path,
            protected_plan_path=protected_plan_path,
        )
        public_path, protected_path = write_custodian_reachability_reports(
            outcome=outcome,
            output_directory=output_directory,
        )
    except TargetReachabilityError as exc:
        print(f"ERROR [CUSTODY INPUT]: {exc}", file=sys.stderr)
        return EXIT_AUDIT_USAGE_ERROR

    attestation = outcome.public_attestation
    print(f"TARGET REACHABILITY: {str(attestation['status']).upper()}")
    print(f"SCENARIOS: {attestation['scenario_count']}")
    print(
        "REACHABLE TARGETS: "
        f"{attestation['reachable_target_count']}/{attestation['target_count']}"
    )
    print(f"PUBLIC ATTESTATION: {public_path}")
    print(f"PROTECTED DETAIL: {protected_path}")
    return EXIT_PASS if outcome.passed else EXIT_EVALUATION_FAILED


def _audit_path_usage_error(
    *,
    repository_root: Path,
    package_root: Path,
    runs_dir: Path,
) -> str | None:
    if not repository_root.is_dir():
        return f"Repository root is not a directory: {repository_root}"
    if not package_root.is_dir():
        return f"Package path is not a directory: {package_root}"
    if runs_dir.exists() and not runs_dir.is_dir():
        return f"Runs path is not a directory: {runs_dir}"
    if _path_is_within(runs_dir, package_root):
        return "Package audit outputs must be outside the audited package."
    return None


def _path_is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


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
    resolved_argv = list(sys.argv[1:] if argv is None else argv)
    if resolved_argv[:1] == ["audit-package"]:
        return _audit_package_main(resolved_argv[1:])

    parser = build_parser()
    args = parser.parse_args(resolved_argv)

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

        if args.command == "validate-package-contract":
            return _validate_package_contract(
                args.repository_root,
                args.package_directory,
            )

        if args.command == "verify-target-reachability":
            return _verify_target_reachability(
                args.repository_root,
                args.custody_root,
                args.public_index,
                args.protected_plan,
                args.output_directory,
            )

        parser.error(f"Unknown command: {args.command}")
        return EXIT_CONFIGURATION_ERROR

    except RepositoryValidationError as exc:
        print(f"ERROR: {exc}")
        return EXIT_EVALUATION_FAILED

    except Exception as exc:
        print(f"ERROR [INTERNAL]: {exc}")
        return EXIT_INTERNAL_ERROR
