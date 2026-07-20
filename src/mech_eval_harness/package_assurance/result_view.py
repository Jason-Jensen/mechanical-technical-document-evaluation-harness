"""Strict package-result loading shared by pure report views."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance.persistence import (
    PackageResultSchemaValidationError,
    validate_package_result_document,
)


class PackageResultViewInputError(RuntimeError):
    """Raised when a package result is not safe to use as a report source."""


def load_package_result_for_reporting(
    result_path: Path,
    schema_path: Path,
) -> dict[str, Any]:
    """Load strict JSON and validate it before any report rendering."""

    try:
        raw = result_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PackageResultViewInputError(
            f"Could not read package result: {result_path}"
        ) from exc

    try:
        document = json.loads(
            raw,
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=_reject_non_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise PackageResultViewInputError(
            f"Package result is not strict JSON: {result_path}"
        ) from exc

    if not isinstance(document, dict):
        raise PackageResultViewInputError(
            "Package result root must be a JSON object."
        )

    try:
        validate_package_result_document(document, schema_path)
    except PackageResultSchemaValidationError as exc:
        raise PackageResultViewInputError(
            f"Package result is not valid for report rendering: {exc}"
        ) from exc
    return document


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"Duplicate JSON object key: {key}")
        document[key] = value
    return document


def _reject_non_json_constant(value: str) -> Any:
    raise ValueError(f"Non-JSON numeric constant: {value}")
