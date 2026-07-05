from __future__ import annotations

import json
from pathlib import Path

import pytest

from mech_eval_harness.validator import (
    RepositoryValidationError,
    load_candidate,
)


ROOT = Path(__file__).resolve().parents[1]
VALID_CANDIDATE = (
    ROOT / "examples" / "candidates" / "MECH-002" / "valid.json"
)


def test_load_candidate_loads_valid_candidate() -> None:
    loaded = load_candidate(ROOT, VALID_CANDIDATE)

    assert loaded.candidate["case_id"] == "MECH-002"
    assert loaded.candidate["candidate_id"] == "mech-002-valid-001"
    assert loaded.payload["shaft_power_kw"] == pytest.approx(21.9911)
    assert loaded.candidate_path == VALID_CANDIDATE


def test_load_candidate_rejects_missing_file(tmp_path: Path) -> None:
    candidate_path = tmp_path / "missing.json"

    with pytest.raises(
        RepositoryValidationError,
        match="File not found",
    ):
        load_candidate(ROOT, candidate_path)


def test_load_candidate_rejects_invalid_json(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text("{not valid json}", encoding="utf-8")

    with pytest.raises(
        RepositoryValidationError,
        match="Invalid JSON",
    ):
        load_candidate(ROOT, candidate_path)


def test_load_candidate_rejects_non_object_root(tmp_path: Path) -> None:
    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text("[]", encoding="utf-8")

    with pytest.raises(
        RepositoryValidationError,
        match="Top-level JSON value must be an object",
    ):
        load_candidate(ROOT, candidate_path)


def test_load_candidate_rejects_missing_required_field(
    tmp_path: Path,
) -> None:
    candidate = json.loads(VALID_CANDIDATE.read_text(encoding="utf-8"))
    del candidate["candidate_id"]

    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(
        json.dumps(candidate, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        RepositoryValidationError,
        match="'candidate_id' is a required property",
    ):
        load_candidate(ROOT, candidate_path)


def test_load_candidate_rejects_wrong_case_id(tmp_path: Path) -> None:
    candidate = json.loads(VALID_CANDIDATE.read_text(encoding="utf-8"))
    candidate["case_id"] = "MECH-003"

    candidate_path = tmp_path / "candidate.json"
    candidate_path.write_text(
        json.dumps(candidate, indent=2) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(
        RepositoryValidationError,
        match="candidate case_id MECH-003 does not match expected case_id MECH-002",
    ):
        load_candidate(
            ROOT,
            candidate_path,
            expected_case_id="MECH-002",
        )