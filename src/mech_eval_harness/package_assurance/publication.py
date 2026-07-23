"""Atomic publication of one complete package-assurance audit run."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Final
from uuid import uuid4

from mech_eval_harness.package_assurance.issue_register import (
    ISSUE_REGISTER_CSV_FILENAME,
    ISSUE_REGISTER_MARKDOWN_FILENAME,
    render_issue_register_views,
)
from mech_eval_harness.package_assurance.persistence import (
    validate_package_result_document,
)
from mech_eval_harness.package_assurance.release_readiness import (
    RELEASE_READINESS_MARKDOWN_FILENAME,
    render_release_readiness_summary,
)
from mech_eval_harness.package_assurance.result_core import (
    AUDIT_PACKAGE_READY_STATUS,
    PACKAGE_RESULT_FILENAME,
    PackageResult,
)


AUDIT_PACKAGE_OUTPUT_FILENAMES: tuple[str, ...] = (
    PACKAGE_RESULT_FILENAME,
    ISSUE_REGISTER_CSV_FILENAME,
    ISSUE_REGISTER_MARKDOWN_FILENAME,
    RELEASE_READINESS_MARKDOWN_FILENAME,
)
PUBLICATION_FAILURE_FILENAME = "publication_failure.txt"
FINAL_RENAME_RETRY_DELAYS_SECONDS: tuple[float, ...] = (0.05, 0.1, 0.2, 0.4)
STAGING_DIRECTORY_PREFIX: Final = ".tmp-"
FAILED_DIRECTORY_PREFIX: Final = ".failed-"
FALLBACK_FAILURE_MARKER_PREFIX: Final = ".failure-"

STAGE_CREATE_STAGING_DIRECTORY: Final = "create_staging_directory"
STAGE_WRITE_PACKAGE_RESULT: Final = "write_package_result"
STAGE_RENDER_ISSUE_REGISTER: Final = "render_issue_register"
STAGE_RENDER_RELEASE_READINESS: Final = "render_release_readiness"
STAGE_WRITE_ISSUE_REGISTER_CSV: Final = "write_issue_register_csv"
STAGE_WRITE_ISSUE_REGISTER_MARKDOWN: Final = "write_issue_register_markdown"
STAGE_WRITE_RELEASE_READINESS: Final = "write_release_readiness"
STAGE_VERIFY_OUTPUT_SET: Final = "verify_staged_output_set"
STAGE_FINALIZE_RUN_DIRECTORY: Final = "finalize_run_directory"


class PackageAuditPublicationError(RuntimeError):
    """Raised when a complete audit run cannot be published safely."""

    def __init__(
        self,
        message: str,
        *,
        diagnostics: PublicationFailureDiagnostics | None = None,
    ) -> None:
        super().__init__(message)
        self.diagnostics = diagnostics


class PackageAuditCollisionError(PackageAuditPublicationError):
    """Raised when the immutable final run directory already exists."""


@dataclass(frozen=True)
class PublicationFailureDiagnostics:
    """Sanitized failure facts safe to preserve with incomplete output evidence."""

    stage: str
    error_type: str
    errno: int | None
    winerror: int | None


@dataclass(frozen=True)
class PackageAuditPublication:
    """Paths published together for one complete package audit."""

    run_directory: Path
    result_path: Path
    issue_register_csv_path: Path
    issue_register_markdown_path: Path
    release_readiness_path: Path


def publish_package_audit(
    *,
    result: PackageResult,
    package_root: Path,
    runs_dir: Path,
    schema_path: Path,
) -> PackageAuditPublication:
    """Prepare all output bytes, then atomically publish one immutable run."""

    expected_generation = {
        "status": AUDIT_PACKAGE_READY_STATUS,
        "output_names": list(AUDIT_PACKAGE_OUTPUT_FILENAMES),
    }
    if dict(result.output_generation) != expected_generation:
        raise PackageAuditPublicationError(
            "Package result does not declare the complete audit output set."
        )

    document = result.to_dict()
    validate_package_result_document(document, schema_path)
    try:
        result_text = (
            json.dumps(
                document,
                indent=2,
                ensure_ascii=False,
                allow_nan=False,
            )
            + "\n"
        )
    except (TypeError, ValueError) as exc:
        raise PackageAuditPublicationError(
            "Package result could not be serialized as strict JSON."
        ) from exc

    resolved_package_root = package_root.resolve()
    resolved_runs_dir = runs_dir.resolve()
    if _is_relative_to(resolved_runs_dir, resolved_package_root):
        raise PackageAuditPublicationError(
            "Package audit outputs must be outside the audited package."
        )

    try:
        resolved_runs_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise PackageAuditPublicationError(
            f"Could not create package runs directory: {resolved_runs_dir}"
        ) from exc

    final_directory = resolved_runs_dir / result.run_id
    if final_directory.exists():
        raise _collision_error(result.run_id)

    staging_directory = resolved_runs_dir / (
        f"{STAGING_DIRECTORY_PREFIX}{uuid4().hex[:8]}"
    )
    stage = STAGE_CREATE_STAGING_DIRECTORY
    try:
        staging_directory.mkdir(exist_ok=False)
        stage = STAGE_WRITE_PACKAGE_RESULT
        staged_result_path = staging_directory / PACKAGE_RESULT_FILENAME
        staged_result_path.write_text(
            result_text,
            encoding="utf-8",
            newline="\n",
        )

        stage = STAGE_RENDER_ISSUE_REGISTER
        issue_views = render_issue_register_views(
            result_path=staged_result_path,
            schema_path=schema_path,
        )
        stage = STAGE_RENDER_RELEASE_READINESS
        readiness_text = render_release_readiness_summary(
            result_path=staged_result_path,
            schema_path=schema_path,
        )
        output_text = (
            (
                STAGE_WRITE_ISSUE_REGISTER_CSV,
                ISSUE_REGISTER_CSV_FILENAME,
                issue_views.csv_text,
            ),
            (
                STAGE_WRITE_ISSUE_REGISTER_MARKDOWN,
                ISSUE_REGISTER_MARKDOWN_FILENAME,
                issue_views.markdown_text,
            ),
            (
                STAGE_WRITE_RELEASE_READINESS,
                RELEASE_READINESS_MARKDOWN_FILENAME,
                readiness_text,
            ),
        )
        for output_stage, filename, text in output_text:
            stage = output_stage
            (staging_directory / filename).write_text(
                text,
                encoding="utf-8",
                newline="\n",
            )

        stage = STAGE_VERIFY_OUTPUT_SET
        staged_names = tuple(
            path.name
            for path in sorted(staging_directory.iterdir(), key=lambda path: path.name)
        )
        if set(staged_names) != set(AUDIT_PACKAGE_OUTPUT_FILENAMES):
            raise PackageAuditPublicationError(
                "Staged audit output set is incomplete or unexpected."
            )

        stage = STAGE_FINALIZE_RUN_DIRECTORY
        _finalize_staged_publication(
            staging_directory=staging_directory,
            final_directory=final_directory,
            run_id=result.run_id,
        )
    except PackageAuditCollisionError as exc:
        diagnostics = _failure_diagnostics(stage, exc)
        _preserve_failed_publication(
            staging_directory,
            result.run_id,
            diagnostics,
        )
        raise
    except Exception as exc:
        diagnostics = _failure_diagnostics(stage, exc)
        _preserve_failed_publication(
            staging_directory,
            result.run_id,
            diagnostics,
        )
        raise PackageAuditPublicationError(
            _failure_message(result.run_id, diagnostics),
            diagnostics=diagnostics,
        ) from exc

    return PackageAuditPublication(
        run_directory=final_directory,
        result_path=final_directory / PACKAGE_RESULT_FILENAME,
        issue_register_csv_path=(
            final_directory / ISSUE_REGISTER_CSV_FILENAME
        ),
        issue_register_markdown_path=(
            final_directory / ISSUE_REGISTER_MARKDOWN_FILENAME
        ),
        release_readiness_path=(
            final_directory / RELEASE_READINESS_MARKDOWN_FILENAME
        ),
    )


def _finalize_staged_publication(
    *,
    staging_directory: Path,
    final_directory: Path,
    run_id: str,
) -> None:
    for attempt in range(len(FINAL_RENAME_RETRY_DELAYS_SECONDS) + 1):
        if final_directory.exists():
            raise _collision_error(run_id)
        try:
            _replace_directory(staging_directory, final_directory)
            return
        except OSError as exc:
            if final_directory.exists():
                raise _collision_error(run_id) from exc
            if not isinstance(exc, PermissionError):
                raise
            if attempt == len(FINAL_RENAME_RETRY_DELAYS_SECONDS):
                raise
            time.sleep(FINAL_RENAME_RETRY_DELAYS_SECONDS[attempt])


def _replace_directory(source: Path, target: Path) -> None:
    source.replace(target)


def _collision_error(run_id: str) -> PackageAuditCollisionError:
    return PackageAuditCollisionError(
        "Package audit run already exists and will not be overwritten: "
        f"{run_id}"
    )


def _preserve_failed_publication(
    staging_directory: Path,
    run_id: str,
    diagnostics: PublicationFailureDiagnostics,
) -> None:
    if not staging_directory.is_dir():
        return
    marker_text = (
        "complete=false\n"
        "phase=publication\n"
        f"stage={diagnostics.stage}\n"
        f"run_id={run_id}\n"
        f"error_type={diagnostics.error_type}\n"
        f"errno={_optional_int_text(diagnostics.errno)}\n"
        f"winerror={_optional_int_text(diagnostics.winerror)}\n"
    )
    marker_written = _write_failure_marker(
        staging_directory / PUBLICATION_FAILURE_FILENAME,
        marker_text,
    )

    failed_directory = staging_directory.parent / (
        f"{FAILED_DIRECTORY_PREFIX}{uuid4().hex[:8]}"
    )
    try:
        staging_directory.replace(failed_directory)
    except OSError:
        evidence_directory = staging_directory
    else:
        evidence_directory = failed_directory

    if not marker_written:
        marker_written = _write_failure_marker(
            evidence_directory / PUBLICATION_FAILURE_FILENAME,
            marker_text,
        )
    if not marker_written:
        _write_failure_marker(
            staging_directory.parent
            / f"{FALLBACK_FAILURE_MARKER_PREFIX}{uuid4().hex[:8]}.txt",
            marker_text,
        )


def _write_failure_marker(path: Path, marker_text: str) -> bool:
    try:
        path.write_text(
            marker_text,
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        return False
    return True


def _failure_diagnostics(
    stage: str,
    error: Exception,
) -> PublicationFailureDiagnostics:
    errno = getattr(error, "errno", None)
    winerror = getattr(error, "winerror", None)
    return PublicationFailureDiagnostics(
        stage=stage,
        error_type=type(error).__name__,
        errno=errno if isinstance(errno, int) else None,
        winerror=winerror if isinstance(winerror, int) else None,
    )


def _failure_message(
    run_id: str,
    diagnostics: PublicationFailureDiagnostics,
) -> str:
    return (
        f"Could not publish complete package audit: {run_id} "
        f"[stage={diagnostics.stage}; "
        f"error_type={diagnostics.error_type}; "
        f"errno={_optional_int_text(diagnostics.errno)}; "
        f"winerror={_optional_int_text(diagnostics.winerror)}]"
    )


def _optional_int_text(value: int | None) -> str:
    return str(value) if value is not None else "not_available"


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
