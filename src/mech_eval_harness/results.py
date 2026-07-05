"""Versioned, JSON-serializable evaluation result records."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mech_eval_harness.evaluation import CheckResult, GateResult
from mech_eval_harness.scoring import FailureEvidence, ScoringResult
from mech_eval_harness.validator import LoadedCase


RESULT_SCHEMA_VERSION = "1.0"
_SCORE_TOLERANCE = 1e-12
_WEIGHT_TOLERANCE = 1e-9


class ResultModelError(ValueError):
    """Raised when a result record is internally inconsistent."""


@dataclass(frozen=True)
class ArtifactReference:
    """Reference to an artifact used by an evaluation run."""

    role: str
    path: str
    artifact_id: str | None
    media_type: str | None

    def __post_init__(self) -> None:
        if self.role not in {"candidate", "reference"}:
            raise ResultModelError(
                "Artifact role must be 'candidate' or 'reference'."
            )

        _require_non_empty_string(self.path, "artifact path")

        if self.artifact_id is not None:
            _require_non_empty_string(
                self.artifact_id,
                "artifact_id",
            )

        if self.media_type is not None:
            _require_non_empty_string(
                self.media_type,
                "artifact media_type",
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "path": self.path,
            "artifact_id": self.artifact_id,
            "media_type": self.media_type,
        }


@dataclass(frozen=True)
class GateResultRecord:
    """Serializable mandatory-gate result."""

    gate_id: str
    kind: str
    passed: bool
    failure_mode: str | None
    evidence: str
    source_reference: str | None = None
    evidence_location: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        _validate_outcome_fields(
            item_type="gate",
            item_id=self.gate_id,
            kind=self.kind,
            passed=self.passed,
            failure_mode=self.failure_mode,
            evidence=self.evidence,
        )

    @classmethod
    def from_result(
        cls,
        result: GateResult,
    ) -> GateResultRecord:
        return cls(
            gate_id=result.gate_id,
            kind=result.kind,
            passed=result.passed,
            failure_mode=result.failure_mode,
            evidence=result.evidence,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "kind": self.kind,
            "passed": self.passed,
            "failure_mode": self.failure_mode,
            "evidence": self.evidence,
            "source_reference": self.source_reference,
            "evidence_location": self.evidence_location,
        }


@dataclass(frozen=True)
class CheckResultRecord:
    """Serializable deterministic-check result."""

    check_id: str
    kind: str
    passed: bool
    weight: float
    failure_mode: str | None
    actual_path: str
    expected_path: str
    actual: Any
    expected: Any
    evidence: str
    source_reference: str | None = None
    evidence_location: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        _validate_outcome_fields(
            item_type="check",
            item_id=self.check_id,
            kind=self.kind,
            passed=self.passed,
            failure_mode=self.failure_mode,
            evidence=self.evidence,
        )

        if (
            not _is_finite_number(self.weight)
            or self.weight <= 0
            or self.weight > 1
        ):
            raise ResultModelError(
                f"Check '{self.check_id}' has an invalid weight."
            )

        _require_non_empty_string(
            self.actual_path,
            "actual_path",
        )
        _require_non_empty_string(
            self.expected_path,
            "expected_path",
        )

    @classmethod
    def from_result(
        cls,
        result: CheckResult,
    ) -> CheckResultRecord:
        return cls(
            check_id=result.check_id,
            kind=result.kind,
            passed=result.passed,
            weight=result.weight,
            failure_mode=result.failure_mode,
            actual_path=result.actual_path,
            expected_path=result.expected_path,
            actual=result.actual,
            expected=result.expected,
            evidence=result.evidence,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "kind": self.kind,
            "passed": self.passed,
            "weight": self.weight,
            "failure_mode": self.failure_mode,
            "actual_path": self.actual_path,
            "expected_path": self.expected_path,
            "actual": self.actual,
            "expected": self.expected,
            "evidence": self.evidence,
            "source_reference": self.source_reference,
            "evidence_location": self.evidence_location,
        }


@dataclass(frozen=True)
class FailureEvidenceRecord:
    """Serializable evidence for one failed gate or check."""

    source: str
    item_id: str
    kind: str
    failure_mode: str
    evidence: str
    weight: float | None
    source_reference: str | None = None
    evidence_location: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if self.source not in {"gate", "check"}:
            raise ResultModelError(
                "Failure source must be 'gate' or 'check'."
            )

        _require_non_empty_string(self.item_id, "failure item_id")
        _require_non_empty_string(self.kind, "failure kind")
        _require_non_empty_string(
            self.failure_mode,
            "failure_mode",
        )
        _require_non_empty_string(self.evidence, "failure evidence")

        if self.source == "gate" and self.weight is not None:
            raise ResultModelError(
                "Gate failure evidence must not have a weight."
            )

        if self.source == "check":
            if (
                not _is_finite_number(self.weight)
                or self.weight <= 0
                or self.weight > 1
            ):
                raise ResultModelError(
                    "Check failure evidence must have a valid weight."
                )

    @classmethod
    def from_evidence(
        cls,
        failure: FailureEvidence,
    ) -> FailureEvidenceRecord:
        return cls(
            source=failure.source,
            item_id=failure.item_id,
            kind=failure.kind,
            failure_mode=failure.failure_mode,
            evidence=failure.evidence,
            weight=failure.weight,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "item_id": self.item_id,
            "kind": self.kind,
            "failure_mode": self.failure_mode,
            "evidence": self.evidence,
            "weight": self.weight,
            "source_reference": self.source_reference,
            "evidence_location": self.evidence_location,
        }


@dataclass(frozen=True)
class EvaluationResultRecord:
    """Complete structured result for one evaluation run."""

    schema_version: str
    run_id: str
    created_at: str
    harness_version: str
    case_id: str
    workflow_id: str
    task_id: str
    environment_id: str
    evaluator_id: str
    candidate_id: str | None
    component_versions: dict[str, str | None]
    artifacts: tuple[ArtifactReference, ...]
    passed: bool
    score: float
    pass_threshold: float
    gate_passed: bool
    passed_weight: float
    total_weight: float
    gates: tuple[GateResultRecord, ...]
    checks: tuple[CheckResultRecord, ...]
    failures: tuple[FailureEvidenceRecord, ...]

    def __post_init__(self) -> None:
        self._validate_identifiers()
        self._validate_versions()
        self._validate_timestamp()
        self._validate_artifacts()
        self._validate_scoring()
        self._validate_failures()

    def _validate_identifiers(self) -> None:
        if self.schema_version != RESULT_SCHEMA_VERSION:
            raise ResultModelError(
                f"Result schema_version must be "
                f"'{RESULT_SCHEMA_VERSION}'."
            )

        for label, value in (
            ("run_id", self.run_id),
            ("harness_version", self.harness_version),
            ("case_id", self.case_id),
            ("workflow_id", self.workflow_id),
            ("task_id", self.task_id),
            ("environment_id", self.environment_id),
            ("evaluator_id", self.evaluator_id),
        ):
            _require_non_empty_string(value, label)

        if self.candidate_id is not None:
            _require_non_empty_string(
                self.candidate_id,
                "candidate_id",
            )

    def _validate_versions(self) -> None:
        expected_keys = {
            "case",
            "task",
            "environment",
            "evaluator",
            "candidate",
        }

        if set(self.component_versions) != expected_keys:
            raise ResultModelError(
                "component_versions must contain exactly: "
                "case, task, environment, evaluator, candidate."
            )

        for component, version in self.component_versions.items():
            if component == "candidate" and version is None:
                continue

            if version is None:
                raise ResultModelError(
                    f"Component version '{component}' is required."
                )

            _require_non_empty_string(
                version,
                f"{component} component version",
            )

    def _validate_timestamp(self) -> None:
        timestamp = self.created_at

        if timestamp.endswith("Z"):
            timestamp = timestamp[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(timestamp)
        except ValueError as exc:
            raise ResultModelError(
                "created_at must be an ISO-8601 timestamp."
            ) from exc

        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ResultModelError(
                "created_at must include a timezone."
            )

    def _validate_artifacts(self) -> None:
        roles = [artifact.role for artifact in self.artifacts]

        if roles.count("candidate") != 1:
            raise ResultModelError(
                "Exactly one candidate artifact is required."
            )

        if roles.count("reference") != 1:
            raise ResultModelError(
                "Exactly one reference artifact is required."
            )

    def _validate_scoring(self) -> None:
        for label, value in (
            ("score", self.score),
            ("pass_threshold", self.pass_threshold),
            ("passed_weight", self.passed_weight),
            ("total_weight", self.total_weight),
        ):
            if (
                not _is_finite_number(value)
                or value < 0
                or value > 1
            ):
                raise ResultModelError(
                    f"{label} must be a finite number from 0 to 1."
                )

        if not math.isclose(
            self.total_weight,
            1.0,
            rel_tol=0.0,
            abs_tol=_WEIGHT_TOLERANCE,
        ):
            raise ResultModelError(
                "total_weight must equal 1.0."
            )

        derived_gate_passed = all(
            gate.passed
            for gate in self.gates
        )

        if self.gate_passed != derived_gate_passed:
            raise ResultModelError(
                "gate_passed does not match the gate results."
            )

        if self.gate_passed and not self.checks:
            raise ResultModelError(
                "Check results are required when all gates pass."
            )

        if not self.gate_passed and self.checks:
            raise ResultModelError(
                "Checks must not run after a mandatory gate fails."
            )

        derived_passed_weight = math.fsum(
            check.weight
            for check in self.checks
            if check.passed
        )

        if not math.isclose(
            self.passed_weight,
            derived_passed_weight,
            rel_tol=0.0,
            abs_tol=_WEIGHT_TOLERANCE,
        ):
            raise ResultModelError(
                "passed_weight does not match the passed checks."
            )

        if self.checks:
            derived_total_weight = math.fsum(
                check.weight
                for check in self.checks
            )

            if not math.isclose(
                self.total_weight,
                derived_total_weight,
                rel_tol=0.0,
                abs_tol=_WEIGHT_TOLERANCE,
            ):
                raise ResultModelError(
                    "total_weight does not match the check weights."
                )

        expected_score = (
            self.passed_weight
            if self.gate_passed
            else 0.0
        )

        if not math.isclose(
            self.score,
            expected_score,
            rel_tol=0.0,
            abs_tol=_SCORE_TOLERANCE,
        ):
            raise ResultModelError(
                "score does not match gate and check results."
            )

        expected_passed = (
            self.gate_passed
            and (
                self.score >= self.pass_threshold
                or math.isclose(
                    self.score,
                    self.pass_threshold,
                    rel_tol=0.0,
                    abs_tol=_SCORE_TOLERANCE,
                )
            )
        )

        if self.passed != expected_passed:
            raise ResultModelError(
                "passed does not match score and pass_threshold."
            )

    def _validate_failures(self) -> None:
        expected: list[
            tuple[str, str, str, str, str, float | None]
        ] = []

        for gate in self.gates:
            if not gate.passed:
                expected.append(
                    (
                        "gate",
                        gate.gate_id,
                        gate.kind,
                        _required_failure_mode(
                            gate.failure_mode
                        ),
                        gate.evidence,
                        None,
                    )
                )

        for check in self.checks:
            if not check.passed:
                expected.append(
                    (
                        "check",
                        check.check_id,
                        check.kind,
                        _required_failure_mode(
                            check.failure_mode
                        ),
                        check.evidence,
                        check.weight,
                    )
                )

        actual = [
            (
                failure.source,
                failure.item_id,
                failure.kind,
                failure.failure_mode,
                failure.evidence,
                failure.weight,
            )
            for failure in self.failures
        ]

        if actual != expected:
            raise ResultModelError(
                "failures do not match failed gates and checks."
            )

    def to_dict(self) -> dict[str, Any]:
        document = {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "created_at": self.created_at,
            "harness_version": self.harness_version,
            "case_id": self.case_id,
            "workflow_id": self.workflow_id,
            "task_id": self.task_id,
            "environment_id": self.environment_id,
            "evaluator_id": self.evaluator_id,
            "candidate_id": self.candidate_id,
            "component_versions": dict(self.component_versions),
            "artifacts": [
                artifact.to_dict()
                for artifact in self.artifacts
            ],
            "passed": self.passed,
            "score": self.score,
            "pass_threshold": self.pass_threshold,
            "gate_passed": self.gate_passed,
            "passed_weight": self.passed_weight,
            "total_weight": self.total_weight,
            "gates": [
                gate.to_dict()
                for gate in self.gates
            ],
            "checks": [
                check.to_dict()
                for check in self.checks
            ],
            "failures": [
                failure.to_dict()
                for failure in self.failures
            ],
        }

        try:
            encoded = json.dumps(
                document,
                allow_nan=False,
                ensure_ascii=False,
            )
        except (TypeError, ValueError) as exc:
            raise ResultModelError(
                "Result contains a value that is not JSON serializable."
            ) from exc

        return json.loads(encoded)


def build_evaluation_result(
    *,
    run_id: str,
    created_at: datetime,
    harness_version: str,
    loaded_case: LoadedCase,
    candidate_id: str | None,
    candidate_schema_version: str | None,
    candidate_path: Path,
    reference_path: Path,
    gate_results: Sequence[GateResult],
    check_results: Sequence[CheckResult],
    scoring_result: ScoringResult,
) -> EvaluationResultRecord:
    """Build a result record from current evaluation outputs."""

    if (
        created_at.tzinfo is None
        or created_at.utcoffset() is None
    ):
        raise ResultModelError(
            "created_at must be timezone-aware."
        )

    created_at_text = (
        created_at
        .astimezone(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )

    return EvaluationResultRecord(
        schema_version=RESULT_SCHEMA_VERSION,
        run_id=run_id,
        created_at=created_at_text,
        harness_version=harness_version,
        case_id=loaded_case.case["case_id"],
        workflow_id=loaded_case.case["workflow_id"],
        task_id=loaded_case.task["task_id"],
        environment_id=loaded_case.environment["environment_id"],
        evaluator_id=loaded_case.evaluator["evaluator_id"],
        candidate_id=candidate_id,
        component_versions={
            "case": loaded_case.case["schema_version"],
            "task": loaded_case.task["schema_version"],
            "environment": loaded_case.environment["schema_version"],
            "evaluator": loaded_case.evaluator["schema_version"],
            "candidate": candidate_schema_version,
        },
        artifacts=(
            ArtifactReference(
                role="candidate",
                path=str(candidate_path),
                artifact_id=candidate_id,
                media_type="application/json",
            ),
            ArtifactReference(
                role="reference",
                path=str(reference_path),
                artifact_id=None,
                media_type="application/json",
            ),
        ),
        passed=scoring_result.passed,
        score=scoring_result.score,
        pass_threshold=scoring_result.pass_threshold,
        gate_passed=scoring_result.gate_passed,
        passed_weight=scoring_result.passed_weight,
        total_weight=scoring_result.total_weight,
        gates=tuple(
            GateResultRecord.from_result(result)
            for result in gate_results
        ),
        checks=tuple(
            CheckResultRecord.from_result(result)
            for result in check_results
        ),
        failures=tuple(
            FailureEvidenceRecord.from_evidence(failure)
            for failure in scoring_result.failures
        ),
    )


def _validate_outcome_fields(
    *,
    item_type: str,
    item_id: str,
    kind: str,
    passed: bool,
    failure_mode: str | None,
    evidence: str,
) -> None:
    _require_non_empty_string(item_id, f"{item_type}_id")
    _require_non_empty_string(kind, f"{item_type} kind")
    _require_non_empty_string(evidence, f"{item_type} evidence")

    if passed:
        if failure_mode is not None:
            raise ResultModelError(
                f"Passed {item_type} '{item_id}' "
                "must not have a failure mode."
            )
    else:
        if failure_mode is None:
            raise ResultModelError(
                f"Failed {item_type} '{item_id}' "
                "must have a failure mode."
            )

        _require_non_empty_string(
            failure_mode,
            f"{item_type} failure_mode",
        )


def _required_failure_mode(
    failure_mode: str | None,
) -> str:
    if failure_mode is None:
        raise ResultModelError(
            "Failed result is missing its failure mode."
        )

    return failure_mode


def _require_non_empty_string(
    value: object,
    label: str,
) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ResultModelError(
            f"{label} must be a non-empty string."
        )


def _is_finite_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )
