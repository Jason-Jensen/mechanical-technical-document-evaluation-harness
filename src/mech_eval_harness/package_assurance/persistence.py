"""Immutable persistence for canonical v0.3.0 package results."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from mech_eval_harness.package_assurance.result_core import (
    PACKAGE_RESULT_FILENAME,
    PackageResult,
)


_RUN_ID_PATTERN = re.compile(r"^RUN-[0-9]{8}T[0-9]{12}Z-[0-9a-f]{8}$")


class PackageResultPersistenceError(RuntimeError):
    """Raised when a package result cannot be persisted safely."""


class PackageResultCollisionError(PackageResultPersistenceError):
    """Raised when an immutable package run directory already exists."""


class PackageResultSchemaValidationError(PackageResultPersistenceError):
    """Raised when a package result fails its versioned schema."""


def validate_package_result_document(
    document: dict[str, Any],
    schema_path: Path,
) -> None:
    """Validate serialized package-result content before any write."""

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PackageResultSchemaValidationError(
            f"Could not read package-result schema: {schema_path}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise PackageResultSchemaValidationError(
            f"Package-result schema is not valid JSON: {schema_path}"
        ) from exc

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise PackageResultSchemaValidationError(
            f"Package-result schema is invalid: {exc.message}"
        ) from exc

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: "/".join(str(part) for part in error.absolute_path),
    )
    if not errors:
        return

    details: list[str] = []
    for error in errors[:5]:
        location = "/".join(str(part) for part in error.absolute_path) or "<root>"
        details.append(f"{location}: {error.message}")
    raise PackageResultSchemaValidationError(
        "Package result failed schema validation: " + "; ".join(details)
    )


def write_package_result(
    *,
    result: PackageResult,
    runs_dir: Path,
    schema_path: Path,
) -> Path:
    """Write one schema-valid package result without overwriting prior evidence."""

    if _RUN_ID_PATTERN.fullmatch(result.run_id) is None:
        raise PackageResultPersistenceError(
            "run_id must use the format "
            "'RUN-YYYYMMDDTHHMMSSffffffZ-xxxxxxxx'."
        )

    document = result.to_dict()
    validate_package_result_document(document, schema_path)
    try:
        serialized = (
            json.dumps(
                document,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        )
    except (TypeError, ValueError) as exc:
        raise PackageResultPersistenceError(
            "Package result could not be serialized as JSON."
        ) from exc

    resolved_runs_dir = runs_dir.resolve()
    try:
        resolved_runs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PackageResultPersistenceError(
            f"Could not create package runs directory: {resolved_runs_dir}"
        ) from exc

    run_dir = resolved_runs_dir / result.run_id
    try:
        run_dir.mkdir(exist_ok=False)
    except FileExistsError as exc:
        raise PackageResultCollisionError(
            "Package run already exists and will not be overwritten: "
            f"{result.run_id}"
        ) from exc
    except OSError as exc:
        raise PackageResultPersistenceError(
            f"Could not create package run directory: {run_dir}"
        ) from exc

    temporary_path = run_dir / f".{PACKAGE_RESULT_FILENAME}.tmp"
    result_path = run_dir / PACKAGE_RESULT_FILENAME
    try:
        temporary_path.write_text(
            serialized,
            encoding="utf-8",
            newline="\n",
        )
        temporary_path.replace(result_path)
    except OSError as exc:
        shutil.rmtree(run_dir, ignore_errors=True)
        raise PackageResultPersistenceError(
            f"Could not persist package result: {result_path}"
        ) from exc
    return result_path
