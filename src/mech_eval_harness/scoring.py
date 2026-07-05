"""Weighted scoring and failure-evidence aggregation."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from mech_eval_harness.evaluation import CheckResult, GateResult


_WEIGHT_TOLERANCE = 1e-9
_SCORE_TOLERANCE = 1e-12
_SUPPORTED_COMPOSITION = "gate_then_weighted_checks"


class ScoringConfigurationError(ValueError):
    """Raised when scoring inputs cannot be evaluated safely."""


@dataclass(frozen=True)
class FailureEvidence:
    """Auditable evidence for one failed gate or check."""

    source: str
    item_id: str
    kind: str
    failure_mode: str
    evidence: str
    weight: float | None


@dataclass(frozen=True)
class ScoringResult:
    """Aggregate weighted outcome from gate and check results."""

    passed: bool
    score: float
    pass_threshold: float
    gate_passed: bool
    passed_weight: float
    total_weight: float
    failures: tuple[FailureEvidence, ...]


def score_evaluation(
    evaluator: dict[str, Any],
    gate_results: Sequence[GateResult],
    check_results: Sequence[CheckResult],
) -> ScoringResult:
    """Aggregate gate and deterministic-check results.

    A failed mandatory gate forces the final score to zero. When all gates
    pass, each passed check contributes its evaluator-declared weight. The
    evaluation passes when the resulting score meets the declared threshold.
    """

    composition = evaluator.get("composition")

    if composition != _SUPPORTED_COMPOSITION:
        raise ScoringConfigurationError(
            (
                "Evaluator composition must be "
                f"'{_SUPPORTED_COMPOSITION}'; found "
                f"{composition!r}."
            )
        )

    pass_threshold = evaluator.get("pass_threshold")

    if (
        not _is_finite_number(pass_threshold)
        or pass_threshold < 0
        or pass_threshold > 1
    ):
        raise ScoringConfigurationError(
            "Evaluator pass_threshold must be a finite number from 0 to 1."
        )

    configured_checks = _validated_check_configuration(evaluator)
    total_weight = math.fsum(
        float(check["weight"])
        for check in configured_checks
    )

    if not math.isclose(
        total_weight,
        1.0,
        rel_tol=0.0,
        abs_tol=_WEIGHT_TOLERANCE,
    ):
        raise ScoringConfigurationError(
            (
                "Evaluator check weights must sum to 1.0; "
                f"found {total_weight:.12f}."
            )
        )

    gate_result_tuple = tuple(gate_results)
    check_result_tuple = tuple(check_results)

    for result in gate_result_tuple:
        _validate_result_evidence(
            source="gate",
            item_id=result.gate_id,
            passed=result.passed,
            failure_mode=result.failure_mode,
            evidence=result.evidence,
        )

    gate_passed = all(
        result.passed
        for result in gate_result_tuple
    )

    if check_result_tuple:
        _validate_check_results(
            configured_checks,
            check_result_tuple,
        )
    elif gate_passed:
        raise ScoringConfigurationError(
            "Check results are required when all mandatory gates pass."
        )

    if check_result_tuple:
        passed_weight = math.fsum(
            float(configured_check["weight"])
            for configured_check, result in zip(
                configured_checks,
                check_result_tuple,
                strict=True,
            )
            if result.passed
        )
    else:
        passed_weight = 0.0

    score = passed_weight if gate_passed else 0.0
    score = min(max(score, 0.0), 1.0)

    passed = gate_passed and _meets_threshold(
        score,
        float(pass_threshold),
    )

    failures = _collect_failure_evidence(
        gate_result_tuple,
        check_result_tuple,
    )

    return ScoringResult(
        passed=passed,
        score=score,
        pass_threshold=float(pass_threshold),
        gate_passed=gate_passed,
        passed_weight=passed_weight,
        total_weight=total_weight,
        failures=failures,
    )


def _validated_check_configuration(
    evaluator: dict[str, Any],
) -> tuple[dict[str, Any], ...]:
    checks = evaluator.get("checks")

    if not isinstance(checks, list) or not checks:
        raise ScoringConfigurationError(
            "Evaluator checks must be a non-empty array."
        )

    validated: list[dict[str, Any]] = []

    for index, check in enumerate(checks):
        if not isinstance(check, dict):
            raise ScoringConfigurationError(
                f"Evaluator check at index {index} must be an object."
            )

        check_id = check.get("check_id")
        kind = check.get("kind")
        failure_mode = check.get("failure_mode")
        weight = check.get("weight")

        for field_name, value in (
            ("check_id", check_id),
            ("kind", kind),
            ("failure_mode", failure_mode),
        ):
            if not isinstance(value, str) or not value:
                raise ScoringConfigurationError(
                    (
                        f"Evaluator check at index {index} has an "
                        f"invalid '{field_name}' value."
                    )
                )

        if (
            not _is_finite_number(weight)
            or weight <= 0
            or weight > 1
        ):
            raise ScoringConfigurationError(
                (
                    f"Evaluator check '{check_id}' weight must be "
                    "a finite number greater than 0 and no greater than 1."
                )
            )

        validated.append(check)

    return tuple(validated)


def _validate_check_results(
    configured_checks: tuple[dict[str, Any], ...],
    check_results: tuple[CheckResult, ...],
) -> None:
    if len(check_results) != len(configured_checks):
        raise ScoringConfigurationError(
            (
                "Check-result count does not match evaluator configuration: "
                f"expected {len(configured_checks)}, "
                f"found {len(check_results)}."
            )
        )

    for index, (configured, result) in enumerate(
        zip(configured_checks, check_results, strict=True)
    ):
        expected_check_id = configured["check_id"]
        expected_kind = configured["kind"]
        expected_weight = float(configured["weight"])

        if result.check_id != expected_check_id:
            raise ScoringConfigurationError(
                (
                    f"Check result at index {index} has check_id "
                    f"'{result.check_id}'; expected "
                    f"'{expected_check_id}'."
                )
            )

        if result.kind != expected_kind:
            raise ScoringConfigurationError(
                (
                    f"Check result '{result.check_id}' has kind "
                    f"'{result.kind}'; expected '{expected_kind}'."
                )
            )

        if not math.isclose(
            result.weight,
            expected_weight,
            rel_tol=0.0,
            abs_tol=_WEIGHT_TOLERANCE,
        ):
            raise ScoringConfigurationError(
                (
                    f"Check result '{result.check_id}' has weight "
                    f"{result.weight}; expected {expected_weight}."
                )
            )

        _validate_result_evidence(
            source="check",
            item_id=result.check_id,
            passed=result.passed,
            failure_mode=result.failure_mode,
            evidence=result.evidence,
        )


def _validate_result_evidence(
    *,
    source: str,
    item_id: str,
    passed: bool,
    failure_mode: str | None,
    evidence: str,
) -> None:
    if passed:
        if failure_mode is not None:
            raise ScoringConfigurationError(
                (
                    f"Passed {source} '{item_id}' must not have "
                    "a failure mode."
                )
            )

        return

    if not isinstance(failure_mode, str) or not failure_mode:
        raise ScoringConfigurationError(
            (
                f"Failed {source} '{item_id}' must have "
                "a failure mode."
            )
        )

    if not isinstance(evidence, str) or not evidence.strip():
        raise ScoringConfigurationError(
            (
                f"Failed {source} '{item_id}' must have "
                "non-empty evidence."
            )
        )


def _collect_failure_evidence(
    gate_results: tuple[GateResult, ...],
    check_results: tuple[CheckResult, ...],
) -> tuple[FailureEvidence, ...]:
    failures: list[FailureEvidence] = []

    for result in gate_results:
        if result.passed:
            continue

        failures.append(
            FailureEvidence(
                source="gate",
                item_id=result.gate_id,
                kind=result.kind,
                failure_mode=_required_failure_mode(result.failure_mode),
                evidence=result.evidence,
                weight=None,
            )
        )

    for result in check_results:
        if result.passed:
            continue

        failures.append(
            FailureEvidence(
                source="check",
                item_id=result.check_id,
                kind=result.kind,
                failure_mode=_required_failure_mode(result.failure_mode),
                evidence=result.evidence,
                weight=result.weight,
            )
        )

    return tuple(failures)


def _required_failure_mode(
    failure_mode: str | None,
) -> str:
    if failure_mode is None:
        raise ScoringConfigurationError(
            "Failed result is missing its failure mode."
        )

    return failure_mode


def _meets_threshold(
    score: float,
    threshold: float,
) -> bool:
    return score >= threshold or math.isclose(
        score,
        threshold,
        rel_tol=0.0,
        abs_tol=_SCORE_TOLERANCE,
    )


def _is_finite_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(value)
    )