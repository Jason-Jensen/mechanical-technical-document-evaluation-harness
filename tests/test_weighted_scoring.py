from __future__ import annotations

from dataclasses import replace

import pytest

from mech_eval_harness.evaluation import CheckResult, GateResult
from mech_eval_harness.scoring import (
    ScoringConfigurationError,
    score_evaluation,
)


def _evaluator(
    *,
    pass_threshold: float = 0.95,
    first_weight: float = 0.6,
    second_weight: float = 0.4,
) -> dict:
    return {
        "composition": "gate_then_weighted_checks",
        "pass_threshold": pass_threshold,
        "checks": [
            {
                "check_id": "first_check",
                "kind": "exact_match",
                "weight": first_weight,
                "failure_mode": "FIRST_FAILURE",
            },
            {
                "check_id": "second_check",
                "kind": "boolean_equals",
                "weight": second_weight,
                "failure_mode": "SECOND_FAILURE",
            },
        ],
    }


def _gate_result(
    *,
    passed: bool = True,
    gate_id: str = "required_fields",
) -> GateResult:
    return GateResult(
        gate_id=gate_id,
        kind="required_fields_present",
        passed=passed,
        failure_mode=None if passed else "INCOMPLETE_DELIVERABLE",
        evidence=(
            "Gate passed."
            if passed
            else "Required candidate field is missing."
        ),
    )


def _check_results(
    evaluator: dict,
    *,
    first_passed: bool = True,
    second_passed: bool = True,
) -> list[CheckResult]:
    results: list[CheckResult] = []

    for configured, passed in zip(
        evaluator["checks"],
        (first_passed, second_passed),
        strict=True,
    ):
        results.append(
            CheckResult(
                check_id=configured["check_id"],
                kind=configured["kind"],
                passed=passed,
                weight=configured["weight"],
                failure_mode=(
                    None
                    if passed
                    else configured["failure_mode"]
                ),
                actual_path="$.value",
                expected_path="$.value",
                actual="actual",
                expected="expected",
                evidence=(
                    "Check passed."
                    if passed
                    else "Actual value does not match expected value."
                ),
            )
        )

    return results


def test_all_checks_pass_with_full_score() -> None:
    evaluator = _evaluator()

    result = score_evaluation(
        evaluator,
        [_gate_result()],
        _check_results(evaluator),
    )

    assert result.passed is True
    assert result.gate_passed is True
    assert result.score == pytest.approx(1.0)
    assert result.passed_weight == pytest.approx(1.0)
    assert result.total_weight == pytest.approx(1.0)
    assert result.pass_threshold == pytest.approx(0.95)
    assert result.failures == ()


def test_threshold_can_pass_with_low_weight_failure() -> None:
    evaluator = _evaluator(
        pass_threshold=0.95,
        first_weight=0.95,
        second_weight=0.05,
    )

    result = score_evaluation(
        evaluator,
        [_gate_result()],
        _check_results(
            evaluator,
            first_passed=True,
            second_passed=False,
        ),
    )

    assert result.score == pytest.approx(0.95)
    assert result.passed is True
    assert len(result.failures) == 1
    assert result.failures[0].item_id == "second_check"
    assert result.failures[0].weight == pytest.approx(0.05)


def test_score_below_threshold_fails() -> None:
    evaluator = _evaluator(
        pass_threshold=0.95,
        first_weight=0.9,
        second_weight=0.1,
    )

    result = score_evaluation(
        evaluator,
        [_gate_result()],
        _check_results(
            evaluator,
            first_passed=True,
            second_passed=False,
        ),
    )

    assert result.score == pytest.approx(0.9)
    assert result.passed is False
    assert result.failures[0].failure_mode == "SECOND_FAILURE"


def test_gate_failure_forces_zero_score() -> None:
    evaluator = _evaluator()

    result = score_evaluation(
        evaluator,
        [_gate_result(passed=False)],
        _check_results(evaluator),
    )

    assert result.gate_passed is False
    assert result.score == pytest.approx(0.0)
    assert result.passed is False
    assert result.passed_weight == pytest.approx(1.0)


def test_gate_failure_allows_no_check_results() -> None:
    evaluator = _evaluator()

    result = score_evaluation(
        evaluator,
        [_gate_result(passed=False)],
        [],
    )

    assert result.score == pytest.approx(0.0)
    assert result.passed_weight == pytest.approx(0.0)
    assert result.passed is False
    assert len(result.failures) == 1
    assert result.failures[0].source == "gate"


def test_failures_preserve_gate_then_check_order() -> None:
    evaluator = _evaluator()

    result = score_evaluation(
        evaluator,
        [_gate_result(passed=False)],
        _check_results(
            evaluator,
            first_passed=True,
            second_passed=False,
        ),
    )

    assert [failure.source for failure in result.failures] == [
        "gate",
        "check",
    ]
    assert [failure.item_id for failure in result.failures] == [
        "required_fields",
        "second_check",
    ]


def test_rejects_unsupported_composition() -> None:
    evaluator = _evaluator()
    evaluator["composition"] = "average_checks"

    with pytest.raises(
        ScoringConfigurationError,
        match="composition must be",
    ):
        score_evaluation(
            evaluator,
            [_gate_result()],
            _check_results(evaluator),
        )


@pytest.mark.parametrize(
    "invalid_threshold",
    [
        True,
        -0.1,
        1.1,
        float("inf"),
        float("nan"),
    ],
    ids=[
        "boolean",
        "negative",
        "above_one",
        "infinite",
        "nan",
    ],
)
def test_rejects_invalid_pass_threshold(
    invalid_threshold: object,
) -> None:
    evaluator = _evaluator()
    evaluator["pass_threshold"] = invalid_threshold

    with pytest.raises(
        ScoringConfigurationError,
        match="pass_threshold",
    ):
        score_evaluation(
            evaluator,
            [_gate_result()],
            _check_results(evaluator),
        )


def test_rejects_weights_not_summing_to_one() -> None:
    evaluator = _evaluator(
        first_weight=0.6,
        second_weight=0.3,
    )

    with pytest.raises(
        ScoringConfigurationError,
        match="must sum to 1.0",
    ):
        score_evaluation(
            evaluator,
            [_gate_result()],
            _check_results(evaluator),
        )


def test_rejects_mismatched_check_result_id() -> None:
    evaluator = _evaluator()
    results = _check_results(evaluator)
    results[0] = replace(
        results[0],
        check_id="wrong_check",
    )

    with pytest.raises(
        ScoringConfigurationError,
        match="expected 'first_check'",
    ):
        score_evaluation(
            evaluator,
            [_gate_result()],
            results,
        )


def test_passed_gates_require_complete_check_results() -> None:
    evaluator = _evaluator()

    with pytest.raises(
        ScoringConfigurationError,
        match="Check results are required",
    ):
        score_evaluation(
            evaluator,
            [_gate_result()],
            [],
        )


def test_failed_check_requires_failure_mode() -> None:
    evaluator = _evaluator()
    results = _check_results(
        evaluator,
        second_passed=False,
    )
    results[1] = replace(
        results[1],
        failure_mode=None,
    )

    with pytest.raises(
        ScoringConfigurationError,
        match="must have a failure mode",
    ):
        score_evaluation(
            evaluator,
            [_gate_result()],
            results,
        )


def test_failed_gate_requires_non_empty_evidence() -> None:
    evaluator = _evaluator()
    failed_gate = replace(
        _gate_result(passed=False),
        evidence="",
    )

    with pytest.raises(
        ScoringConfigurationError,
        match="non-empty evidence",
    ):
        score_evaluation(
            evaluator,
            [failed_gate],
            [],
        )