from __future__ import annotations

import pytest

from mech_eval_harness.evaluation import (
    CheckConfigurationError,
    run_deterministic_checks,
)


def _check(
    kind: str,
    *,
    actual_path: str = "$.value",
    expected_path: str = "$.value",
) -> dict:
    return {
        "check_id": "test_check",
        "kind": kind,
        "actual_path": actual_path,
        "expected_path": expected_path,
        "weight": 0.5,
        "failure_mode": "TEST_FAILURE",
    }


def _evaluator(check: dict) -> dict:
    return {"checks": [check]}


def test_exact_match_passes_for_identical_values() -> None:
    results = run_deterministic_checks(
        {"value": "REV-C"},
        {"value": "REV-C"},
        _evaluator(_check("exact_match")),
    )

    assert results[0].passed is True
    assert results[0].failure_mode is None
    assert results[0].actual == "REV-C"
    assert results[0].expected == "REV-C"


def test_exact_match_is_type_sensitive() -> None:
    results = run_deterministic_checks(
        {"value": True},
        {"value": 1},
        _evaluator(_check("exact_match")),
    )

    assert results[0].passed is False
    assert results[0].failure_mode == "TEST_FAILURE"


def test_boolean_equals_rejects_string_boolean() -> None:
    results = run_deterministic_checks(
        {"value": "true"},
        {"value": True},
        _evaluator(_check("boolean_equals")),
    )

    assert results[0].passed is False
    assert "found string" in results[0].evidence


def test_set_equals_ignores_order_and_duplicates() -> None:
    results = run_deterministic_checks(
        {"value": ["WRONG_REVISION", "MISSING_NOTE", "WRONG_REVISION"]},
        {"value": ["MISSING_NOTE", "WRONG_REVISION"]},
        _evaluator(_check("set_equals")),
    )

    assert results[0].passed is True


def test_set_equals_reports_missing_and_unexpected_items() -> None:
    results = run_deterministic_checks(
        {"value": ["WRONG_REVISION", "EXTRA_CODE"]},
        {"value": ["WRONG_REVISION", "MISSING_NOTE"]},
        _evaluator(_check("set_equals")),
    )

    assert results[0].passed is False
    assert "MISSING_NOTE" in results[0].evidence
    assert "EXTRA_CODE" in results[0].evidence


def test_contains_all_allows_extra_items() -> None:
    results = run_deterministic_checks(
        {"value": ["A", "B", "C"]},
        {"value": ["A", "C"]},
        _evaluator(_check("contains_all")),
    )

    assert results[0].passed is True


def test_contains_all_reports_missing_items() -> None:
    results = run_deterministic_checks(
        {"value": ["A"]},
        {"value": ["A", "B"]},
        _evaluator(_check("contains_all")),
    )

    assert results[0].passed is False
    assert '"B"' in results[0].evidence


def test_missing_actual_path_returns_failed_result() -> None:
    results = run_deterministic_checks(
        {},
        {"value": "REV-C"},
        _evaluator(_check("exact_match")),
    )

    assert results[0].passed is False
    assert results[0].actual is None
    assert "was not found" in results[0].evidence


def test_missing_expected_path_is_configuration_error() -> None:
    with pytest.raises(
        CheckConfigurationError,
        match="was not found in the reference",
    ):
        run_deterministic_checks(
            {"value": "REV-C"},
            {},
            _evaluator(_check("exact_match")),
        )

def test_missing_required_check_field_is_configuration_error() -> None:
    check = _check("exact_match")
    del check["expected_path"]

    with pytest.raises(
        CheckConfigurationError,
        match="missing required fields: expected_path",
    ):
        run_deterministic_checks(
            {"value": "REV-C"},
            {"value": "REV-C"},
            _evaluator(check),
        )


def test_nested_paths_are_resolved() -> None:
    results = run_deterministic_checks(
        {"result": {"revision": "REV-C"}},
        {"approved": {"revision": "REV-C"}},
        _evaluator(
            _check(
                "exact_match",
                actual_path="$.result.revision",
                expected_path="$.approved.revision",
            )
        ),
    )

    assert results[0].passed is True
    assert results[0].actual == "REV-C"
    assert results[0].expected == "REV-C"