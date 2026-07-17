"""Typed records and deterministic outcomes for package-assurance gates."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import TYPE_CHECKING, Any, Literal, Mapping

if TYPE_CHECKING:
    from mech_eval_harness.package_assurance.manifest import LoadedPackageManifest


PackageResultState = Literal[
    "automatic_pass",
    "automatic_fail",
    "engineering_review_required",
    "missing_authoritative_information",
    "extraction_or_tool_failure",
    "evaluator_uncertainty",
]
GateStatus = Literal["passed", "failed", "skipped"]


@dataclass(frozen=True)
class EvidenceLocator:
    """Package-relative evidence for one source value or file reference."""

    source_type: str
    source_file: str
    format: str
    row_number: int | None = None
    header_row_number: int | None = None
    column_name: str | None = None
    row_key_column: str | None = None
    row_key_value: str | None = None
    json_pointer: str | None = None
    record_id: str | None = None
    property_name: str | None = None
    file_ref_id: str | None = None
    declared_relative_path: str | None = None
    resolved_package_relative_path: str | None = None
    boundary_check: str | None = None
    original_value: Any = None
    normalized_value: Any = None

    def __post_init__(self) -> None:
        for label, value in (
            ("source_type", self.source_type),
            ("source_file", self.source_file),
            ("format", self.format),
        ):
            if not isinstance(value, str) or not value:
                raise ValueError(f"Evidence {label} must be a non-empty string")

        source_path = PurePosixPath(self.source_file)
        windows_path = PureWindowsPath(self.source_file)
        if (
            "\\" in self.source_file
            or source_path.is_absolute()
            or windows_path.is_absolute()
            or bool(windows_path.drive)
            or ".." in source_path.parts
        ):
            raise ValueError("Evidence source_file must be package-relative")

    def to_dict(self) -> dict[str, Any]:
        document: dict[str, Any] = {
            "source_type": self.source_type,
            "source_file": self.source_file,
            "format": self.format,
        }
        optional = {
            "row_number": self.row_number,
            "header_row_number": self.header_row_number,
            "column_name": self.column_name,
            "row_key": (
                {
                    "column_name": self.row_key_column,
                    "value": self.row_key_value,
                }
                if self.row_key_column is not None
                and self.row_key_value is not None
                else None
            ),
            "json_pointer": self.json_pointer,
            "record_id": self.record_id,
            "property_name": self.property_name,
            "file_ref_id": self.file_ref_id,
            "declared_relative_path": self.declared_relative_path,
            "resolved_package_relative_path": self.resolved_package_relative_path,
            "boundary_check": self.boundary_check,
        }
        document.update(
            (key, value)
            for key, value in optional.items()
            if value is not None
        )
        if self.format in {"csv", "json"}:
            document["original_value"] = self.original_value
            document["normalized_value"] = self.normalized_value
        return document


@dataclass(frozen=True)
class StructuredSourceRecord:
    """One adapter-produced source record with original and parsed values."""

    source_type: str
    record_type: str
    source_file: str
    format: Literal["csv", "json"]
    schema_version: str
    original_values: Mapping[str, Any]
    values: Mapping[str, Any]
    row_number: int | None = None
    header_row_number: int | None = None
    row_key_name: str | None = None
    row_key_value: str | None = None
    json_pointer: str | None = None
    record_id: str | None = None

    def field_locator(
        self,
        field_name: str,
        *,
        original_value: Any | None = None,
        normalized_value: Any | None = None,
    ) -> EvidenceLocator:
        """Build an exact CSV or RFC 6901 JSON field locator."""

        if original_value is None:
            original_value = self.original_values.get(field_name)
        if normalized_value is None:
            normalized_value = self.values.get(field_name)

        if self.format == "csv":
            return EvidenceLocator(
                source_type=self.source_type,
                source_file=self.source_file,
                format="csv",
                row_number=self.row_number,
                header_row_number=self.header_row_number,
                column_name=field_name,
                row_key_column=self.row_key_name,
                row_key_value=self.row_key_value,
                original_value=original_value,
                normalized_value=normalized_value,
            )

        pointer = self.json_pointer or ""
        escaped = field_name.replace("~", "~0").replace("/", "~1")
        return EvidenceLocator(
            source_type=self.source_type,
            source_file=self.source_file,
            format="json",
            json_pointer=f"{pointer}/{escaped}",
            record_id=self.record_id,
            property_name=field_name,
            original_value=original_value,
            normalized_value=normalized_value,
        )


@dataclass(frozen=True)
class SourceLoadError:
    """Controlled adapter failure without an absolute machine path."""

    source_type: str
    source_file: str
    format: str
    code: str
    message: str
    row_number: int | None = None
    column_name: str | None = None
    json_pointer: str | None = None

    def evidence_locator(self) -> EvidenceLocator:
        return EvidenceLocator(
            source_type=self.source_type,
            source_file=self.source_file,
            format=self.format,
            row_number=self.row_number,
            header_row_number=1 if self.row_number is not None else None,
            column_name=self.column_name,
            json_pointer=self.json_pointer,
            property_name=self.column_name if self.format == "json" else None,
            original_value=None,
            normalized_value=None,
        )


@dataclass(frozen=True)
class LoadedStructuredSources:
    """Successfully parsed source documents and typed records."""

    records: tuple[StructuredSourceRecord, ...]
    documents: Mapping[str, Mapping[str, Any]]

    def records_for(self, source_type: str) -> tuple[StructuredSourceRecord, ...]:
        return tuple(
            record for record in self.records if record.source_type == source_type
        )

    def records_of_type(self, record_type: str) -> tuple[StructuredSourceRecord, ...]:
        return tuple(
            record for record in self.records if record.record_type == record_type
        )


@dataclass(frozen=True)
class PackageGateFinding:
    """One deterministic, evidence-linked gate failure."""

    finding_id: str
    gate_id: str
    gate_version: str
    code: str
    state: PackageResultState
    release_hold: bool
    message: str
    affected_identifiers: tuple[str, ...]
    evidence: tuple[EvidenceLocator, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "gate_id": self.gate_id,
            "gate_version": self.gate_version,
            "code": self.code,
            "state": self.state,
            "release_hold": self.release_hold,
            "message": self.message,
            "affected_identifiers": list(self.affected_identifiers),
            "evidence": [locator.to_dict() for locator in self.evidence],
        }


@dataclass(frozen=True)
class PackageGateResult:
    """Passed, failed, or dependency-skipped result for one package gate."""

    gate_id: str
    gate_version: str
    kind: str
    status: GateStatus
    summary: str
    findings: tuple[PackageGateFinding, ...] = ()
    evidence: tuple[EvidenceLocator, ...] = ()
    blocked_by: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status == "passed" and self.findings:
            raise ValueError("Passed package gates cannot contain findings")
        if self.status == "failed" and not self.findings:
            raise ValueError("Failed package gates require at least one finding")
        if self.status == "skipped":
            if self.findings:
                raise ValueError("Skipped package gates cannot contain findings")
            if not self.blocked_by:
                raise ValueError("Skipped package gates require blocked_by")
        elif self.blocked_by:
            raise ValueError("Only skipped package gates may set blocked_by")

    @property
    def passed(self) -> bool:
        return self.status == "passed"

    @property
    def skipped(self) -> bool:
        return self.status == "skipped"

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "gate_version": self.gate_version,
            "kind": self.kind,
            "status": self.status,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
            "evidence": [locator.to_dict() for locator in self.evidence],
            "blocked_by": list(self.blocked_by),
        }


@dataclass(frozen=True)
class PackageGateEvaluation:
    """P2.1 output without selecting a package-level result state."""

    package_id: str | None
    gates: tuple[PackageGateResult, ...]
    manifest: LoadedPackageManifest | None
    sources: LoadedStructuredSources | None

    @property
    def dependent_checks_allowed(self) -> bool:
        return bool(self.gates) and all(result.passed for result in self.gates)

    def to_dict(self) -> dict[str, Any]:
        return {
            "package_id": self.package_id,
            "dependent_checks_allowed": self.dependent_checks_allowed,
            "gates": [result.to_dict() for result in self.gates],
        }
