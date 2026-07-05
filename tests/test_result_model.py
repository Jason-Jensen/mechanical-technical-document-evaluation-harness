from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from mech_eval_harness.evaluation import (
    run_deterministic_checks,
    run_mandatory_gates,
)
from mech_eval_harness.results import (
    ResultModelError,
    build_evaluation_result,
)
from mech_eval_harness.scoring import score_evaluation
from mech_eval_harness.validator import (
    load_case_by_id,
    load_candidate,
    load_json,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_CANDIDATE = (
    ROOT
    / "examples"
    / "candidates"
    / "MECH-002"
    / "valid.json"
)
RESULT_SCHEMA = ROOT / "schemas" / "result.schema.json"
CREATED_AT = datetime(
    2026,
    7,
    5,
    20,
    29,
    tzinfo=timezone.utc,
)


def _assert_schema_valid(document: dict) -> None:
    schema = json.loads(
        RESULT_SCHEMA.read_text(encoding="utf-8")
    )

    Draft202012Validator.check_schema(schema)

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )
    errors = sorted(
        validator.iter_errors(document),
        key=lambda error: list(error.path),
    )

    assert errors == []


def _build_result(
    candidate_path: Path,
):
    loaded_case = load_case_by_id(ROOT, "MECH-002")

    reference_path = (
        ROOT
        / loaded_case.case["reference_dir"]
        / loaded_case.evaluator["reference_file"]
    )

    gate_results = run_mandatory_gates(
        candidate_path,
        loaded_case.task,
        loaded_case.evaluator,
    )

    check_results = []
    candidate_id = None
    candidate_schema_version = None

    if all(result.passed for result in gate_results):
        loaded_candidate = load_candidate(
            ROOT,
            candidate_path,
            expected_case_id="MECH-002",
        )

        candidate_id = loaded_candidate.candidate["candidate_id"]
        candidate_schema_version = (
            loaded_candidate.candidate["schema_version"]
        )

        check_results = run_deterministic_checks(
            loaded_candidate.payload,
            load_json(reference_path),
            loaded_case.evaluator,
        )

    scoring_result = score_evaluation(
        loaded_case.evaluator,
        gate_results,
        check_results,
    )

    return build_evaluation_result(
        run_id="RUN-20260705-001",
        created_at=CREATED_AT,
        harness_version="0.2.0",
        loaded_case=loaded_case,
        candidate_id=candidate_id,
        candidate_schema_version=candidate_schema_version,
        candidate_path=candidate_path,
        reference_path=reference_path,
        gate_results=gate_results,
        check_results=check_results,
        scoring_result=scoring_result,
    )


def test_passing_result_validates_against_schema() -> None:
    result = _build_result(VALID_CANDIDATE)
    document = result.to_dict()

    _assert_schema_valid(document)

    assert document["passed"] is True
    assert document["score"] == 1.0
    assert document["candidate_id"] == "mech-002-valid-001"
    assert len(document["gates"]) == 4
    assert len(document["checks"]) == 5
    assert document["failures"] == []


def test_result_preserves_actual_and_expected_json_values() -> None:
    result = _build_result(VALID_CANDIDATE)
    document = result.to_dict()

    shaft_power = next(
        check
        for check in document["checks"]
        if check["check_id"] == "shaft_power"
    )
    verification = next(
        check
        for check in document["checks"]
        if check["check_id"] == "verification"
    )

    assert shaft_power["actual"] == 21.9911
    assert shaft_power["expected"] == 21.9911
    assert verification["actual"] is True
    assert verification["expected"] is True


def test_failed_check_result_validates_against_schema(
    tmp_path: Path,
) -> None:
    candidate = json.loads(
        VALID_CANDIDATE.read_text(encoding="utf-8")
    )
    candidate["candidate_id"] = "mech-002-failed-result"
    candidate["payload"]["shaft_power_kw"] = 999.0

    candidate_path = tmp_path / "failed-check.json"
    candidate_path.write_text(
        json.dumps(candidate),
        encoding="utf-8",
    )

    result = _build_result(candidate_path)
    document = result.to_dict()

    _assert_schema_valid(document)

    assert document["passed"] is False
    assert document["score"] == 0.65
    assert document["gate_passed"] is True
    assert len(document["failures"]) == 1
    assert document["failures"][0]["source"] == "check"
    assert document["failures"][0]["item_id"] == "shaft_power"
    assert (
        document["failures"][0]["failure_mode"]
        == "WRONG_FORMULA"
    )


def test_failed_gate_result_validates_against_schema(
    tmp_path: Path,
) -> None:
    missing_candidate = tmp_path / "missing.json"

    result = _build_result(missing_candidate)
    document = result.to_dict()

    _assert_schema_valid(document)

    assert document["passed"] is False
    assert document["score"] == 0.0
    assert document["gate_passed"] is False
    assert document["candidate_id"] is None
    assert document["component_versions"]["candidate"] is None
    assert document["checks"] == []
    assert len(document["failures"]) == 1
    assert document["failures"][0]["source"] == "gate"


def test_result_is_json_serializable() -> None:
    result = _build_result(VALID_CANDIDATE)

    encoded = json.dumps(
        result.to_dict(),
        allow_nan=False,
    )

    decoded = json.loads(encoded)

    assert decoded["schema_version"] == "1.0"
    assert decoded["run_id"] == "RUN-20260705-001"


def test_inconsistent_pass_state_is_rejected(
    tmp_path: Path,
) -> None:
    failed_result = _build_result(
        tmp_path / "missing.json"
    )

    with pytest.raises(
        ResultModelError,
        match="passed does not match",
    ):
        replace(
            failed_result,
            passed=True,
        )


def test_inconsistent_score_is_rejected() -> None:
    passing_result = _build_result(VALID_CANDIDATE)

    with pytest.raises(
        ResultModelError,
        match="score does not match",
    ):
        replace(
            passing_result,
            score=0.5,
        )


def test_naive_created_at_is_rejected() -> None:
    loaded_case = load_case_by_id(ROOT, "MECH-002")

    with pytest.raises(
        ResultModelError,
        match="timezone-aware",
    ):
        build_evaluation_result(
            run_id="RUN-INVALID-TIME",
            created_at=datetime(2026, 7, 5, 20, 29),
            harness_version="0.2.0",
            loaded_case=loaded_case,
            candidate_id=None,
            candidate_schema_version=None,
            candidate_path=VALID_CANDIDATE,
            reference_path=(
                ROOT
                / loaded_case.case["reference_dir"]
                / loaded_case.evaluator["reference_file"]
            ),
            gate_results=[],
            check_results=[],
            scoring_result=score_evaluation(
                loaded_case.evaluator,
                [
                    run_mandatory_gates(
                        ROOT / "does-not-exist.json",
                        loaded_case.task,
                        loaded_case.evaluator,
                    )[0]
                ],
                [],
            ),
        )


def test_schema_rejects_unknown_top_level_property() -> None:
    result = _build_result(VALID_CANDIDATE)
    document = result.to_dict()
    document["unexpected"] = True

    schema = json.loads(
        RESULT_SCHEMA.read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)

    messages = [
        error.message
        for error in validator.iter_errors(document)
    ]

    assert any(
        "Additional properties are not allowed" in message
        for message in messages
    )
