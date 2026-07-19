"""Canonical package result construction and deterministic state routing."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Mapping, Sequence

from mech_eval_harness.package_assurance.gates import (
    PACKAGE_GATE_ORDER,
)
from mech_eval_harness.package_assurance.manifest import (
    PACKAGE_MANIFEST_FILENAME,
    LoadedPackageManifest,
)
from mech_eval_harness.package_assurance.models import (
    EvidenceLocator,
    PackageGateEvaluation,
    PackageGateFinding,
    PackageGateResult,
    PackageRelationshipEvaluation,
    PackageResultState,
    RelationshipCheckResult,
    RelationshipFinding,
)
from mech_eval_harness.package_assurance.relationships import (
    RELATIONSHIP_CHECK_ORDER,
)


PACKAGE_RESULT_SCHEMA_VERSION = "0.3.0"
PACKAGE_EVALUATOR_VERSION = "0.3.0"
PACKAGE_RESULT_ROUTER_VERSION = "0.3.0"
WORKFLOW_CONTRACT_VERSION = "0.3.0"
PACKAGE_RESULT_FILENAME = "package_result.json"
REQUIRED_EVALUATION_INCOMPLETE_CODE = "REQUIRED_EVALUATION_INCOMPLETE"
RESULT_COMPLETENESS_CONTROL_ID = "WORKFLOW-PACKAGE-RESULT-COMPLETENESS"
ENGINEERING_REVIEW_LIMITATION = (
    "This result supports qualified human review and is not engineering sign-off, "
    "a code-compliance opinion, an autonomous release decision, or a safety-critical "
    "final decision."
)

PACKAGE_STATE_PRECEDENCE: tuple[PackageResultState, ...] = (
    "automatic_fail",
    "extraction_or_tool_failure",
    "missing_authoritative_information",
    "evaluator_uncertainty",
    "engineering_review_required",
    "automatic_pass",
)

InputStatus = Literal["available", "missing", "unreadable", "outside_package"]
FingerprintStatus = Literal["complete", "partial"]
ControlType = Literal["gate", "relationship_check", "evaluator"]


@dataclass(frozen=True)
class InputArtifact:
    """One controlled package-relative input included in the fingerprint."""

    path: str
    status: InputStatus
    sha256: str | None
    size_bytes: int | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "status": self.status,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
        }


@dataclass(frozen=True)
class PackageInputFingerprint:
    """Reproducible identity of the controlled package input boundary."""

    algorithm: str
    status: FingerprintStatus
    sha256: str
    artifacts: tuple[InputArtifact, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "status": self.status,
            "sha256": self.sha256,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
        }


@dataclass(frozen=True)
class CanonicalPackageFinding:
    """The single report-ready representation of one non-pass condition."""

    finding_id: str
    control_type: ControlType
    control_id: str
    control_version: str
    package_id: str | None
    code: str
    result_state: PackageResultState
    severity: Literal["high"]
    release_hold: bool
    authority_rule_id: str | None
    governing_control_id: str | None
    message: str
    affected_identifiers: tuple[str, ...]
    expected_value: Any
    actual_value: Any
    review_owner: str
    evaluator_version: str
    evidence: tuple[EvidenceLocator, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "control_type": self.control_type,
            "control_id": self.control_id,
            "control_version": self.control_version,
            "package_id": self.package_id,
            "code": self.code,
            "result_state": self.result_state,
            "severity": self.severity,
            "release_hold": self.release_hold,
            "authority_rule_id": self.authority_rule_id,
            "governing_control_id": self.governing_control_id,
            "message": self.message,
            "affected_identifiers": list(self.affected_identifiers),
            "expected_value": self.expected_value,
            "actual_value": self.actual_value,
            "review_owner": self.review_owner,
            "evaluator_version": self.evaluator_version,
            "evidence": [locator.to_dict() for locator in self.evidence],
        }


@dataclass(frozen=True)
class CompletenessIssue:
    """One exact defect in the required evaluator result set."""

    code: str
    control_type: str
    control_id: str | None
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "control_type": self.control_type,
            "control_id": self.control_id,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class RequiredResultCompleteness:
    """Evidence that every accepted gate and check result was accounted for."""

    status: Literal["complete", "incomplete"]
    automatic_pass_eligible: bool
    expected_gate_ids: tuple[str, ...]
    actual_gate_ids: tuple[str, ...]
    expected_check_ids: tuple[str, ...]
    actual_check_ids: tuple[str, ...]
    issues: tuple[CompletenessIssue, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "automatic_pass_eligible": self.automatic_pass_eligible,
            "expected_gate_ids": list(self.expected_gate_ids),
            "actual_gate_ids": list(self.actual_gate_ids),
            "expected_check_ids": list(self.expected_check_ids),
            "actual_check_ids": list(self.actual_check_ids),
            "issues": [issue.to_dict() for issue in self.issues],
        }


@dataclass(frozen=True)
class PackageRunMetadata:
    """Declared volatile metadata that may differ across identical runs."""

    started_at: str
    completed_at: str
    duration_ms: int
    host: Mapping[str, str]
    output_location: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "duration_ms": self.duration_ms,
            "host": dict(sorted(self.host.items())),
            "output_location": self.output_location,
        }


@dataclass(frozen=True)
class PackageResult:
    """Immutable canonical result content for one structured package audit."""

    run_id: str
    run_metadata: PackageRunMetadata
    package_id: str | None
    versions: Mapping[str, str | None]
    input_fingerprint: PackageInputFingerprint
    package_state: PackageResultState
    release_hold: bool
    blocking_states: tuple[PackageResultState, ...]
    gate_results: tuple[Mapping[str, Any], ...]
    relationship_results: tuple[Mapping[str, Any], ...]
    findings: tuple[CanonicalPackageFinding, ...]
    completeness: RequiredResultCompleteness
    output_generation: Mapping[str, Any]
    engineering_review_limitation: str = ENGINEERING_REVIEW_LIMITATION

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": PACKAGE_RESULT_SCHEMA_VERSION,
            "run_id": self.run_id,
            "run_metadata": self.run_metadata.to_dict(),
            "package_id": self.package_id,
            "versions": dict(self.versions),
            "input_fingerprint": self.input_fingerprint.to_dict(),
            "package_state": self.package_state,
            "release_hold": self.release_hold,
            "blocking_states": list(self.blocking_states),
            "gate_results": [dict(result) for result in self.gate_results],
            "relationship_results": [
                dict(result) for result in self.relationship_results
            ],
            "findings": [finding.to_dict() for finding in self.findings],
            "required_result_completeness": self.completeness.to_dict(),
            "output_generation": dict(self.output_generation),
            "engineering_review_limitation": self.engineering_review_limitation,
        }


def route_package_state(
    states: Sequence[PackageResultState],
) -> tuple[PackageResultState, tuple[PackageResultState, ...]]:
    """Select the highest-precedence state and retain every blocking state."""

    invalid = sorted(set(states) - set(PACKAGE_STATE_PRECEDENCE))
    if invalid:
        raise ValueError(f"Unsupported package result states: {invalid}")

    observed = set(states)
    blocking_states = tuple(
        state
        for state in PACKAGE_STATE_PRECEDENCE
        if state != "automatic_pass" and state in observed
    )
    if not blocking_states:
        return "automatic_pass", ()
    return blocking_states[0], blocking_states


def build_package_result(
    *,
    run_id: str,
    started_at: datetime,
    completed_at: datetime,
    package_root: Path,
    gate_evaluation: PackageGateEvaluation,
    relationship_evaluation: PackageRelationshipEvaluation,
    host_metadata: Mapping[str, str] | None = None,
    output_location: str | None = None,
) -> PackageResult:
    """Build one canonical package result from accepted gate and check outputs."""

    run_metadata = _build_run_metadata(
        started_at,
        completed_at,
        host_metadata=host_metadata,
        output_location=output_location,
    )
    package_root = package_root.resolve()
    if not package_root.is_dir():
        raise ValueError("package_root must identify an existing directory")

    raw_findings = [
        _canonical_gate_finding(gate_evaluation.package_id, finding)
        for gate in gate_evaluation.gates
        for finding in gate.findings
    ]
    raw_findings.extend(
        _canonical_relationship_finding(finding)
        for check in relationship_evaluation.checks
        for finding in check.findings
    )

    duplicate_finding_ids = tuple(
        sorted(
            finding_id
            for finding_id, count in Counter(
                finding.finding_id for finding in raw_findings
            ).items()
            if count > 1
        )
    )
    completeness = _required_result_completeness(
        gate_evaluation,
        relationship_evaluation,
        duplicate_finding_ids=duplicate_finding_ids,
    )
    if completeness.issues:
        raw_findings.append(
            _completeness_finding(
                package_id=gate_evaluation.package_id,
                completeness=completeness,
            )
        )

    findings_by_id: dict[str, CanonicalPackageFinding] = {}
    for finding in raw_findings:
        findings_by_id.setdefault(finding.finding_id, finding)
    findings = tuple(sorted(findings_by_id.values(), key=_finding_sort_key))

    package_state, blocking_states = route_package_state(
        [finding.result_state for finding in findings]
    )
    if package_state == "automatic_pass" and not completeness.automatic_pass_eligible:
        raise RuntimeError("An incomplete required result set cannot route to pass")

    manifest = gate_evaluation.manifest
    return PackageResult(
        run_id=run_id,
        run_metadata=run_metadata,
        package_id=gate_evaluation.package_id,
        versions={
            "package_result_schema": PACKAGE_RESULT_SCHEMA_VERSION,
            "evaluator": PACKAGE_EVALUATOR_VERSION,
            "router": PACKAGE_RESULT_ROUTER_VERSION,
            "workflow_contract": WORKFLOW_CONTRACT_VERSION,
            "package_manifest": (
                manifest.manifest.get("schema_version") if manifest else None
            ),
            "authority_map": _authority_map_version(gate_evaluation),
        },
        input_fingerprint=build_package_input_fingerprint(
            package_root=package_root,
            manifest=manifest,
        ),
        package_state=package_state,
        release_hold=any(finding.release_hold for finding in findings),
        blocking_states=blocking_states,
        gate_results=tuple(
            _gate_result_summary(result) for result in gate_evaluation.gates
        ),
        relationship_results=tuple(
            _relationship_result_summary(result)
            for result in relationship_evaluation.checks
        ),
        findings=findings,
        completeness=completeness,
        output_generation={
            "status": "package_result_ready",
            "output_names": [PACKAGE_RESULT_FILENAME],
        },
    )


def build_package_input_fingerprint(
    *,
    package_root: Path,
    manifest: LoadedPackageManifest | None,
) -> PackageInputFingerprint:
    """Hash only declared sources and controlled file references."""

    package_root = package_root.resolve()
    declared_paths: set[str] = set()
    if manifest is None:
        declared_paths.add(PACKAGE_MANIFEST_FILENAME)
    else:
        for path in (*manifest.source_paths.values(), *manifest.file_reference_paths.values()):
            try:
                declared_paths.add(path.relative_to(package_root).as_posix())
            except ValueError:
                declared_paths.add(path.as_posix())

    hasher = hashlib.sha256()
    artifacts: list[InputArtifact] = []
    for relative_path in sorted(declared_paths):
        status, raw = _read_fingerprint_input(package_root, relative_path)
        digest = hashlib.sha256(raw).hexdigest() if raw is not None else None
        size = len(raw) if raw is not None else None
        artifact = InputArtifact(
            path=relative_path,
            status=status,
            sha256=digest,
            size_bytes=size,
        )
        artifacts.append(artifact)

        path_bytes = relative_path.encode("utf-8")
        status_bytes = status.encode("ascii")
        hasher.update(len(path_bytes).to_bytes(4, "big"))
        hasher.update(path_bytes)
        hasher.update(len(status_bytes).to_bytes(1, "big"))
        hasher.update(status_bytes)
        if raw is not None:
            hasher.update(len(raw).to_bytes(8, "big"))
            hasher.update(raw)
        else:
            hasher.update((0).to_bytes(8, "big"))

    is_complete = manifest is not None and all(
        artifact.status == "available" for artifact in artifacts
    )
    return PackageInputFingerprint(
        algorithm="sha256-path-status-size-bytes-v1",
        status="complete" if is_complete else "partial",
        sha256=hasher.hexdigest(),
        artifacts=tuple(artifacts),
    )


def _read_fingerprint_input(
    package_root: Path,
    relative_path: str,
) -> tuple[InputStatus, bytes | None]:
    candidate = package_root / Path(relative_path)
    try:
        resolved = candidate.resolve()
        resolved.relative_to(package_root)
    except (OSError, ValueError):
        return "outside_package", None
    if not resolved.is_file():
        return "missing", None
    try:
        return "available", resolved.read_bytes()
    except OSError:
        return "unreadable", None


def _required_result_completeness(
    gate_evaluation: PackageGateEvaluation,
    relationship_evaluation: PackageRelationshipEvaluation,
    *,
    duplicate_finding_ids: tuple[str, ...],
) -> RequiredResultCompleteness:
    issues: list[CompletenessIssue] = []
    actual_gate_ids = tuple(result.gate_id for result in gate_evaluation.gates)
    actual_check_ids = tuple(result.check_id for result in relationship_evaluation.checks)
    issues.extend(_sequence_issues("gate", PACKAGE_GATE_ORDER, actual_gate_ids))
    issues.extend(
        _sequence_issues("relationship_check", RELATIONSHIP_CHECK_ORDER, actual_check_ids)
    )

    failed_gate_ids = {
        result.gate_id
        for result in gate_evaluation.gates
        if result.status == "failed"
    }
    for result in gate_evaluation.gates:
        if result.status == "skipped" and not failed_gate_ids.intersection(
            result.blocked_by
        ):
            issues.append(
                CompletenessIssue(
                    code="unexpected_gate_skip",
                    control_type="gate",
                    control_id=result.gate_id,
                    detail=(
                        "Skipped gate is not blocked by an actually failed gate: "
                        f"{list(result.blocked_by)}"
                    ),
                )
            )
    for result in relationship_evaluation.checks:
        if result.status == "skipped" and not failed_gate_ids.intersection(
            result.blocked_by
        ):
            issues.append(
                CompletenessIssue(
                    code="unexpected_relationship_check_skip",
                    control_type="relationship_check",
                    control_id=result.check_id,
                    detail=(
                        "Skipped relationship check is not blocked by an actually "
                        f"failed gate: {list(result.blocked_by)}"
                    ),
                )
            )

    if gate_evaluation.package_id != relationship_evaluation.package_id:
        issues.append(
            CompletenessIssue(
                code="package_identity_mismatch",
                control_type="evaluator",
                control_id=None,
                detail=(
                    "Gate and relationship evaluations identify different packages: "
                    f"{gate_evaluation.package_id!r} != "
                    f"{relationship_evaluation.package_id!r}"
                ),
            )
        )
    for finding_id in duplicate_finding_ids:
        issues.append(
            CompletenessIssue(
                code="duplicate_finding_id",
                control_type="evaluator",
                control_id=None,
                detail=f"Canonical finding ID occurs more than once: {finding_id}",
            )
        )

    structurally_complete = not issues
    all_passed = (
        actual_gate_ids == PACKAGE_GATE_ORDER
        and actual_check_ids == RELATIONSHIP_CHECK_ORDER
        and all(result.status == "passed" for result in gate_evaluation.gates)
        and all(
            result.status == "passed" for result in relationship_evaluation.checks
        )
    )
    return RequiredResultCompleteness(
        status="complete" if structurally_complete else "incomplete",
        automatic_pass_eligible=structurally_complete and all_passed,
        expected_gate_ids=PACKAGE_GATE_ORDER,
        actual_gate_ids=actual_gate_ids,
        expected_check_ids=RELATIONSHIP_CHECK_ORDER,
        actual_check_ids=actual_check_ids,
        issues=tuple(issues),
    )


def _sequence_issues(
    control_type: str,
    expected: tuple[str, ...],
    actual: tuple[str, ...],
) -> list[CompletenessIssue]:
    issues: list[CompletenessIssue] = []
    expected_counts = Counter(expected)
    actual_counts = Counter(actual)
    for control_id in expected:
        if actual_counts[control_id] == 0:
            issues.append(
                CompletenessIssue(
                    code=f"missing_{control_type}",
                    control_type=control_type,
                    control_id=control_id,
                    detail=f"Required {control_type} result is missing.",
                )
            )
        elif actual_counts[control_id] > 1:
            issues.append(
                CompletenessIssue(
                    code=f"duplicate_{control_type}",
                    control_type=control_type,
                    control_id=control_id,
                    detail=(
                        f"Required {control_type} occurs "
                        f"{actual_counts[control_id]} times."
                    ),
                )
            )
    for control_id in actual:
        if expected_counts[control_id] == 0:
            issues.append(
                CompletenessIssue(
                    code=f"unexpected_{control_type}",
                    control_type=control_type,
                    control_id=control_id,
                    detail=f"Unexpected {control_type} result is present.",
                )
            )
    if actual_counts == expected_counts and actual != expected:
        issues.append(
            CompletenessIssue(
                code=f"out_of_order_{control_type}",
                control_type=control_type,
                control_id=None,
                detail=f"Required {control_type} results are out of accepted order.",
            )
        )
    return issues


def _canonical_gate_finding(
    package_id: str | None,
    finding: PackageGateFinding,
) -> CanonicalPackageFinding:
    return CanonicalPackageFinding(
        finding_id=finding.finding_id,
        control_type="gate",
        control_id=finding.gate_id,
        control_version=finding.gate_version,
        package_id=package_id,
        code=finding.code,
        result_state=finding.state,
        severity="high",
        release_hold=finding.release_hold,
        authority_rule_id=None,
        governing_control_id=finding.gate_id,
        message=finding.message,
        affected_identifiers=finding.affected_identifiers,
        expected_value={"gate_status": "passed"},
        actual_value={"gate_status": "failed", "finding_code": finding.code},
        review_owner="qualified_package_reviewer",
        evaluator_version=PACKAGE_EVALUATOR_VERSION,
        evidence=finding.evidence,
    )


def _canonical_relationship_finding(
    finding: RelationshipFinding,
) -> CanonicalPackageFinding:
    return CanonicalPackageFinding(
        finding_id=finding.finding_id,
        control_type="relationship_check",
        control_id=finding.check_id,
        control_version=finding.check_version,
        package_id=finding.package_id,
        code=finding.code,
        result_state=finding.result_state,
        severity=finding.severity,
        release_hold=finding.release_hold,
        authority_rule_id=finding.authority_rule_id,
        governing_control_id=None,
        message=finding.message,
        affected_identifiers=finding.affected_identifiers,
        expected_value=finding.expected_value,
        actual_value=finding.actual_value,
        review_owner=finding.review_owner,
        evaluator_version=PACKAGE_EVALUATOR_VERSION,
        evidence=finding.evidence,
    )


def _completeness_finding(
    *,
    package_id: str | None,
    completeness: RequiredResultCompleteness,
) -> CanonicalPackageFinding:
    semantic = {
        "code": REQUIRED_EVALUATION_INCOMPLETE_CODE,
        "package_id": package_id,
        "actual_gate_ids": list(completeness.actual_gate_ids),
        "actual_check_ids": list(completeness.actual_check_ids),
        "issues": [issue.to_dict() for issue in completeness.issues],
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    return CanonicalPackageFinding(
        finding_id=f"FND-{digest.upper()}",
        control_type="evaluator",
        control_id="package_result_router",
        control_version=PACKAGE_RESULT_ROUTER_VERSION,
        package_id=package_id,
        code=REQUIRED_EVALUATION_INCOMPLETE_CODE,
        result_state="evaluator_uncertainty",
        severity="high",
        release_hold=True,
        authority_rule_id=None,
        governing_control_id=RESULT_COMPLETENESS_CONTROL_ID,
        message=(
            "The required package evaluation result set is incomplete or "
            "internally inconsistent."
        ),
        affected_identifiers=(),
        expected_value={
            "gate_ids": list(completeness.expected_gate_ids),
            "relationship_check_ids": list(completeness.expected_check_ids),
        },
        actual_value={
            "gate_ids": list(completeness.actual_gate_ids),
            "relationship_check_ids": list(completeness.actual_check_ids),
            "issues": [issue.to_dict() for issue in completeness.issues],
        },
        review_owner="evaluator_maintainer",
        evaluator_version=PACKAGE_EVALUATOR_VERSION,
        evidence=(),
    )


def _gate_result_summary(result: PackageGateResult) -> Mapping[str, Any]:
    return {
        "gate_id": result.gate_id,
        "gate_version": result.gate_version,
        "kind": result.kind,
        "status": result.status,
        "summary": result.summary,
        "finding_ids": [finding.finding_id for finding in result.findings],
        "evidence": [locator.to_dict() for locator in result.evidence],
        "blocked_by": list(result.blocked_by),
    }


def _relationship_result_summary(
    result: RelationshipCheckResult,
) -> Mapping[str, Any]:
    return {
        "check_id": result.check_id,
        "check_version": result.check_version,
        "status": result.status,
        "summary": result.summary,
        "finding_ids": [finding.finding_id for finding in result.findings],
        "evidence": [locator.to_dict() for locator in result.evidence],
        "blocked_by": list(result.blocked_by),
    }


def _authority_map_version(
    gate_evaluation: PackageGateEvaluation,
) -> str | None:
    if gate_evaluation.sources is None:
        return None
    authority = gate_evaluation.sources.documents.get("authority_map")
    if not isinstance(authority, Mapping):
        return None
    version = authority.get("schema_version")
    return version if isinstance(version, str) else None


def _build_run_metadata(
    started_at: datetime,
    completed_at: datetime,
    *,
    host_metadata: Mapping[str, str] | None,
    output_location: str | None,
) -> PackageRunMetadata:
    for label, value in (("started_at", started_at), ("completed_at", completed_at)):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{label} must be timezone-aware")
    if completed_at < started_at:
        raise ValueError("completed_at cannot precede started_at")
    duration_ms = round((completed_at - started_at).total_seconds() * 1000)
    return PackageRunMetadata(
        started_at=_format_datetime(started_at),
        completed_at=_format_datetime(completed_at),
        duration_ms=duration_ms,
        host=dict(host_metadata or {}),
        output_location=output_location,
    )


def _format_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def _finding_sort_key(finding: CanonicalPackageFinding) -> tuple[int, int, str]:
    state_order = PACKAGE_STATE_PRECEDENCE.index(finding.result_state)
    control_order = {
        control_id: index
        for index, control_id in enumerate(
            (*PACKAGE_GATE_ORDER, *RELATIONSHIP_CHECK_ORDER, "package_result_router")
        )
    }
    return (
        state_order,
        control_order.get(finding.control_id, len(control_order)),
        finding.finding_id,
    )
