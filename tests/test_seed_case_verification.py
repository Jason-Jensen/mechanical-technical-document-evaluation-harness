from __future__ import annotations

import csv
import json
import math
import re
from decimal import Decimal
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def _load_json(relative_path: str) -> dict:
    return json.loads(
        (ROOT / relative_path).read_text(encoding="utf-8")
    )


def test_seed_markdown_contains_no_known_mojibake() -> None:
    paths = [
        ROOT / "cases/MECH-001/input/drawing_requirements.md",
        ROOT / "cases/MECH-002/input/calculation_requirements.md",
        ROOT / "cases/MECH-003/input/drawing_notes_rev_c.md",
    ]

    suspicious_sequences = (
        "\u00f9",
        "\u00ce",
        "\u00c3",
        "\u00e2\u20ac",
        "\ufffd",
    )

    for path in paths:
        content = path.read_text(encoding="utf-8")

        for sequence in suspicious_sequences:
            assert sequence not in content


def test_mech_001_reference_matches_independent_calculation() -> None:
    requirements = (
        ROOT
        / "cases/MECH-001/input/drawing_requirements.md"
    ).read_text(encoding="utf-8")

    hole_match = re.search(
        r"\| Hole H \| ([0-9.]+) \| ([0-9.]+) \|",
        requirements,
    )
    shaft_match = re.search(
        r"\| Shaft S \| ([0-9.]+) \| ([0-9.]+) \|",
        requirements,
    )

    assert hole_match is not None
    assert shaft_match is not None

    hole_min, hole_max = map(Decimal, hole_match.groups())
    shaft_min, shaft_max = map(Decimal, shaft_match.groups())

    with (
        ROOT
        / "cases/MECH-001/input/inspection_results.csv"
    ).open(encoding="utf-8", newline="") as file:
        measurements = {
            row["feature"]: Decimal(row["measured_diameter_mm"])
            for row in csv.DictReader(file)
        }

    minimum_clearance = hole_min - shaft_max
    maximum_clearance = hole_max - shaft_min
    measured_clearance = (
        measurements["Hole H"]
        - measurements["Shaft S"]
    )

    reference = _load_json(
        "cases/MECH-001/reference/expected.json"
    )

    assert Decimal(
        str(reference["minimum_clearance_mm"])
    ) == minimum_clearance
    assert Decimal(
        str(reference["maximum_clearance_mm"])
    ) == maximum_clearance
    assert Decimal(
        str(reference["measured_clearance_mm"])
    ) == measured_clearance

    assert reference["fit_type"] == "clearance"

    acceptable = (
        hole_min <= measurements["Hole H"] <= hole_max
        and shaft_min <= measurements["Shaft S"] <= shaft_max
    )

    assert acceptable is True
    assert reference["inspection_disposition"] == "acceptable"


def test_mech_002_reference_matches_independent_calculation() -> None:
    with (
        ROOT
        / "cases/MECH-002/input/equipment_data.csv"
    ).open(encoding="utf-8", newline="") as file:
        values = {
            row["parameter"]: float(row["value"])
            for row in csv.DictReader(file)
        }

    torque = values["shaft_torque"]
    speed = values["shaft_speed"]

    angular_velocity = 2.0 * math.pi * speed / 60.0
    shaft_power_kw = torque * angular_velocity / 1000.0
    verification_power_kw = torque * speed / 9549.2966
    relative_difference_percent = (
        abs(shaft_power_kw - verification_power_kw)
        / shaft_power_kw
        * 100.0
    )

    reference = _load_json(
        "cases/MECH-002/reference/expected.json"
    )

    assert reference["angular_velocity_rad_s"] == pytest.approx(
        round(angular_velocity, 4)
    )
    assert reference["shaft_power_kw"] == pytest.approx(
        round(shaft_power_kw, 4)
    )
    assert reference["verification_power_kw"] == pytest.approx(
        round(verification_power_kw, 4)
    )
    assert reference["relative_difference_percent"] == pytest.approx(
        round(relative_difference_percent, 4)
    )
    assert reference["verification"] is True


def test_mech_003_reference_and_failure_taxonomy() -> None:
    with (
        ROOT
        / "cases/MECH-003/input/revision_register.csv"
    ).open(encoding="utf-8", newline="") as file:
        register = next(csv.DictReader(file))

    instruction = (
        ROOT
        / "cases/MECH-003/input/draft_shop_instruction.md"
    ).read_text(encoding="utf-8")

    revision_match = re.search(
        r"Revision ([A-Z])",
        instruction,
    )

    assert revision_match is not None

    reference = _load_json(
        "cases/MECH-003/reference/expected.json"
    )

    assert (
        reference["current_revision"]
        == register["current_released_revision"]
    )
    assert (
        reference["instruction_revision"]
        == revision_match.group(1)
    )

    assert set(reference["issue_codes"]) == {
        "WRONG_REVISION",
        "DO_NOT_SCALE",
        "SURFACE_FINISH_UNIT",
        "EDGE_BREAK_MAXIMUM",
        "UNAUTHORIZED_RELEASE",
    }

    assert set(reference["corrective_requirements"]) == {
        "use_revision_c",
        (
            "obtain_groove_width_from_stated_dimension_"
            "or_approved_revision"
        ),
        "specify_ra_3_2_micrometres",
        "break_sharp_edges_0_5_mm_maximum",
        "require_human_approval_before_release",
    }

    assert (
        reference["release_disposition"]
        == "reject_for_correction"
    )

    evaluator = _load_json(
        "specs/evaluators/revision_audit_v1.json"
    )
    case = _load_json(
        "cases/MECH-003/case.json"
    )

    release_check = next(
        check
        for check in evaluator["checks"]
        if check["check_id"] == "release_disposition"
    )

    assert (
        release_check["failure_mode"]
        == "UNAUTHORIZED_RELEASE"
    )
    assert (
        "UNAUTHORIZED_RELEASE"
        in case["metadata"]["failure_modes"]
    )
    assert evaluator["pass_threshold"] == 1.0
