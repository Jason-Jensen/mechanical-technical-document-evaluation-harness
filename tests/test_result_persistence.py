from __future__ import annotations

import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mech_eval_harness.evaluation import (
    run_deterministic_checks,
    run_mandatory_gates,
)
from mech_eval_harness.persistence import (
    ResultCollisionError,
    ResultPersistenceError,
    ResultSchemaValidationError,
    generate_run_id,
    validate_result_document,
    write_result_record,
)
from mech_eval_harness.results import (
    EvaluationResultRecord,
    build_evaluation_result,
)
from mech_eval_harness.scoring import score_evaluation
from mech_eval_harness.validator import (
    load_candidate,
    load_case_by_id,
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
    47,
    0,
    123456,
    tzinfo=timezone.utc,
)
RUN_ID = "RUN-20260705T204700123456Z-deadbeef"


def _build_passing_result(
    *,
    run_id: str = RUN_ID,
) -> EvaluationResultRecord:
    loaded_case = load_case_by_id(ROOT, "MECH-002")
    loaded_candidate = load_candidate(
        ROOT,
        VALID_CANDIDATE,
        expected_case_id="MECH-002",
    )

    reference_path = (
        ROOT
        / loaded_case.case["reference_dir"]
        / loaded_case.evaluator["reference_file"]
    )

    gate_results = run_mandatory_gates(
        VALID_CANDIDATE,
        loaded_case.task,
        loaded_case.evaluator,
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
        run_id=run_id,
        created_at=CREATED_AT,
        harness_version="0.2.0",
        loaded_case=loaded_case,
        candidate_id=(
            loaded_candidate.candidate["candidate_id"]
        ),
        candidate_schema_version=(
            loaded_candidate.candidate["schema_version"]
        ),
        candidate_path=VALID_CANDIDATE,
        reference_path=reference_path,
        gate_results=gate_results,
        check_results=check_results,
        scoring_result=scoring_result,
    )


def test_generate_run_id_uses_utc_and_safe_format() -> None:
    local_time = datetime(
        2026,
        7,
        5,
        14,
        47,
        0,
        123456,
        tzinfo=timezone(timedelta(hours=-6)),
    )

    run_id = generate_run_id(
        local_time,
        unique_suffix="deadbeef",
    )

    assert (
        run_id
        == "RUN-20260705T204700123456Z-deadbeef"
    )


def test_write_result_record_is_bom_free_and_schema_valid(
    tmp_path: Path,
) -> None:
    result = _build_passing_result()

    result_path = write_result_record(
        result=result,
        runs_dir=tmp_path / "runs",
        schema_path=RESULT_SCHEMA,
    )

    assert result_path == (
        tmp_path
        / "runs"
        / RUN_ID
        / "result.json"
    )
    assert result_path.is_file()

    raw = result_path.read_bytes()

    assert not raw.startswith(b"\xef\xbb\xbf")

    document = json.loads(raw.decode("utf-8"))

    validate_result_document(
        document,
        RESULT_SCHEMA,
    )

    assert document["run_id"] == RUN_ID
    assert document["passed"] is True
    assert document["score"] == 1.0


def test_existing_run_is_never_overwritten(
    tmp_path: Path,
) -> None:
    result = _build_passing_result()
    runs_dir = tmp_path / "runs"

    result_path = write_result_record(
        result=result,
        runs_dir=runs_dir,
        schema_path=RESULT_SCHEMA,
    )
    original_bytes = result_path.read_bytes()

    with pytest.raises(
        ResultCollisionError,
        match="will not be overwritten",
    ):
        write_result_record(
            result=result,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert result_path.read_bytes() == original_bytes


def test_unsafe_run_id_is_rejected_before_writing(
    tmp_path: Path,
) -> None:
    result = replace(
        _build_passing_result(),
        run_id="../escape",
    )
    runs_dir = tmp_path / "runs"

    with pytest.raises(
        ResultPersistenceError,
        match="run_id must use the format",
    ):
        write_result_record(
            result=result,
            runs_dir=runs_dir,
            schema_path=RESULT_SCHEMA,
        )

    assert not runs_dir.exists()
    assert not (tmp_path / "escape").exists()


def test_schema_invalid_document_is_rejected() -> None:
    document = _build_passing_result().to_dict()
    document["score"] = 2.0

    with pytest.raises(
        ResultSchemaValidationError,
        match="failed schema validation",
    ):
        validate_result_document(
            document,
            RESULT_SCHEMA,
        )
