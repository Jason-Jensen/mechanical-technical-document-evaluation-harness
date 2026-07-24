"""Run the D-118 authoring controls with development-only synthetic packages."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance import (
    PACKAGE_RESULT_FILENAME,
    execute_package_audit,
    validate_package_contract,
    verify_custodian_target_reachability,
    write_custodian_reachability_reports,
)
from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
from mech_eval_harness.package_assurance.relationships import (
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
)


PROOF_REPORT_JSON = "benchmark_authoring_control_proof.json"
PROOF_REPORT_MARKDOWN = "benchmark_authoring_control_proof.md"
DEVELOPMENT_PACKAGE = Path(
    "benchmarks/package_assurance/development/pump_skid_clean_v1/package"
)


class BenchmarkAuthoringControlProofError(RuntimeError):
    """Raised when development-only corrective-action proof cannot complete."""


def run_benchmark_authoring_control_proof(
    *,
    repository_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    """Prove the public validator and redacted reachability workflow end to end."""

    repository_root = repository_root.resolve()
    output_root = output_root.resolve()
    if not repository_root.is_dir():
        raise BenchmarkAuthoringControlProofError(
            "Repository root is not a directory."
        )
    if output_root.exists():
        raise BenchmarkAuthoringControlProofError(
            "Proof output already exists and will not be overwritten."
        )
    benchmark_root = (
        repository_root / "benchmarks" / "package_assurance"
    ).resolve()
    if _is_relative_to(output_root, benchmark_root):
        raise BenchmarkAuthoringControlProofError(
            "Generated proof must stay outside versioned benchmark definitions."
        )

    package_source = (repository_root / DEVELOPMENT_PACKAGE).resolve()
    packages_root = output_root / "development-packages"
    results_root = output_root / "results"
    output_root.mkdir(parents=True)
    clean = _copy_producer_package(package_source, packages_root / "clean")
    relationship_fault = _copy_producer_package(
        package_source,
        packages_root / "relationship-fault",
    )
    scope_defect = _copy_producer_package(
        package_source,
        packages_root / "scope-defect",
    )
    _set_relationship_revision_fault(relationship_fault)
    _set_authority_scope_defect(scope_defect)

    validations = {
        "clean": validate_package_contract(
            repository_root=repository_root,
            package_root=clean,
        ),
        "relationship_fault": validate_package_contract(
            repository_root=repository_root,
            package_root=relationship_fault,
        ),
        "scope_defect": validate_package_contract(
            repository_root=repository_root,
            package_root=scope_defect,
        ),
    }
    result_paths = {
        "clean": _audit_result(
            repository_root,
            clean,
            results_root / "clean",
            "RUN-20260724T000000000000Z-d1180001",
        ),
        "relationship_fault": _audit_result(
            repository_root,
            relationship_fault,
            results_root / "relationship-fault",
            "RUN-20260724T000000000000Z-d1180002",
        ),
        "scope_defect": _audit_result(
            repository_root,
            scope_defect,
            results_root / "scope-defect",
            "RUN-20260724T000000000000Z-d1180003",
        ),
    }

    reachable_root = output_root / "custody-reachable"
    reachable_index, reachable_plan = _prepare_custody_case(
        reachable_root,
        clean_result=result_paths["clean"],
        fault_result=result_paths["relationship_fault"],
        target_kind="relationship_check",
        target_id=DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    )
    reachable_outcome = verify_custodian_target_reachability(
        repository_root=repository_root,
        custody_root=reachable_root,
        public_index_path=reachable_index,
        protected_plan_path=reachable_plan,
    )
    reachable_public, reachable_protected = write_custodian_reachability_reports(
        outcome=reachable_outcome,
        output_directory=reachable_root / "verification",
    )

    blocker_root = output_root / "custody-unplanned-blocker"
    blocker_index, blocker_plan = _prepare_custody_case(
        blocker_root,
        clean_result=result_paths["clean"],
        fault_result=result_paths["scope_defect"],
        target_kind="relationship_check",
        target_id=DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    )
    blocker_outcome = verify_custodian_target_reachability(
        repository_root=repository_root,
        custody_root=blocker_root,
        public_index_path=blocker_index,
        protected_plan_path=blocker_plan,
    )
    blocker_public, blocker_protected = write_custodian_reachability_reports(
        outcome=blocker_outcome,
        output_directory=blocker_root / "verification",
    )

    scope_codes = {
        code
        for gate in validations["scope_defect"].gates
        for code in gate.finding_codes
    }
    controls = {
        "clean_public_contract_passed": (
            validations["clean"].public_contract_complete
        ),
        "relationship_fault_public_contract_passed": (
            validations["relationship_fault"].public_contract_complete
        ),
        "d117_scope_defect_rejected": (
            not validations["scope_defect"].public_contract_complete
            and validations["scope_defect"].failed_gate_ids
            == (AUTHORITY_GATE_ID,)
            and "AUTHORITY_SCOPE_CONFLICT" in scope_codes
        ),
        "relationship_target_reachable": reachable_outcome.passed,
        "unplanned_authority_blocker_rejected": (
            not blocker_outcome.passed
            and blocker_outcome.public_attestation["reachable_target_count"] == 0
            and blocker_outcome.public_attestation["unplanned_blocker_count"] == 1
        ),
        "public_attestations_redacted": (
            reachable_outcome.public_attestation["protected_values_published"]
            is False
            and blocker_outcome.public_attestation["protected_values_published"]
            is False
            and "scenarios" not in reachable_outcome.public_attestation
            and "scenarios" not in blocker_outcome.public_attestation
        ),
    }
    report = {
        "schema_version": "0.3.0",
        "proof_id": "PROOF-D118-AUTHORING-CONTROLS-001",
        "status": "passed" if all(controls.values()) else "failed",
        "input_class": "development_only_synthetic",
        "semantic_held_out_executions": 0,
        "controls": controls,
        "public_contract_results": {
            name: validation.to_dict()
            for name, validation in validations.items()
        },
        "reachability_attestations": {
            "reachable": reachable_outcome.public_attestation,
            "unplanned_blocker": blocker_outcome.public_attestation,
        },
        "generated_artifacts": {
            "reachable_public": reachable_public.relative_to(output_root).as_posix(),
            "reachable_protected": (
                reachable_protected.relative_to(output_root).as_posix()
            ),
            "blocker_public": blocker_public.relative_to(output_root).as_posix(),
            "blocker_protected": (
                blocker_protected.relative_to(output_root).as_posix()
            ),
        },
        "claim_boundary": (
            "Development-only operating proof of authoring controls. It does not "
            "authorize or evaluate a new external family, establish benchmark "
            "accuracy, or support release or engineering claims."
        ),
    }
    _write_json(output_root / PROOF_REPORT_JSON, report)
    (output_root / PROOF_REPORT_MARKDOWN).write_text(
        _render_markdown(report),
        encoding="utf-8",
    )
    return report


def _copy_producer_package(source: Path, target: Path) -> Path:
    shutil.copytree(
        source,
        target,
        ignore=shutil.ignore_patterns("expected"),
    )
    return target


def _set_relationship_revision_fault(package_root: Path) -> None:
    path = package_root / "inputs" / "drawing_metadata.json"
    document = _load_json(path)
    current = document["records"][0]["revision_id"]
    document["records"][0]["revision_id"] = "B" if current != "B" else "A"
    _write_json(path, document)


def _set_authority_scope_defect(package_root: Path) -> None:
    path = package_root / "authority" / "authority_map.json"
    document = _load_json(path)
    document["applies_to"] = "FAMILY-NOT-PACKAGE"
    _write_json(path, document)


def _audit_result(
    repository_root: Path,
    package_root: Path,
    runs_dir: Path,
    run_id: str,
) -> Path:
    outcome = execute_package_audit(
        repository_root=repository_root,
        package_root=package_root,
        runs_dir=runs_dir,
        schema_path=repository_root / "schemas" / "package_result.schema.json",
        run_id=run_id,
    )
    return outcome.publication.result_path


def _prepare_custody_case(
    custody_root: Path,
    *,
    clean_result: Path,
    fault_result: Path,
    target_kind: str,
    target_id: str,
) -> tuple[Path, Path]:
    result_paths = {}
    for token, source in (("S01", clean_result), ("S02", fault_result)):
        target = custody_root / "results" / token / PACKAGE_RESULT_FILENAME
        target.parent.mkdir(parents=True)
        shutil.copy2(source, target)
        result_paths[token] = target.relative_to(custody_root).as_posix()

    public_index_path = custody_root / "public_index.json"
    protected_plan_path = custody_root / "protected" / "target_plan.json"
    protected_plan_path.parent.mkdir(parents=True)
    _write_json(
        public_index_path,
        {
            "schema_version": "0.3.0",
            "family_id": f"FAM-D118-{custody_root.name.upper()}",
            "scenario_results": [
                {
                    "scenario_token": token,
                    "package_result_path": result_paths[token],
                }
                for token in ("S01", "S02")
            ],
        },
    )
    _write_json(
        protected_plan_path,
        {
            "schema_version": "0.3.0",
            "family_id": f"FAM-D118-{custody_root.name.upper()}",
            "commitment_nonce": "d118" * 16,
            "scenarios": [
                {
                    "scenario_token": "S01",
                    "scenario_role": "clean",
                    "targets": [],
                },
                {
                    "scenario_token": "S02",
                    "scenario_role": "fault",
                    "targets": [
                        {
                            "kind": target_kind,
                            "control_id": target_id,
                        }
                    ],
                },
            ],
        },
    )
    return public_index_path, protected_plan_path


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# D-118 Benchmark-Authoring Control Proof",
        "",
        f"**Status:** {str(report['status']).upper()}",
        "",
        "## Development-Only Controls",
        "",
    ]
    for control, passed in report["controls"].items():
        lines.append(f"- {'PASS' if passed else 'FAIL'} `{control}`")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            str(report["claim_boundary"]),
            "",
            "No held-out semantic execution was performed.",
            "",
        ]
    )
    return "\n".join(lines)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run development-only proof of the D-118 authoring controls."
    )
    parser.add_argument("repository_root", type=Path)
    parser.add_argument("output_root", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        report = run_benchmark_authoring_control_proof(
            repository_root=args.repository_root,
            output_root=args.output_root,
        )
    except BenchmarkAuthoringControlProofError as exc:
        print(f"ERROR: {exc}")
        return 2
    print(f"STATUS: {str(report['status']).upper()}")
    print(f"REPORT: {args.output_root.resolve() / PROOF_REPORT_JSON}")
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
