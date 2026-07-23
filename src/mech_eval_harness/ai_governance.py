from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker


SYSTEM_PATH = Path("governance/ai_management_system.json")
SCHEMA_PATH = Path("schemas/ai_management_system.schema.json")
ALLOWED_REFERENCE_HOSTS = {
    "airc.nist.gov",
    "doi.org",
    "www.iso.org",
    "www.nist.gov",
}


class AIManagementSystemValidationError(ValueError):
    """Raised when the repository's AI management system is inconsistent."""


@dataclass(frozen=True)
class AIManagementSystemSummary:
    management_system_id: str
    system_count: int
    risk_count: int
    control_count: int
    gate_count: int
    release_authorized: bool
    release_state: str
    hold_risk_ids: tuple[str, ...]
    hold_nonconformity_ids: tuple[str, ...]
    pending_decision_ids: tuple[str, ...]

    @property
    def release_ready(self) -> bool:
        return (
            not self.hold_risk_ids
            and not self.hold_nonconformity_ids
            and not self.pending_decision_ids
            and self.release_state in {"ready_for_owner_decision", "authorized"}
        )


def _load_json_object(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise AIManagementSystemValidationError(
            f"Missing required governance file: {path.as_posix()}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise AIManagementSystemValidationError(
            f"Invalid JSON in {path.as_posix()}: {exc.msg}"
        ) from exc
    if not isinstance(value, dict):
        raise AIManagementSystemValidationError(
            f"Top-level JSON must be an object: {path.as_posix()}"
        )
    return value


def _format_json_path(parts: Iterable[object]) -> str:
    rendered = "$"
    for part in parts:
        if isinstance(part, int):
            rendered += f"[{part}]"
        else:
            rendered += f".{part}"
    return rendered


def _validate_schema(system: dict[str, Any], schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(system),
        key=lambda error: tuple(str(part) for part in error.absolute_path),
    )
    if not errors:
        return
    details = "; ".join(
        f"{_format_json_path(error.absolute_path)}: {error.message}"
        for error in errors[:10]
    )
    if len(errors) > 10:
        details += f"; and {len(errors) - 10} more"
    raise AIManagementSystemValidationError(
        f"AI management system schema validation failed: {details}"
    )


def _index_unique(
    records: list[dict[str, Any]],
    id_field: str,
    label: str,
) -> dict[str, dict[str, Any]]:
    indexed: dict[str, dict[str, Any]] = {}
    for record in records:
        identifier = record[id_field]
        if identifier in indexed:
            raise AIManagementSystemValidationError(
                f"Duplicate {label} identifier: {identifier}"
            )
        indexed[identifier] = record
    return indexed


def _require_known(
    values: Iterable[str],
    known: dict[str, Any],
    context: str,
) -> None:
    unknown = sorted(set(values) - set(known))
    if unknown:
        raise AIManagementSystemValidationError(
            f"{context} references unknown identifiers: {', '.join(unknown)}"
        )


def _risk_level(score: int) -> str:
    if score <= 4:
        return "low"
    if score <= 9:
        return "medium"
    if score <= 16:
        return "high"
    return "critical"


def _validate_reference_path(root: Path, reference: str) -> None:
    if "\\" in reference:
        raise AIManagementSystemValidationError(
            f"Governance evidence path must use POSIX separators: {reference}"
        )
    path = PurePosixPath(reference)
    if path.is_absolute() or ".." in path.parts:
        raise AIManagementSystemValidationError(
            f"Governance evidence path must be repository-relative: {reference}"
        )
    resolved = root.joinpath(*path.parts)
    if not resolved.is_file():
        raise AIManagementSystemValidationError(
            f"Governance evidence path does not exist: {reference}"
        )


def referenced_document_paths(system: dict[str, Any]) -> tuple[str, ...]:
    references: set[str] = {
        system["policy_ref"],
        system["manual_ref"],
        system["impact_assessment_ref"],
        system["alignment_assessment_ref"],
        *system["documented_information"],
    }
    for item in system["systems"]:
        references.add(item["impact_assessment_ref"])
    for collection_name in (
        "risks",
        "controls",
        "quality_objectives",
        "nonconformities",
    ):
        for item in system[collection_name]:
            references.update(item["evidence_refs"])
    references.update(item["report_ref"] for item in system["audits"])
    references.update(
        item["report_ref"] for item in system["management_reviews"]
    )
    return tuple(sorted(references))


def _validate_sources(system: dict[str, Any]) -> None:
    for source in system["sources"]:
        parsed = urlparse(source["url"])
        if parsed.hostname not in ALLOWED_REFERENCE_HOSTS:
            raise AIManagementSystemValidationError(
                f"Governance source {source['source_id']} is not on an approved "
                f"authoritative host: {source['url']}"
            )
        if source["repository_copy_allowed"]:
            raise AIManagementSystemValidationError(
                f"Governance source {source['source_id']} must not authorize a "
                "repository copy"
            )


def _validate_relationships(system: dict[str, Any]) -> None:
    sources = _index_unique(system["sources"], "source_id", "source")
    roles = _index_unique(system["roles"], "role_id", "role")
    systems = _index_unique(system["systems"], "system_id", "system")
    risks = _index_unique(system["risks"], "risk_id", "risk")
    controls = _index_unique(system["controls"], "control_id", "control")
    gates = _index_unique(system["mandatory_gates"], "gate_id", "gate")
    objectives = _index_unique(
        system["quality_objectives"], "objective_id", "objective"
    )
    nonconformities = _index_unique(
        system["nonconformities"], "nonconformity_id", "nonconformity"
    )
    audits = _index_unique(system["audits"], "audit_id", "audit")
    reviews = _index_unique(
        system["management_reviews"], "review_id", "management review"
    )

    all_ids: list[str] = []
    for collection in (
        sources,
        roles,
        systems,
        risks,
        controls,
        gates,
        objectives,
        nonconformities,
        audits,
        reviews,
    ):
        all_ids.extend(collection)
    duplicate_global_ids = sorted(
        identifier for identifier in set(all_ids) if all_ids.count(identifier) > 1
    )
    if duplicate_global_ids:
        raise AIManagementSystemValidationError(
            "Identifiers must be globally unique across governance records: "
            + ", ".join(duplicate_global_ids)
        )

    if not any(role["may_authorize_release"] for role in roles.values()):
        raise AIManagementSystemValidationError(
            "At least one human role must have release authority"
        )
    if sum(role["may_authorize_release"] for role in roles.values()) != 1:
        raise AIManagementSystemValidationError(
            "Exactly one governance role must have release authority"
        )

    for item in systems.values():
        _require_known(
            [item["owner_role_id"]], roles, f"System {item['system_id']} owner"
        )
        _require_known(
            item["risk_ids"], risks, f"System {item['system_id']} risk list"
        )
        if (
            item["lifecycle_status"] == "active"
            and "restricted_not_authorized" in item["data_classes"]
        ):
            raise AIManagementSystemValidationError(
                f"Active system {item['system_id']} cannot use the "
                "restricted_not_authorized data class"
            )
        if (
            item["classification"] == "future_ai_capability"
            and item["lifecycle_status"] != "blocked_not_authorized"
        ):
            raise AIManagementSystemValidationError(
                f"Future AI system {item['system_id']} must remain blocked"
            )

    for risk in risks.values():
        _require_known(
            risk["system_ids"], systems, f"Risk {risk['risk_id']} system list"
        )
        _require_known(
            [risk["owner_role_id"]], roles, f"Risk {risk['risk_id']} owner"
        )
        _require_known(
            risk["control_ids"], controls, f"Risk {risk['risk_id']} controls"
        )
        expected_inherent = risk["inherent_likelihood"] * risk["inherent_impact"]
        if risk["inherent_score"] != expected_inherent:
            raise AIManagementSystemValidationError(
                f"Risk {risk['risk_id']} inherent score must equal likelihood "
                "times impact"
            )
        expected_residual = risk["residual_likelihood"] * risk["residual_impact"]
        if risk["residual_score"] != expected_residual:
            raise AIManagementSystemValidationError(
                f"Risk {risk['risk_id']} residual score must equal likelihood "
                "times impact"
            )
        level = _risk_level(risk["residual_score"])
        if level in {"high", "critical"} and not risk["release_hold"]:
            owner = roles[risk["owner_role_id"]]
            accepted = risk["status"] == "accepted" and owner["may_accept_high_risk"]
            if not accepted:
                raise AIManagementSystemValidationError(
                    f"Risk {risk['risk_id']} has {level} residual risk without "
                    "a release hold or authorized acceptance"
                )
        if risk["status"] == "controlled" and level in {"high", "critical"}:
            raise AIManagementSystemValidationError(
                f"Risk {risk['risk_id']} cannot be controlled while residual "
                f"risk remains {level}"
            )

    minimum_controls = set(system["minimum_control_ids"])
    missing_minimum = sorted(minimum_controls - set(controls))
    if missing_minimum:
        raise AIManagementSystemValidationError(
            "Missing minimum AI controls: " + ", ".join(missing_minimum)
        )
    for control_id in minimum_controls:
        if controls[control_id]["implementation_status"] == "deferred_not_triggered":
            raise AIManagementSystemValidationError(
                f"Minimum control {control_id} cannot be deferred"
            )

    for control in controls.values():
        _require_known(
            [control["owner_role_id"]],
            roles,
            f"Control {control['control_id']} owner",
        )
        _require_known(
            control["risk_ids"], risks, f"Control {control['control_id']} risks"
        )
        if control["implementation_status"] == "partially_implemented":
            if not control.get("gap") or not control.get("action_ref"):
                raise AIManagementSystemValidationError(
                    f"Partial control {control['control_id']} requires a gap "
                    "and action_ref"
                )

    for gate in gates.values():
        _require_known(
            gate["required_control_ids"],
            controls,
            f"Gate {gate['gate_id']} controls",
        )

    for objective in objectives.values():
        _require_known(
            [objective["owner_role_id"]],
            roles,
            f"Objective {objective['objective_id']} owner",
        )

    for item in nonconformities.values():
        _require_known(
            [item["owner_role_id"]],
            roles,
            f"Nonconformity {item['nonconformity_id']} owner",
        )
        _require_known(
            item["risk_ids"],
            risks,
            f"Nonconformity {item['nonconformity_id']} risks",
        )

    for audit in audits.values():
        _require_known(
            audit["finding_ids"],
            nonconformities,
            f"Audit {audit['audit_id']} findings",
        )


def _validate_release_alignment(system: dict[str, Any]) -> None:
    release = system["release_status"]
    expected_risk_holds = sorted(
        risk["risk_id"] for risk in system["risks"] if risk["release_hold"]
    )
    expected_nonconformity_holds = sorted(
        item["nonconformity_id"]
        for item in system["nonconformities"]
        if item["release_hold"] and item["status"] != "closed"
    )
    if sorted(release["hold_risk_ids"]) != expected_risk_holds:
        raise AIManagementSystemValidationError(
            "Release hold_risk_ids must exactly match release-holding risks"
        )
    if (
        sorted(release["hold_nonconformity_ids"])
        != expected_nonconformity_holds
    ):
        raise AIManagementSystemValidationError(
            "Release hold_nonconformity_ids must exactly match open "
            "release-holding nonconformities"
        )

    release_blocked = bool(
        expected_risk_holds
        or expected_nonconformity_holds
        or release["pending_decision_ids"]
    )
    if release_blocked:
        if release["release_authorized"] or release["release_state"] != "held":
            raise AIManagementSystemValidationError(
                "Release must remain held and unauthorized while mandatory "
                "holds or pending decisions exist"
            )
        if system["status"] != "operational_release_held":
            raise AIManagementSystemValidationError(
                "Management-system status must report operational_release_held"
            )
    else:
        if release["release_state"] == "held":
            raise AIManagementSystemValidationError(
                "Release state cannot remain held when no release blocker is "
                "recorded"
            )
        expected_authorized = release["release_state"] == "authorized"
        if release["release_authorized"] != expected_authorized:
            raise AIManagementSystemValidationError(
                "release_authorized must be true exactly when release_state is "
                "authorized"
            )
        if system["status"] != "operational_release_ready":
            raise AIManagementSystemValidationError(
                "Management-system status must report operational_release_ready"
            )


def validate_ai_management_system(root: Path) -> AIManagementSystemSummary:
    root = root.resolve()
    system = _load_json_object(root / SYSTEM_PATH)
    schema = _load_json_object(root / SCHEMA_PATH)
    _validate_schema(system, schema)
    _validate_sources(system)
    _validate_relationships(system)
    _validate_release_alignment(system)

    effective_date = date.fromisoformat(system["effective_date"])
    next_review_date = date.fromisoformat(system["next_review_date"])
    if next_review_date <= effective_date:
        raise AIManagementSystemValidationError(
            "next_review_date must be later than effective_date"
        )

    for reference in referenced_document_paths(system):
        _validate_reference_path(root, reference)

    release = system["release_status"]
    return AIManagementSystemSummary(
        management_system_id=system["management_system_id"],
        system_count=len(system["systems"]),
        risk_count=len(system["risks"]),
        control_count=len(system["controls"]),
        gate_count=len(system["mandatory_gates"]),
        release_authorized=release["release_authorized"],
        release_state=release["release_state"],
        hold_risk_ids=tuple(sorted(release["hold_risk_ids"])),
        hold_nonconformity_ids=tuple(
            sorted(release["hold_nonconformity_ids"])
        ),
        pending_decision_ids=tuple(sorted(release["pending_decision_ids"])),
    )


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate the repository AI management and quality system."
    )
    parser.add_argument(
        "root",
        nargs="?",
        default=".",
        help="Repository root (default: current directory).",
    )
    parser.add_argument(
        "--require-release-ready",
        action="store_true",
        help="Fail when any mandatory release hold remains open.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        summary = validate_ai_management_system(Path(args.root))
    except AIManagementSystemValidationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(
        f"PASS {summary.management_system_id} | systems={summary.system_count} "
        f"| risks={summary.risk_count} | controls={summary.control_count} "
        f"| gates={summary.gate_count}"
    )
    if summary.release_ready:
        print(f"RELEASE: {summary.release_state.upper()} | no mandatory holds")
        return 0

    print(
        f"RELEASE: HELD | risks={','.join(summary.hold_risk_ids) or 'none'} "
        "| nonconformities="
        f"{','.join(summary.hold_nonconformity_ids) or 'none'} "
        f"| pending={','.join(summary.pending_decision_ids) or 'none'}"
    )
    if args.require_release_ready:
        print(
            "ERROR: Mandatory AI management-system release holds remain open.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
