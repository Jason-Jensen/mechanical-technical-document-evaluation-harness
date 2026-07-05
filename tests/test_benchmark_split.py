from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "benchmarks" / "mvp_v1" / "split.json"
CHECKLIST_PATH = (
    ROOT / "benchmarks" / "mvp_v1" / "review-checklist.md"
)


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_manifest() -> dict:
    return _load_json(MANIFEST_PATH)


def _manifest_membership() -> tuple[list[str], list[str]]:
    manifest = _load_manifest()

    return (
        manifest["development_case_ids"],
        manifest["held_out_case_ids"],
    )


def _repository_case_ids() -> set[str]:
    return {
        _load_json(case_path)["case_id"]
        for case_path in ROOT.glob("cases/MECH-*/case.json")
    }


def test_split_manifest_has_unique_complete_membership() -> None:
    development, held_out = _manifest_membership()
    combined = development + held_out

    assert development
    assert held_out
    assert len(combined) == len(set(combined))
    assert set(combined) == _repository_case_ids()


def test_case_metadata_matches_split_manifest() -> None:
    development, held_out = _manifest_membership()

    expected_splits = {
        **{
            case_id: "development"
            for case_id in development
        },
        **{
            case_id: "held_out"
            for case_id in held_out
        },
    }

    actual_splits = {}

    for case_path in ROOT.glob("cases/MECH-*/case.json"):
        case = _load_json(case_path)

        actual_splits[case["case_id"]] = (
            case["metadata"]["dataset_split"]
        )

    assert actual_splits == expected_splits


def test_held_out_cases_have_no_candidate_examples() -> None:
    _, held_out = _manifest_membership()

    for case_id in held_out:
        candidate_dir = (
            ROOT
            / "examples"
            / "candidates"
            / case_id
        )

        assert not candidate_dir.exists(), (
            f"Held-out candidate leakage: {candidate_dir}"
        )


def test_split_manifest_preserves_controls_and_disclosure() -> None:
    manifest = _load_manifest()
    selection = manifest["selection"]
    controls = manifest["controls"]

    assert manifest["benchmark_id"] == "MECHANICAL-MVP-V1"
    assert manifest["frozen_date"] == "2026-07-05"

    assert (
        selection["contamination_status"]
        == "historically_seen_during_case_authoring"
    )
    assert "not claimed to be a pristine blind case" in (
        selection["limitation"]
    )

    assert controls == {
        "held_out_candidate_examples_prohibited": True,
        "split_changes_require_documented_decision": True,
        "case_metadata_must_match_manifest": True,
        "held_out_results_must_be_reported_separately": True,
    }


def test_review_checklist_matches_manifest_membership() -> None:
    development, held_out = _manifest_membership()
    expected_splits = {
        **{
            case_id: "development"
            for case_id in development
        },
        **{
            case_id: "held_out"
            for case_id in held_out
        },
    }

    checklist = CHECKLIST_PATH.read_text(encoding="utf-8")
    table_splits = {}

    for line in checklist.splitlines():
        if not line.startswith("| MECH-"):
            continue

        cells = [
            cell.strip()
            for cell in line.strip("|").split("|")
        ]

        case_id = cells[0]
        split = cells[6]
        table_splits[case_id] = split

    assert table_splits == expected_splits
