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