"""Controlled P4.1 development benchmark for structured package assurance."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from mech_eval_harness.package_assurance.audit import (
    execute_package_audit,
    package_state_exit_code,
)
from mech_eval_harness.package_assurance.gates import PACKAGE_GATE_ORDER
from mech_eval_harness.package_assurance.publication import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
)
from mech_eval_harness.package_assurance.relationships import (
    RELATIONSHIP_CHECK_ORDER,
)


DEVELOPMENT_BENCHMARK_SCHEMA_VERSION = "0.3.0"
DEVELOPMENT_BENCHMARK_REPORT_VERSION = "0.3.0"
DEVELOPMENT_BENCHMARK_DEFINITION = Path(
    "benchmarks/package_assurance/development/"
    "pump_skid_clean_v1/development_benchmark_v1.json"
)
DEVELOPMENT_BENCHMARK_OUTPUT_ROOT = Path(
    "runs/package_assurance-development-benchmark"
)
BENCHMARK_REPORT_JSON = "benchmark_report.json"
BENCHMARK_REPORT_MARKDOWN = "benchmark_report.md"

_PACKAGE_STATES = {
    "automatic_pass": 0,
    "automatic_fail": 1,
    "engineering_review_required": 2,
    "missing_authoritative_information": 3,
    "extraction_or_tool_failure": 4,
    "evaluator_uncertainty": 5,
}
_HEX_DIGEST_LENGTH = 64


class DevelopmentBenchmarkError(RuntimeError):
    """Raised when the development benchmark cannot run safely."""


@dataclass(frozen=True)
class DevelopmentScenario:
    """One reviewed development scenario and its exact expected outcome."""

    scenario_id: str
    package_id: str
    scenario_type: str
    seeded_fault_id: str | None
    mutation_id: str
    mutation_note: str
    expected_package_state: str
    expected_cli_exit_code: int
    expected_release_hold: bool
    expected_blocking_states: tuple[str, ...]
    expected_finding_codes: tuple[str, ...]
    expected_failed_gates: tuple[str, ...]
    expected_skipped_gates: tuple[str, ...]
    expected_failed_checks: tuple[str, ...]
    expected_skipped_checks: tuple[str, ...]
    expected_publication_sha256: str


@dataclass(frozen=True)
class DevelopmentBenchmarkDefinition:
    """Validated benchmark metadata and executable scenario matrix."""

    path: Path
    benchmark_id: str
    benchmark_revision: str
    split: str
    baseline_package_root: Path
    baseline_content_hash: str
    baseline_acceptance_commit: str
    repeat_count: int
    full_audit_states: tuple[str, ...]
    contract_only_states: tuple[str, ...]
    scenarios: tuple[DevelopmentScenario, ...]
    deferred_claims: tuple[str, ...]


def load_development_benchmark_definition(
    repository_root: Path,
    definition_path: Path = DEVELOPMENT_BENCHMARK_DEFINITION,
) -> DevelopmentBenchmarkDefinition:
    """Load and validate the frozen development benchmark definition."""

    repository_root = repository_root.resolve()
    path = _resolve_inside(repository_root, definition_path)
    document = _read_json(path)
    _require_exact_keys(
        document,
        {
            "schema_version",
            "benchmark_id",
            "benchmark_revision",
            "split",
            "baseline",
            "runner_contract",
            "scope",
            "scenarios",
        },
        "benchmark definition",
    )
    if document["schema_version"] != DEVELOPMENT_BENCHMARK_SCHEMA_VERSION:
        raise DevelopmentBenchmarkError(
            "Unsupported development benchmark schema_version: "
            f"{document['schema_version']!r}"
        )
    if document["split"] != "development":
        raise DevelopmentBenchmarkError(
            "The P4.1 runner accepts only the development split."
        )

    baseline = _require_mapping(document["baseline"], "baseline")
    _require_exact_keys(
        baseline,
        {
            "package_root",
            "accepted_content_hash",
            "accepted_at_commit",
            "producer_hidden_roots",
        },
        "baseline",
    )
    baseline_root = _resolve_inside(
        repository_root,
        _require_string(baseline["package_root"], "baseline.package_root"),
    )
    if "held_out" in baseline_root.parts:
        raise DevelopmentBenchmarkError(
            "The P4.1 development runner cannot address held-out paths."
        )
    hidden_roots = _require_string_list(
        baseline["producer_hidden_roots"],
        "baseline.producer_hidden_roots",
    )
    if hidden_roots != ("expected",):
        raise DevelopmentBenchmarkError(
            "The accepted development producer-hidden root must be exactly expected."
        )

    runner = _require_mapping(document["runner_contract"], "runner_contract")
    _require_exact_keys(
        runner,
        {
            "repeat_count",
            "required_output_names",
            "normalized_result_exclusions",
            "oracle_comparison",
        },
        "runner_contract",
    )
    repeat_count = runner["repeat_count"]
    if repeat_count != 2:
        raise DevelopmentBenchmarkError(
            "The accepted P4.1 repeat_count must be exactly 2."
        )
    if tuple(runner["required_output_names"]) != AUDIT_PACKAGE_OUTPUT_FILENAMES:
        raise DevelopmentBenchmarkError(
            "Benchmark output names do not match the audit publication contract."
        )
    if runner["normalized_result_exclusions"] != ["run_id", "run_metadata"]:
        raise DevelopmentBenchmarkError(
            "Only run_id and run_metadata may be excluded from comparison."
        )
    if runner["oracle_comparison"] != "exact_normalized_publication_sha256":
        raise DevelopmentBenchmarkError("Unsupported benchmark oracle comparison.")

    scope = _require_mapping(document["scope"], "scope")
    _require_exact_keys(
        scope,
        {
            "mandatory_gate_ids",
            "relationship_check_ids",
            "full_audit_states",
            "contract_only_states",
            "deferred_claims",
            "held_out_semantic_execution",
        },
        "scope",
    )
    if tuple(scope["mandatory_gate_ids"]) != PACKAGE_GATE_ORDER:
        raise DevelopmentBenchmarkError(
            "Benchmark mandatory gates do not match the evaluator order."
        )
    if tuple(scope["relationship_check_ids"]) != RELATIONSHIP_CHECK_ORDER:
        raise DevelopmentBenchmarkError(
            "Benchmark relationship checks do not match the evaluator order."
        )
    if scope["held_out_semantic_execution"] != "prohibited_in_p4_1":
        raise DevelopmentBenchmarkError(
            "P4.1 must prohibit held-out semantic execution."
        )
    full_audit_states = _require_string_list(
        scope["full_audit_states"], "scope.full_audit_states"
    )
    contract_only_states = _require_string_list(
        scope["contract_only_states"], "scope.contract_only_states"
    )
    if set(full_audit_states) | set(contract_only_states) != set(_PACKAGE_STATES):
        raise DevelopmentBenchmarkError(
            "Full-audit and contract-only states must partition all six states."
        )
    if set(full_audit_states) & set(contract_only_states):
        raise DevelopmentBenchmarkError(
            "A result state cannot be both full-audit and contract-only."
        )

    raw_scenarios = document["scenarios"]
    if not isinstance(raw_scenarios, list) or not raw_scenarios:
        raise DevelopmentBenchmarkError("scenarios must be a non-empty array.")
    scenarios = tuple(_parse_scenario(item) for item in raw_scenarios)
    _require_unique(
        (scenario.scenario_id for scenario in scenarios), "scenario_id"
    )
    _require_unique((scenario.package_id for scenario in scenarios), "package_id")
    if {scenario.expected_package_state for scenario in scenarios} != set(
        full_audit_states
    ):
        raise DevelopmentBenchmarkError(
            "Executable scenarios must cover every declared full-audit state."
        )
    unknown_mutations = sorted(
        {scenario.mutation_id for scenario in scenarios} - set(_MUTATIONS)
    )
    if unknown_mutations:
        raise DevelopmentBenchmarkError(
            "Unknown development mutation(s): " + ", ".join(unknown_mutations)
        )

    return DevelopmentBenchmarkDefinition(
        path=path,
        benchmark_id=_require_string(document["benchmark_id"], "benchmark_id"),
        benchmark_revision=_require_string(
            document["benchmark_revision"], "benchmark_revision"
        ),
        split="development",
        baseline_package_root=baseline_root,
        baseline_content_hash=_require_sha256(
            baseline["accepted_content_hash"], "baseline.accepted_content_hash"
        ),
        baseline_acceptance_commit=_require_string(
            baseline["accepted_at_commit"], "baseline.accepted_at_commit"
        ),
        repeat_count=repeat_count,
        full_audit_states=full_audit_states,
        contract_only_states=contract_only_states,
        scenarios=scenarios,
        deferred_claims=_require_string_list(
            scope["deferred_claims"], "scope.deferred_claims"
        ),
    )


def run_development_benchmark(
    *,
    repository_root: Path,
    output_root: Path,
    definition_path: Path = DEVELOPMENT_BENCHMARK_DEFINITION,
    compare_oracles: bool = True,
    selected_scenario_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Generate, execute twice, compare, and preserve development scenarios."""

    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    definition = load_development_benchmark_definition(
        repository_root, definition_path
    )
    actual_baseline_hash = _package_tree_hash(definition.baseline_package_root)
    if actual_baseline_hash != definition.baseline_content_hash:
        raise DevelopmentBenchmarkError(
            "Development baseline hash changed: expected "
            f"{definition.baseline_content_hash}, observed {actual_baseline_hash}."
        )
    if output_root.exists():
        raise DevelopmentBenchmarkError(
            f"Benchmark output already exists and will not be overwritten: {output_root}"
        )
    benchmarks_root = (repository_root / "benchmarks").resolve()
    if _is_relative_to(output_root, benchmarks_root):
        raise DevelopmentBenchmarkError(
            "Generated benchmark evidence must remain outside versioned "
            "benchmark definitions."
        )
    output_root.mkdir(parents=True)

    scenarios = _select_scenarios(definition, selected_scenario_ids)
    started_at = datetime.now(timezone.utc)
    scenario_reports: list[dict[str, Any]] = []
    for index, scenario in enumerate(scenarios):
        try:
            scenario_report = _run_scenario(
                repository_root=repository_root,
                output_root=output_root,
                definition=definition,
                scenario=scenario,
                scenario_index=index,
                benchmark_started_at=started_at,
                compare_oracles=compare_oracles,
            )
        except Exception as exc:
            scenario_report = _failed_scenario_report(scenario, exc)
        scenario_reports.append(scenario_report)

    complete_matrix = len(scenarios) == len(definition.scenarios)
    passed = all(report["passed"] for report in scenario_reports)
    acceptance_claim_eligible = compare_oracles and complete_matrix
    mode = (
        "observation_only"
        if not compare_oracles
        else "acceptance"
        if complete_matrix
        else "acceptance_subset"
    )
    report = {
        "report_version": DEVELOPMENT_BENCHMARK_REPORT_VERSION,
        "benchmark_id": definition.benchmark_id,
        "benchmark_revision": definition.benchmark_revision,
        "split": definition.split,
        "mode": mode,
        "status": (
            "passed"
            if acceptance_claim_eligible and passed
            else "failed"
            if acceptance_claim_eligible
            else "unscored"
        ),
        "evaluator_commit": _git_commit(repository_root),
        "definition_sha256": _sha256_file(definition.path),
        "baseline_content_hash": actual_baseline_hash,
        "baseline_acceptance_commit": definition.baseline_acceptance_commit,
        "repeat_count": definition.repeat_count,
        "complete_matrix": complete_matrix,
        "acceptance_claim_eligible": acceptance_claim_eligible,
        "scenario_count": len(scenario_reports),
        "scenario_pass_count": sum(
            1 for scenario_report in scenario_reports if scenario_report["passed"]
        ),
        "full_audit_states": list(definition.full_audit_states),
        "contract_only_states": list(definition.contract_only_states),
        "deferred_claims": list(definition.deferred_claims),
        "coverage": _coverage_report(definition, scenario_reports),
        "scenarios": scenario_reports,
    }
    _write_json(output_root / BENCHMARK_REPORT_JSON, report)
    (output_root / BENCHMARK_REPORT_MARKDOWN).write_text(
        _render_markdown_report(report), encoding="utf-8", newline="\n"
    )
    return report


def development_benchmark_exit_code(report: Mapping[str, Any]) -> int:
    """Return zero only for a complete, passing acceptance-mode benchmark."""

    return 0 if report.get("status") == "passed" else 1


def normalized_publication_sha256(run_directory: Path) -> str:
    """Hash all four audit outputs after removing declared run metadata."""

    run_directory = run_directory.resolve()
    names = tuple(sorted(path.name for path in run_directory.iterdir()))
    if names != tuple(sorted(AUDIT_PACKAGE_OUTPUT_FILENAMES)):
        raise DevelopmentBenchmarkError(
            "Audit publication does not contain exactly the four required outputs."
        )
    result = _read_json(run_directory / "package_result.json")
    run_id = result.pop("run_id")
    result.pop("run_metadata")
    normalized_outputs: dict[str, Any] = {"package_result.json": result}
    normalized_outputs["issue_register.csv"] = (
        run_directory / "issue_register.csv"
    ).read_text(encoding="utf-8")
    for name in ("issue_register.md", "release_readiness.md"):
        normalized_outputs[name] = (run_directory / name).read_text(
            encoding="utf-8"
        ).replace(run_id, "<RUN_ID>")
    return _canonical_sha256(normalized_outputs)


def _run_scenario(
    *,
    repository_root: Path,
    output_root: Path,
    definition: DevelopmentBenchmarkDefinition,
    scenario: DevelopmentScenario,
    scenario_index: int,
    benchmark_started_at: datetime,
    compare_oracles: bool,
) -> dict[str, Any]:
    scenario_root = output_root / "scenarios" / scenario.scenario_id
    package_root = scenario_root / "package"
    runs_root = scenario_root / "runs"
    _stage_producer_visible_package(definition.baseline_package_root, package_root)
    _assign_scenario_identity(package_root, scenario.package_id)
    _MUTATIONS[scenario.mutation_id](package_root)

    run_reports: list[dict[str, Any]] = []
    for repetition in range(1, definition.repeat_count + 1):
        repetition_root = runs_root / f"repeat-{repetition}"
        run_id = _benchmark_run_id(
            benchmark_started_at,
            scenario.scenario_id,
            scenario_index,
            repetition,
        )
        outcome = execute_package_audit(
            repository_root=repository_root,
            package_root=package_root,
            runs_dir=repetition_root,
            schema_path=repository_root / "schemas/package_result.schema.json",
            run_id=run_id,
        )
        result = outcome.result.to_dict()
        run_reports.append(
            {
                "repetition": repetition,
                "run_id": result["run_id"],
                "run_directory": outcome.publication.run_directory.relative_to(
                    output_root
                ).as_posix(),
                "package_state": result["package_state"],
                "cli_exit_code": package_state_exit_code(result["package_state"]),
                "release_hold": result["release_hold"],
                "blocking_states": result["blocking_states"],
                "finding_codes": [
                    finding["code"] for finding in result["findings"]
                ],
                "failed_gates": _status_ids(result["gate_results"], "failed"),
                "skipped_gates": _status_ids(result["gate_results"], "skipped"),
                "failed_checks": _status_ids(
                    result["relationship_results"], "failed"
                ),
                "skipped_checks": _status_ids(
                    result["relationship_results"], "skipped"
                ),
                "publication_sha256": normalized_publication_sha256(
                    outcome.publication.run_directory
                ),
                "output_names": sorted(
                    path.name for path in outcome.publication.run_directory.iterdir()
                ),
            }
        )

    first = run_reports[0]
    repetition_hashes = [run["publication_sha256"] for run in run_reports]
    checks = {
        "producer_hidden_assets_excluded": not (package_root / "expected").exists(),
        "repetitions_identical": len(set(repetition_hashes)) == 1,
        "package_state_matches": (
            first["package_state"] == scenario.expected_package_state
        ),
        "cli_exit_matches": (
            first["cli_exit_code"] == scenario.expected_cli_exit_code
        ),
        "release_hold_matches": (
            first["release_hold"] == scenario.expected_release_hold
        ),
        "blocking_states_match": (
            tuple(first["blocking_states"]) == scenario.expected_blocking_states
        ),
        "finding_codes_match": (
            tuple(first["finding_codes"]) == scenario.expected_finding_codes
        ),
        "failed_gates_match": (
            tuple(first["failed_gates"]) == scenario.expected_failed_gates
        ),
        "skipped_gates_match": (
            tuple(first["skipped_gates"]) == scenario.expected_skipped_gates
        ),
        "failed_checks_match": (
            tuple(first["failed_checks"]) == scenario.expected_failed_checks
        ),
        "skipped_checks_match": (
            tuple(first["skipped_checks"]) == scenario.expected_skipped_checks
        ),
        "exact_oracle_matches": (
            not compare_oracles
            or first["publication_sha256"]
            == scenario.expected_publication_sha256
        ),
    }
    return {
        "scenario_id": scenario.scenario_id,
        "package_id": scenario.package_id,
        "scenario_type": scenario.scenario_type,
        "seeded_fault_id": scenario.seeded_fault_id,
        "mutation_id": scenario.mutation_id,
        "mutation_note": scenario.mutation_note,
        "expected": {
            "package_state": scenario.expected_package_state,
            "cli_exit_code": scenario.expected_cli_exit_code,
            "release_hold": scenario.expected_release_hold,
            "blocking_states": list(scenario.expected_blocking_states),
            "finding_codes": list(scenario.expected_finding_codes),
            "failed_gates": list(scenario.expected_failed_gates),
            "skipped_gates": list(scenario.expected_skipped_gates),
            "failed_checks": list(scenario.expected_failed_checks),
            "skipped_checks": list(scenario.expected_skipped_checks),
            "publication_sha256": scenario.expected_publication_sha256,
        },
        "checks": checks,
        "passed": all(checks.values()),
        "runs": run_reports,
    }


def _coverage_report(
    definition: DevelopmentBenchmarkDefinition,
    scenario_reports: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    observed_failed_gates = {
        gate_id
        for report in scenario_reports
        if report["runs"]
        for gate_id in report["runs"][0]["failed_gates"]
    }
    observed_failed_checks = {
        check_id
        for report in scenario_reports
        if report["runs"]
        for check_id in report["runs"][0]["failed_checks"]
    }
    observed_states = {
        report["runs"][0]["package_state"]
        for report in scenario_reports
        if report["runs"]
    }
    return {
        "mandatory_gate_failure_coverage": {
            "covered": [
                gate_id
                for gate_id in PACKAGE_GATE_ORDER
                if gate_id in observed_failed_gates
            ],
            "missing": [
                gate_id
                for gate_id in PACKAGE_GATE_ORDER
                if gate_id not in observed_failed_gates
            ],
        },
        "relationship_failure_coverage": {
            "covered": [
                check_id
                for check_id in RELATIONSHIP_CHECK_ORDER
                if check_id in observed_failed_checks
            ],
            "missing": [
                check_id
                for check_id in RELATIONSHIP_CHECK_ORDER
                if check_id not in observed_failed_checks
            ],
        },
        "full_audit_state_coverage": {
            "covered": [
                state
                for state in definition.full_audit_states
                if state in observed_states
            ],
            "missing": [
                state
                for state in definition.full_audit_states
                if state not in observed_states
            ],
        },
        "contract_only_states": list(definition.contract_only_states),
    }


def _render_markdown_report(report: Mapping[str, Any]) -> str:
    coverage = report["coverage"]
    lines = [
        "# P4.1 Development Benchmark Report",
        "",
        f"- Benchmark: `{report['benchmark_id']}`",
        f"- Revision: `{report['benchmark_revision']}`",
        f"- Evaluator commit: `{report['evaluator_commit']}`",
        f"- Mode: `{report['mode']}`",
        f"- Status: `{report['status']}`",
        f"- Scenarios: {report['scenario_pass_count']}/{report['scenario_count']} passed",
        f"- Repetitions per scenario: {report['repeat_count']}",
        "",
        "## Coverage",
        "",
        "| Area | Covered | Missing |",
        "| --- | ---: | ---: |",
        "| Mandatory gate failures | "
        f"{len(coverage['mandatory_gate_failure_coverage']['covered'])} | "
        f"{len(coverage['mandatory_gate_failure_coverage']['missing'])} |",
        "| Relationship check failures | "
        f"{len(coverage['relationship_failure_coverage']['covered'])} | "
        f"{len(coverage['relationship_failure_coverage']['missing'])} |",
        "| Full-audit states | "
        f"{len(coverage['full_audit_state_coverage']['covered'])} | "
        f"{len(coverage['full_audit_state_coverage']['missing'])} |",
        "",
        "Contract-only states: "
        + ", ".join(f"`{state}`" for state in report["contract_only_states"]),
        "",
        "## Scenarios",
        "",
        "| Scenario | Expected state | Findings | Repeatable | Exact oracle | Result |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for scenario in report["scenarios"]:
        checks = scenario["checks"]
        run = scenario["runs"][0] if scenario["runs"] else None
        lines.append(
            f"| `{scenario['scenario_id']}` | "
            f"`{scenario['expected']['package_state']}` | "
            f"{len(run['finding_codes']) if run else 0} | "
            f"{'yes' if checks.get('repetitions_identical') else 'no'} | "
            f"{'yes' if checks.get('exact_oracle_matches') else 'no'} | "
            f"{'pass' if scenario['passed'] else 'fail'} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This report covers the development split only. It does not execute or "
            "inspect protected held-out semantics, approve engineering work, or "
            "establish real-world accuracy.",
            "",
        ]
    )
    return "\n".join(lines)


def _parse_scenario(value: Any) -> DevelopmentScenario:
    document = _require_mapping(value, "scenario")
    _require_exact_keys(
        document,
        {
            "scenario_id",
            "package_id",
            "scenario_type",
            "seeded_fault_id",
            "mutation_id",
            "mutation_note",
            "expected_package_state",
            "expected_cli_exit_code",
            "expected_release_hold",
            "expected_blocking_states",
            "expected_finding_codes",
            "expected_failed_gates",
            "expected_skipped_gates",
            "expected_failed_checks",
            "expected_skipped_checks",
            "expected_publication_sha256",
        },
        "scenario",
    )
    state = _require_string(
        document["expected_package_state"], "expected_package_state"
    )
    if state not in _PACKAGE_STATES:
        raise DevelopmentBenchmarkError(f"Unsupported expected state: {state}")
    expected_exit = document["expected_cli_exit_code"]
    if not isinstance(expected_exit, int) or isinstance(expected_exit, bool):
        raise DevelopmentBenchmarkError("expected_cli_exit_code must be an integer.")
    if expected_exit != _PACKAGE_STATES[state]:
        raise DevelopmentBenchmarkError(
            f"Expected exit {expected_exit!r} does not match state {state}."
        )
    scenario_type = _require_string(document["scenario_type"], "scenario_type")
    if scenario_type not in {"clean", "single_fault", "compound_fault"}:
        raise DevelopmentBenchmarkError(
            f"Unsupported development scenario_type: {scenario_type}"
        )
    fault_id = document["seeded_fault_id"]
    if fault_id is not None and not isinstance(fault_id, str):
        raise DevelopmentBenchmarkError("seeded_fault_id must be a string or null.")
    if (scenario_type == "clean") != (fault_id is None):
        raise DevelopmentBenchmarkError(
            "Only a clean scenario may omit seeded_fault_id."
        )
    finding_codes = _require_string_list(
        document["expected_finding_codes"], "expected_finding_codes"
    )
    if scenario_type == "clean" and finding_codes:
        raise DevelopmentBenchmarkError("The clean scenario cannot expect findings.")
    if scenario_type != "clean" and not finding_codes:
        raise DevelopmentBenchmarkError("Fault scenarios must expect a finding.")
    release_hold = document["expected_release_hold"]
    if not isinstance(release_hold, bool):
        raise DevelopmentBenchmarkError("expected_release_hold must be Boolean.")
    expected_hash = _require_sha256(
        document["expected_publication_sha256"],
        "expected_publication_sha256",
    )
    if expected_hash == "0" * _HEX_DIGEST_LENGTH:
        raise DevelopmentBenchmarkError(
            "expected_publication_sha256 cannot be an unfrozen placeholder."
        )
    return DevelopmentScenario(
        scenario_id=_require_string(document["scenario_id"], "scenario_id"),
        package_id=_require_string(document["package_id"], "package_id"),
        scenario_type=scenario_type,
        seeded_fault_id=fault_id,
        mutation_id=_require_string(document["mutation_id"], "mutation_id"),
        mutation_note=_require_string(document["mutation_note"], "mutation_note"),
        expected_package_state=state,
        expected_cli_exit_code=expected_exit,
        expected_release_hold=release_hold,
        expected_blocking_states=_require_string_list(
            document["expected_blocking_states"], "expected_blocking_states"
        ),
        expected_finding_codes=finding_codes,
        expected_failed_gates=_ordered_subset(
            document["expected_failed_gates"], PACKAGE_GATE_ORDER, "failed gates"
        ),
        expected_skipped_gates=_ordered_subset(
            document["expected_skipped_gates"], PACKAGE_GATE_ORDER, "skipped gates"
        ),
        expected_failed_checks=_ordered_subset(
            document["expected_failed_checks"],
            RELATIONSHIP_CHECK_ORDER,
            "failed checks",
        ),
        expected_skipped_checks=_ordered_subset(
            document["expected_skipped_checks"],
            RELATIONSHIP_CHECK_ORDER,
            "skipped checks",
        ),
        expected_publication_sha256=expected_hash,
    )


def _failed_scenario_report(
    scenario: DevelopmentScenario, exc: Exception
) -> dict[str, Any]:
    return {
        "scenario_id": scenario.scenario_id,
        "package_id": scenario.package_id,
        "scenario_type": scenario.scenario_type,
        "seeded_fault_id": scenario.seeded_fault_id,
        "mutation_id": scenario.mutation_id,
        "mutation_note": scenario.mutation_note,
        "expected": {
            "package_state": scenario.expected_package_state,
            "cli_exit_code": scenario.expected_cli_exit_code,
            "release_hold": scenario.expected_release_hold,
            "blocking_states": list(scenario.expected_blocking_states),
            "finding_codes": list(scenario.expected_finding_codes),
            "failed_gates": list(scenario.expected_failed_gates),
            "skipped_gates": list(scenario.expected_skipped_gates),
            "failed_checks": list(scenario.expected_failed_checks),
            "skipped_checks": list(scenario.expected_skipped_checks),
            "publication_sha256": scenario.expected_publication_sha256,
        },
        "checks": {},
        "passed": False,
        "runs": [],
        "execution_error": {
            "type": type(exc).__name__,
            "message": str(exc),
        },
    }


def _stage_producer_visible_package(source: Path, target: Path) -> None:
    def ignore_hidden(current: str, names: list[str]) -> set[str]:
        if Path(current).resolve() == source.resolve() and "expected" in names:
            return {"expected"}
        return set()

    shutil.copytree(source, target, ignore=ignore_hidden)
    if (target / "expected").exists():
        raise DevelopmentBenchmarkError(
            "Producer-hidden expected assets entered a staged package."
        )


def _assign_scenario_identity(package_root: Path, package_id: str) -> None:
    manifest_path = package_root / "package_manifest.json"
    manifest = _read_json(manifest_path)
    manifest["package_id"] = package_id
    _write_json(manifest_path, manifest)
    authority_path = package_root / "authority/authority_map.json"
    authority = _read_json(authority_path)
    authority["applies_to"] = package_id
    _write_json(authority_path, authority)


def _mutation_clean(package_root: Path) -> None:
    del package_root


def _mutation_manifest_malformed(package_root: Path) -> None:
    (package_root / "package_manifest.json").write_text(
        "{\n", encoding="utf-8", newline="\n"
    )


def _mutation_manifest_schema_unsupported(package_root: Path) -> None:
    _mutate_json(
        package_root / "package_manifest.json",
        lambda document: document.__setitem__("schema_version", "0.4.0"),
    )


def _mutation_source_missing(package_root: Path) -> None:
    (package_root / "inputs/drawing_metadata.json").unlink()


def _mutation_authority_rule_missing(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        document["rules"] = [
            rule
            for rule in document["rules"]
            if rule["field"] != "drawing.current_revision"
        ]

    _mutate_json(package_root / "authority/authority_map.json", mutate)


def _mutation_authority_source_contradiction(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        rule = next(
            item for item in document["rules"] if item["rule_id"] == "AUTH-DWG-001"
        )
        rule["secondary_sources"].append(rule["authoritative_source"])

    _mutate_json(package_root / "authority/authority_map.json", mutate)


def _mutation_controlled_file_missing(package_root: Path) -> None:
    manifest = _read_json(package_root / "package_manifest.json")
    (package_root / manifest["file_references"][0]["path"]).unlink()


def _mutation_identifier_whitespace(package_root: Path) -> None:
    _mutate_csv(
        package_root / "inputs/bom_or_equipment_list.csv",
        lambda rows: rows[0].__setitem__("datasheet_id", " DS-P-101 "),
    )


def _mutation_duplicate_document_id(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        document["records"][1]["document_id"] = document["records"][0][
            "document_id"
        ]

    _mutate_json(package_root / "inputs/drawing_metadata.json", mutate)


def _mutation_revision_invalid(package_root: Path) -> None:
    _mutate_json(
        package_root / "inputs/drawing_metadata.json",
        lambda document: document["records"][0].__setitem__("revision_id", "c"),
    )


def _mutation_evidence_requirement_missing(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        document["evidence_locator_requirements"]["csv"]["required_fields"].remove(
            "row_key"
        )

    _mutate_json(package_root / "authority/authority_map.json", mutate)


def _mutation_drawing_revision_mismatch(package_root: Path) -> None:
    _mutate_json(
        package_root / "inputs/drawing_metadata.json",
        lambda document: document["records"][0].__setitem__("revision_id", "A"),
    )


def _mutation_drawing_metadata_missing(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        document["records"] = [
            record
            for record in document["records"]
            if record["record_id"] != "DWMETA-001"
        ]

    _mutate_json(package_root / "inputs/drawing_metadata.json", mutate)


def _mutation_drawing_register_missing(package_root: Path) -> None:
    _mutate_csv(
        package_root / "inputs/drawing_register.csv",
        lambda rows: rows.__setitem__(
            slice(None),
            [row for row in rows if row["document_id"] != "DOC-DWG-001"],
        ),
    )


def _mutation_drawing_file_reference_mismatch(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        record = next(
            item for item in document["records"] if item["record_id"] == "DWMETA-001"
        )
        record["file_ref_id"] = "FILE-DWG-002"

    _mutate_json(package_root / "inputs/drawing_metadata.json", mutate)


def _mutation_drawing_manifest_mapping_missing(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        document["relationship_declarations"] = [
            item
            for item in document["relationship_declarations"]
            if item["relationship_id"] != "REL-DOC-FILE-001"
        ]

    _mutate_json(package_root / "package_manifest.json", mutate)


def _mutation_bom_manifest_target_mismatch(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        relationship = next(
            item
            for item in document["relationship_declarations"]
            if item["relationship_id"] == "REL-ITEM-EQ-001"
        )
        relationship["target"]["identifier"] = "M-101A"

    _mutate_json(package_root / "package_manifest.json", mutate)


def _mutation_bom_drawing_tag_missing(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        record = next(
            item for item in document["records"] if item["record_id"] == "DWMETA-001"
        )
        record["equipment_tags"] = ["P-101A"]

    _mutate_json(package_root / "inputs/drawing_metadata.json", mutate)


def _mutation_datasheet_authority_missing(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        document["datasheets"] = [
            item
            for item in document["datasheets"]
            if item["record_id"] != "DSMETA-001"
        ]

    _mutate_json(package_root / "inputs/datasheet_spec_metadata.json", mutate)


def _mutation_datasheet_association_mismatch(package_root: Path) -> None:
    def mutate(rows: list[dict[str, str]]) -> None:
        record = next(item for item in rows if item["item_id"] == "ITEM-PUMP-001")
        record["datasheet_id"] = "DS-M-101"

    _mutate_csv(package_root / "inputs/bom_or_equipment_list.csv", mutate)


def _mutation_datasheet_manifest_mismatch(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        relationship = next(
            item
            for item in document["relationship_declarations"]
            if item["relationship_id"] == "REL-EQ-DS-001"
        )
        relationship["target"]["identifier"] = "DS-M-101"

    _mutate_json(package_root / "package_manifest.json", mutate)


def _mutation_specification_revision_mismatch(package_root: Path) -> None:
    def mutate(document: dict[str, Any]) -> None:
        record = next(
            item
            for item in document["specifications"]
            if item["record_id"] == "SPMETA-001"
        )
        record["revision_id"] = "B"

    _mutate_json(package_root / "inputs/datasheet_spec_metadata.json", mutate)


_MUTATIONS: dict[str, Callable[[Path], None]] = {
    "clean": _mutation_clean,
    "manifest_malformed": _mutation_manifest_malformed,
    "manifest_schema_unsupported": _mutation_manifest_schema_unsupported,
    "source_missing": _mutation_source_missing,
    "authority_rule_missing": _mutation_authority_rule_missing,
    "authority_source_contradiction": _mutation_authority_source_contradiction,
    "controlled_file_missing": _mutation_controlled_file_missing,
    "identifier_whitespace": _mutation_identifier_whitespace,
    "duplicate_document_id": _mutation_duplicate_document_id,
    "revision_invalid": _mutation_revision_invalid,
    "evidence_requirement_missing": _mutation_evidence_requirement_missing,
    "drawing_revision_mismatch": _mutation_drawing_revision_mismatch,
    "drawing_metadata_missing": _mutation_drawing_metadata_missing,
    "drawing_register_missing": _mutation_drawing_register_missing,
    "drawing_file_reference_mismatch": _mutation_drawing_file_reference_mismatch,
    "drawing_manifest_mapping_missing": _mutation_drawing_manifest_mapping_missing,
    "bom_manifest_target_mismatch": _mutation_bom_manifest_target_mismatch,
    "bom_drawing_tag_missing": _mutation_bom_drawing_tag_missing,
    "datasheet_authority_missing": _mutation_datasheet_authority_missing,
    "datasheet_association_mismatch": _mutation_datasheet_association_mismatch,
    "datasheet_manifest_mismatch": _mutation_datasheet_manifest_mismatch,
    "specification_revision_mismatch": _mutation_specification_revision_mismatch,
}


def _mutate_json(path: Path, mutate: Callable[[dict[str, Any]], None]) -> None:
    document = _read_json(path)
    mutate(document)
    _write_json(path, document)


def _mutate_csv(
    path: Path, mutate: Callable[[list[dict[str, str]]], None]
) -> None:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        rows = list(reader)
    if fieldnames is None:
        raise DevelopmentBenchmarkError(f"CSV source has no header: {path}")
    mutate(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _select_scenarios(
    definition: DevelopmentBenchmarkDefinition,
    selected_scenario_ids: Sequence[str] | None,
) -> tuple[DevelopmentScenario, ...]:
    if selected_scenario_ids is None:
        return definition.scenarios
    requested = tuple(selected_scenario_ids)
    _require_unique(requested, "selected scenario ID")
    by_id = {scenario.scenario_id: scenario for scenario in definition.scenarios}
    unknown = sorted(set(requested) - set(by_id))
    if unknown:
        raise DevelopmentBenchmarkError(
            "Unknown selected scenario(s): " + ", ".join(unknown)
        )
    return tuple(by_id[scenario_id] for scenario_id in requested)


def _benchmark_run_id(
    started_at: datetime,
    scenario_id: str,
    scenario_index: int,
    repetition: int,
) -> str:
    timestamp = started_at + timedelta(
        seconds=scenario_index, microseconds=repetition
    )
    prefix = timestamp.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    suffix = hashlib.sha256(
        f"{scenario_id}:{repetition}".encode("ascii")
    ).hexdigest()[:8]
    return f"RUN-{prefix}-{suffix}"


def _status_ids(results: Sequence[Mapping[str, Any]], status: str) -> list[str]:
    return [
        str(result.get("gate_id") or result.get("check_id"))
        for result in results
        if result["status"] == status
    ]


def _package_tree_hash(package_root: Path) -> str:
    tree_hash_input = bytearray()
    for path in sorted(
        (path for path in package_root.rglob("*") if path.is_file()),
        key=lambda item: item.relative_to(package_root).as_posix(),
    ):
        relative = path.relative_to(package_root).as_posix()
        digest = _sha256_file(path)
        tree_hash_input.extend(relative.encode("utf-8"))
        tree_hash_input.extend(b"\0")
        tree_hash_input.extend(digest.encode("ascii"))
        tree_hash_input.extend(b"\n")
    return hashlib.sha256(tree_hash_input).hexdigest()


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_commit(repository_root: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repository_root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "unavailable"


def _read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise DevelopmentBenchmarkError(f"Could not read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise DevelopmentBenchmarkError(f"JSON root must be an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _resolve_inside(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise DevelopmentBenchmarkError(
            f"Benchmark path resolves outside the repository: {path}"
        ) from exc
    return resolved


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DevelopmentBenchmarkError(f"{label} must be an object.")
    return value


def _require_exact_keys(
    value: Mapping[str, Any], expected: set[str], label: str
) -> None:
    missing = sorted(expected - set(value))
    extra = sorted(set(value) - expected)
    if missing or extra:
        raise DevelopmentBenchmarkError(
            f"{label} keys differ; missing={missing}, extra={extra}."
        )


def _require_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise DevelopmentBenchmarkError(f"{label} must be a non-empty string.")
    return value


def _require_string_list(value: Any, label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise DevelopmentBenchmarkError(
            f"{label} must be an array of non-empty strings."
        )
    if len(value) != len(set(value)):
        raise DevelopmentBenchmarkError(f"{label} must not contain duplicates.")
    return tuple(value)


def _ordered_subset(
    value: Any, order: Sequence[str], label: str
) -> tuple[str, ...]:
    items = _require_string_list(value, label)
    unknown = sorted(set(items) - set(order))
    if unknown:
        raise DevelopmentBenchmarkError(
            f"{label} contains unknown IDs: {', '.join(unknown)}"
        )
    expected_order = tuple(item for item in order if item in items)
    if items != expected_order:
        raise DevelopmentBenchmarkError(f"{label} must use evaluator order.")
    return items


def _require_sha256(value: Any, label: str) -> str:
    text = _require_string(value, label)
    if len(text) != _HEX_DIGEST_LENGTH or any(
        character not in "0123456789abcdef" for character in text
    ):
        raise DevelopmentBenchmarkError(f"{label} must be a lowercase SHA-256.")
    return text


def _require_unique(values: Sequence[str] | Any, label: str) -> None:
    materialized = tuple(values)
    if len(materialized) != len(set(materialized)):
        raise DevelopmentBenchmarkError(f"{label} values must be unique.")
