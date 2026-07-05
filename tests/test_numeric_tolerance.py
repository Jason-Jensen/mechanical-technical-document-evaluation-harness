from __future__ import annotations

import pytest

from mech_eval_harness.evaluation import (
    CheckConfigurationError,
    run_deterministic_checks,
)


def _numeric_check() -> dict:
    return {
        "check_id": "numeric_test",
        "kind": "numeric_close",
        "actual_path": "$.value",
        "expected_path": "$.value",
        "absolute_tolerance": 0.05,
        "weight": 0.5,
        "failure_mode": "NUMERIC_ERROR",
    }


def _evaluator(check: dict) -> dict:
    return {"checks": [check]}


def test_numeric_close_passes_within_tolerance() -> None:
    results = run_deterministic_checks(
        {"value": 10.04},
        {"value": 10.0},
        _evaluator(_numeric_check()),
    )

    assert results[0].passed is True
    assert results[0].failure_mode is None
    assert "absolute difference 0.04" in results[0].evidence
    assert "tolerance 0.05" in results[0].evidence


def test_numeric_close_passes_exact_tolerance_boundary() -> None:
    check = _numeric_check()
    check["absolute_tolerance"] = 0.5

    results = run_deterministic_checks(
        {"value": 10.5},
        {"value": 10.0},
        _evaluator(check),
    )

    assert results[0].passed is True
    assert "absolute difference 0.5" in results[0].evidence
    assert "tolerance 0.5" in results[0].evidence


def test_numeric_close_fails_outside_tolerance() -> None:
    check = _numeric_check()
    check["absolute_tolerance"] = 0.5

    results = run_deterministic_checks(
        {"value": 10.51},
        {"value": 10.0},
        _evaluator(check),
    )

    assert results[0].passed is False
    assert results[0].failure_mode == "NUMERIC_ERROR"
    assert "absolute difference 0.51" in results[0].evidence
    assert "tolerance 0.5" in results[0].evidence


def test_numeric_close_accepts_integer_and_float_values() -> None:
    check = _numeric_check()
    check["absolute_tolerance"] = 0

    results = run_deterministic_checks(
        {"value": 10},
        {"value": 10.0},
        _evaluator(check),
    )

    assert results[0].passed is True


def test_numeric_close_rejects_boolean_candidate_value() -> None:
    check = _numeric_check()
    check["absolute_tolerance"] = 0

    results = run_deterministic_checks(
        {"value": True},
        {"value": 1.0},
        _evaluator(check),
    )

    assert results[0].passed is False
    assert results[0].failure_mode == "NUMERIC_ERROR"
    assert "finite number" in results[0].evidence
    assert "boolean" in results[0].evidence


def test_numeric_close_rejects_boolean_reference_value() -> None:
    with pytest.raises(
        CheckConfigurationError,
        match="expected value must be a finite number",
    ):
        run_deterministic_checks(
            {"value": 1.0},
            {"value": True},
            _evaluator(_numeric_check()),
        )


def test_numeric_close_requires_absolute_tolerance() -> None:
    check = _numeric_check()
    del check["absolute_tolerance"]

    with pytest.raises(
        CheckConfigurationError,
        match="requires 'absolute_tolerance'",
    ):
        run_deterministic_checks(
            {"value": 10.0},
            {"value": 10.0},
            _evaluator(check),
        )


@pytest.mark.parametrize(
    "invalid_tolerance",
    [
        True,
        -0.1,
        float("inf"),
        float("nan"),
    ],
    ids=[
        "boolean",
        "negative",
        "infinite",
        "nan",
    ],
)
def test_numeric_close_rejects_invalid_tolerance(
    invalid_tolerance: object,
) -> None:
    check = _numeric_check()
    check["absolute_tolerance"] = invalid_tolerance

    with pytest.raises(
        CheckConfigurationError,
        match="finite non-negative number",
    ):
        run_deterministic_checks(
            {"value": 10.0},
            {"value": 10.0},
            _evaluator(check),
        )