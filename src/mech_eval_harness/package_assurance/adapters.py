"""Structured JSON and CSV adapters for the v0.3.0 pilot sources."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping

from mech_eval_harness.package_assurance.manifest import LoadedPackageManifest
from mech_eval_harness.package_assurance.models import (
    LoadedStructuredSources,
    SourceLoadError,
    StructuredSourceRecord,
)


SUPPORTED_JSON_SOURCE_SCHEMA_VERSIONS = frozenset(
    {"0.3.0-fixture-example"}
)


@dataclass(frozen=True)
class SourceLoadOutcome:
    """Successful source records plus every controlled load/parse error."""

    sources: LoadedStructuredSources
    errors: tuple[SourceLoadError, ...]


@dataclass(frozen=True)
class _CsvSourceSpec:
    record_type: str
    required_fields: tuple[str, ...]
    row_key: str
    converters: Mapping[str, Callable[[str], Any]]


_CSV_SOURCE_SPECS = {
    "drawing_register": _CsvSourceSpec(
        record_type="drawing_register_record",
        required_fields=(
            "document_id",
            "drawing_number",
            "title",
            "revision_id",
            "revision_scheme",
            "document_status",
            "discipline",
            "owner",
            "required_for_release",
            "file_ref_id",
        ),
        row_key="document_id",
        converters={"required_for_release": lambda value: _parse_bool(value)},
    ),
    "bom_or_equipment_list": _CsvSourceSpec(
        record_type="equipment_item",
        required_fields=(
            "item_id",
            "equipment_tag",
            "item_type",
            "description",
            "quantity",
            "quantity_unit",
            "part_or_material_id",
            "drawing_number",
            "datasheet_id",
            "specification_id",
            "required_for_release",
        ),
        row_key="item_id",
        converters={
            "quantity": lambda value: _parse_decimal(value),
            "required_for_release": lambda value: _parse_bool(value),
        },
    ),
    "revision_history": _CsvSourceSpec(
        record_type="revision_history_record",
        required_fields=(
            "revision_record_id",
            "document_id",
            "owner_identifier_type",
            "owner_identifier",
            "revision_id",
            "revision_scheme",
            "sequence_index",
            "revision_status",
            "release_status",
            "effective_date",
        ),
        row_key="revision_record_id",
        converters={
            "sequence_index": lambda value: _parse_positive_integer(value),
            "effective_date": lambda value: _parse_date(value),
        },
    ),
}

_JSON_RECORD_SPECS: dict[
    str,
    tuple[tuple[str, str, tuple[str, ...]], ...],
] = {
    "drawing_metadata": (
        (
            "records",
            "drawing_metadata_record",
            (
                "record_id",
                "document_id",
                "drawing_number",
                "title",
                "revision_id",
                "revision_scheme",
                "document_status",
                "discipline",
                "owner",
                "equipment_tags",
                "required_for_release",
                "file_ref_id",
            ),
        ),
    ),
    "datasheet_spec_metadata": (
        (
            "datasheets",
            "datasheet_record",
            (
                "record_id",
                "document_id",
                "datasheet_id",
                "equipment_tag",
                "title",
                "revision_id",
                "revision_scheme",
                "revision_sequence",
                "document_status",
                "required_for_release",
                "file_ref_id",
            ),
        ),
        (
            "specifications",
            "specification_record",
            (
                "record_id",
                "document_id",
                "specification_id",
                "equipment_tags",
                "title",
                "revision_id",
                "revision_scheme",
                "revision_sequence",
                "document_status",
                "required_for_release",
                "file_ref_id",
            ),
        ),
    ),
}


def load_structured_sources(manifest: LoadedPackageManifest) -> SourceLoadOutcome:
    """Load every declared source without raising pre-result parse exceptions."""

    records: list[StructuredSourceRecord] = []
    errors: list[SourceLoadError] = []
    documents: dict[str, Mapping[str, Any]] = {
        "package_manifest": manifest.manifest,
    }

    declaration_by_type = {
        declaration["source_type"]: declaration
        for declaration in manifest.manifest["source_inventory"]
    }
    for source_type in declaration_by_type:
        if source_type == "package_manifest":
            continue

        declaration = declaration_by_type[source_type]
        source_file = declaration["path"]
        source_format = declaration["format"]
        source_path = manifest.source_paths[source_type]

        if not source_path.is_file():
            errors.append(
                SourceLoadError(
                    source_type=source_type,
                    source_file=source_file,
                    format=source_format,
                    code="SOURCE_FILE_MISSING",
                    message=f"Required source file is missing: {source_file}",
                )
            )
            continue

        if source_format == "csv":
            source_records, source_errors = _load_csv_source(
                source_type=source_type,
                source_file=source_file,
                source_path=source_path,
                schema_version=manifest.manifest["schema_version"],
            )
            records.extend(source_records)
            errors.extend(source_errors)
            continue

        document, source_records, source_errors = _load_json_source(
            source_type=source_type,
            source_file=source_file,
            source_path=source_path,
        )
        if document is not None:
            documents[source_type] = document
        records.extend(source_records)
        errors.extend(source_errors)

    return SourceLoadOutcome(
        sources=LoadedStructuredSources(
            records=tuple(records),
            documents=MappingProxyType(documents),
        ),
        errors=tuple(errors),
    )


def _load_csv_source(
    *,
    source_type: str,
    source_file: str,
    source_path: Path,
    schema_version: str,
) -> tuple[list[StructuredSourceRecord], list[SourceLoadError]]:
    spec = _CSV_SOURCE_SPECS.get(source_type)
    if spec is None:
        return [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_PROFILE_UNSUPPORTED",
                message=f"No v0.3.0 CSV adapter is declared for {source_type}",
            )
        ]

    try:
        with source_path.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle, strict=True))
    except UnicodeError:
        return [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_ENCODING_INVALID",
                message=f"Required CSV source is not valid UTF-8: {source_file}",
            )
        ]
    except (OSError, csv.Error) as exc:
        detail = str(exc) if isinstance(exc, csv.Error) else exc.strerror
        return [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_PARSE_FAILED",
                message=(
                    "Required CSV source could not be parsed: "
                    f"{detail or type(exc).__name__}"
                ),
            )
        ]

    if not rows:
        return [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_HEADER_MISSING",
                message=f"Required CSV source has no header row: {source_file}",
            )
        ]

    header = rows[0]
    header_errors: list[SourceLoadError] = []
    if any(not name for name in header):
        header_errors.append(
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_HEADER_INVALID",
                message="CSV header names must be non-empty",
                row_number=1,
            )
        )
    if len(header) != len(set(header)):
        header_errors.append(
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_HEADER_DUPLICATE",
                message="CSV header names must be unique",
                row_number=1,
            )
        )
    missing_headers = sorted(set(spec.required_fields) - set(header))
    if missing_headers:
        header_errors.append(
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="csv",
                code="SOURCE_HEADER_INCOMPLETE",
                message=(
                    "CSV source is missing required headers: "
                    + ", ".join(missing_headers)
                ),
                row_number=1,
            )
        )
    if header_errors:
        return [], header_errors

    records: list[StructuredSourceRecord] = []
    errors: list[SourceLoadError] = []
    for row_number, row in enumerate(rows[1:], start=2):
        if not row or all(value == "" for value in row):
            continue
        if len(row) != len(header):
            errors.append(
                SourceLoadError(
                    source_type=source_type,
                    source_file=source_file,
                    format="csv",
                    code="SOURCE_ROW_WIDTH_INVALID",
                    message=(
                        f"CSV row {row_number} has {len(row)} values; "
                        f"expected {len(header)}"
                    ),
                    row_number=row_number,
                )
            )
            continue

        original = dict(zip(header, row, strict=True))
        parsed: dict[str, Any] = dict(original)
        row_valid = True
        for field_name, converter in spec.converters.items():
            try:
                parsed[field_name] = converter(original[field_name])
            except ValueError as exc:
                row_valid = False
                errors.append(
                    SourceLoadError(
                        source_type=source_type,
                        source_file=source_file,
                        format="csv",
                        code="SOURCE_VALUE_INVALID",
                        message=(
                            f"CSV row {row_number} column {field_name}: {exc}"
                        ),
                        row_number=row_number,
                        column_name=field_name,
                    )
                )
        if not row_valid:
            continue

        records.append(
            StructuredSourceRecord(
                source_type=source_type,
                record_type=spec.record_type,
                source_file=source_file,
                format="csv",
                schema_version=schema_version,
                original_values=MappingProxyType(original),
                values=MappingProxyType(parsed),
                row_number=row_number,
                header_row_number=1,
                row_key_name=spec.row_key,
                row_key_value=original.get(spec.row_key),
            )
        )

    return records, errors


def _load_json_source(
    *,
    source_type: str,
    source_file: str,
    source_path: Path,
) -> tuple[
    Mapping[str, Any] | None,
    list[StructuredSourceRecord],
    list[SourceLoadError],
]:
    try:
        with source_path.open("r", encoding="utf-8") as handle:
            document = json.load(handle)
    except UnicodeError:
        return None, [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_ENCODING_INVALID",
                message=f"Required JSON source is not valid UTF-8: {source_file}",
            )
        ]
    except json.JSONDecodeError as exc:
        return None, [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_PARSE_FAILED",
                message=(
                    f"Invalid JSON at line {exc.lineno}, column {exc.colno}: "
                    f"{exc.msg}"
                ),
                json_pointer="",
            )
        ]
    except OSError as exc:
        return None, [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_READ_FAILED",
                message=(
                    "Required JSON source could not be read: "
                    f"{exc.strerror or type(exc).__name__}"
                ),
            )
        ]

    if not isinstance(document, dict):
        return None, [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_ROOT_INVALID",
                message="Required JSON source must contain an object root",
                json_pointer="",
            )
        ]

    if source_type == "authority_map":
        return MappingProxyType(document), [], []

    record_specs = _JSON_RECORD_SPECS.get(source_type)
    if record_specs is None:
        return MappingProxyType(document), [], [
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_PROFILE_UNSUPPORTED",
                message=f"No v0.3.0 JSON adapter is declared for {source_type}",
                json_pointer="",
            )
        ]

    errors: list[SourceLoadError] = []
    schema_version = document.get("schema_version")
    if not isinstance(schema_version, str) or not schema_version:
        errors.append(
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_SCHEMA_VERSION_MISSING",
                message="JSON source must declare a non-empty schema_version",
                json_pointer="/schema_version",
            )
        )
        schema_version = "<missing>"
    elif schema_version not in SUPPORTED_JSON_SOURCE_SCHEMA_VERSIONS:
        expected_versions = ", ".join(
            sorted(SUPPORTED_JSON_SOURCE_SCHEMA_VERSIONS)
        )
        errors.append(
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_SCHEMA_VERSION_UNSUPPORTED",
                message=(
                    f"JSON source schema_version {schema_version!r} is unsupported; "
                    f"expected one of: {expected_versions}"
                ),
                json_pointer="/schema_version",
            )
        )
    if document.get("source_type") != source_type:
        errors.append(
            SourceLoadError(
                source_type=source_type,
                source_file=source_file,
                format="json",
                code="SOURCE_TYPE_MISMATCH",
                message=f"JSON source_type must equal {source_type}",
                json_pointer="/source_type",
            )
        )

    records: list[StructuredSourceRecord] = []
    for collection_name, record_type, required_fields in record_specs:
        collection = document.get(collection_name)
        if not isinstance(collection, list):
            errors.append(
                SourceLoadError(
                    source_type=source_type,
                    source_file=source_file,
                    format="json",
                    code="SOURCE_RECORD_COLLECTION_INVALID",
                    message=f"JSON property {collection_name} must be an array",
                    json_pointer=f"/{collection_name}",
                )
            )
            continue

        for index, record in enumerate(collection):
            pointer = f"/{collection_name}/{index}"
            if not isinstance(record, dict):
                errors.append(
                    SourceLoadError(
                        source_type=source_type,
                        source_file=source_file,
                        format="json",
                        code="SOURCE_RECORD_INVALID",
                        message=f"JSON record at {pointer} must be an object",
                        json_pointer=pointer,
                    )
                )
                continue

            missing = sorted(set(required_fields) - set(record))
            if missing:
                errors.append(
                    SourceLoadError(
                        source_type=source_type,
                        source_file=source_file,
                        format="json",
                        code="SOURCE_RECORD_INCOMPLETE",
                        message=(
                            f"JSON record at {pointer} is missing required fields: "
                            + ", ".join(missing)
                        ),
                        json_pointer=pointer,
                    )
                )
                continue

            type_errors = _json_record_type_errors(record)
            if type_errors:
                errors.extend(
                    SourceLoadError(
                        source_type=source_type,
                        source_file=source_file,
                        format="json",
                        code="SOURCE_VALUE_INVALID",
                        message=f"JSON record at {pointer}: {message}",
                        json_pointer=f"{pointer}/{field_name}",
                        column_name=field_name,
                    )
                    for field_name, message in type_errors
                )
                continue

            records.append(
                StructuredSourceRecord(
                    source_type=source_type,
                    record_type=record_type,
                    source_file=source_file,
                    format="json",
                    schema_version=schema_version,
                    original_values=MappingProxyType(dict(record)),
                    values=MappingProxyType(dict(record)),
                    json_pointer=pointer,
                    record_id=record["record_id"],
                )
            )

    return MappingProxyType(document), records, errors


def _json_record_type_errors(record: Mapping[str, Any]) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    for field_name in (
        "record_id",
        "document_id",
        "drawing_number",
        "datasheet_id",
        "specification_id",
        "equipment_tag",
        "title",
        "revision_id",
        "revision_scheme",
        "document_status",
        "discipline",
        "owner",
        "file_ref_id",
    ):
        if field_name in record and not isinstance(record[field_name], str):
            errors.append((field_name, "value must be a string"))

    if "required_for_release" in record and not isinstance(
        record["required_for_release"], bool
    ):
        errors.append(("required_for_release", "value must be a Boolean"))

    for field_name in ("equipment_tags", "revision_sequence"):
        if field_name not in record:
            continue
        value = record[field_name]
        if not isinstance(value, list) or any(
            not isinstance(item, str) for item in value
        ):
            errors.append((field_name, "value must be an array of strings"))
    return errors


def _parse_bool(value: str) -> bool:
    if value == "true":
        return True
    if value == "false":
        return False
    raise ValueError("value must be lowercase true or false")


def _parse_decimal(value: str) -> Decimal:
    try:
        parsed = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("value must be a base-10 number") from exc
    if not parsed.is_finite():
        raise ValueError("value must be finite")
    return parsed


def _parse_positive_integer(value: str) -> int:
    if not value.isdigit() or int(value) < 1:
        raise ValueError("value must be a positive base-10 integer")
    return int(value)


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("value must be an ISO-8601 calendar date") from exc
