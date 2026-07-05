"""Mandatory gate execution for candidate artifacts."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GateResult:
    """Result from one mandatory pre-scoring gate."""

    gate_id: str
    kind: str
    passed: bool
    failure_mode: str | None
    evidence: str

class CheckConfigurationError(ValueError):
    """Raised when an evaluator check definition cannot be executed safely."""


@dataclass(frozen=True)
class CheckResult:
    """Structured result from one deterministic evaluator check."""

    check_id: str
    kind: str
    passed: bool
    weight: float
    failure_mode: str | None
    actual_path: str
    expected_path: str
    actual: Any
    expected: Any
    evidence: str

def run_mandatory_gates(
    candidate_path: Path,
    task: dict[str, Any],
    evaluator: dict[str, Any],
) -> list[GateResult]:
    """Run mandatory gates in evaluator order.

    Execution stops after the first failed gate because later gates may depend
    on evidence produced by earlier gates.
    """

    results: list[GateResult] = []
    candidate: dict[str, Any] | None = None

    for gate in evaluator["gates"]:
        gate_id = gate["gate_id"]
        kind = gate["kind"]
        failure_mode = gate["failure_mode"]

        if kind == "output_exists":
            result = _run_output_exists_gate(
                candidate_path,
                gate_id=gate_id,
                kind=kind,
                failure_mode=failure_mode,
            )

        elif kind == "valid_json":
            result, candidate = _run_valid_json_gate(
                candidate_path,
                gate_id=gate_id,
                kind=kind,
                failure_mode=failure_mode,
            )

        elif kind == "required_fields_present":
            result = _run_required_fields_gate(
                candidate,
                task,
                gate_id=gate_id,
                kind=kind,
                failure_mode=failure_mode,
            )

        elif kind == "field_types_match":
            result = _run_field_types_gate(
                candidate,
                task,
                gate_id=gate_id,
                kind=kind,
                failure_mode=failure_mode,
            )

        else:
            raise ValueError(f"Unsupported gate kind: {kind}")

        results.append(result)

        if not result.passed:
            break

    return results


def _run_output_exists_gate(
    candidate_path: Path,
    *,
    gate_id: str,
    kind: str,
    failure_mode: str,
) -> GateResult:
    if candidate_path.is_file():
        return _passed(
            gate_id,
            kind,
            f"Candidate file exists: {candidate_path}",
        )

    return _failed(
        gate_id,
        kind,
        failure_mode,
        f"Candidate file does not exist: {candidate_path}",
    )


def _run_valid_json_gate(
    candidate_path: Path,
    *,
    gate_id: str,
    kind: str,
    failure_mode: str,
) -> tuple[GateResult, dict[str, Any] | None]:
    try:
        with candidate_path.open("r", encoding="utf-8") as file:
            candidate = json.load(file)
    except json.JSONDecodeError as exc:
        return (
            _failed(
                gate_id,
                kind,
                failure_mode,
                (
                    f"Invalid JSON at line {exc.lineno}, "
                    f"column {exc.colno}: {exc.msg}"
                ),
            ),
            None,
        )
    except OSError as exc:
        return (
            _failed(
                gate_id,
                kind,
                failure_mode,
                f"Could not read candidate file: {exc}",
            ),
            None,
        )

    if not isinstance(candidate, dict):
        return (
            _failed(
                gate_id,
                kind,
                failure_mode,
                "Top-level JSON value must be an object.",
            ),
            None,
        )

    return (
        _passed(
            gate_id,
            kind,
            "Candidate file contains valid JSON with an object root.",
        ),
        candidate,
    )


def _run_required_fields_gate(
    candidate: dict[str, Any] | None,
    task: dict[str, Any],
    *,
    gate_id: str,
    kind: str,
    failure_mode: str,
) -> GateResult:
    payload = _candidate_payload(candidate)

    if payload is None:
        return _failed(
            gate_id,
            kind,
            failure_mode,
            "Candidate payload must be an object.",
        )

    required_fields = task["deliverable"]["required_fields"]
    missing_fields = [
        field
        for field in required_fields
        if field not in payload
    ]

    if missing_fields:
        return _failed(
            gate_id,
            kind,
            failure_mode,
            (
                "Missing required payload fields: "
                + ", ".join(sorted(missing_fields))
            ),
        )

    return _passed(
        gate_id,
        kind,
        "All required payload fields are present.",
    )


def _run_field_types_gate(
    candidate: dict[str, Any] | None,
    task: dict[str, Any],
    *,
    gate_id: str,
    kind: str,
    failure_mode: str,
) -> GateResult:
    payload = _candidate_payload(candidate)

    if payload is None:
        return _failed(
            gate_id,
            kind,
            failure_mode,
            "Candidate payload must be an object.",
        )

    field_types = task["deliverable"].get("field_types", {})
    mismatches: list[str] = []

    for field, expected_type in field_types.items():
        if field not in payload:
            continue

        value = payload[field]

        if not _matches_declared_type(value, expected_type):
            mismatches.append(
                (
                    f"payload.{field} expected {expected_type}; "
                    f"found {_json_type_name(value)}"
                )
            )

    if mismatches:
        return _failed(
            gate_id,
            kind,
            failure_mode,
            "; ".join(mismatches),
        )

    return _passed(
        gate_id,
        kind,
        "All declared payload field types match.",
    )


def _candidate_payload(
    candidate: dict[str, Any] | None,
) -> dict[str, Any] | None:
    if candidate is None:
        return None

    payload = candidate.get("payload")

    if not isinstance(payload, dict):
        return None

    return payload


def _matches_declared_type(value: Any, expected_type: str) -> bool:
    if expected_type == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    if expected_type == "integer":
        return isinstance(value, int) and not isinstance(value, bool)

    if expected_type == "boolean":
        return isinstance(value, bool)

    if expected_type == "string":
        return isinstance(value, str)

    if expected_type == "array":
        return isinstance(value, list)

    if expected_type == "object":
        return isinstance(value, dict)

    raise ValueError(f"Unsupported declared field type: {expected_type}")


def _json_type_name(value: Any) -> str:
    if value is None:
        return "null"

    if isinstance(value, bool):
        return "boolean"

    if isinstance(value, int):
        return "integer"

    if isinstance(value, float):
        return "number"

    if isinstance(value, str):
        return "string"

    if isinstance(value, list):
        return "array"

    if isinstance(value, dict):
        return "object"

    return type(value).__name__


def _passed(
    gate_id: str,
    kind: str,
    evidence: str,
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        kind=kind,
        passed=True,
        failure_mode=None,
        evidence=evidence,
    )


def _failed(
    gate_id: str,
    kind: str,
    failure_mode: str,
    evidence: str,
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        kind=kind,
        passed=False,
        failure_mode=failure_mode,
        evidence=evidence,
    )

_SUPPORTED_NON_NUMERIC_CHECKS = {
    "exact_match",
    "boolean_equals",
    "set_equals",
    "contains_all",
}

_REQUIRED_CHECK_FIELDS = {
    "check_id",
    "kind",
    "actual_path",
    "expected_path",
    "weight",
    "failure_mode",
}


def run_deterministic_checks(
    candidate_payload: dict[str, Any],
    reference_payload: dict[str, Any],
    evaluator: dict[str, Any],
) -> list[CheckResult]:
    """Execute evaluator checks in their declared order.

    Candidate and reference files must already have been loaded and validated.
    This function performs comparison only.
    """

    checks = evaluator.get("checks")

    if not isinstance(checks, list):
        raise CheckConfigurationError(
            "Evaluator 'checks' must be an array."
        )

    results: list[CheckResult] = []

    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise CheckConfigurationError(
                f"Check at index {index} must be an object."
            )

        results.append(
            _run_deterministic_check(
                candidate_payload,
                reference_payload,
                check,
                index=index,
            )
        )

    return results


def _run_deterministic_check(
    candidate_payload: dict[str, Any],
    reference_payload: dict[str, Any],
    check: dict[str, Any],
    *,
    index: int,
) -> CheckResult:
    missing_fields = sorted(_REQUIRED_CHECK_FIELDS - check.keys())

    if missing_fields:
        raise CheckConfigurationError(
            (
                f"Check at index {index} is missing required fields: "
                + ", ".join(missing_fields)
            )
        )

    check_id = check["check_id"]
    kind = check["kind"]
    actual_path = check["actual_path"]
    expected_path = check["expected_path"]
    weight = check["weight"]
    failure_mode = check["failure_mode"]

    for field_name, value in (
        ("check_id", check_id),
        ("kind", kind),
        ("actual_path", actual_path),
        ("expected_path", expected_path),
        ("failure_mode", failure_mode),
    ):
        if not isinstance(value, str) or not value:
            raise CheckConfigurationError(
                (
                    f"Check at index {index} has an invalid "
                    f"'{field_name}' value."
                )
            )

    if (
        not isinstance(weight, (int, float))
        or isinstance(weight, bool)
        or weight <= 0
    ):
        raise CheckConfigurationError(
            f"Check '{check_id}' has an invalid weight."
        )

    if kind not in _SUPPORTED_NON_NUMERIC_CHECKS:
        raise CheckConfigurationError(
            (
                f"Check '{check_id}' uses unsupported kind '{kind}'. "
                "Numeric checks are implemented in WBS 1.4."
            )
        )

    expected_found, expected = _resolve_value_path(
        reference_payload,
        expected_path,
    )

    if not expected_found:
        raise CheckConfigurationError(
            (
                f"Check '{check_id}' expected path "
                f"'{expected_path}' was not found in the reference."
            )
        )

    actual_found, actual = _resolve_value_path(
        candidate_payload,
        actual_path,
    )

    if not actual_found:
        return _build_check_result(
            check_id=check_id,
            kind=kind,
            passed=False,
            weight=float(weight),
            failure_mode=failure_mode,
            actual_path=actual_path,
            expected_path=expected_path,
            actual=None,
            expected=expected,
            evidence=(
                f"Actual path '{actual_path}' was not found "
                "in the candidate payload."
            ),
        )

    if kind == "exact_match":
        passed = _json_identity(actual) == _json_identity(expected)

        if passed:
            evidence = "Actual value matches expected value."
        else:
            evidence = (
                f"Expected {_display_json(expected)} from "
                f"'{expected_path}'; found {_display_json(actual)} "
                f"at '{actual_path}'."
            )

    elif kind == "boolean_equals":
        if not isinstance(expected, bool):
            raise CheckConfigurationError(
                (
                    f"Check '{check_id}' expected value must be "
                    "a Boolean."
                )
            )

        passed = isinstance(actual, bool) and actual == expected

        if passed:
            evidence = "Actual Boolean matches expected Boolean."
        elif not isinstance(actual, bool):
            evidence = (
                f"Expected a Boolean at '{actual_path}'; "
                f"found {_json_type_name(actual)}."
            )
        else:
            evidence = (
                f"Expected {_display_json(expected)}; "
                f"found {_display_json(actual)}."
            )

    elif kind == "set_equals":
        if not isinstance(expected, list):
            raise CheckConfigurationError(
                (
                    f"Check '{check_id}' expected value must be "
                    "an array."
                )
            )

        if not isinstance(actual, list):
            passed = False
            evidence = (
                f"Expected an array at '{actual_path}'; "
                f"found {_json_type_name(actual)}."
            )
        else:
            missing = _collection_difference(expected, actual)
            unexpected = _collection_difference(actual, expected)
            passed = not missing and not unexpected

            if passed:
                evidence = (
                    "Actual and expected sets match; "
                    "order and duplicate count were ignored."
                )
            else:
                evidence = (
                    f"Missing items: {_display_json(missing)}; "
                    f"unexpected items: {_display_json(unexpected)}."
                )

    else:
        if not isinstance(expected, list):
            raise CheckConfigurationError(
                (
                    f"Check '{check_id}' expected value must be "
                    "an array."
                )
            )

        if not isinstance(actual, list):
            passed = False
            evidence = (
                f"Expected an array at '{actual_path}'; "
                f"found {_json_type_name(actual)}."
            )
        else:
            missing = _collection_difference(expected, actual)
            passed = not missing

            if passed:
                evidence = (
                    "Actual collection contains every required item."
                )
            else:
                evidence = (
                    "Candidate collection is missing required items: "
                    f"{_display_json(missing)}."
                )

    return _build_check_result(
        check_id=check_id,
        kind=kind,
        passed=passed,
        weight=float(weight),
        failure_mode=failure_mode,
        actual_path=actual_path,
        expected_path=expected_path,
        actual=actual,
        expected=expected,
        evidence=evidence,
    )


def _resolve_value_path(
    document: dict[str, Any],
    path: str,
) -> tuple[bool, Any]:
    if not path.startswith("$."):
        return False, None

    current: Any = document

    for segment in path[2:].split("."):
        if not isinstance(current, dict) or segment not in current:
            return False, None

        current = current[segment]

    return True, current


def _json_identity(value: Any) -> str:
    return (
        f"{_json_type_name(value)}:"
        + json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
    )


def _collection_difference(
    left: list[Any],
    right: list[Any],
) -> list[Any]:
    right_identities = {
        _json_identity(item)
        for item in right
    }

    difference: list[Any] = []
    seen: set[str] = set()

    for item in left:
        identity = _json_identity(item)

        if identity not in right_identities and identity not in seen:
            difference.append(item)
            seen.add(identity)

    return difference


def _display_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        ensure_ascii=False,
    )


def _build_check_result(
    *,
    check_id: str,
    kind: str,
    passed: bool,
    weight: float,
    failure_mode: str,
    actual_path: str,
    expected_path: str,
    actual: Any,
    expected: Any,
    evidence: str,
) -> CheckResult:
    return CheckResult(
        check_id=check_id,
        kind=kind,
        passed=passed,
        weight=weight,
        failure_mode=None if passed else failure_mode,
        actual_path=actual_path,
        expected_path=expected_path,
        actual=actual,
        expected=expected,
        evidence=evidence,
    )