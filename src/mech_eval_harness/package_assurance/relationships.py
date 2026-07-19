"""Deterministic P2.2 cross-document relationship checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any, Mapping

from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
from mech_eval_harness.package_assurance.manifest import (
    PACKAGE_MANIFEST_FILENAME,
    LoadedPackageManifest,
)
from mech_eval_harness.package_assurance.models import (
    EvidenceLocator,
    LoadedStructuredSources,
    PackageGateEvaluation,
    PackageRelationshipEvaluation,
    RelationshipCheckResult,
    RelationshipFinding,
    StructuredSourceRecord,
)


RELATIONSHIP_CHECK_VERSION = "0.3.0"
DRAWING_REGISTER_METADATA_REVISION_CHECK_ID = (
    "drawing_register_metadata_revision"
)
DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID = (
    "drawing_register_metadata_presence"
)
DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID = (
    "drawing_metadata_register_authority"
)
DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID = (
    "drawing_register_metadata_file_reference"
)
DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID = (
    "drawing_register_manifest_file_reciprocity"
)
DRAWING_REVISION_MISMATCH_CODE = "DRAWING_REVISION_MISMATCH"
DRAWING_METADATA_MISSING_CODE = "DRAWING_METADATA_MISSING"
DRAWING_REGISTER_AUTHORITY_MISSING_CODE = (
    "DRAWING_REGISTER_AUTHORITY_MISSING"
)
DRAWING_FILE_REFERENCE_MISMATCH_CODE = "DRAWING_FILE_REFERENCE_MISMATCH"
DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE = (
    "DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED"
)
DRAWING_REVISION_AUTHORITY_RULE_ID = "AUTH-DWG-001"
DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID = "AUTH-DWG-002"

RELATIONSHIP_CHECK_ORDER = (
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
)


def run_package_relationships(
    gate_evaluation: PackageGateEvaluation,
) -> PackageRelationshipEvaluation:
    """Run accepted P2.2 checks after the complete P2.1 gate boundary."""

    blocked_by = _blocking_gate_ids(gate_evaluation)
    if (
        blocked_by
        or not gate_evaluation.dependent_checks_allowed
        or gate_evaluation.package_id is None
        or gate_evaluation.sources is None
    ):
        if not blocked_by:
            blocked_by = ("package_gate_evaluation",)
        return PackageRelationshipEvaluation(
            package_id=gate_evaluation.package_id,
            checks=tuple(
                _skipped_check(
                    check_id=check_id,
                    blocked_by=blocked_by,
                    summary=(
                        "Skipped because the complete P2.1 prerequisite gate "
                        "set did not pass."
                    ),
                )
                for check_id in RELATIONSHIP_CHECK_ORDER
            ),
        )

    authority_rule = _drawing_revision_authority_rule(
        gate_evaluation.sources
    )
    if authority_rule is None:
        return PackageRelationshipEvaluation(
            package_id=gate_evaluation.package_id,
            checks=tuple(
                _skipped_check(
                    check_id=check_id,
                    blocked_by=(AUTHORITY_GATE_ID,),
                    summary=(
                        "Skipped because the accepted AUTH-DWG-001 drawing "
                        "revision authority rule is unavailable."
                    ),
                )
                for check_id in RELATIONSHIP_CHECK_ORDER
            ),
        )

    revision_check = _drawing_register_metadata_revision_check(
        package_id=gate_evaluation.package_id,
        sources=gate_evaluation.sources,
    )
    presence_check = _drawing_register_metadata_presence_check(
        package_id=gate_evaluation.package_id,
        sources=gate_evaluation.sources,
    )
    authority_check = _drawing_metadata_register_authority_check(
        package_id=gate_evaluation.package_id,
        sources=gate_evaluation.sources,
    )
    if _drawing_file_reference_authority_rule(gate_evaluation.sources) is None:
        file_reference_check = _skipped_check(
            check_id=DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-DWG-002 drawing "
                "file-reference authority rule is unavailable."
            ),
        )
        reciprocity_check = _skipped_check(
            check_id=DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-DWG-002 drawing "
                "file-reference authority rule is unavailable."
            ),
        )
    elif gate_evaluation.manifest is None:
        file_reference_check = _skipped_check(
            check_id=DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
            blocked_by=("package_gate_evaluation",),
            summary=(
                "Skipped because the accepted loaded package manifest is "
                "unavailable."
            ),
        )
        reciprocity_check = _skipped_check(
            check_id=DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
            blocked_by=("package_gate_evaluation",),
            summary=(
                "Skipped because the accepted loaded package manifest is "
                "unavailable."
            ),
        )
    else:
        file_reference_check = (
            _drawing_register_metadata_file_reference_check(
                package_id=gate_evaluation.package_id,
                sources=gate_evaluation.sources,
                manifest=gate_evaluation.manifest,
            )
        )
        reciprocity_check = (
            _drawing_register_manifest_file_reciprocity_check(
                package_id=gate_evaluation.package_id,
                sources=gate_evaluation.sources,
                manifest=gate_evaluation.manifest,
            )
        )
    return PackageRelationshipEvaluation(
        package_id=gate_evaluation.package_id,
        checks=(
            revision_check,
            presence_check,
            authority_check,
            file_reference_check,
            reciprocity_check,
        ),
    )


def _blocking_gate_ids(
    evaluation: PackageGateEvaluation,
) -> tuple[str, ...]:
    failed = tuple(
        gate.gate_id for gate in evaluation.gates if gate.status == "failed"
    )
    if failed:
        return failed
    return tuple(
        gate.gate_id for gate in evaluation.gates if gate.status != "passed"
    )


def _drawing_revision_authority_rule(
    sources: LoadedStructuredSources,
) -> Mapping[str, Any] | None:
    authority_map = sources.documents.get("authority_map")
    if not isinstance(authority_map, Mapping):
        return None
    rules = authority_map.get("rules")
    if not isinstance(rules, list):
        return None
    for rule in rules:
        if not isinstance(rule, Mapping):
            continue
        if rule.get("rule_id") != DRAWING_REVISION_AUTHORITY_RULE_ID:
            continue
        secondary_sources = rule.get("secondary_sources")
        if (
            rule.get("field") == "drawing.current_revision"
            and rule.get("authoritative_source") == "drawing_register"
            and isinstance(secondary_sources, list)
            and "drawing_metadata" in secondary_sources
        ):
            return rule
    return None


def _drawing_file_reference_authority_rule(
    sources: LoadedStructuredSources,
) -> Mapping[str, Any] | None:
    authority_map = sources.documents.get("authority_map")
    if not isinstance(authority_map, Mapping):
        return None
    rules = authority_map.get("rules")
    if not isinstance(rules, list):
        return None
    for rule in rules:
        if not isinstance(rule, Mapping):
            continue
        if rule.get("rule_id") != DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID:
            continue
        if (
            rule.get("field") == "drawing.file_ref_id"
            and rule.get("authoritative_source") == "drawing_register"
            and rule.get("secondary_sources") == ["drawing_metadata"]
            and rule.get("agreement_rule")
            == (
                "declared drawing file reference must resolve to the same "
                "canonical drawing"
            )
            and rule.get("normalization_profile")
            == "canonical_identifier_v1"
            and rule.get("required_for_release") is True
            and rule.get("on_missing_authority")
            == "missing_authoritative_information"
            and rule.get("on_missing_value") == "automatic_fail"
            and rule.get("on_conflict") == "automatic_fail"
            and rule.get("release_hold_on_conflict") is True
            and rule.get("review_owner") == "document_control"
        ):
            return rule
    return None


def _drawing_register_metadata_revision_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    register_by_drawing = _records_by_drawing_number(
        sources.records_of_type("drawing_register_record")
    )
    metadata_by_drawing = _records_by_drawing_number(
        sources.records_of_type("drawing_metadata_record")
    )
    drawing_numbers = sorted(
        register_by_drawing.keys() & metadata_by_drawing.keys()
    )

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for drawing_number in drawing_numbers:
        register_record = register_by_drawing[drawing_number]
        metadata_record = metadata_by_drawing[drawing_number]
        expected_original = register_record.original_values["revision_id"]
        actual_original = metadata_record.original_values["revision_id"]
        expected_value = _normalize_revision(
            register_record.values["revision_id"]
        )
        actual_value = _normalize_revision(
            metadata_record.values["revision_id"]
        )
        pair_evidence = _revision_evidence(
            drawing_number=drawing_number,
            register_record=register_record,
            metadata_record=metadata_record,
            expected_original=expected_original,
            expected_value=expected_value,
            actual_original=actual_original,
            actual_value=actual_value,
        )
        evidence.extend(pair_evidence)
        if expected_value == actual_value:
            continue

        document_id = str(register_record.values["document_id"])
        findings.append(
            _revision_mismatch_finding(
                package_id=package_id,
                document_id=document_id,
                drawing_number=drawing_number,
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=pair_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Compared {len(drawing_numbers)} exact drawing pair(s) and "
                f"found {len(findings)} authoritative revision mismatch(es)."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(drawing_numbers)} exact drawing pair(s) agree with the "
            "authoritative drawing-register revision."
        ),
        evidence=tuple(evidence),
    )


def _drawing_register_metadata_presence_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    register_by_drawing = _records_by_drawing_number(
        sources.records_of_type("drawing_register_record")
    )
    metadata_records = sources.records_of_type("drawing_metadata_record")
    metadata_by_drawing = _records_by_drawing_number(metadata_records)
    drawing_numbers = sorted(register_by_drawing)
    collection_locator = _metadata_collection_locator(metadata_records)

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for drawing_number in drawing_numbers:
        register_record = register_by_drawing[drawing_number]
        register_locator = _register_drawing_number_locator(
            drawing_number=drawing_number,
            register_record=register_record,
        )
        evidence.append(register_locator)
        if drawing_number in metadata_by_drawing:
            continue

        findings.append(
            _missing_metadata_finding(
                package_id=package_id,
                document_id=str(register_record.values["document_id"]),
                drawing_number=drawing_number,
                evidence=(register_locator, collection_locator),
            )
        )

    evidence.append(collection_locator)
    if findings:
        return RelationshipCheckResult(
            check_id=DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                "Authoritative drawing-register entries checked: "
                f"{len(drawing_numbers)}; missing drawing-metadata "
                f"counterparts found: {len(findings)}."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            "Authoritative drawing-register entries checked: "
            f"{len(drawing_numbers)}; no missing drawing-metadata counterparts "
            "were found."
        ),
        evidence=tuple(evidence),
    )


def _drawing_metadata_register_authority_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    metadata_records = sources.records_of_type("drawing_metadata_record")
    metadata_by_drawing = _records_by_drawing_number(metadata_records)
    register_records = sources.records_of_type("drawing_register_record")
    register_by_drawing = _records_by_drawing_number(register_records)
    drawing_numbers = sorted(metadata_by_drawing)
    collection_locator = _register_collection_locator(register_records)

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for drawing_number in drawing_numbers:
        metadata_record = metadata_by_drawing[drawing_number]
        metadata_locator = _metadata_drawing_number_locator(
            drawing_number=drawing_number,
            metadata_record=metadata_record,
        )
        evidence.append(metadata_locator)
        if drawing_number in register_by_drawing:
            continue

        findings.append(
            _missing_register_authority_finding(
                package_id=package_id,
                document_id=str(metadata_record.values["document_id"]),
                drawing_number=drawing_number,
                evidence=(metadata_locator, collection_locator),
            )
        )

    evidence.append(collection_locator)
    if findings:
        return RelationshipCheckResult(
            check_id=DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Drawing-metadata records checked: {len(drawing_numbers)}; "
                f"records without drawing-register authority: {len(findings)}."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(drawing_numbers)} drawing-metadata record(s) have an "
            "authoritative drawing-register record."
        ),
        evidence=tuple(evidence),
    )


def _drawing_register_metadata_file_reference_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
    manifest: LoadedPackageManifest,
) -> RelationshipCheckResult:
    register_by_drawing = _records_by_drawing_number(
        sources.records_of_type("drawing_register_record")
    )
    metadata_by_drawing = _records_by_drawing_number(
        sources.records_of_type("drawing_metadata_record")
    )
    drawing_numbers = sorted(
        register_by_drawing.keys() & metadata_by_drawing.keys()
    )

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for drawing_number in drawing_numbers:
        register_record = register_by_drawing[drawing_number]
        metadata_record = metadata_by_drawing[drawing_number]
        expected_original = register_record.original_values["file_ref_id"]
        actual_original = metadata_record.original_values["file_ref_id"]
        expected_value = _normalize_identifier(
            register_record.values["file_ref_id"]
        )
        actual_value = _normalize_identifier(
            metadata_record.values["file_ref_id"]
        )
        pair_evidence = _file_reference_evidence(
            manifest=manifest,
            register_record=register_record,
            metadata_record=metadata_record,
            expected_original=expected_original,
            expected_value=expected_value,
            actual_original=actual_original,
            actual_value=actual_value,
        )
        evidence.extend(pair_evidence)
        if expected_value == actual_value:
            continue

        findings.append(
            _file_reference_mismatch_finding(
                package_id=package_id,
                document_id=str(register_record.values["document_id"]),
                drawing_number=drawing_number,
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=pair_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Compared {len(drawing_numbers)} exact drawing pair(s) and "
                f"found {len(findings)} authoritative file-reference "
                "mismatch(es)."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(drawing_numbers)} exact drawing pair(s) agree with the "
            "authoritative drawing-register file reference."
        ),
        evidence=tuple(evidence),
    )


def _drawing_register_manifest_file_reciprocity_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
    manifest: LoadedPackageManifest,
) -> RelationshipCheckResult:
    register_by_drawing = _records_by_drawing_number(
        sources.records_of_type("drawing_register_record")
    )
    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []

    for drawing_number in sorted(register_by_drawing):
        register_record = register_by_drawing[drawing_number]
        document_id = _normalize_identifier(
            register_record.values["document_id"]
        )
        file_ref_id = _normalize_identifier(
            register_record.values["file_ref_id"]
        )
        inventory_matches = _matching_manifest_inventory(
            manifest,
            document_id=document_id,
            drawing_number=drawing_number,
        )
        required_mappings = _required_document_file_mappings(
            manifest,
            document_id=document_id,
        )
        matching_mappings = tuple(
            item
            for item in required_mappings
            if item[1]["target"].get("identifier_type") == "file_ref_id"
            and _normalize_identifier(
                item[1]["target"].get("identifier")
            )
            == file_ref_id
        )
        conflicting_mappings = tuple(
            item for item in required_mappings if item not in matching_mappings
        )

        inventory_file_ref_ids = sorted(
            _normalize_identifier(item[1].get("file_ref_id"))
            for item in inventory_matches
            if isinstance(item[1].get("file_ref_id"), str)
        )
        file_reference_declarations = _matching_manifest_file_references(
            manifest,
            file_ref_id=file_ref_id,
        )
        file_reference_resolved = file_ref_id in manifest.file_reference_paths

        failed_clauses: list[str] = []
        if len(inventory_matches) != 1:
            failed_clauses.append("manifest_inventory_match")
        if inventory_file_ref_ids != [file_ref_id]:
            failed_clauses.append("manifest_inventory_file_reference")
        if (
            len(file_reference_declarations) != 1
            or not file_reference_resolved
        ):
            failed_clauses.append("manifest_file_reference_resolution")
        if len(matching_mappings) != 1:
            failed_clauses.append("required_document_to_file_mapping")
        if conflicting_mappings:
            failed_clauses.append(
                "conflicting_required_document_to_file_mapping"
            )

        expected_value = {
            "document_inventory": {
                "match_count": 1,
                "document_id": document_id,
                "drawing_number": drawing_number,
                "file_ref_id": file_ref_id,
            },
            "file_reference": {
                "file_ref_id": file_ref_id,
                "declared_count": 1,
                "resolved_inside_allowed_root": True,
            },
            "required_document_to_file": {
                "match_count": 1,
                "document_id": document_id,
                "file_ref_id": file_ref_id,
                "conflicting_count": 0,
            },
        }
        actual_value = {
            "failed_clauses": failed_clauses,
            "document_inventory": {
                "match_count": len(inventory_matches),
                "file_ref_ids": inventory_file_ref_ids,
            },
            "file_reference": {
                "declared_count": len(file_reference_declarations),
                "resolved_inside_allowed_root": file_reference_resolved,
            },
            "required_document_to_file": {
                "matching_relationship_ids": [
                    _relationship_id(item) for item in matching_mappings
                ],
                "conflicting_mappings": [
                    _normalized_document_file_mapping(item)
                    for item in conflicting_mappings
                ],
            },
        }
        drawing_evidence = _drawing_manifest_reciprocity_evidence(
            manifest=manifest,
            register_record=register_record,
            document_id=document_id,
            drawing_number=drawing_number,
            file_ref_id=file_ref_id,
            inventory_matches=inventory_matches,
            file_reference_declarations=file_reference_declarations,
            required_mappings=required_mappings,
            matching_mappings=matching_mappings,
            conflicting_mappings=conflicting_mappings,
        )
        evidence.extend(drawing_evidence)
        if not failed_clauses:
            continue

        findings.append(
            _drawing_manifest_reciprocity_finding(
                package_id=package_id,
                document_id=document_id,
                drawing_number=drawing_number,
                file_ref_id=file_ref_id,
                failed_clauses=tuple(failed_clauses),
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=drawing_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Checked {len(register_by_drawing)} authoritative drawing(s) "
                f"and found {len(findings)} non-reciprocal manifest mapping(s)."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(register_by_drawing)} authoritative drawing(s) have "
            "one reciprocal manifest inventory, file, and required mapping."
        ),
        evidence=tuple(evidence),
    )


def _records_by_drawing_number(
    records: tuple[StructuredSourceRecord, ...],
) -> dict[str, StructuredSourceRecord]:
    return {
        _normalize_identifier(record.values["drawing_number"]): record
        for record in records
    }


def _normalize_identifier(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("P2.1 accepted drawing identifiers must be strings")
    return value.strip()


def _normalize_revision(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("P2.1 accepted drawing revisions must be strings")
    return value.strip()


def _revision_evidence(
    *,
    drawing_number: str,
    register_record: StructuredSourceRecord,
    metadata_record: StructuredSourceRecord,
    expected_original: Any,
    expected_value: str,
    actual_original: Any,
    actual_value: str,
) -> tuple[EvidenceLocator, EvidenceLocator]:
    register_locator = replace(
        register_record.field_locator(
            "revision_id",
            original_value=expected_original,
            normalized_value=expected_value,
        ),
        row_key_column="drawing_number",
        row_key_value=drawing_number,
    )
    metadata_locator = metadata_record.field_locator(
        "revision_id",
        original_value=actual_original,
        normalized_value=actual_value,
    )
    return register_locator, metadata_locator


def _file_reference_evidence(
    *,
    manifest: LoadedPackageManifest,
    register_record: StructuredSourceRecord,
    metadata_record: StructuredSourceRecord,
    expected_original: Any,
    expected_value: str,
    actual_original: Any,
    actual_value: str,
) -> tuple[EvidenceLocator, ...]:
    evidence = [
        register_record.field_locator(
            "file_ref_id",
            original_value=expected_original,
            normalized_value=expected_value,
        ),
        metadata_record.field_locator(
            "file_ref_id",
            original_value=actual_original,
            normalized_value=actual_value,
        ),
    ]
    expected_locator = _manifest_file_reference_locator(
        manifest,
        expected_value,
    )
    if expected_locator is not None:
        evidence.append(expected_locator)
    if actual_value != expected_value:
        actual_locator = _manifest_file_reference_locator(
            manifest,
            actual_value,
        )
        if actual_locator is not None:
            evidence.append(actual_locator)
    return tuple(evidence)


def _manifest_file_reference_locator(
    manifest: LoadedPackageManifest,
    file_ref_id: str,
) -> EvidenceLocator | None:
    declarations = manifest.manifest.get("file_references")
    if not isinstance(declarations, list):
        return None
    declaration = next(
        (
            item
            for item in declarations
            if isinstance(item, Mapping)
            and item.get("file_ref_id") == file_ref_id
        ),
        None,
    )
    resolved = manifest.file_reference_paths.get(file_ref_id)
    if declaration is None or resolved is None:
        return None
    declared_path = declaration.get("path")
    if not isinstance(declared_path, str):
        return None
    try:
        package_relative = resolved.relative_to(manifest.package_root).as_posix()
    except ValueError:
        package_relative = declared_path
    inside_allowed_root = any(
        resolved != allowed_root and resolved.is_relative_to(allowed_root)
        for allowed_root in manifest.allowed_file_roots
    )
    return EvidenceLocator(
        source_type="package_manifest",
        source_file=PACKAGE_MANIFEST_FILENAME,
        format="file_reference",
        file_ref_id=file_ref_id,
        declared_relative_path=declared_path,
        resolved_package_relative_path=package_relative,
        boundary_check=(
            "inside_allowed_root"
            if inside_allowed_root
            else "outside_allowed_root"
        ),
    )


def _matching_manifest_inventory(
    manifest: LoadedPackageManifest,
    *,
    document_id: str,
    drawing_number: str,
) -> tuple[tuple[int, Mapping[str, Any]], ...]:
    inventory = manifest.manifest.get("document_inventory")
    if not isinstance(inventory, list):
        return ()
    return tuple(
        (index, item)
        for index, item in enumerate(inventory)
        if isinstance(item, Mapping)
        and item.get("document_id") == document_id
        and item.get("drawing_number") == drawing_number
    )


def _matching_manifest_file_references(
    manifest: LoadedPackageManifest,
    *,
    file_ref_id: str,
) -> tuple[tuple[int, Mapping[str, Any]], ...]:
    references = manifest.manifest.get("file_references")
    if not isinstance(references, list):
        return ()
    return tuple(
        (index, item)
        for index, item in enumerate(references)
        if isinstance(item, Mapping) and item.get("file_ref_id") == file_ref_id
    )


def _required_document_file_mappings(
    manifest: LoadedPackageManifest,
    *,
    document_id: str,
) -> tuple[tuple[int, Mapping[str, Any]], ...]:
    relationships = manifest.manifest.get("relationship_declarations")
    if not isinstance(relationships, list):
        return ()
    return tuple(
        sorted(
            (
                (index, item)
                for index, item in enumerate(relationships)
                if isinstance(item, Mapping)
                and item.get("relationship_type") == "document_to_file"
                and item.get("required_for_release") is True
                and isinstance(item.get("source"), Mapping)
                and item["source"].get("identifier_type") == "document_id"
                and item["source"].get("identifier") == document_id
                and isinstance(item.get("target"), Mapping)
            ),
            key=_relationship_id,
        )
    )


def _relationship_id(item: tuple[int, Mapping[str, Any]]) -> str:
    return str(item[1].get("relationship_id", ""))


def _normalized_document_file_mapping(
    item: tuple[int, Mapping[str, Any]],
) -> dict[str, Any]:
    relationship = item[1]
    source = relationship["source"]
    target = relationship["target"]
    return {
        "relationship_id": _relationship_id(item),
        "document_id": source.get("identifier"),
        "file_ref_id": target.get("identifier"),
        "required_for_release": relationship.get("required_for_release"),
    }


def _drawing_manifest_reciprocity_evidence(
    *,
    manifest: LoadedPackageManifest,
    register_record: StructuredSourceRecord,
    document_id: str,
    drawing_number: str,
    file_ref_id: str,
    inventory_matches: tuple[tuple[int, Mapping[str, Any]], ...],
    file_reference_declarations: tuple[
        tuple[int, Mapping[str, Any]], ...
    ],
    required_mappings: tuple[tuple[int, Mapping[str, Any]], ...],
    matching_mappings: tuple[tuple[int, Mapping[str, Any]], ...],
    conflicting_mappings: tuple[tuple[int, Mapping[str, Any]], ...],
) -> tuple[EvidenceLocator, ...]:
    locators = [
        register_record.field_locator(
            "document_id",
            normalized_value=document_id,
        ),
        _register_drawing_number_locator(
            drawing_number=drawing_number,
            register_record=register_record,
        ),
        register_record.field_locator(
            "file_ref_id",
            normalized_value=file_ref_id,
        ),
    ]
    if len(inventory_matches) == 1:
        locators.append(
            _manifest_item_locator(
                "document_inventory",
                inventory_matches[0],
                normalized_value={
                    "document_id": document_id,
                    "drawing_number": drawing_number,
                    "file_ref_id": inventory_matches[0][1].get(
                        "file_ref_id"
                    ),
                },
            )
        )
    else:
        locators.append(
            _manifest_collection_search_locator(
                manifest,
                "document_inventory",
                expected_value={
                    "document_id": document_id,
                    "drawing_number": drawing_number,
                    "file_ref_id": file_ref_id,
                },
            )
        )

    file_locator = _manifest_file_reference_locator(manifest, file_ref_id)
    if len(file_reference_declarations) == 1 and file_locator is not None:
        locators.append(file_locator)
    else:
        locators.append(
            _manifest_collection_search_locator(
                manifest,
                "file_references",
                expected_value={"file_ref_id": file_ref_id},
            )
        )

    if len(matching_mappings) == 1 and not conflicting_mappings:
        locators.append(
            _manifest_item_locator(
                "relationship_declarations",
                matching_mappings[0],
                normalized_value=_normalized_document_file_mapping(
                    matching_mappings[0]
                ),
            )
        )
    else:
        locators.append(
            _manifest_collection_search_locator(
                manifest,
                "relationship_declarations",
                expected_value={
                    "relationship_type": "document_to_file",
                    "document_id": document_id,
                    "file_ref_id": file_ref_id,
                    "required_for_release": True,
                },
            )
        )
        locators.extend(
            _manifest_item_locator(
                "relationship_declarations",
                item,
                normalized_value=_normalized_document_file_mapping(item),
            )
            for item in required_mappings
        )
    return tuple(locators)


def _manifest_item_locator(
    collection_name: str,
    item: tuple[int, Mapping[str, Any]],
    *,
    normalized_value: Any,
) -> EvidenceLocator:
    index, document = item
    record_id = document.get("relationship_id") or document.get("document_id")
    return EvidenceLocator(
        source_type="package_manifest",
        source_file=PACKAGE_MANIFEST_FILENAME,
        format="json",
        json_pointer=f"/{collection_name}/{index}",
        record_id=str(record_id) if record_id is not None else None,
        property_name=collection_name,
        original_value=dict(document),
        normalized_value=normalized_value,
    )


def _manifest_collection_search_locator(
    manifest: LoadedPackageManifest,
    collection_name: str,
    *,
    expected_value: Mapping[str, Any],
) -> EvidenceLocator:
    collection = manifest.manifest.get(collection_name)
    original_value = collection if isinstance(collection, list) else []
    return EvidenceLocator(
        source_type="package_manifest",
        source_file=PACKAGE_MANIFEST_FILENAME,
        format="json",
        json_pointer=f"/{collection_name}",
        property_name=collection_name,
        original_value=original_value,
        normalized_value={
            "expected": dict(expected_value),
            "searched_count": len(original_value),
        },
    )


def _register_drawing_number_locator(
    *,
    drawing_number: str,
    register_record: StructuredSourceRecord,
) -> EvidenceLocator:
    return replace(
        register_record.field_locator(
            "drawing_number",
            original_value=register_record.original_values["drawing_number"],
            normalized_value=drawing_number,
        ),
        row_key_column="drawing_number",
        row_key_value=drawing_number,
    )


def _metadata_collection_locator(
    metadata_records: tuple[StructuredSourceRecord, ...],
) -> EvidenceLocator:
    original_membership = [
        record.original_values["drawing_number"] for record in metadata_records
    ]
    normalized_membership = sorted(
        _normalize_identifier(record.values["drawing_number"])
        for record in metadata_records
    )
    return EvidenceLocator(
        source_type="drawing_metadata",
        source_file="inputs/drawing_metadata.json",
        format="json",
        json_pointer="/records",
        property_name="records",
        original_value=original_membership,
        normalized_value=normalized_membership,
    )


def _metadata_drawing_number_locator(
    *,
    drawing_number: str,
    metadata_record: StructuredSourceRecord,
) -> EvidenceLocator:
    return metadata_record.field_locator(
        "drawing_number",
        original_value=metadata_record.original_values["drawing_number"],
        normalized_value=drawing_number,
    )


def _register_collection_locator(
    register_records: tuple[StructuredSourceRecord, ...],
) -> EvidenceLocator:
    original_membership = [
        record.original_values["drawing_number"] for record in register_records
    ]
    normalized_membership = sorted(
        _normalize_identifier(record.values["drawing_number"])
        for record in register_records
    )
    return EvidenceLocator(
        source_type="drawing_register",
        source_file="inputs/drawing_register.csv",
        format="csv",
        row_number=1,
        header_row_number=1,
        column_name="drawing_number",
        original_value=original_membership,
        normalized_value=normalized_membership,
    )


def _revision_mismatch_finding(
    *,
    package_id: str,
    document_id: str,
    drawing_number: str,
    expected_value: str,
    actual_value: str,
    evidence: tuple[EvidenceLocator, EvidenceLocator],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": DRAWING_REVISION_MISMATCH_CODE,
        "authority_rule_id": DRAWING_REVISION_AUTHORITY_RULE_ID,
        "drawing_number": drawing_number,
        "result_state": result_state,
        "severity": "high",
        "release_hold": True,
        "expected_value": expected_value,
        "actual_value": actual_value,
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    return RelationshipFinding(
        finding_id=f"FND-{digest.upper()}",
        check_id=DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=DRAWING_REVISION_MISMATCH_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=DRAWING_REVISION_AUTHORITY_RULE_ID,
        message=(
            f"Drawing metadata revision {actual_value} conflicts with "
            f"authoritative drawing-register revision {expected_value} for "
            f"{drawing_number}."
        ),
        affected_identifiers=(document_id, drawing_number),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="document_control",
        evidence=evidence,
    )


def _file_reference_mismatch_finding(
    *,
    package_id: str,
    document_id: str,
    drawing_number: str,
    expected_value: str,
    actual_value: str,
    evidence: tuple[EvidenceLocator, ...],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": DRAWING_FILE_REFERENCE_MISMATCH_CODE,
        "authority_rule_id": DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID,
        "drawing_number": drawing_number,
        "result_state": result_state,
        "severity": "high",
        "release_hold": True,
        "expected_value": expected_value,
        "actual_value": actual_value,
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    return RelationshipFinding(
        finding_id=f"FND-{digest.upper()}",
        check_id=DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=DRAWING_FILE_REFERENCE_MISMATCH_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID,
        message=(
            f"Drawing metadata file reference {actual_value} conflicts with "
            "authoritative drawing-register file reference "
            f"{expected_value} for {drawing_number}."
        ),
        affected_identifiers=(
            document_id,
            drawing_number,
            expected_value,
            actual_value,
        ),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="document_control",
        evidence=evidence,
    )


def _drawing_manifest_reciprocity_finding(
    *,
    package_id: str,
    document_id: str,
    drawing_number: str,
    file_ref_id: str,
    failed_clauses: tuple[str, ...],
    expected_value: Mapping[str, Any],
    actual_value: Mapping[str, Any],
    evidence: tuple[EvidenceLocator, ...],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE,
        "authority_rule_id": DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID,
        "drawing_number": drawing_number,
        "result_state": result_state,
        "severity": "high",
        "release_hold": True,
        "expected_value": expected_value,
        "actual_value": actual_value,
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    return RelationshipFinding(
        finding_id=f"FND-{digest.upper()}",
        check_id=DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID,
        message=(
            f"Authoritative drawing {drawing_number} is not reciprocal with "
            "the package manifest: " + ", ".join(failed_clauses) + "."
        ),
        affected_identifiers=(document_id, drawing_number, file_ref_id),
        expected_value=dict(expected_value),
        actual_value=dict(actual_value),
        review_owner="document_control",
        evidence=evidence,
    )


def _missing_metadata_finding(
    *,
    package_id: str,
    document_id: str,
    drawing_number: str,
    evidence: tuple[EvidenceLocator, EvidenceLocator],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    expected_value = "drawing_metadata counterpart"
    actual_value = "missing"
    semantic = {
        "package_id": package_id,
        "check_id": DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": DRAWING_METADATA_MISSING_CODE,
        "authority_rule_id": DRAWING_REVISION_AUTHORITY_RULE_ID,
        "drawing_number": drawing_number,
        "result_state": result_state,
        "severity": "high",
        "release_hold": True,
        "expected_value": expected_value,
        "actual_value": actual_value,
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    return RelationshipFinding(
        finding_id=f"FND-{digest.upper()}",
        check_id=DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=DRAWING_METADATA_MISSING_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=DRAWING_REVISION_AUTHORITY_RULE_ID,
        message=(
            f"Authoritative drawing-register drawing {drawing_number} has no "
            "drawing-metadata counterpart."
        ),
        affected_identifiers=(document_id, drawing_number),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="document_control",
        evidence=evidence,
    )


def _missing_register_authority_finding(
    *,
    package_id: str,
    document_id: str,
    drawing_number: str,
    evidence: tuple[EvidenceLocator, EvidenceLocator],
) -> RelationshipFinding:
    result_state = "missing_authoritative_information"
    expected_value = "authoritative drawing_register record"
    actual_value = "missing"
    semantic = {
        "package_id": package_id,
        "check_id": DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": DRAWING_REGISTER_AUTHORITY_MISSING_CODE,
        "authority_rule_id": DRAWING_REVISION_AUTHORITY_RULE_ID,
        "drawing_number": drawing_number,
        "result_state": result_state,
        "severity": "high",
        "release_hold": True,
        "expected_value": expected_value,
        "actual_value": actual_value,
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    return RelationshipFinding(
        finding_id=f"FND-{digest.upper()}",
        check_id=DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=DRAWING_REGISTER_AUTHORITY_MISSING_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=DRAWING_REVISION_AUTHORITY_RULE_ID,
        message=(
            f"Drawing metadata {drawing_number} has no authoritative "
            "drawing-register record."
        ),
        affected_identifiers=(document_id, drawing_number),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="document_control",
        evidence=evidence,
    )


def _skipped_check(
    *,
    check_id: str,
    blocked_by: tuple[str, ...],
    summary: str,
) -> RelationshipCheckResult:
    return RelationshipCheckResult(
        check_id=check_id,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="skipped",
        summary=summary,
        blocked_by=blocked_by,
    )
