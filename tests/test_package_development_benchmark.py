from __future__ import annotations

import json
from pathlib import Path

import pytest

from mech_eval_harness.package_assurance import (
    PACKAGE_GATE_ORDER,
    RELATIONSHIP_CHECK_ORDER,
)
from mech_eval_harness.package_assurance.development_benchmark import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
    BENCHMARK_REPORT_JSON,
    BENCHMARK_REPORT_MARKDOWN,
    DevelopmentBenchmarkError,
    development_benchmark_exit_code,
    load_development_benchmark_definition,
    run_development_benchmark,
)


ROOT = Path(__file__).resolve().parents[1]


def test_development_benchmark_definition_freezes_bounded_matrix() -> None:
    definition = load_development_benchmark_definition(ROOT)

    assert definition.benchmark_revision == "P4.1-DEV-1"
    assert definition.split == "development"
    assert definition.repeat_count == 2
    assert definition.baseline_content_hash == (
        "a4b278e5bd20f3b64a85d52c478747b1115e15bbaf63b19bf47f5dffddfaf31a"
    )
    assert len(definition.scenarios) == 22
    assert sum(scenario.scenario_type == "clean" for scenario in definition.scenarios) == 1
    assert {
        scenario.expected_package_state for scenario in definition.scenarios
    } == {
        "automatic_pass",
        "automatic_fail",
        "missing_authoritative_information",
        "extraction_or_tool_failure",
    }
    assert definition.contract_only_states == (
        "engineering_review_required",
        "evaluator_uncertainty",
    )
    expected_gate_coverage = {
        gate_id
        for scenario in definition.scenarios
        for gate_id in scenario.expected_failed_gates
    }
    expected_check_coverage = {
        check_id
        for scenario in definition.scenarios
        for check_id in scenario.expected_failed_checks
    }
    assert expected_gate_coverage == set(PACKAGE_GATE_ORDER)
    assert expected_check_coverage == set(RELATIONSHIP_CHECK_ORDER)
    assert "held_out" not in definition.baseline_package_root.parts


def test_complete_development_benchmark_is_exact_repeatable_and_preserved(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "development-benchmark"

    report = run_development_benchmark(
        repository_root=ROOT,
        output_root=output_root,
    )

    assert report["status"] == "passed"
    assert development_benchmark_exit_code(report) == 0
    assert report["complete_matrix"] is True
    assert report["scenario_count"] == report["scenario_pass_count"] == 22
    assert report["coverage"]["mandatory_gate_failure_coverage"]["missing"] == []
    assert report["coverage"]["relationship_failure_coverage"]["missing"] == []
    assert report["coverage"]["full_audit_state_coverage"]["missing"] == []
    assert (output_root / BENCHMARK_REPORT_JSON).is_file()
    assert (output_root / BENCHMARK_REPORT_MARKDOWN).is_file()

    stored_report = json.loads(
        (output_root / BENCHMARK_REPORT_JSON).read_text(encoding="utf-8")
    )
    assert stored_report == report
    for scenario in report["scenarios"]:
        assert scenario["passed"] is True
        assert all(scenario["checks"].values())
        assert len(scenario["runs"]) == 2
        assert len(
            {run["publication_sha256"] for run in scenario["runs"]}
        ) == 1
        scenario_root = output_root / "scenarios" / scenario["scenario_id"]
        assert not (scenario_root / "package" / "expected").exists()
        for run in scenario["runs"]:
            run_directory = output_root / run["run_directory"]
            assert {path.name for path in run_directory.iterdir()} == set(
                AUDIT_PACKAGE_OUTPUT_FILENAMES
            )


def test_development_benchmark_never_overwrites_existing_evidence(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "existing"
    output_root.mkdir()

    with pytest.raises(DevelopmentBenchmarkError, match="will not be overwritten"):
        run_development_benchmark(
            repository_root=ROOT,
            output_root=output_root,
            selected_scenario_ids=["SCN-DEV-PUMP-SKID-CLEAN-001"],
        )


def test_scenario_subset_is_useful_but_cannot_claim_benchmark_acceptance(
    tmp_path: Path,
) -> None:
    report = run_development_benchmark(
        repository_root=ROOT,
        output_root=tmp_path / "subset",
        selected_scenario_ids=["SCN-DEV-PUMP-SKID-CLEAN-001"],
    )

    assert report["mode"] == "acceptance_subset"
    assert report["status"] == "unscored"
    assert report["complete_matrix"] is False
    assert report["acceptance_claim_eligible"] is False
    assert report["scenario_pass_count"] == report["scenario_count"] == 1
    assert development_benchmark_exit_code(report) == 1


def test_generated_evidence_cannot_enter_versioned_benchmark_tree() -> None:
    output_root = ROOT / "benchmarks/package_assurance/generated-do-not-create"

    with pytest.raises(
        DevelopmentBenchmarkError,
        match="outside versioned benchmark definitions",
    ):
        run_development_benchmark(
            repository_root=ROOT,
            output_root=output_root,
            selected_scenario_ids=["SCN-DEV-PUMP-SKID-CLEAN-001"],
        )
    assert not output_root.exists()
