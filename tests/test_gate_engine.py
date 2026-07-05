from __future__ import annotations

import json
from pathlib import Path

from mech_eval_harness.evaluation import run_mandatory_gates
from mech_eval_harness.validator import load_case_by_id


ROOT = Path(__file__).resolve().parents[1]
VALID_CANDIDATE = (
    ROOT / "examples" / "candidates" / "MECH-002" / "valid.json"
)


def _mech_002_specs() -> tuple[dict, dict]:
    loaded_case = load_case_by_id(ROOT, "MECH-002")
    return loaded_case.task, loaded_case.evaluator


def _write_modified_candidate(
    tmp_path: Path,
    *,
    field: str,
    value: object,
) -> Path:
    candidate = json.loads(
        VALID_CANDIDATE.read_text(encoding="utf-8")
    )
    candidate["payload"][field] = value

    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(
        json.dumps(candidate, indent=2) + "\n",
        encoding="utf-8",
    )
    return candidate_path


def test_valid_candidate_passes_all_mandatory_gates() -> None:
    task, evaluator = _mech_002_specs()

    results = run_mandatory_gates(
        VALID_CANDIDATE,
        task,
        evaluator,
    )

    assert [result.gate_id for result in results] == [
        "output_exists",
        "valid_json",
        "required_fields",
        "field_types",
    ]
    assert all(result.passed for result in results)
    assert all(result.failure_mode is None for result in results)


def test_missing_candidate_stops_after_output_exists(
    tmp_path: Path,
) -> None:
    task, evaluator = _mech_002_specs()

    results = run_mandatory_gates(
        tmp_path / "missing.json",
        task,
        evaluator,
    )

    assert len(results) == 1
    assert results[0].gate_id == "output_exists"
    assert results[0].passed is False
    assert results[0].failure_mode == "INCOMPLETE_DELIVERABLE"
    assert "does not exist" in results[0].evidence


def test_malformed_json_stops_after_valid_json(
    tmp_path: Path,
) -> None:
    task, evaluator = _mech_002_specs()
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text("{not valid json}", encoding="utf-8")

    results = run_mandatory_gates(
        candidate_path,
        task,
        evaluator,
    )

    assert [result.gate_id for result in results] == [
        "output_exists",
        "valid_json",
    ]
    assert results[-1].passed is False
    assert results[-1].failure_mode == "INVALID_FILE"
    assert "Invalid JSON" in results[-1].evidence


def test_missing_payload_field_fails_required_fields(
    tmp_path: Path,
) -> None:
    task, evaluator = _mech_002_specs()
    candidate = json.loads(
        VALID_CANDIDATE.read_text(encoding="utf-8")
    )
    del candidate["payload"]["verification_power_kw"]

    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(
        json.dumps(candidate, indent=2) + "\n",
        encoding="utf-8",
    )

    results = run_mandatory_gates(
        candidate_path,
        task,
        evaluator,
    )

    assert [result.gate_id for result in results] == [
        "output_exists",
        "valid_json",
        "required_fields",
    ]
    assert results[-1].passed is False
    assert results[-1].failure_mode == "INCOMPLETE_DELIVERABLE"
    assert "verification_power_kw" in results[-1].evidence


def test_wrong_boolean_type_fails_field_types(
    tmp_path: Path,
) -> None:
    task, evaluator = _mech_002_specs()
    candidate_path = _write_modified_candidate(
        tmp_path,
        field="verification",
        value="true",
    )

    results = run_mandatory_gates(
        candidate_path,
        task,
        evaluator,
    )

    assert results[-1].gate_id == "field_types"
    assert results[-1].passed is False
    assert results[-1].failure_mode == "INVALID_FILE"
    assert "verification" in results[-1].evidence
    assert "expected boolean" in results[-1].evidence
    assert "found string" in results[-1].evidence


def test_boolean_does_not_count_as_number(
    tmp_path: Path,
) -> None:
    task, evaluator = _mech_002_specs()
    candidate_path = _write_modified_candidate(
        tmp_path,
        field="shaft_power_kw",
        value=True,
    )

    results = run_mandatory_gates(
        candidate_path,
        task,
        evaluator,
    )

    assert results[-1].gate_id == "field_types"
    assert results[-1].passed is False
    assert "shaft_power_kw" in results[-1].evidence
    assert "expected number" in results[-1].evidence
    assert "found boolean" in results[-1].evidence

def test_non_object_json_stops_after_valid_json(
    tmp_path: Path,
) -> None:
    task, evaluator = _mech_002_specs()
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text("[]", encoding="utf-8")

    results = run_mandatory_gates(
        candidate_path,
        task,
        evaluator,
    )

    assert [result.gate_id for result in results] == [
        "output_exists",
        "valid_json",
    ]
    assert results[-1].passed is False
    assert results[-1].failure_mode == "INVALID_FILE"
    assert (
        results[-1].evidence
        == "Top-level JSON value must be an object."
    )
