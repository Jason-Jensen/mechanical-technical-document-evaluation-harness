"""Repository validation for evaluation specifications and case assets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


class RepositoryValidationError(ValueError):
    """Raised when a specification repository is invalid."""


@dataclass(frozen=True)
class LoadedCase:
    case: dict[str, Any]
    task: dict[str, Any]
    environment: dict[str, Any]
    evaluator: dict[str, Any]
    case_path: Path

@dataclass(frozen=True)
class LoadedCandidate:
    candidate: dict[str, Any]
    candidate_path: Path

    @property
    def payload(self) -> dict[str, Any]:
        return self.candidate["payload"]

SCHEMA_FILES = {
    "case": "schemas/case.schema.json",
    "task": "schemas/task.schema.json",
    "environment": "schemas/environment.schema.json",
    "evaluator": "schemas/evaluator.schema.json",
}

CANDIDATE_SCHEMA_FILE = "schemas/candidate.schema.json"

def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)
    except FileNotFoundError as exc:
        raise RepositoryValidationError(f"File not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RepositoryValidationError(
            f"Invalid JSON in {path} at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc

    if not isinstance(value, dict):
        raise RepositoryValidationError(f"Top-level JSON value must be an object: {path}")
    return value

def load_candidate(
    root: Path,
    candidate_path: Path,
    *,
    expected_case_id: str | None = None,
) -> LoadedCandidate:
    root = root.resolve()
    candidate_path = candidate_path.resolve()

    candidate = load_json(candidate_path)

    schema_path = _safe_resolve(root, CANDIDATE_SCHEMA_FILE)
    schema = load_json(schema_path)

    try:
        relative_candidate_path = candidate_path.relative_to(root)
        label = str(relative_candidate_path)
    except ValueError:
        label = str(candidate_path)

    _validate_schema(candidate, schema, label)

    if (
        expected_case_id is not None
        and candidate["case_id"] != expected_case_id
    ):
        raise RepositoryValidationError(
            f"candidate case_id {candidate['case_id']} does not match "
            f"expected case_id {expected_case_id}"
        )

    return LoadedCandidate(
        candidate=candidate,
        candidate_path=candidate_path,
    )

def _validate_schema(data: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if not errors:
        return

    messages: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        messages.append(f"{label}:{location}: {error.message}")
    raise RepositoryValidationError("; ".join(messages))


def _safe_resolve(root: Path, relative_path: str) -> Path:
    candidate = (root / relative_path).resolve()
    root_resolved = root.resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError as exc:
        raise RepositoryValidationError(
            f"Path escapes repository root: {relative_path}"
        ) from exc
    return candidate


def _require_unique(items: list[dict[str, Any]], key: str, label: str) -> None:
    values = [item[key] for item in items]
    if len(values) != len(set(values)):
        raise RepositoryValidationError(f"{label} values must be unique")


def _validate_evaluator_rules(evaluator: dict[str, Any]) -> None:
    _require_unique(evaluator["gates"], "gate_id", "gate_id")
    _require_unique(evaluator["checks"], "check_id", "check_id")

    weight_sum = sum(check["weight"] for check in evaluator["checks"])
    if abs(weight_sum - 1.0) > 1e-9:
        raise RepositoryValidationError(
            f"evaluator check weights must sum to 1.0; found {weight_sum:.12f}"
        )

    for check in evaluator["checks"]:
        if check["kind"] == "numeric_close" and "absolute_tolerance" not in check:
            raise RepositoryValidationError(
                f"numeric_close check requires absolute_tolerance: {check['check_id']}"
            )


def discover_case_files(root: Path) -> list[Path]:
    return sorted(root.glob("cases/MECH-*/case.json"))

def load_case_by_id(root: Path, case_id: str) -> LoadedCase:
    root = root.resolve()

    for case_path in discover_case_files(root):
        if case_path.parent.name == case_id:
            return load_case(root, case_path)

    raise RepositoryValidationError(f"Unknown case_id: {case_id}")

def load_case(root: Path, case_path: Path) -> LoadedCase:
    schemas = {
        name: load_json(_safe_resolve(root, rel_path))
        for name, rel_path in SCHEMA_FILES.items()
    }

    case = load_json(case_path)
    _validate_schema(case, schemas["case"], str(case_path.relative_to(root)))

    task_path = _safe_resolve(root, case["task_spec"])
    environment_path = _safe_resolve(root, case["environment_spec"])
    evaluator_path = _safe_resolve(root, case["evaluator_spec"])

    task = load_json(task_path)
    environment = load_json(environment_path)
    evaluator = load_json(evaluator_path)

    _validate_schema(task, schemas["task"], case["task_spec"])
    _validate_schema(environment, schemas["environment"], case["environment_spec"])
    _validate_schema(evaluator, schemas["evaluator"], case["evaluator_spec"])
    _validate_evaluator_rules(evaluator)

    if case["workflow_id"] != task["workflow_id"]:
        raise RepositoryValidationError(
            f"{case['case_id']}: workflow_id differs between case and task"
        )
    if case["workflow_id"] != evaluator["workflow_id"]:
        raise RepositoryValidationError(
            f"{case['case_id']}: workflow_id differs between case and evaluator"
        )

    input_dir = _safe_resolve(root, case["input_dir"])
    reference_dir = _safe_resolve(root, case["reference_dir"])
    if not input_dir.is_dir():
        raise RepositoryValidationError(f"Input directory not found: {case['input_dir']}")
    if not reference_dir.is_dir():
        raise RepositoryValidationError(
            f"Reference directory not found: {case['reference_dir']}"
        )

    for asset in task["input_assets"]:
        asset_path = _safe_resolve(input_dir, asset["path"])
        if not asset_path.is_file():
            raise RepositoryValidationError(
                f"{case['case_id']}: missing input asset: {asset['path']}"
            )

    reference_file = _safe_resolve(reference_dir, evaluator["reference_file"])
    if not reference_file.is_file():
        raise RepositoryValidationError(
            f"{case['case_id']}: missing reference file: {evaluator['reference_file']}"
        )
    load_json(reference_file)

    return LoadedCase(
        case=case,
        task=task,
        environment=environment,
        evaluator=evaluator,
        case_path=case_path,
    )


def validate_repository(root: Path) -> list[LoadedCase]:
    root = root.resolve()
    case_files = discover_case_files(root)
    if not case_files:
        raise RepositoryValidationError(f"No cases found under: {root / 'cases'}")

    loaded = [load_case(root, path) for path in case_files]

    case_ids = [item.case["case_id"] for item in loaded]
    if len(case_ids) != len(set(case_ids)):
        raise RepositoryValidationError("case_id values must be unique")

    return loaded
