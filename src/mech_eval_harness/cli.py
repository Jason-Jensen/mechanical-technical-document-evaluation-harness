"""Command-line interface for Month 1 repository validation."""

from __future__ import annotations

import argparse
from pathlib import Path

from mech_eval_harness.validator import (
    RepositoryValidationError,
    load_case_by_id,
    validate_repository,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mech-eval",
        description="Validate and inspect mechanical evaluation-case specifications.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser(
        "validate", help="Validate all cases and linked specifications."
    )
    validate_parser.add_argument("root", type=Path)

    list_parser = subparsers.add_parser(
        "list", help="List validated cases."
    )
    list_parser.add_argument("root", type=Path)

    inspect_parser = subparsers.add_parser(
        "inspect", help="Inspect one validated case."
    )
    inspect_parser.add_argument("root", type=Path)
    inspect_parser.add_argument("case_id")

    return parser


def _validate(root: Path) -> int:
    cases = validate_repository(root)
    for loaded in cases:
        print(
            f"PASS {loaded.case['case_id']} | "
            f"{loaded.case['workflow_id']} | {loaded.case['title']}"
        )
    print(f"{len(cases)} case(s) passed repository validation.")
    return 0


def _list(root: Path) -> int:
    cases = validate_repository(root)
    for loaded in cases:
        metadata = loaded.case["metadata"]
        print(
            f"{loaded.case['case_id']} | {loaded.case['workflow_id']} | "
            f"{metadata['difficulty']} | {metadata['dataset_split']} | "
            f"{loaded.case['title']}"
        )
    return 0


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
    return 0

    raise RepositoryValidationError(f"Unknown case_id: {case_id}")


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
    except RepositoryValidationError as exc:
        print(f"ERROR: {exc}")
        return 1

    parser.error(f"Unknown command: {args.command}")
    return 2
