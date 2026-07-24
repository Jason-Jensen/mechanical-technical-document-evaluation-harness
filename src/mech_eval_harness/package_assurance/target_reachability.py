"""Custodian-only verification that protected benchmark targets are reachable."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping

from mech_eval_harness.package_assurance.gates import PACKAGE_GATE_ORDER
from mech_eval_harness.package_assurance.persistence import (
    PackageResultSchemaValidationError,
    validate_package_result_document,
)
from mech_eval_harness.package_assurance.relationships import (
    RELATIONSHIP_CHECK_ORDER,
)


TARGET_REACHABILITY_VERIFIER_ID = "VER-PKG-TARGET-REACHABILITY-001"
TARGET_REACHABILITY_VERIFIER_VERSION = "0.3.0"
PUBLIC_REACHABILITY_FILENAME = "target_reachability.public.json"
PROTECTED_REACHABILITY_FILENAME = "target_reachability.protected.json"
PROTECTED_COMMITMENT_NONCE_HEX_LENGTH = 64

class TargetReachabilityError(ValueError):
    """Raised when custody inputs cannot support a valid reachability check."""


@dataclass(frozen=True)
class CustodianReachabilityOutcome:
    """Redacted public attestation plus protected scenario-level detail."""

    public_attestation: Mapping[str, Any]
    protected_detail: Mapping[str, Any]

    @property
    def passed(self) -> bool:
        return self.public_attestation["status"] == "passed"


def verify_custodian_target_reachability(
    *,
    repository_root: Path,
    custody_root: Path,
    public_index_path: Path,
    protected_plan_path: Path,
) -> CustodianReachabilityOutcome:
    """Verify clean gates and protected target reachability from frozen results."""

    repository_root = repository_root.resolve()
    custody_root = custody_root.resolve()
    if not repository_root.is_dir():
        raise TargetReachabilityError("Repository root is not a directory.")
    if not custody_root.is_dir():
        raise TargetReachabilityError("Custody root is not a directory.")

    public_index_path = _confined_input(
        custody_root,
        public_index_path,
        "public index",
    )
    protected_plan_path = _confined_input(
        custody_root,
        protected_plan_path,
        "protected plan",
    )
    public_index = _load_object(public_index_path, "public index")
    protected_plan = _load_object(protected_plan_path, "protected plan")
    family_id, indexed_scenarios = _parse_public_index(
        public_index,
        custody_root,
    )
    planned_scenarios = _parse_protected_plan(protected_plan, family_id)
    if set(indexed_scenarios) != set(planned_scenarios):
        raise TargetReachabilityError(
            "Public index and protected plan scenario tokens do not match."
        )

    schema_path = repository_root / "schemas" / "package_result.schema.json"
    result_documents: dict[str, dict[str, Any]] = {}
    result_hashes: dict[str, str] = {}
    result_paths: dict[str, str] = {}
    for token, result_path in indexed_scenarios.items():
        document = _load_object(result_path, f"package result for {token}")
        try:
            validate_package_result_document(document, schema_path)
        except PackageResultSchemaValidationError as exc:
            raise TargetReachabilityError(
                f"Package result for {token} is not schema-valid."
            ) from exc
        _require_control_order(document, token)
        result_documents[token] = document
        result_hashes[token] = _sha256_file(result_path)
        result_paths[token] = result_path.relative_to(custody_root).as_posix()

    scenario_details: list[dict[str, Any]] = []
    clean_passes = True
    target_count = 0
    reachable_target_count = 0
    unplanned_blocker_count = 0
    for token in sorted(planned_scenarios):
        plan = planned_scenarios[token]
        document = result_documents[token]
        gate_statuses = {
            gate["gate_id"]: gate["status"] for gate in document["gate_results"]
        }
        relationship_statuses = {
            check["check_id"]: check["status"]
            for check in document["relationship_results"]
        }
        relationship_blockers = {
            check["check_id"]: tuple(check["blocked_by"])
            for check in document["relationship_results"]
        }
        gate_blockers = {
            gate["gate_id"]: tuple(gate["blocked_by"])
            for gate in document["gate_results"]
        }
        all_gates_passed = all(
            gate_statuses[gate_id] == "passed" for gate_id in PACKAGE_GATE_ORDER
        )
        if plan["scenario_role"] == "clean":
            clean_passes = clean_passes and all_gates_passed
            if not all_gates_passed:
                unplanned_blocker_count += 1

        target_details: list[dict[str, Any]] = []
        for target in plan["targets"]:
            target_count += 1
            reachable, blockers, target_status = _target_reachability(
                target=target,
                gate_statuses=gate_statuses,
                gate_blockers=gate_blockers,
                relationship_statuses=relationship_statuses,
                relationship_blockers=relationship_blockers,
            )
            if reachable:
                reachable_target_count += 1
            else:
                unplanned_blocker_count += 1
            target_details.append(
                {
                    "kind": target["kind"],
                    "control_id": target["control_id"],
                    "status": target_status,
                    "reachable": reachable,
                    "unplanned_blockers": list(blockers),
                }
            )

        scenario_details.append(
            {
                "scenario_token": token,
                "scenario_role": plan["scenario_role"],
                "package_id": document["package_id"],
                "package_result_path": result_paths[token],
                "package_result_sha256": result_hashes[token],
                "all_mandatory_gates_passed": all_gates_passed,
                "targets": target_details,
            }
        )

    status = (
        "passed"
        if clean_passes
        and target_count > 0
        and reachable_target_count == target_count
        else "failed"
    )
    protected_detail = {
        "schema_version": TARGET_REACHABILITY_VERIFIER_VERSION,
        "verifier_id": TARGET_REACHABILITY_VERIFIER_ID,
        "verifier_version": TARGET_REACHABILITY_VERIFIER_VERSION,
        "family_id": family_id,
        "status": status,
        "scenarios": scenario_details,
        "claim_boundary": (
            "Protected detail proves control reachability only. Exact expected "
            "findings, values, engineering correctness, and release remain separate."
        ),
    }
    protected_detail_sha256 = _sha256_bytes(_pretty_bytes(protected_detail))
    roles = [plan["scenario_role"] for plan in planned_scenarios.values()]
    public_attestation = {
        "schema_version": TARGET_REACHABILITY_VERIFIER_VERSION,
        "verifier_id": TARGET_REACHABILITY_VERIFIER_ID,
        "verifier_version": TARGET_REACHABILITY_VERIFIER_VERSION,
        "family_id": family_id,
        "status": status,
        "scenario_count": len(planned_scenarios),
        "clean_scenario_count": roles.count("clean"),
        "fault_scenario_count": roles.count("fault"),
        "target_count": target_count,
        "reachable_target_count": reachable_target_count,
        "unplanned_blocker_count": unplanned_blocker_count,
        "clean_all_mandatory_gates_passed": clean_passes,
        "public_index_sha256": _sha256_file(public_index_path),
        "protected_plan_sha256": _sha256_file(protected_plan_path),
        "result_set_sha256": _result_set_sha256(result_paths, result_hashes),
        "protected_detail_sha256": protected_detail_sha256,
        "protected_values_published": False,
        "claim_boundary": (
            "Aggregate target-reachability attestation only; no scenario mapping, "
            "target identity, expected finding, value, or release claim is published."
        ),
    }
    return CustodianReachabilityOutcome(
        public_attestation=public_attestation,
        protected_detail=protected_detail,
    )


def write_custodian_reachability_reports(
    *,
    outcome: CustodianReachabilityOutcome,
    output_directory: Path,
) -> tuple[Path, Path]:
    """Write protected detail first and the redacted public completion marker last."""

    output_directory = output_directory.resolve()
    try:
        output_directory.mkdir(parents=True, exist_ok=False)
    except FileExistsError as exc:
        raise TargetReachabilityError(
            "Reachability output directory already exists and will not be overwritten."
        ) from exc
    except OSError as exc:
        raise TargetReachabilityError(
            "Reachability output directory could not be created."
        ) from exc

    protected_path = output_directory / PROTECTED_REACHABILITY_FILENAME
    public_path = output_directory / PUBLIC_REACHABILITY_FILENAME
    try:
        protected_path.write_bytes(_pretty_bytes(outcome.protected_detail))
        public_path.write_bytes(_pretty_bytes(outcome.public_attestation))
    except OSError as exc:
        raise TargetReachabilityError(
            "Reachability reports could not be written completely."
        ) from exc
    return public_path, protected_path


def _parse_public_index(
    document: Mapping[str, Any],
    custody_root: Path,
) -> tuple[str, dict[str, Path]]:
    _require_exact_keys(
        document,
        {"schema_version", "family_id", "scenario_results"},
        "public index",
    )
    _require_version(document, "public index")
    family_id = _nonempty_string(document["family_id"], "public index family_id")
    rows = document["scenario_results"]
    if not isinstance(rows, list) or not rows:
        raise TargetReachabilityError(
            "Public index scenario_results must be a non-empty array."
        )

    scenarios: dict[str, Path] = {}
    paths: set[Path] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TargetReachabilityError(
                f"Public index scenario_results[{index}] must be an object."
            )
        _require_exact_keys(
            row,
            {"scenario_token", "package_result_path"},
            f"public index scenario_results[{index}]",
        )
        token = _nonempty_string(
            row["scenario_token"],
            f"public index scenario_results[{index}].scenario_token",
        )
        if token in scenarios:
            raise TargetReachabilityError(
                f"Public index repeats scenario token: {token}"
            )
        result_path = _resolve_relative_path(
            custody_root,
            row["package_result_path"],
            f"package result for {token}",
        )
        if result_path in paths:
            raise TargetReachabilityError(
                "Public index package_result_path values must be unique."
            )
        if not result_path.is_file():
            raise TargetReachabilityError(
                f"Package result for {token} is not a file."
            )
        scenarios[token] = result_path
        paths.add(result_path)
    return family_id, scenarios


def _parse_protected_plan(
    document: Mapping[str, Any],
    family_id: str,
) -> dict[str, dict[str, Any]]:
    _require_exact_keys(
        document,
        {"schema_version", "family_id", "commitment_nonce", "scenarios"},
        "protected plan",
    )
    _require_version(document, "protected plan")
    commitment_nonce = _nonempty_string(
        document["commitment_nonce"],
        "protected plan commitment_nonce",
    )
    if (
        len(commitment_nonce) != PROTECTED_COMMITMENT_NONCE_HEX_LENGTH
        or any(character not in "0123456789abcdef" for character in commitment_nonce)
    ):
        raise TargetReachabilityError(
            "Protected plan commitment_nonce must be 64 lowercase hexadecimal "
            "characters generated inside custody."
        )
    if document["family_id"] != family_id:
        raise TargetReachabilityError(
            "Public index and protected plan family_id values do not match."
        )
    rows = document["scenarios"]
    if not isinstance(rows, list) or not rows:
        raise TargetReachabilityError(
            "Protected plan scenarios must be a non-empty array."
        )

    scenarios: dict[str, dict[str, Any]] = {}
    clean_count = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise TargetReachabilityError(
                f"Protected plan scenarios[{index}] must be an object."
            )
        _require_exact_keys(
            row,
            {"scenario_token", "scenario_role", "targets"},
            f"protected plan scenarios[{index}]",
        )
        token = _nonempty_string(
            row["scenario_token"],
            f"protected plan scenarios[{index}].scenario_token",
        )
        if token in scenarios:
            raise TargetReachabilityError(
                f"Protected plan repeats scenario token: {token}"
            )
        role = row["scenario_role"]
        if role not in {"clean", "fault"}:
            raise TargetReachabilityError(
                f"Protected plan scenario {token} has an invalid scenario_role."
            )
        targets = _parse_targets(row["targets"], token)
        if role == "clean":
            clean_count += 1
            if targets:
                raise TargetReachabilityError(
                    "The clean scenario must not declare protected fault targets."
                )
        elif not targets:
            raise TargetReachabilityError(
                f"Fault scenario {token} must declare at least one target."
            )
        scenarios[token] = {
            "scenario_role": role,
            "targets": targets,
        }
    if clean_count != 1:
        raise TargetReachabilityError(
            "Protected plan must declare exactly one clean scenario."
        )
    if len(scenarios) < 2:
        raise TargetReachabilityError(
            "Protected plan must include at least one fault scenario."
        )
    return scenarios


def _parse_targets(value: Any, token: str) -> tuple[dict[str, str], ...]:
    if not isinstance(value, list):
        raise TargetReachabilityError(
            f"Protected plan targets for {token} must be an array."
        )
    targets: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, target in enumerate(value):
        if not isinstance(target, dict):
            raise TargetReachabilityError(
                f"Protected target {token}[{index}] must be an object."
            )
        _require_exact_keys(
            target,
            {"kind", "control_id"},
            f"protected target {token}[{index}]",
        )
        kind = target["kind"]
        control_id = target["control_id"]
        if kind not in {"gate", "relationship_check"}:
            raise TargetReachabilityError(
                f"Protected target {token}[{index}] has an invalid kind."
            )
        control_id = _nonempty_string(
            control_id,
            f"protected target {token}[{index}].control_id",
        )
        allowed = (
            PACKAGE_GATE_ORDER if kind == "gate" else RELATIONSHIP_CHECK_ORDER
        )
        if control_id not in allowed:
            raise TargetReachabilityError(
                f"Protected target {token}[{index}] is not an accepted control."
            )
        key = (kind, control_id)
        if key in seen:
            raise TargetReachabilityError(
                f"Protected plan repeats a target for scenario {token}."
            )
        seen.add(key)
        targets.append({"kind": kind, "control_id": control_id})
    return tuple(targets)


def _target_reachability(
    *,
    target: Mapping[str, str],
    gate_statuses: Mapping[str, str],
    gate_blockers: Mapping[str, tuple[str, ...]],
    relationship_statuses: Mapping[str, str],
    relationship_blockers: Mapping[str, tuple[str, ...]],
) -> tuple[bool, tuple[str, ...], str]:
    control_id = target["control_id"]
    if target["kind"] == "gate":
        target_index = PACKAGE_GATE_ORDER.index(control_id)
        predecessors = PACKAGE_GATE_ORDER[:target_index]
        failed_predecessors = [
            gate_id
            for gate_id in predecessors
            if gate_statuses[gate_id] == "failed"
        ]
        blockers = failed_predecessors or [
            gate_id
            for gate_id in predecessors
            if gate_statuses[gate_id] != "passed"
        ]
        target_status = gate_statuses[control_id]
        if target_status == "skipped":
            blockers.extend(gate_blockers[control_id])
    else:
        failed_gates = [
            gate_id
            for gate_id in PACKAGE_GATE_ORDER
            if gate_statuses[gate_id] == "failed"
        ]
        blockers = failed_gates or [
            gate_id
            for gate_id in PACKAGE_GATE_ORDER
            if gate_statuses[gate_id] != "passed"
        ]
        target_status = relationship_statuses[control_id]
        if target_status == "skipped":
            blockers.extend(relationship_blockers[control_id])
    unique_blockers = tuple(dict.fromkeys(blockers))
    return (
        target_status != "skipped" and not unique_blockers,
        unique_blockers,
        target_status,
    )


def _require_control_order(document: Mapping[str, Any], token: str) -> None:
    gate_ids = tuple(gate["gate_id"] for gate in document["gate_results"])
    if gate_ids != PACKAGE_GATE_ORDER:
        raise TargetReachabilityError(
            f"Package result for {token} does not contain the accepted gate order."
        )
    check_ids = tuple(
        check["check_id"] for check in document["relationship_results"]
    )
    if check_ids != RELATIONSHIP_CHECK_ORDER:
        raise TargetReachabilityError(
            f"Package result for {token} does not contain the accepted check order."
        )


def _confined_input(root: Path, path: Path, label: str) -> Path:
    candidate = path if path.is_absolute() else root / path
    candidate = candidate.resolve()
    if not _is_relative_to(candidate, root) or not candidate.is_file():
        raise TargetReachabilityError(
            f"{label.capitalize()} must be a file inside the custody root."
        )
    return candidate


def _resolve_relative_path(root: Path, value: Any, label: str) -> Path:
    value = _nonempty_string(value, label)
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or "\\" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise TargetReachabilityError(
            f"{label.capitalize()} must use a confined POSIX-relative path."
        )
    candidate = (root / Path(*posix_path.parts)).resolve()
    if not _is_relative_to(candidate, root):
        raise TargetReachabilityError(
            f"{label.capitalize()} escapes the custody root."
        )
    return candidate


def _load_object(path: Path, label: str) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TargetReachabilityError(f"Could not read {label}.") from exc
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise TargetReachabilityError(f"{label.capitalize()} is not valid JSON.") from exc
    if not isinstance(document, dict):
        raise TargetReachabilityError(
            f"{label.capitalize()} must contain a top-level object."
        )
    return document


def _require_exact_keys(
    document: Mapping[str, Any],
    expected: set[str],
    label: str,
) -> None:
    actual = set(document)
    if actual != expected:
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        raise TargetReachabilityError(
            f"{label.capitalize()} keys are invalid; "
            f"missing={missing}, unexpected={unexpected}."
        )


def _require_version(document: Mapping[str, Any], label: str) -> None:
    if document["schema_version"] != TARGET_REACHABILITY_VERIFIER_VERSION:
        raise TargetReachabilityError(
            f"{label.capitalize()} schema_version must be "
            f"{TARGET_REACHABILITY_VERIFIER_VERSION}."
        )


def _nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise TargetReachabilityError(f"{label.capitalize()} must be non-empty.")
    return value


def _result_set_sha256(
    result_paths: Mapping[str, str],
    result_hashes: Mapping[str, str],
) -> str:
    lines = [
        f"{result_hashes[token]}  {result_paths[token]}\n"
        for token in sorted(result_paths)
    ]
    return _sha256_bytes("".join(lines).encode("utf-8"))


def _pretty_bytes(document: Mapping[str, Any]) -> bytes:
    return (
        json.dumps(
            document,
            indent=2,
            ensure_ascii=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
