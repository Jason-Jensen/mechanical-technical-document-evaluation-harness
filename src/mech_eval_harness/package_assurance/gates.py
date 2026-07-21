"""Deterministic P2.1 package inventory and evaluability gates."""

from __future__ import annotations

import hashlib
import json
import re
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
from typing import Any, Collection, Mapping

from mech_eval_harness.package_assurance.adapters import (
    SourceLoadOutcome,
    load_structured_sources,
)
from mech_eval_harness.package_assurance.manifest import (
    PACKAGE_MANIFEST_FILENAME,
    REQUIRED_SOURCE_DECLARATIONS,
    SUPPORTED_PACKAGE_MANIFEST_VERSIONS,
    LoadedPackageManifest,
    PackageManifestError,
    load_package_manifest,
)
from mech_eval_harness.package_assurance.models import (
    EvidenceLocator,
    LoadedStructuredSources,
    PackageGateEvaluation,
    PackageGateFinding,
    PackageGateResult,
    PackageResultState,
    StructuredSourceRecord,
)


PACKAGE_GATE_VERSION = "0.3.0"

MANIFEST_GATE_ID = "GATE-PKG-MANIFEST-001"
SOURCE_INVENTORY_GATE_ID = "GATE-PKG-SOURCE-INVENTORY-001"
AUTHORITY_GATE_ID = "GATE-PKG-AUTHORITY-001"
BOUNDARY_GATE_ID = "GATE-PKG-BOUNDARY-001"
IDENTIFIER_GATE_ID = "GATE-PKG-IDENTIFIER-001"
DUPLICATE_GATE_ID = "GATE-PKG-DUPLICATE-001"
REVISION_GATE_ID = "GATE-PKG-REVISION-001"
EVIDENCE_GATE_ID = "GATE-PKG-EVIDENCE-001"

PACKAGE_GATE_ORDER = (
    MANIFEST_GATE_ID,
    SOURCE_INVENTORY_GATE_ID,
    AUTHORITY_GATE_ID,
    BOUNDARY_GATE_ID,
    IDENTIFIER_GATE_ID,
    DUPLICATE_GATE_ID,
    REVISION_GATE_ID,
    EVIDENCE_GATE_ID,
)

_GATE_KINDS = {
    MANIFEST_GATE_ID: "manifest",
    SOURCE_INVENTORY_GATE_ID: "source_inventory_and_parse",
    AUTHORITY_GATE_ID: "authority_map",
    BOUNDARY_GATE_ID: "package_boundary_and_file_references",
    IDENTIFIER_GATE_ID: "canonical_identifiers",
    DUPLICATE_GATE_ID: "duplicate_identifiers",
    REVISION_GATE_ID: "revision_evaluability",
    EVIDENCE_GATE_ID: "evidence_locators",
}

_ALLOWED_STATES = {
    "automatic_pass",
    "automatic_fail",
    "engineering_review_required",
    "missing_authoritative_information",
    "extraction_or_tool_failure",
    "evaluator_uncertainty",
}
_EXPECTED_STATE_PRECEDENCE = [
    "automatic_fail",
    "extraction_or_tool_failure",
    "missing_authoritative_information",
    "evaluator_uncertainty",
    "engineering_review_required",
    "automatic_pass",
]
_EXPECTED_CLI_EXITS = {
    "automatic_pass": 0,
    "automatic_fail": 1,
    "engineering_review_required": 2,
    "missing_authoritative_information": 3,
    "extraction_or_tool_failure": 4,
    "evaluator_uncertainty": 5,
}
_REQUIRED_AUTHORITY_FIELDS = {
    "package.required_sources",
    "package.allowed_file_reference_roots",
    "document.required_for_release",
    "drawing.current_revision",
    "drawing.file_ref_id",
    "drawing.title",
    "revision.current_status",
    "bom.item_quantity",
    "bom.equipment_tag",
    "equipment.datasheet_id",
    "equipment.required_operating_pressure",
    "specification.current_revision",
}
_REQUIRED_AUTHORITY_RULE_KEYS = {
    "rule_id",
    "field",
    "authoritative_source",
    "secondary_sources",
    "required_for_release",
    "agreement_rule",
    "on_missing_authority",
    "on_missing_value",
    "on_conflict",
    "release_hold_on_conflict",
    "review_owner",
}
_CONTRACT_EVIDENCE_FIELDS = {
    "csv": {
        "source_type",
        "source_file",
        "format",
        "row_number",
        "header_row_number",
        "column_name",
        "row_key",
        "original_value",
        "normalized_value",
    },
    "json": {
        "source_type",
        "source_file",
        "format",
        "json_pointer",
        "record_id",
        "property_name",
        "original_value",
        "normalized_value",
    },
    "file_reference": {
        "file_ref_id",
        "declared_relative_path",
        "resolved_package_relative_path",
        "boundary_check",
    },
}

_IDENTIFIER_FIELDS = {
    "drawing_register_record": (
        "document_id",
        "drawing_number",
        "file_ref_id",
    ),
    "drawing_metadata_record": (
        "record_id",
        "document_id",
        "drawing_number",
        "file_ref_id",
    ),
    "equipment_item": (
        "item_id",
        "equipment_tag",
        "drawing_number",
        "datasheet_id",
        "specification_id",
    ),
    "datasheet_record": (
        "record_id",
        "document_id",
        "datasheet_id",
        "equipment_tag",
        "file_ref_id",
    ),
    "specification_record": (
        "record_id",
        "document_id",
        "specification_id",
        "file_ref_id",
    ),
    "revision_history_record": (
        "revision_record_id",
        "document_id",
        "owner_identifier",
    ),
}
_OPTIONAL_IDENTIFIER_FIELDS = {
    "equipment_item": (
        "drawing_number",
        "datasheet_id",
        "specification_id",
    ),
}
_LIST_IDENTIFIER_FIELDS = {
    "drawing_metadata_record": ("equipment_tags",),
    "specification_record": ("equipment_tags",),
}
_DUPLICATE_CHECKS = (
    ("drawing_register_record", "document_id", None),
    ("drawing_register_record", "drawing_number", "drawing_number"),
    ("drawing_metadata_record", "record_id", None),
    ("drawing_metadata_record", "document_id", None),
    ("drawing_metadata_record", "drawing_number", "drawing_number"),
    ("equipment_item", "item_id", None),
    ("equipment_item", "equipment_tag", "equipment_tag"),
    ("datasheet_record", "record_id", None),
    ("datasheet_record", "document_id", None),
    ("datasheet_record", "datasheet_id", None),
    ("specification_record", "record_id", None),
    ("specification_record", "document_id", None),
    ("specification_record", "specification_id", None),
    ("revision_history_record", "revision_record_id", None),
)
_SUPPORTED_REVISION_SCHEMES = {
    "alpha_upper",
    "numeric_integer",
    "numeric_zero_padded",
    "explicit_sequence",
}


def run_package_gates(
    repository_root: Path,
    manifest_path: Path,
    *,
    allowed_package_root: Path,
    supported_schema_versions: Collection[
        str
    ] = SUPPORTED_PACKAGE_MANIFEST_VERSIONS,
) -> PackageGateEvaluation:
    """Run P2.1 gates without selecting a package-level result state."""

    try:
        manifest = load_package_manifest(
            repository_root,
            manifest_path,
            allowed_package_root=allowed_package_root,
            supported_schema_versions=supported_schema_versions,
        )
    except PackageManifestError as exc:
        manifest_result = _manifest_failure(
            str(exc),
            repository_root=repository_root,
            package_root=allowed_package_root,
        )
        blocked = tuple(
            _skipped(
                gate_id,
                blocked_by=(MANIFEST_GATE_ID,),
                summary=f"Skipped because {MANIFEST_GATE_ID} did not pass.",
            )
            for gate_id in PACKAGE_GATE_ORDER[1:]
        )
        return PackageGateEvaluation(
            package_id=None,
            gates=(manifest_result, *blocked),
            manifest=None,
            sources=None,
        )

    manifest_result = _passed(
        MANIFEST_GATE_ID,
        summary=(
            f"Manifest {PACKAGE_MANIFEST_FILENAME} is readable, schema-valid, "
            "supported, and confined to the allowed package root."
        ),
        evidence=(
            EvidenceLocator(
                source_type="package_manifest",
                source_file=PACKAGE_MANIFEST_FILENAME,
                format="json",
                json_pointer="/package_id",
                property_name="package_id",
                original_value=manifest.package_id,
                normalized_value=manifest.package_id,
            ),
        ),
    )

    source_outcome = load_structured_sources(manifest)
    source_result = _source_inventory_gate(manifest, source_outcome)
    authority_result = _authority_gate(manifest, source_outcome.sources)
    boundary_result = _boundary_gate(manifest)

    if source_result.passed:
        identifier_result = _identifier_gate(source_outcome.sources)
    else:
        identifier_result = _skipped(
            IDENTIFIER_GATE_ID,
            blocked_by=(SOURCE_INVENTORY_GATE_ID,),
            summary=(
                "Skipped because complete parsed source records are required "
                "for identifier validation."
            ),
        )

    dependency_blockers = tuple(
        gate_id
        for gate_id, result in (
            (SOURCE_INVENTORY_GATE_ID, source_result),
            (AUTHORITY_GATE_ID, authority_result),
        )
        if not result.passed
    )
    if dependency_blockers:
        duplicate_result = _skipped(
            DUPLICATE_GATE_ID,
            blocked_by=dependency_blockers,
            summary=(
                "Skipped because complete source records and a valid duplicate "
                "authority policy are required."
            ),
        )
        revision_result = _skipped(
            REVISION_GATE_ID,
            blocked_by=dependency_blockers,
            summary=(
                "Skipped because complete source records and revision authority "
                "declarations are required."
            ),
        )
        evidence_result = _skipped(
            EVIDENCE_GATE_ID,
            blocked_by=dependency_blockers,
            summary=(
                "Skipped because complete source records and authority-declared "
                "evidence requirements are required."
            ),
        )
    else:
        authority_map = source_outcome.sources.documents["authority_map"]
        duplicate_result = _duplicate_gate(
            source_outcome.sources,
            authority_map,
        )
        revision_result = _revision_gate(
            manifest,
            source_outcome.sources,
            authority_map,
        )
        evidence_result = _evidence_gate(
            manifest,
            source_outcome.sources,
            authority_map,
        )

    return PackageGateEvaluation(
        package_id=manifest.package_id,
        gates=(
            manifest_result,
            source_result,
            authority_result,
            boundary_result,
            identifier_result,
            duplicate_result,
            revision_result,
            evidence_result,
        ),
        manifest=manifest,
        sources=source_outcome.sources,
    )


def _manifest_failure(
    message: str,
    *,
    repository_root: Path,
    package_root: Path,
) -> PackageGateResult:
    message = _portable_error_message(
        message,
        repository_root=repository_root,
        package_root=package_root,
    )
    extraction_tokens = (
        "Package manifest error: File not found",
        "Package manifest error: Invalid JSON",
        "Package manifest could not be read",
        "Top-level JSON value must be an object",
    )
    state: PackageResultState = (
        "extraction_or_tool_failure"
        if any(token in message for token in extraction_tokens)
        else "automatic_fail"
    )
    code = (
        "MANIFEST_UNREADABLE"
        if state == "extraction_or_tool_failure"
        else "MANIFEST_INVALID"
    )
    locator = EvidenceLocator(
        source_type="package_manifest",
        source_file=PACKAGE_MANIFEST_FILENAME,
        format="json",
        json_pointer="",
        original_value=None,
        normalized_value=None,
    )
    finding = _finding(
        gate_id=MANIFEST_GATE_ID,
        code=code,
        state=state,
        message=message,
        evidence=(locator,),
    )
    return _failed(
        MANIFEST_GATE_ID,
        summary="The package manifest could not establish a valid package boundary.",
        findings=(finding,),
        evidence=(locator,),
    )


def _source_inventory_gate(
    manifest: LoadedPackageManifest,
    outcome: SourceLoadOutcome,
) -> PackageGateResult:
    evidence = tuple(
        EvidenceLocator(
            source_type=declaration["source_type"],
            source_file=declaration["path"],
            format=declaration["format"],
            json_pointer="" if declaration["format"] == "json" else None,
            original_value=None,
            normalized_value=None,
        )
        for declaration in manifest.manifest["source_inventory"]
    )
    if not outcome.errors:
        return _passed(
            SOURCE_INVENTORY_GATE_ID,
            summary=(
                "All seven mandatory sources are declared and loadable; "
                f"{len(outcome.sources.records)} structured records were parsed."
            ),
            evidence=evidence,
        )

    findings = tuple(
        _finding(
            gate_id=SOURCE_INVENTORY_GATE_ID,
            code=error.code,
            state="extraction_or_tool_failure",
            message=error.message,
            affected_identifiers=(error.source_type,),
            evidence=(error.evidence_locator(),),
        )
        for error in outcome.errors
    )
    return _failed(
        SOURCE_INVENTORY_GATE_ID,
        summary=(
            f"{len(outcome.errors)} mandatory source load or parse failure(s) "
            "prevent complete source evaluation."
        ),
        findings=findings,
        evidence=evidence,
    )


def _authority_gate(
    manifest: LoadedPackageManifest,
    sources: LoadedStructuredSources,
) -> PackageGateResult:
    source_file = manifest.manifest["authority_map_ref"]
    authority = sources.documents.get("authority_map")
    if authority is None:
        locator = _json_locator("authority_map", source_file, "")
        finding = _finding(
            gate_id=AUTHORITY_GATE_ID,
            code="AUTHORITY_MAP_UNAVAILABLE",
            state="missing_authoritative_information",
            message="The declared authority map is unavailable for validation.",
            evidence=(locator,),
        )
        return _failed(
            AUTHORITY_GATE_ID,
            summary="No usable authority map is available.",
            findings=(finding,),
            evidence=(locator,),
        )

    findings: list[PackageGateFinding] = []

    def add(
        code: str,
        state: PackageResultState,
        message: str,
        pointer: str,
        *,
        affected: tuple[str, ...] = (),
        original: Any = None,
    ) -> None:
        findings.append(
            _finding(
                gate_id=AUTHORITY_GATE_ID,
                code=code,
                state=state,
                message=message,
                affected_identifiers=affected,
                evidence=(
                    _json_locator(
                        "authority_map",
                        source_file,
                        pointer,
                        original_value=original,
                    ),
                ),
            )
        )

    required_top_level = {
        "schema_version",
        "applies_to",
        "required_sources",
        "normalization_profiles",
        "revision_schemes",
        "duplicate_policies",
        "rules",
        "evidence_locator_requirements",
        "package_state_precedence",
        "cli_exit_codes",
    }
    for key in sorted(required_top_level - set(authority)):
        add(
            "AUTHORITY_FIELD_MISSING",
            "missing_authoritative_information",
            f"Authority map is missing required property: {key}",
            "",
            affected=(key,),
        )

    if authority.get("schema_version") != PACKAGE_GATE_VERSION:
        add(
            "AUTHORITY_VERSION_INVALID",
            "automatic_fail",
            f"Authority map schema_version must be {PACKAGE_GATE_VERSION}.",
            "/schema_version",
            original=authority.get("schema_version"),
        )
    if authority.get("applies_to") != manifest.package_id:
        add(
            "AUTHORITY_SCOPE_CONFLICT",
            "automatic_fail",
            "Authority map applies_to does not match the package_id.",
            "/applies_to",
            affected=(manifest.package_id,),
            original=authority.get("applies_to"),
        )

    required_sources = authority.get("required_sources")
    expected_sources = set(REQUIRED_SOURCE_DECLARATIONS)
    if not isinstance(required_sources, list) or any(
        not isinstance(item, str) for item in required_sources
    ):
        add(
            "AUTHORITY_REQUIRED_SOURCES_INVALID",
            "automatic_fail",
            "Authority required_sources must be an array of source identifiers.",
            "/required_sources",
            original=required_sources,
        )
    else:
        missing = sorted(expected_sources - set(required_sources))
        unexpected = sorted(set(required_sources) - expected_sources)
        if missing:
            add(
                "AUTHORITY_REQUIRED_SOURCE_MISSING",
                "missing_authoritative_information",
                "Authority map omits mandatory source declarations: "
                + ", ".join(missing),
                "/required_sources",
                affected=tuple(missing),
                original=required_sources,
            )
        if unexpected or len(required_sources) != len(set(required_sources)):
            add(
                "AUTHORITY_REQUIRED_SOURCES_CONTRADICTORY",
                "automatic_fail",
                "Authority required_sources contains unexpected or duplicate values.",
                "/required_sources",
                affected=tuple(unexpected),
                original=required_sources,
            )

    profiles = _authority_object_list(
        authority,
        "normalization_profiles",
        "id",
        add,
    )
    profile_ids = _unique_authority_ids(
        profiles,
        "id",
        "/normalization_profiles",
        "AUTHORITY_NORMALIZATION_PROFILE_DUPLICATE",
        add,
    )
    for index, profile in enumerate(profiles):
        route = profile.get("on_ambiguous_normalization")
        if not isinstance(route, str) or route not in _ALLOWED_STATES:
            add(
                "AUTHORITY_NORMALIZATION_ROUTE_INVALID",
                "automatic_fail",
                "Normalization ambiguity route is not a permitted result state.",
                f"/normalization_profiles/{index}/on_ambiguous_normalization",
                affected=(str(profile.get("id", "<missing>")),),
                original=route,
            )

    revision_schemes = _authority_object_list(
        authority,
        "revision_schemes",
        "id",
        add,
    )
    revision_scheme_ids = _unique_authority_ids(
        revision_schemes,
        "id",
        "/revision_schemes",
        "AUTHORITY_REVISION_SCHEME_DUPLICATE",
        add,
    )
    for index, scheme in enumerate(revision_schemes):
        scheme_kind = scheme.get("scheme")
        if (
            not isinstance(scheme_kind, str)
            or scheme_kind not in _SUPPORTED_REVISION_SCHEMES
        ):
            add(
                "AUTHORITY_REVISION_SCHEME_INVALID",
                "automatic_fail",
                "Authority revision scheme is unsupported.",
                f"/revision_schemes/{index}/scheme",
                affected=(str(scheme.get("id", "<missing>")),),
                original=scheme_kind,
            )
        if scheme_kind == "explicit_sequence":
            allowed_values = scheme.get("allowed_values")
            if (
                not isinstance(allowed_values, list)
                or not allowed_values
                or any(not isinstance(value, str) for value in allowed_values)
                or len(allowed_values) != len(set(allowed_values))
            ):
                add(
                    "AUTHORITY_REVISION_SEQUENCE_INVALID",
                    "automatic_fail",
                    (
                        "Explicit authority revision sequence must be non-empty "
                        "and unique."
                    ),
                    f"/revision_schemes/{index}/allowed_values",
                    affected=(str(scheme.get("id", "<missing>")),),
                    original=allowed_values,
                )

    duplicate_policies = _authority_object_list(
        authority,
        "duplicate_policies",
        "controlled_identifier",
        add,
    )
    duplicate_policy_ids = _unique_authority_ids(
        duplicate_policies,
        "controlled_identifier",
        "/duplicate_policies",
        "AUTHORITY_DUPLICATE_POLICY_CONTRADICTORY",
        add,
    )
    for index, policy in enumerate(duplicate_policies):
        pointer = f"/duplicate_policies/{index}"
        controlled_identifier = policy.get("controlled_identifier")
        if policy.get("default") != "forbidden":
            add(
                "AUTHORITY_DUPLICATE_POLICY_DEFAULT_INVALID",
                "automatic_fail",
                "Declared duplicate policies must remain forbidden by default.",
                f"{pointer}/default",
                affected=(str(controlled_identifier),),
                original=policy.get("default"),
            )

        representation = policy.get("intentional_duplicate_representation")
        if not isinstance(representation, dict):
            add(
                "AUTHORITY_DUPLICATE_REPRESENTATION_INVALID",
                "automatic_fail",
                "Intentional duplicate representation must be an object.",
                f"{pointer}/intentional_duplicate_representation",
                affected=(str(controlled_identifier),),
                original=representation,
            )
            continue

        required_fields = representation.get("required_fields")
        if (
            not isinstance(required_fields, list)
            or not required_fields
            or any(not isinstance(field, str) or not field for field in required_fields)
            or len(required_fields) != len(set(required_fields))
        ):
            add(
                "AUTHORITY_DUPLICATE_REQUIRED_FIELDS_INVALID",
                "automatic_fail",
                "Intentional duplicate required_fields must be non-empty and unique.",
                f"{pointer}/intentional_duplicate_representation/required_fields",
                affected=(str(controlled_identifier),),
                original=required_fields,
            )
        else:
            required_disambiguation = {
                str(controlled_identifier),
                "duplicate_instance_id",
                "authorizing_source_ref",
            }
            missing_disambiguation = sorted(
                required_disambiguation - set(required_fields)
            )
            if missing_disambiguation:
                add(
                    "AUTHORITY_DUPLICATE_DISAMBIGUATION_INCOMPLETE",
                    "automatic_fail",
                    "Intentional duplicate policy omits required disambiguation: "
                    + ", ".join(missing_disambiguation),
                    f"{pointer}/intentional_duplicate_representation/required_fields",
                    affected=(
                        str(controlled_identifier),
                        *missing_disambiguation,
                    ),
                    original=required_fields,
                )

        if representation.get("on_missing_disambiguation") != "automatic_fail":
            add(
                "AUTHORITY_DUPLICATE_MISSING_ROUTE_INVALID",
                "automatic_fail",
                "Missing duplicate disambiguation must route to automatic_fail.",
                (
                    f"{pointer}/intentional_duplicate_representation/"
                    "on_missing_disambiguation"
                ),
                affected=(str(controlled_identifier),),
                original=representation.get("on_missing_disambiguation"),
            )

        allowed_roles = representation.get("allowed_duplicate_roles")
        if allowed_roles is not None and (
            not isinstance(allowed_roles, list)
            or not allowed_roles
            or any(not isinstance(role, str) or not role for role in allowed_roles)
            or len(allowed_roles) != len(set(allowed_roles))
        ):
            add(
                "AUTHORITY_DUPLICATE_ROLES_INVALID",
                "automatic_fail",
                "Allowed duplicate roles must be non-empty unique strings.",
                (
                    f"{pointer}/intentional_duplicate_representation/"
                    "allowed_duplicate_roles"
                ),
                affected=(str(controlled_identifier),),
                original=allowed_roles,
            )

    rules = _authority_object_list(authority, "rules", "rule_id", add)
    _unique_authority_ids(
        rules,
        "rule_id",
        "/rules",
        "AUTHORITY_RULE_ID_DUPLICATE",
        add,
    )
    field_counts: dict[str, int] = defaultdict(int)
    declared_fields: set[str] = set()
    for index, rule in enumerate(rules):
        pointer = f"/rules/{index}"
        missing_keys = sorted(_REQUIRED_AUTHORITY_RULE_KEYS - set(rule))
        if missing_keys:
            add(
                "AUTHORITY_RULE_INCOMPLETE",
                "missing_authoritative_information",
                "Authority rule is missing required properties: "
                + ", ".join(missing_keys),
                pointer,
                affected=(str(rule.get("rule_id", "<missing>")),),
            )
            continue

        rule_id = str(rule["rule_id"])
        field = rule["field"]
        if not isinstance(field, str) or not field:
            add(
                "AUTHORITY_RULE_FIELD_INVALID",
                "automatic_fail",
                "Authority rule field must be a non-empty string.",
                f"{pointer}/field",
                affected=(rule_id,),
                original=field,
            )
        else:
            field_counts[field] += 1
            declared_fields.add(field)

        for text_key in ("agreement_rule", "review_owner"):
            text_value = rule[text_key]
            if not isinstance(text_value, str) or not text_value.strip():
                add(
                    "AUTHORITY_RULE_TEXT_INVALID",
                    "automatic_fail",
                    f"Authority {text_key} must be a non-empty string.",
                    f"{pointer}/{text_key}",
                    affected=(rule_id,),
                    original=text_value,
                )

        authoritative_source = rule["authoritative_source"]
        secondary_sources = rule["secondary_sources"]
        if (
            not isinstance(authoritative_source, str)
            or authoritative_source not in expected_sources
        ):
            add(
                "AUTHORITY_SOURCE_UNKNOWN",
                "automatic_fail",
                "Authority rule names an unknown authoritative source.",
                f"{pointer}/authoritative_source",
                affected=(rule_id,),
                original=authoritative_source,
            )
        if not isinstance(secondary_sources, list) or any(
            not isinstance(source, str) or source not in expected_sources
            for source in secondary_sources
        ):
            add(
                "AUTHORITY_SECONDARY_SOURCE_INVALID",
                "automatic_fail",
                "Authority rule secondary_sources contains an unknown source.",
                f"{pointer}/secondary_sources",
                affected=(rule_id,),
                original=secondary_sources,
            )
        elif (
            authoritative_source in secondary_sources
            or len(secondary_sources) != len(set(secondary_sources))
        ):
            add(
                "AUTHORITY_SOURCE_CONTRADICTION",
                "automatic_fail",
                "Authoritative and secondary source declarations are contradictory.",
                f"{pointer}/secondary_sources",
                affected=(rule_id,),
                original=secondary_sources,
            )

        for route_key in (
            "on_missing_authority",
            "on_missing_value",
            "on_conflict",
        ):
            route = rule[route_key]
            if not isinstance(route, str) or route not in _ALLOWED_STATES:
                add(
                    "AUTHORITY_ROUTE_INVALID",
                    "automatic_fail",
                    f"Authority {route_key} is not a permitted result state.",
                    f"{pointer}/{route_key}",
                    affected=(rule_id,),
                    original=route,
                )

        required_for_release = rule["required_for_release"]
        release_hold = rule["release_hold_on_conflict"]
        if not isinstance(required_for_release, bool) or not isinstance(
            release_hold, bool
        ):
            add(
                "AUTHORITY_RELEASE_CONTROL_INVALID",
                "automatic_fail",
                "Authority release-control fields must be Boolean.",
                pointer,
                affected=(rule_id,),
            )
        elif required_for_release and not release_hold:
            add(
                "AUTHORITY_RELEASE_CONTROL_CONTRADICTION",
                "automatic_fail",
                "A release-required authority rule cannot disable conflict holds.",
                f"{pointer}/release_hold_on_conflict",
                affected=(rule_id,),
                original=release_hold,
            )

        profile_ref = rule.get("normalization_profile")
        if profile_ref is not None and (
            not isinstance(profile_ref, str) or profile_ref not in profile_ids
        ):
            add(
                "AUTHORITY_NORMALIZATION_PROFILE_UNRESOLVED",
                "missing_authoritative_information",
                "Authority rule references an undeclared normalization profile.",
                f"{pointer}/normalization_profile",
                affected=(rule_id, str(profile_ref)),
                original=profile_ref,
            )
        revision_ref = rule.get("revision_scheme")
        if revision_ref is not None and (
            not isinstance(revision_ref, str)
            or revision_ref not in revision_scheme_ids
        ):
            add(
                "AUTHORITY_REVISION_SCHEME_UNRESOLVED",
                "missing_authoritative_information",
                "Authority rule references an undeclared revision scheme.",
                f"{pointer}/revision_scheme",
                affected=(rule_id, str(revision_ref)),
                original=revision_ref,
            )
        duplicate_ref = rule.get("duplicate_policy")
        if duplicate_ref is not None and (
            not isinstance(duplicate_ref, str)
            or duplicate_ref not in duplicate_policy_ids
        ):
            add(
                "AUTHORITY_DUPLICATE_POLICY_UNRESOLVED",
                "missing_authoritative_information",
                "Authority rule references an undeclared duplicate policy.",
                f"{pointer}/duplicate_policy",
                affected=(rule_id, str(duplicate_ref)),
                original=duplicate_ref,
            )

    for field, count in sorted(field_counts.items()):
        if count > 1:
            add(
                "AUTHORITY_FIELD_CONTRADICTORY",
                "automatic_fail",
                f"Multiple authority rules control the same field: {field}",
                "/rules",
                affected=(field,),
                original=count,
            )
    missing_fields = sorted(_REQUIRED_AUTHORITY_FIELDS - declared_fields)
    if missing_fields:
        add(
            "AUTHORITY_REQUIRED_RULE_MISSING",
            "missing_authoritative_information",
            "Authority map omits required controlled fields: "
            + ", ".join(missing_fields),
            "/rules",
            affected=tuple(missing_fields),
        )

    if authority.get("package_state_precedence") != _EXPECTED_STATE_PRECEDENCE:
        add(
            "AUTHORITY_STATE_PRECEDENCE_CONTRADICTORY",
            "automatic_fail",
            "Declared package-state precedence does not match the accepted contract.",
            "/package_state_precedence",
            original=authority.get("package_state_precedence"),
        )
    if authority.get("cli_exit_codes") != _EXPECTED_CLI_EXITS:
        add(
            "AUTHORITY_EXIT_CODES_CONTRADICTORY",
            "automatic_fail",
            "Declared CLI exit mapping does not match the accepted contract.",
            "/cli_exit_codes",
            original=authority.get("cli_exit_codes"),
        )

    evidence = (
        _json_locator(
            "authority_map",
            source_file,
            "/rules",
            original_value=len(rules),
            normalized_value=len(rules),
        ),
    )
    if findings:
        return _failed(
            AUTHORITY_GATE_ID,
            summary=(
                f"Authority map has {len(findings)} unresolved or contradictory "
                "condition(s)."
            ),
            findings=tuple(findings),
            evidence=evidence,
        )
    return _passed(
        AUTHORITY_GATE_ID,
        summary=(
            f"Authority map is package-scoped and resolves {len(rules)} unique "
            "rules with valid profiles, schemes, policies, and routes."
        ),
        evidence=evidence,
    )


def _authority_object_list(
    authority: Mapping[str, Any],
    key: str,
    identifier_key: str,
    add: Any,
) -> list[Mapping[str, Any]]:
    value = authority.get(key)
    if not isinstance(value, list):
        add(
            "AUTHORITY_COLLECTION_INVALID",
            "automatic_fail",
            f"Authority property {key} must be an array.",
            f"/{key}",
            original=value,
        )
        return []

    records: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            add(
                "AUTHORITY_COLLECTION_ITEM_INVALID",
                "automatic_fail",
                f"Authority {key}[{index}] must be an object.",
                f"/{key}/{index}",
                original=item,
            )
            continue
        identifier = item.get(identifier_key)
        if not isinstance(identifier, str) or not identifier:
            add(
                "AUTHORITY_IDENTIFIER_INVALID",
                "automatic_fail",
                f"Authority {key}[{index}].{identifier_key} must be non-empty.",
                f"/{key}/{index}/{identifier_key}",
                original=identifier,
            )
        records.append(item)
    return records


def _unique_authority_ids(
    records: list[Mapping[str, Any]],
    key: str,
    pointer: str,
    code: str,
    add: Any,
) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for record in records:
        value = record.get(key)
        if not isinstance(value, str) or not value:
            continue
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    for duplicate in sorted(duplicates):
        add(
            code,
            "automatic_fail",
            f"Authority identifier is declared more than once: {duplicate}",
            pointer,
            affected=(duplicate,),
        )
    return seen


def _boundary_gate(manifest: LoadedPackageManifest) -> PackageGateResult:
    findings: list[PackageGateFinding] = []
    evidence: list[EvidenceLocator] = []
    references = {
        item["file_ref_id"]: item
        for item in manifest.manifest["file_references"]
    }
    for file_ref_id, declaration in references.items():
        resolved = manifest.file_reference_paths[file_ref_id]
        package_relative = _package_relative(manifest.package_root, resolved)
        inside_package = package_relative is not None
        inside_allowed_root = any(
            resolved != allowed_root and _is_relative_to(resolved, allowed_root)
            for allowed_root in manifest.allowed_file_roots
        )
        boundary_check = (
            "inside_allowed_root"
            if inside_package and inside_allowed_root
            else "outside_allowed_root"
        )
        locator = EvidenceLocator(
            source_type="package_manifest",
            source_file=PACKAGE_MANIFEST_FILENAME,
            format="file_reference",
            file_ref_id=file_ref_id,
            declared_relative_path=declaration["path"],
            resolved_package_relative_path=(
                package_relative or declaration["path"]
            ),
            boundary_check=boundary_check,
        )
        evidence.append(locator)

        if not inside_package or not inside_allowed_root:
            findings.append(
                _finding(
                    gate_id=BOUNDARY_GATE_ID,
                    code="FILE_REFERENCE_OUTSIDE_BOUNDARY",
                    state="automatic_fail",
                    message=(
                        f"Controlled file reference {file_ref_id} resolves outside "
                        "its allowed package root."
                    ),
                    affected_identifiers=(file_ref_id,),
                    evidence=(locator,),
                )
            )
        elif not resolved.is_file():
            findings.append(
                _finding(
                    gate_id=BOUNDARY_GATE_ID,
                    code="BROKEN_FILE_REFERENCE",
                    state="automatic_fail",
                    message=(
                        f"Controlled file reference {file_ref_id} does not resolve "
                        f"to a file: {declaration['path']}"
                    ),
                    affected_identifiers=(file_ref_id,),
                    evidence=(locator,),
                )
            )

    if findings:
        return _failed(
            BOUNDARY_GATE_ID,
            summary=(
                f"{len(findings)} controlled file boundary or existence "
                "failure(s) found."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )
    return _passed(
        BOUNDARY_GATE_ID,
        summary=(
            f"All {len(references)} controlled file references exist inside "
            "their declared package root."
        ),
        evidence=tuple(evidence),
    )


def _identifier_gate(sources: LoadedStructuredSources) -> PackageGateResult:
    findings: list[PackageGateFinding] = []
    evidence: list[EvidenceLocator] = []
    checked = 0
    for record in sources.records:
        optional_fields = _OPTIONAL_IDENTIFIER_FIELDS.get(
            record.record_type,
            (),
        )
        for field_name in _IDENTIFIER_FIELDS.get(record.record_type, ()):
            value = record.original_values.get(field_name)
            locator = _record_value_locator(record, field_name, value)
            evidence.append(locator)
            if field_name in optional_fields and value == "":
                continue
            checked += 1
            if not _is_canonical_identifier(value):
                findings.append(
                    _finding(
                        gate_id=IDENTIFIER_GATE_ID,
                        code="CANONICAL_IDENTIFIER_INVALID",
                        state="automatic_fail",
                        message=(
                            f"{record.record_type}.{field_name} is not a valid "
                            "package-scoped canonical identifier."
                        ),
                        affected_identifiers=_record_affected_identifiers(record),
                        evidence=(locator,),
                    )
                )

        for field_name in _LIST_IDENTIFIER_FIELDS.get(record.record_type, ()):
            values = record.original_values.get(field_name)
            if not isinstance(values, list):
                continue
            for index, value in enumerate(values):
                checked += 1
                locator = _record_value_locator(
                    record,
                    field_name,
                    value,
                    list_index=index,
                )
                evidence.append(locator)
                if not _is_canonical_identifier(value):
                    findings.append(
                        _finding(
                            gate_id=IDENTIFIER_GATE_ID,
                            code="CANONICAL_IDENTIFIER_INVALID",
                            state="automatic_fail",
                            message=(
                                f"{record.record_type}.{field_name}[{index}] is not "
                                "a valid package-scoped canonical identifier."
                            ),
                            affected_identifiers=_record_affected_identifiers(record),
                            evidence=(locator,),
                        )
                    )

    if findings:
        return _failed(
            IDENTIFIER_GATE_ID,
            summary=f"{len(findings)} invalid canonical identifier value(s) found.",
            findings=tuple(findings),
            evidence=tuple(evidence),
        )
    return _passed(
        IDENTIFIER_GATE_ID,
        summary=(
            f"All {checked} present or required source identifiers are "
            "structurally valid."
        ),
        evidence=tuple(evidence),
    )


def _duplicate_gate(
    sources: LoadedStructuredSources,
    authority_map: Mapping[str, Any],
) -> PackageGateResult:
    findings: list[PackageGateFinding] = []
    evidence: list[EvidenceLocator] = []
    policies = {
        policy["controlled_identifier"]: policy
        for policy in authority_map.get("duplicate_policies", [])
        if isinstance(policy, dict)
        and isinstance(policy.get("controlled_identifier"), str)
    }

    for record_type, field_name, policy_name in _DUPLICATE_CHECKS:
        grouped: dict[str, list[StructuredSourceRecord]] = defaultdict(list)
        for record in sources.records_of_type(record_type):
            value = record.original_values.get(field_name)
            if isinstance(value, str):
                grouped[value].append(record)

        for value, group in sorted(grouped.items()):
            group_evidence = tuple(
                _record_value_locator(record, field_name, value)
                for record in group
            )
            evidence.extend(group_evidence)
            if len(group) < 2:
                continue
            if policy_name is not None and _intentional_duplicate_is_valid(
                group,
                policies.get(policy_name),
            ):
                continue
            findings.append(
                _finding(
                    gate_id=DUPLICATE_GATE_ID,
                    code="DUPLICATE_CANONICAL_IDENTIFIER",
                    state="automatic_fail",
                    message=(
                        f"Duplicate {field_name} is not covered by a complete "
                        f"intentional-duplicate declaration: {value}"
                    ),
                    affected_identifiers=(value,),
                    evidence=group_evidence,
                )
            )

    history_groups: dict[tuple[str, str], list[StructuredSourceRecord]] = (
        defaultdict(list)
    )
    for record in sources.records_of_type("revision_history_record"):
        key = (
            str(record.original_values.get("document_id")),
            str(record.original_values.get("revision_id")),
        )
        history_groups[key].append(record)
    for (document_id, revision_id), group in sorted(history_groups.items()):
        if len(group) < 2:
            continue
        group_evidence = tuple(
            _record_value_locator(record, "revision_id", revision_id)
            for record in group
        )
        findings.append(
            _finding(
                gate_id=DUPLICATE_GATE_ID,
                code="DUPLICATE_SCOPED_REVISION",
                state="automatic_fail",
                message=(
                    f"Revision {revision_id} is duplicated within document "
                    f"{document_id}."
                ),
                affected_identifiers=(document_id, revision_id),
                evidence=group_evidence,
            )
        )
        evidence.extend(group_evidence)

    if findings:
        return _failed(
            DUPLICATE_GATE_ID,
            summary=f"{len(findings)} undeclared duplicate condition(s) found.",
            findings=tuple(findings),
            evidence=tuple(evidence),
        )
    return _passed(
        DUPLICATE_GATE_ID,
        summary="All source-local canonical identifiers satisfy duplicate policy.",
        evidence=tuple(evidence),
    )


def _intentional_duplicate_is_valid(
    records: list[StructuredSourceRecord],
    policy: Mapping[str, Any] | None,
) -> bool:
    if policy is None:
        return False
    representation = policy.get("intentional_duplicate_representation")
    if not isinstance(representation, dict):
        return False
    required_fields = representation.get("required_fields")
    if not isinstance(required_fields, list) or not required_fields:
        return False
    for record in records:
        if any(
            field not in record.original_values
            or record.original_values[field] is None
            or record.original_values[field] == ""
            for field in required_fields
        ):
            return False
    if "duplicate_instance_id" in required_fields:
        instance_ids = [
            record.original_values["duplicate_instance_id"] for record in records
        ]
        if len(instance_ids) != len(set(instance_ids)):
            return False
    allowed_roles = representation.get("allowed_duplicate_roles")
    if allowed_roles is not None:
        if not isinstance(allowed_roles, list):
            return False
        if any(
            record.original_values.get("duplicate_role") not in allowed_roles
            for record in records
        ):
            return False
    return True


def _revision_gate(
    manifest: LoadedPackageManifest,
    sources: LoadedStructuredSources,
    authority_map: Mapping[str, Any],
) -> PackageGateResult:
    del authority_map  # Authority references are validated by the predecessor gate.
    findings: list[PackageGateFinding] = []
    evidence: list[EvidenceLocator] = []
    manifest_revisions = {
        document["document_id"]: document["current_revision"]
        for document in manifest.manifest["document_inventory"]
    }

    revision_records = tuple(
        record
        for record in sources.records
        if "revision_id" in record.original_values
        and "revision_scheme" in record.original_values
    )
    for record in revision_records:
        revision_id = record.original_values["revision_id"]
        scheme = record.original_values["revision_scheme"]
        declaration = manifest_revisions.get(
            str(record.original_values.get("document_id")),
            {},
        )
        sequence = record.original_values.get("revision_sequence")
        if not isinstance(sequence, list):
            sequence = declaration.get("allowed_values")
        locator = _record_value_locator(record, "revision_id", revision_id)
        evidence.append(locator)
        valid, detail = _validate_revision_value(
            revision_id,
            scheme,
            sequence=sequence,
            width=declaration.get("width"),
            max_letters=declaration.get("max_letters", 3),
        )
        if not valid:
            findings.append(
                _finding(
                    gate_id=REVISION_GATE_ID,
                    code="REVISION_FORMAT_INVALID",
                    state="automatic_fail",
                    message=(
                        f"Revision {revision_id!r} is invalid for scheme "
                        f"{scheme!r}: {detail}"
                    ),
                    affected_identifiers=(
                        str(record.original_values.get("document_id", "<unknown>")),
                        str(revision_id),
                    ),
                    evidence=(locator,),
                )
            )

    history_by_document: dict[str, list[StructuredSourceRecord]] = defaultdict(list)
    for record in sources.records_of_type("revision_history_record"):
        history_by_document[str(record.original_values["document_id"])].append(record)

    for document_id, history in sorted(history_by_document.items()):
        ordered = sorted(history, key=lambda item: item.values["sequence_index"])
        indices = [record.values["sequence_index"] for record in ordered]
        expected_indices = list(range(1, len(ordered) + 1))
        current = [
            record
            for record in ordered
            if record.original_values["revision_status"] == "current"
        ]
        document_evidence = tuple(
            _record_value_locator(
                record,
                "revision_status",
                record.original_values["revision_status"],
            )
            for record in ordered
        )
        evidence.extend(document_evidence)
        if indices != expected_indices:
            findings.append(
                _finding(
                    gate_id=REVISION_GATE_ID,
                    code="REVISION_SEQUENCE_INDEX_INVALID",
                    state="automatic_fail",
                    message=(
                        f"Revision sequence indexes for {document_id} must be "
                        f"contiguous from 1; found {indices}."
                    ),
                    affected_identifiers=(document_id,),
                    evidence=document_evidence,
                )
            )
        if len(current) != 1:
            findings.append(
                _finding(
                    gate_id=REVISION_GATE_ID,
                    code="REVISION_CURRENT_STATUS_INVALID",
                    state="automatic_fail",
                    message=(
                        f"Revision history for {document_id} must contain exactly "
                        f"one current record; found {len(current)}."
                    ),
                    affected_identifiers=(document_id,),
                    evidence=document_evidence,
                )
            )
        elif current[0] is not ordered[-1]:
            findings.append(
                _finding(
                    gate_id=REVISION_GATE_ID,
                    code="REVISION_CURRENT_NOT_LATEST",
                    state="automatic_fail",
                    message=(
                        f"The current revision for {document_id} is not the final "
                        "declared sequence entry."
                    ),
                    affected_identifiers=(document_id,),
                    evidence=document_evidence,
                )
            )

        if current:
            current_index = current[0].values["sequence_index"]
            invalid_status = [
                record
                for record in ordered
                if record.values["sequence_index"] < current_index
                and record.original_values["revision_status"] != "superseded"
            ]
            if invalid_status:
                findings.append(
                    _finding(
                        gate_id=REVISION_GATE_ID,
                        code="REVISION_SUPERSEDED_STATUS_INVALID",
                        state="automatic_fail",
                        message=(
                            f"Earlier revisions for {document_id} must be marked "
                            "superseded."
                        ),
                        affected_identifiers=(document_id,),
                        evidence=tuple(
                            _record_value_locator(
                                record,
                                "revision_status",
                                record.original_values["revision_status"],
                            )
                            for record in invalid_status
                        ),
                    )
                )

        schemes = {
            str(record.original_values["revision_scheme"]) for record in ordered
        }
        if len(schemes) > 1:
            findings.append(
                _finding(
                    gate_id=REVISION_GATE_ID,
                    code="REVISION_SCHEME_MIXED",
                    state="automatic_fail",
                    message=(
                        f"Revision history for {document_id} mixes schemes: "
                        + ", ".join(sorted(schemes))
                    ),
                    affected_identifiers=(document_id,),
                    evidence=document_evidence,
                )
            )
        elif ordered:
            declaration = manifest_revisions.get(document_id, {})
            sequence = declaration.get("allowed_values")
            order_values = [
                _revision_order_value(
                    str(record.original_values["revision_id"]),
                    str(record.original_values["revision_scheme"]),
                    sequence=sequence,
                )
                for record in ordered
            ]
            if any(value is None for value in order_values):
                findings.append(
                    _finding(
                        gate_id=REVISION_GATE_ID,
                        code="REVISION_ORDER_UNRESOLVED",
                        state="missing_authoritative_information",
                        message=(
                            f"Revision order for {document_id} cannot be resolved "
                            "from its declared scheme."
                        ),
                        affected_identifiers=(document_id,),
                        evidence=document_evidence,
                    )
                )
            elif any(
                left >= right
                for left, right in zip(order_values, order_values[1:])
            ):
                findings.append(
                    _finding(
                        gate_id=REVISION_GATE_ID,
                        code="REVISION_PROGRESSION_INVALID",
                        state="automatic_fail",
                        message=(
                            f"Revision labels for {document_id} do not progress in "
                            "declared sequence order."
                        ),
                        affected_identifiers=(document_id,),
                        evidence=document_evidence,
                    )
                )

    if findings:
        return _failed(
            REVISION_GATE_ID,
            summary=f"{len(findings)} revision evaluability failure(s) found.",
            findings=tuple(findings),
            evidence=tuple(evidence),
        )
    return _passed(
        REVISION_GATE_ID,
        summary=(
            f"All {len(revision_records)} revision values and "
            f"{len(history_by_document)} document histories are evaluable."
        ),
        evidence=tuple(evidence),
    )


def _validate_revision_value(
    revision_id: Any,
    scheme: Any,
    *,
    sequence: Any,
    width: Any,
    max_letters: Any,
) -> tuple[bool, str]:
    if not isinstance(revision_id, str) or not isinstance(scheme, str):
        return False, "revision_id and revision_scheme must be strings"
    if scheme == "alpha_upper":
        maximum = max_letters if isinstance(max_letters, int) else 3
        valid = bool(re.fullmatch(r"[A-Z]{1,3}", revision_id)) and (
            len(revision_id) <= maximum
        )
        return valid, f"expected 1 to {maximum} uppercase letters"
    if scheme == "numeric_integer":
        return bool(re.fullmatch(r"[0-9]+", revision_id)), (
            "expected a non-negative base-10 integer"
        )
    if scheme == "numeric_zero_padded":
        if not isinstance(width, int) or width < 1:
            return False, "numeric_zero_padded requires a declared width"
        return (
            bool(re.fullmatch(r"[0-9]+", revision_id))
            and len(revision_id) == width,
            f"expected exactly {width} base-10 digits",
        )
    if scheme == "explicit_sequence":
        if not isinstance(sequence, list) or not sequence:
            return False, "explicit_sequence requires declared allowed values"
        return revision_id in sequence, "revision is not in the explicit sequence"
    return False, f"unsupported revision scheme {scheme!r}"


def _revision_order_value(
    revision_id: str,
    scheme: str,
    *,
    sequence: Any,
) -> int | None:
    if scheme == "alpha_upper" and re.fullmatch(r"[A-Z]{1,3}", revision_id):
        value = 0
        for character in revision_id:
            value = value * 26 + (ord(character) - ord("A") + 1)
        return value
    if scheme in {"numeric_integer", "numeric_zero_padded"} and revision_id.isdigit():
        return int(revision_id)
    if scheme == "explicit_sequence" and isinstance(sequence, list):
        try:
            return sequence.index(revision_id)
        except ValueError:
            return None
    return None


def _evidence_gate(
    manifest: LoadedPackageManifest,
    sources: LoadedStructuredSources,
    authority_map: Mapping[str, Any],
) -> PackageGateResult:
    findings: list[PackageGateFinding] = []
    evidence: list[EvidenceLocator] = []
    requirements = authority_map.get("evidence_locator_requirements")
    if not isinstance(requirements, dict):
        locator = _json_locator(
            "authority_map",
            manifest.manifest["authority_map_ref"],
            "/evidence_locator_requirements",
            original_value=requirements,
        )
        finding = _finding(
            gate_id=EVIDENCE_GATE_ID,
            code="EVIDENCE_REQUIREMENTS_INVALID",
            state="automatic_fail",
            message="Authority evidence_locator_requirements must be an object.",
            evidence=(locator,),
        )
        return _failed(
            EVIDENCE_GATE_ID,
            summary="Evidence-locator requirements are not usable.",
            findings=(finding,),
            evidence=(locator,),
        )

    declared_required: dict[str, set[str]] = {}
    for locator_type, contract_fields in _CONTRACT_EVIDENCE_FIELDS.items():
        declaration = requirements.get(locator_type)
        pointer = f"/evidence_locator_requirements/{locator_type}/required_fields"
        required_fields = (
            declaration.get("required_fields")
            if isinstance(declaration, dict)
            else None
        )
        locator = _json_locator(
            "authority_map",
            manifest.manifest["authority_map_ref"],
            pointer,
            original_value=required_fields,
        )
        evidence.append(locator)
        if not isinstance(required_fields, list) or any(
            not isinstance(field, str) for field in required_fields
        ):
            findings.append(
                _finding(
                    gate_id=EVIDENCE_GATE_ID,
                    code="EVIDENCE_REQUIREMENTS_INVALID",
                    state="automatic_fail",
                    message=(
                        f"Evidence requirements for {locator_type} must declare "
                        "an array of field names."
                    ),
                    affected_identifiers=(locator_type,),
                    evidence=(locator,),
                )
            )
            continue
        if len(required_fields) != len(set(required_fields)):
            findings.append(
                _finding(
                    gate_id=EVIDENCE_GATE_ID,
                    code="EVIDENCE_REQUIREMENTS_DUPLICATE",
                    state="automatic_fail",
                    message=(
                        f"Evidence requirements for {locator_type} contain "
                        "duplicate field names."
                    ),
                    affected_identifiers=(locator_type,),
                    evidence=(locator,),
                )
            )
        required_set = set(required_fields)
        declared_required[locator_type] = required_set
        missing = sorted(contract_fields - required_set)
        if missing:
            findings.append(
                _finding(
                    gate_id=EVIDENCE_GATE_ID,
                    code="EVIDENCE_REQUIREMENT_INCOMPLETE",
                    state="automatic_fail",
                    message=(
                        f"Evidence requirements for {locator_type} omit: "
                        + ", ".join(missing)
                    ),
                    affected_identifiers=(locator_type, *missing),
                    evidence=(locator,),
                )
            )

    generated: list[EvidenceLocator] = []
    for record in sources.records:
        field_name = record.row_key_name or "record_id"
        generated.append(record.field_locator(field_name))
    for declaration in manifest.manifest["file_references"]:
        file_ref_id = declaration["file_ref_id"]
        resolved = manifest.file_reference_paths[file_ref_id]
        generated.append(
            EvidenceLocator(
                source_type="package_manifest",
                source_file=PACKAGE_MANIFEST_FILENAME,
                format="file_reference",
                file_ref_id=file_ref_id,
                declared_relative_path=declaration["path"],
                resolved_package_relative_path=(
                    _package_relative(manifest.package_root, resolved)
                    or declaration["path"]
                ),
                boundary_check="inside_allowed_root",
            )
        )

    for locator in generated:
        evidence.append(locator)
        locator_type = locator.format
        required_fields = declared_required.get(locator_type)
        if required_fields is None:
            continue
        missing = sorted(required_fields - set(locator.to_dict()))
        if missing:
            findings.append(
                _finding(
                    gate_id=EVIDENCE_GATE_ID,
                    code="EVIDENCE_LOCATOR_UNSATISFIED",
                    state="automatic_fail",
                    message=(
                        f"Generated {locator_type} locator cannot provide: "
                        + ", ".join(missing)
                    ),
                    affected_identifiers=(
                        locator.record_id
                        or locator.file_ref_id
                        or locator.source_file,
                    ),
                    evidence=(locator,),
                )
            )

    if findings:
        return _failed(
            EVIDENCE_GATE_ID,
            summary=f"{len(findings)} evidence-locator contract failure(s) found.",
            findings=tuple(findings),
            evidence=tuple(evidence),
        )
    return _passed(
        EVIDENCE_GATE_ID,
        summary=(
            f"All {len(generated)} generated record and file-reference locators "
            "satisfy the authority-declared evidence contract."
        ),
        evidence=tuple(evidence),
    )


def _record_value_locator(
    record: StructuredSourceRecord,
    field_name: str,
    value: Any,
    *,
    list_index: int | None = None,
) -> EvidenceLocator:
    normalized = value.strip() if isinstance(value, str) else value
    locator = record.field_locator(
        field_name,
        original_value=value,
        normalized_value=normalized,
    )
    if list_index is not None and locator.json_pointer is not None:
        locator = replace(
            locator,
            json_pointer=f"{locator.json_pointer}/{list_index}",
        )
    return locator


def _is_canonical_identifier(value: Any) -> bool:
    return (
        isinstance(value, str)
        and 1 <= len(value) <= 128
        and value == value.strip()
        and not any(ord(character) < 32 or ord(character) == 127 for character in value)
    )


def _record_affected_identifiers(
    record: StructuredSourceRecord,
) -> tuple[str, ...]:
    for value in (record.row_key_value, record.record_id):
        if _is_canonical_identifier(value):
            return (value,)
    return ()


def _json_locator(
    source_type: str,
    source_file: str,
    pointer: str,
    *,
    record_id: str | None = None,
    property_name: str | None = None,
    original_value: Any = None,
    normalized_value: Any = None,
) -> EvidenceLocator:
    return EvidenceLocator(
        source_type=source_type,
        source_file=source_file,
        format="json",
        json_pointer=pointer,
        record_id=record_id,
        property_name=property_name,
        original_value=original_value,
        normalized_value=(
            original_value if normalized_value is None else normalized_value
        ),
    )


def _finding(
    *,
    gate_id: str,
    code: str,
    state: PackageResultState,
    message: str,
    evidence: tuple[EvidenceLocator, ...],
    affected_identifiers: tuple[str, ...] = (),
    release_hold: bool = True,
) -> PackageGateFinding:
    semantic = {
        "gate_id": gate_id,
        "gate_version": PACKAGE_GATE_VERSION,
        "code": code,
        "state": state,
        "release_hold": release_hold,
        "affected_identifiers": list(affected_identifiers),
        "evidence": [locator.to_dict() for locator in evidence],
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("ascii")
    ).hexdigest()[:16]
    return PackageGateFinding(
        finding_id=f"FND-{digest.upper()}",
        gate_id=gate_id,
        gate_version=PACKAGE_GATE_VERSION,
        code=code,
        state=state,
        release_hold=release_hold,
        message=message,
        affected_identifiers=affected_identifiers,
        evidence=evidence,
    )


def _passed(
    gate_id: str,
    *,
    summary: str,
    evidence: tuple[EvidenceLocator, ...] = (),
) -> PackageGateResult:
    return PackageGateResult(
        gate_id=gate_id,
        gate_version=PACKAGE_GATE_VERSION,
        kind=_GATE_KINDS[gate_id],
        status="passed",
        summary=summary,
        evidence=evidence,
    )


def _failed(
    gate_id: str,
    *,
    summary: str,
    findings: tuple[PackageGateFinding, ...],
    evidence: tuple[EvidenceLocator, ...] = (),
) -> PackageGateResult:
    return PackageGateResult(
        gate_id=gate_id,
        gate_version=PACKAGE_GATE_VERSION,
        kind=_GATE_KINDS[gate_id],
        status="failed",
        summary=summary,
        findings=findings,
        evidence=evidence,
    )


def _skipped(
    gate_id: str,
    *,
    blocked_by: tuple[str, ...],
    summary: str,
) -> PackageGateResult:
    return PackageGateResult(
        gate_id=gate_id,
        gate_version=PACKAGE_GATE_VERSION,
        kind=_GATE_KINDS[gate_id],
        status="skipped",
        summary=summary,
        blocked_by=blocked_by,
    )


def _package_relative(root: Path, path: Path) -> str | None:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return None


def _portable_error_message(
    message: str,
    *,
    repository_root: Path,
    package_root: Path,
) -> str:
    replacements = (
        (package_root.resolve(), "<package_root>"),
        (repository_root.resolve(), "<repository_root>"),
    )
    for root, label in replacements:
        message = message.replace(str(root), label)
        message = message.replace(root.as_posix(), label)
    return message.replace("\\", "/")


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
