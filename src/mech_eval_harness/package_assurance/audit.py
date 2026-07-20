"""Bounded end-to-end package-assurance audit workflow."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from mech_eval_harness.package_assurance.gates import run_package_gates
from mech_eval_harness.package_assurance.manifest import (
    PACKAGE_MANIFEST_FILENAME,
)
from mech_eval_harness.package_assurance.models import PackageResultState
from mech_eval_harness.package_assurance.publication import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
    PackageAuditPublication,
    publish_package_audit,
)
from mech_eval_harness.package_assurance.relationships import (
    run_package_relationships,
)
from mech_eval_harness.package_assurance.result_core import (
    AUDIT_PACKAGE_READY_STATUS,
    PackageResult,
    build_package_result,
)
from mech_eval_harness.persistence import generate_run_id


PACKAGE_STATE_EXIT_CODES: dict[PackageResultState, int] = {
    "automatic_pass": 0,
    "automatic_fail": 1,
    "engineering_review_required": 2,
    "missing_authoritative_information": 3,
    "extraction_or_tool_failure": 4,
    "evaluator_uncertainty": 5,
}


@dataclass(frozen=True)
class PackageAuditOutcome:
    """The canonical result and atomically published files for one run."""

    result: PackageResult
    publication: PackageAuditPublication


def execute_package_audit(
    *,
    repository_root: Path,
    package_root: Path,
    runs_dir: Path,
    schema_path: Path,
    run_id: str | None = None,
    started_at: datetime | None = None,
) -> PackageAuditOutcome:
    """Run the accepted pipeline and publish its result and report views."""

    repository_root = repository_root.resolve()
    package_root = package_root.resolve()
    runs_dir = runs_dir.resolve()
    started_at = started_at or datetime.now(timezone.utc)
    run_id = run_id or generate_run_id(started_at)

    gate_evaluation = run_package_gates(
        repository_root,
        Path(PACKAGE_MANIFEST_FILENAME),
        allowed_package_root=package_root,
    )
    relationship_evaluation = run_package_relationships(gate_evaluation)
    completed_at = datetime.now(timezone.utc)
    result = build_package_result(
        run_id=run_id,
        started_at=started_at,
        completed_at=completed_at,
        package_root=package_root,
        gate_evaluation=gate_evaluation,
        relationship_evaluation=relationship_evaluation,
        output_location=_portable_output_location(
            repository_root,
            runs_dir / run_id,
        ),
        output_generation_status=AUDIT_PACKAGE_READY_STATUS,
        output_names=AUDIT_PACKAGE_OUTPUT_FILENAMES,
    )
    publication = publish_package_audit(
        result=result,
        package_root=package_root,
        runs_dir=runs_dir,
        schema_path=schema_path,
    )
    return PackageAuditOutcome(result=result, publication=publication)


def package_state_exit_code(state: PackageResultState) -> int:
    """Return the accepted stable CLI exit for one package result state."""

    try:
        return PACKAGE_STATE_EXIT_CODES[state]
    except KeyError as exc:
        raise ValueError(f"Unsupported package result state: {state}") from exc


def _portable_output_location(repository_root: Path, run_directory: Path) -> str:
    try:
        return run_directory.relative_to(repository_root).as_posix()
    except ValueError:
        return run_directory.name
