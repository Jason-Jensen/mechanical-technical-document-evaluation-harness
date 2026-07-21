"""Atomic publication of one complete package-assurance audit run."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
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


class PackageAuditPublicationError(RuntimeError):
    """Raised when a complete audit run cannot be published safely."""


class PackageAuditCollisionError(PackageAuditPublicationError):
    """Raised when the immutable final run directory already exists."""


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
        f".{result.run_id}.{uuid4().hex[:8]}.tmp"
    )
    try:
        staging_directory.mkdir(exist_ok=False)
        staged_result_path = staging_directory / PACKAGE_RESULT_FILENAME
        staged_result_path.write_text(
            result_text,
            encoding="utf-8",
            newline="\n",
        )

        issue_views = render_issue_register_views(
            result_path=staged_result_path,
            schema_path=schema_path,
        )
        readiness_text = render_release_readiness_summary(
            result_path=staged_result_path,
            schema_path=schema_path,
        )
        output_text = {
            ISSUE_REGISTER_CSV_FILENAME: issue_views.csv_text,
            ISSUE_REGISTER_MARKDOWN_FILENAME: issue_views.markdown_text,
            RELEASE_READINESS_MARKDOWN_FILENAME: readiness_text,
        }
        for filename, text in output_text.items():
            (staging_directory / filename).write_text(
                text,
                encoding="utf-8",
                newline="\n",
            )

        staged_names = tuple(
            path.name
            for path in sorted(staging_directory.iterdir(), key=lambda path: path.name)
        )
        if set(staged_names) != set(AUDIT_PACKAGE_OUTPUT_FILENAMES):
            raise PackageAuditPublicationError(
                "Staged audit output set is incomplete or unexpected."
            )

        _finalize_staged_publication(
            staging_directory=staging_directory,
            final_directory=final_directory,
            run_id=result.run_id,
        )
    except PackageAuditCollisionError as exc:
        _preserve_failed_publication(staging_directory, result.run_id, exc)
        raise
    except Exception as exc:
        _preserve_failed_publication(staging_directory, result.run_id, exc)
        if isinstance(exc, PackageAuditPublicationError):
            raise
        raise PackageAuditPublicationError(
            f"Could not publish complete package audit: {result.run_id}"
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
    error: Exception,
) -> None:
    if not staging_directory.is_dir():
        return
    marker = staging_directory / PUBLICATION_FAILURE_FILENAME
    try:
        marker.write_text(
            "complete=false\n"
            "phase=publication\n"
            f"error_type={type(error).__name__}\n",
            encoding="utf-8",
            newline="\n",
        )
    except OSError:
        pass

    failed_directory = staging_directory.parent / (
        f".{run_id}.publication-failed-{uuid4().hex[:8]}"
    )
    try:
        staging_directory.replace(failed_directory)
    except OSError:
        pass


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True
