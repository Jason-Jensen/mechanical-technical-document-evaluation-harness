"""Immutable local persistence for structured evaluation results."""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError

from mech_eval_harness.results import EvaluationResultRecord


_RUN_ID_PATTERN = re.compile(
    r"^RUN-[0-9]{8}T[0-9]{12}Z-[0-9a-f]{8}$"
)
_SUFFIX_PATTERN = re.compile(r"^[0-9a-f]{8}$")


class ResultPersistenceError(RuntimeError):
    """Raised when a result record cannot be persisted safely."""


class ResultCollisionError(ResultPersistenceError):
    """Raised when a run directory already exists."""


class ResultSchemaValidationError(ResultPersistenceError):
    """Raised when a result document does not satisfy its schema."""


def generate_run_id(
    created_at: datetime | None = None,
    *,
    unique_suffix: str | None = None,
) -> str:
    """Generate a filesystem-safe UTC run identifier."""

    if created_at is None:
        created_at = datetime.now(timezone.utc)

    if (
        created_at.tzinfo is None
        or created_at.utcoffset() is None
    ):
        raise ResultPersistenceError(
            "Run-ID creation time must be timezone-aware."
        )

    if unique_suffix is None:
        unique_suffix = uuid4().hex[:8]

    if _SUFFIX_PATTERN.fullmatch(unique_suffix) is None:
        raise ResultPersistenceError(
            "Run-ID suffix must contain exactly eight "
            "lowercase hexadecimal characters."
        )

    utc_time = created_at.astimezone(timezone.utc)
    timestamp = utc_time.strftime("%Y%m%dT%H%M%S%fZ")
    run_id = f"RUN-{timestamp}-{unique_suffix}"

    _validate_run_id(run_id)
    return run_id


def validate_result_document(
    document: dict[str, Any],
    schema_path: Path,
) -> None:
    """Validate one serialized result document against its schema."""

    try:
        schema_text = schema_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ResultSchemaValidationError(
            f"Could not read result schema: {schema_path}"
        ) from exc

    try:
        schema = json.loads(schema_text)
    except json.JSONDecodeError as exc:
        raise ResultSchemaValidationError(
            f"Result schema is not valid JSON: {schema_path}"
        ) from exc

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise ResultSchemaValidationError(
            f"Result schema is invalid: {exc.message}"
        ) from exc

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )

    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: "/".join(
            str(part)
            for part in error.absolute_path
        ),
    )

    if not errors:
        return

    details = []

    for error in errors[:5]:
        location = "/".join(
            str(part)
            for part in error.absolute_path
        )
        location = location or "<root>"
        details.append(f"{location}: {error.message}")

    raise ResultSchemaValidationError(
        "Result document failed schema validation: "
        + "; ".join(details)
    )


def write_result_record(
    *,
    result: EvaluationResultRecord,
    runs_dir: Path,
    schema_path: Path,
) -> Path:
    """Write one result to a new run directory without overwriting."""

    _validate_run_id(result.run_id)

    document = result.to_dict()
    validate_result_document(document, schema_path)

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
        raise ResultPersistenceError(
            "Result document could not be serialized as JSON."
        ) from exc

    resolved_runs_dir = runs_dir.resolve()

    try:
        resolved_runs_dir.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as exc:
        raise ResultPersistenceError(
            f"Could not create runs directory: "
            f"{resolved_runs_dir}"
        ) from exc

    run_dir = resolved_runs_dir / result.run_id

    try:
        run_dir.mkdir(exist_ok=False)
    except FileExistsError as exc:
        raise ResultCollisionError(
            f"Run already exists and will not be overwritten: "
            f"{result.run_id}"
        ) from exc
    except OSError as exc:
        raise ResultPersistenceError(
            f"Could not create run directory: {run_dir}"
        ) from exc

    temporary_path = run_dir / ".result.json.tmp"
    result_path = run_dir / "result.json"

    try:
        temporary_path.write_text(
            serialized,
            encoding="utf-8",
            newline="\n",
        )
        temporary_path.replace(result_path)
    except OSError as exc:
        shutil.rmtree(run_dir, ignore_errors=True)
        raise ResultPersistenceError(
            f"Could not persist result record: {result_path}"
        ) from exc

    return result_path


def _validate_run_id(run_id: str) -> None:
    if _RUN_ID_PATTERN.fullmatch(run_id) is None:
        raise ResultPersistenceError(
            "run_id must use the format "
            "'RUN-YYYYMMDDTHHMMSSffffffZ-xxxxxxxx'."
        )
