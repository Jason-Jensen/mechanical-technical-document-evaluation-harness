"""Datasheet-domain package relationship checks."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from mech_eval_harness.package_assurance._relationship_common import (
    RELATIONSHIP_CHECK_VERSION,
    _manifest_collection_search_locator,
    _manifest_item_locator,
    _normalize_identifier,
    _relationship_id,
    _skipped_check,
)
from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
from mech_eval_harness.package_assurance.manifest import LoadedPackageManifest
from mech_eval_harness.package_assurance.models import (
    EvidenceLocator,
    LoadedStructuredSources,
    RelationshipCheckResult,
    RelationshipFinding,
    StructuredSourceRecord,
)


EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID = (
    "equipment_datasheet_authority_presence"
)
EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE = (
    "EQUIPMENT_DATASHEET_AUTHORITY_MISSING"
)
EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID = "equipment_datasheet_association"
EQUIPMENT_DATASHEET_MISMATCH_CODE = "EQUIPMENT_DATASHEET_MISMATCH"
EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID = (
    "equipment_datasheet_manifest_reciprocity"
)
EQUIPMENT_DATASHEET_RECIPROCITY_FAILED_CODE = "EQUIPMENT_DATASHEET_RECIPROCITY_FAILED"
EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID = "AUTH-SPEC-001"


def _equipment_datasheet_authority_rule(
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
        if rule.get("rule_id") != EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID:
            continue
        if (
            rule.get("field") == "equipment.datasheet_id"
            and rule.get("authoritative_source") == "datasheet_spec_metadata"
            and rule.get("secondary_sources") == ["bom_or_equipment_list"]
            and rule.get("agreement_rule")
            == (
                "required equipment tags must map to the current datasheet or "
                "specification metadata"
            )
            and rule.get("normalization_profile")
            == "canonical_identifier_v1"
            and rule.get("required_for_release") is True
            and rule.get("on_missing_authority")
            == "missing_authoritative_information"
            and rule.get("on_missing_value") == "automatic_fail"
            and rule.get("on_conflict") == "automatic_fail"
            and rule.get("release_hold_on_conflict") is True
            and rule.get("review_owner") == "mechanical_engineering"
        ):
            return rule
    return None


def _evaluate_equipment_datasheet_authority_presence(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    if _equipment_datasheet_authority_rule(sources) is None:
        return _skipped_check(
            check_id=EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-SPEC-001 equipment "
                "datasheet authority rule is unavailable."
            ),
        )
    return _equipment_datasheet_authority_presence_check(
        package_id=package_id,
        sources=sources,
    )


def _evaluate_equipment_datasheet_association(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    if _equipment_datasheet_authority_rule(sources) is None:
        return _skipped_check(
            check_id=EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-SPEC-001 equipment "
                "datasheet authority rule is unavailable."
            ),
        )
    return _equipment_datasheet_association_check(
        package_id=package_id,
        sources=sources,
    )


def _evaluate_equipment_datasheet_manifest_reciprocity(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
    manifest: LoadedPackageManifest | None,
) -> RelationshipCheckResult:
    if _equipment_datasheet_authority_rule(sources) is None:
        return _skipped_check(
            check_id=EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-SPEC-001 equipment "
                "datasheet authority rule is unavailable."
            ),
        )
    if manifest is None:
        return _skipped_check(
            check_id=EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
            blocked_by=("package_gate_evaluation",),
            summary=(
                "Skipped because the accepted loaded package manifest is unavailable."
            ),
        )
    return _equipment_datasheet_manifest_reciprocity_check(
        package_id=package_id,
        sources=sources,
        manifest=manifest,
    )


def _equipment_datasheet_authority_presence_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    bom_records = tuple(
        sorted(
            (
                record
                for record in sources.records_of_type("equipment_item")
                if record.values["required_for_release"] is True
            ),
            key=lambda record: (
                _normalize_identifier(record.values["equipment_tag"]),
                _normalize_identifier(record.values["item_id"]),
            ),
        )
    )
    datasheet_records = tuple(
        sorted(
            sources.records_of_type("datasheet_record"),
            key=lambda record: (
                _normalize_identifier(record.values["equipment_tag"]),
                _normalize_identifier(record.values["datasheet_id"]),
                _normalize_identifier(record.values["record_id"]),
            ),
        )
    )

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for bom_record in bom_records:
        item_id = _normalize_identifier(bom_record.values["item_id"])
        equipment_tag = _normalize_identifier(
            bom_record.values["equipment_tag"]
        )
        matching_records = tuple(
            record
            for record in datasheet_records
            if record.values["required_for_release"] is True
            and _normalize_identifier(record.values["equipment_tag"])
            == equipment_tag
        )
        item_evidence = (
            bom_record.field_locator(
                "equipment_tag",
                normalized_value=equipment_tag,
            ),
            _datasheet_equipment_tag_search_locator(
                datasheet_records=datasheet_records,
                equipment_tag=equipment_tag,
                matching_records=matching_records,
            ),
        )
        evidence.extend(item_evidence)
        if len(matching_records) == 1:
            continue
        findings.append(
            _equipment_datasheet_authority_missing_finding(
                package_id=package_id,
                item_id=item_id,
                equipment_tag=equipment_tag,
                actual_count=len(matching_records),
                evidence=item_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Checked {len(bom_records)} release-required BOM equipment "
                f"tag(s) and found {len(findings)} without exactly one "
                "authoritative datasheet record."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(bom_records)} release-required BOM equipment tag(s) "
            "have exactly one authoritative datasheet record."
        ),
        evidence=tuple(evidence),
    )


def _equipment_datasheet_association_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    bom_records = tuple(
        sorted(
            (
                record
                for record in sources.records_of_type("equipment_item")
                if record.values["required_for_release"] is True
            ),
            key=lambda record: (
                _normalize_identifier(record.values["equipment_tag"]),
                _normalize_identifier(record.values["item_id"]),
            ),
        )
    )
    datasheet_records = tuple(
        sorted(
            sources.records_of_type("datasheet_record"),
            key=lambda record: (
                _normalize_identifier(record.values["equipment_tag"]),
                _normalize_identifier(record.values["datasheet_id"]),
                _normalize_identifier(record.values["record_id"]),
            ),
        )
    )

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    comparable_count = 0
    check_8_owned_count = 0
    for bom_record in bom_records:
        equipment_tag = _normalize_identifier(
            bom_record.values["equipment_tag"]
        )
        matching_records = tuple(
            record
            for record in datasheet_records
            if record.values["required_for_release"] is True
            and _normalize_identifier(record.values["equipment_tag"])
            == equipment_tag
        )
        if len(matching_records) != 1:
            check_8_owned_count += 1
            continue

        comparable_count += 1
        item_id = _normalize_identifier(bom_record.values["item_id"])
        authoritative_record = matching_records[0]
        expected_value = _normalize_identifier(
            authoritative_record.values["datasheet_id"]
        )
        actual_value = _normalize_identifier(bom_record.values["datasheet_id"])
        pair_evidence = (
            authoritative_record.field_locator(
                "datasheet_id",
                normalized_value=expected_value,
            ),
            bom_record.field_locator(
                "datasheet_id",
                normalized_value=actual_value,
            ),
        )
        evidence.extend(pair_evidence)
        if expected_value == actual_value:
            continue
        findings.append(
            _equipment_datasheet_mismatch_finding(
                package_id=package_id,
                item_id=item_id,
                equipment_tag=equipment_tag,
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=pair_evidence,
            )
        )

    ownership_note = (
        f" {check_8_owned_count} equipment tag(s) remained owned by check 8 "
        "because they did not have exactly one authoritative record."
        if check_8_owned_count
        else ""
    )
    if findings:
        return RelationshipCheckResult(
            check_id=EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Compared {comparable_count} equipment/datasheet "
                f"association(s) and found {len(findings)} mismatch(es)."
                f"{ownership_note}"
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {comparable_count} comparable equipment/datasheet "
            f"association(s) match.{ownership_note}"
        ),
        evidence=tuple(evidence),
    )


def _equipment_datasheet_manifest_reciprocity_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
    manifest: LoadedPackageManifest,
) -> RelationshipCheckResult:
    datasheet_records = tuple(
        sorted(
            sources.records_of_type("datasheet_record"),
            key=lambda record: (
                _normalize_identifier(record.values["equipment_tag"]),
                _normalize_identifier(record.values["datasheet_id"]),
                _normalize_identifier(record.values["record_id"]),
            ),
        )
    )
    authoritative_by_equipment = _required_authoritative_datasheet_mappings(
        datasheet_records
    )
    declared_by_equipment = _required_equipment_datasheet_mappings(manifest)
    required_bom_equipment_tags = {
        _normalize_identifier(record.values["equipment_tag"])
        for record in sources.records_of_type("equipment_item")
        if record.values["required_for_release"] is True
    }
    equipment_tags = sorted(
        authoritative_by_equipment.keys() | declared_by_equipment.keys()
    )

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    comparable_count = 0
    check_8_owned_count = 0
    for equipment_tag in equipment_tags:
        authoritative_records = authoritative_by_equipment.get(equipment_tag, ())
        declarations = declared_by_equipment.get(equipment_tag, ())
        if (
            equipment_tag in required_bom_equipment_tags
            and len(authoritative_records) != 1
        ):
            check_8_owned_count += 1
            continue

        comparable_count += 1
        expected_mappings = tuple(
            _normalized_authoritative_datasheet_mapping(record)
            for record in authoritative_records
        )
        actual_mappings = tuple(
            _normalized_equipment_datasheet_declaration(item) for item in declarations
        )
        expected_value = _mapping_comparison_value(
            expected_mappings,
            missing_value="authoritative release-required datasheet mapping",
        )
        actual_value = _mapping_comparison_value(
            actual_mappings,
            missing_value="missing",
        )
        pair_evidence = _equipment_datasheet_reciprocity_evidence(
            manifest=manifest,
            datasheet_records=datasheet_records,
            equipment_tag=equipment_tag,
            authoritative_records=authoritative_records,
            declarations=declarations,
            expected_value=expected_value,
        )
        evidence.extend(pair_evidence)
        if expected_mappings == actual_mappings and expected_mappings:
            continue
        findings.append(
            _equipment_datasheet_reciprocity_finding(
                package_id=package_id,
                equipment_tag=equipment_tag,
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=pair_evidence,
            )
        )

    ownership_note = (
        f" {check_8_owned_count} equipment tag(s) remained owned by check 8 "
        "because they did not have exactly one authoritative record."
        if check_8_owned_count
        else ""
    )
    if findings:
        return RelationshipCheckResult(
            check_id=EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Checked {comparable_count} authoritative or declared "
                "equipment/datasheet mapping(s) and found "
                f"{len(findings)} non-reciprocal mapping(s).{ownership_note}"
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {comparable_count} comparable equipment/datasheet mapping(s) "
            f"have reciprocal manifest declarations.{ownership_note}"
        ),
        evidence=tuple(evidence),
    )


def _required_authoritative_datasheet_mappings(
    datasheet_records: tuple[StructuredSourceRecord, ...],
) -> dict[str, tuple[StructuredSourceRecord, ...]]:
    grouped: dict[str, list[StructuredSourceRecord]] = {}
    for record in datasheet_records:
        if record.values["required_for_release"] is not True:
            continue
        equipment_tag = _normalize_identifier(record.values["equipment_tag"])
        grouped.setdefault(equipment_tag, []).append(record)
    return {equipment_tag: tuple(records) for equipment_tag, records in grouped.items()}


def _required_equipment_datasheet_mappings(
    manifest: LoadedPackageManifest,
) -> dict[str, tuple[tuple[int, Mapping[str, Any]], ...]]:
    relationships = manifest.manifest.get("relationship_declarations")
    if not isinstance(relationships, list):
        return {}

    grouped: dict[str, list[tuple[int, Mapping[str, Any]]]] = {}
    for index, item in enumerate(relationships):
        if (
            not isinstance(item, Mapping)
            or item.get("relationship_type") != "equipment_to_datasheet"
            or item.get("required_for_release") is not True
            or not isinstance(item.get("source"), Mapping)
            or item["source"].get("identifier_type") != "equipment_tag"
            or not isinstance(item["source"].get("identifier"), str)
            or not isinstance(item.get("target"), Mapping)
            or item["target"].get("identifier_type") != "datasheet_id"
            or not isinstance(item["target"].get("identifier"), str)
        ):
            continue
        equipment_tag = _normalize_identifier(item["source"]["identifier"])
        grouped.setdefault(equipment_tag, []).append((index, item))

    return {
        equipment_tag: tuple(
            sorted(items, key=_equipment_datasheet_declaration_sort_key)
        )
        for equipment_tag, items in grouped.items()
    }


def _equipment_datasheet_declaration_sort_key(
    item: tuple[int, Mapping[str, Any]],
) -> tuple[str, str]:
    target = item[1]["target"]
    return (
        _normalize_identifier(target["identifier"]),
        _relationship_id(item),
    )


def _normalized_authoritative_datasheet_mapping(
    record: StructuredSourceRecord,
) -> dict[str, Any]:
    return {
        "equipment_tag": _normalize_identifier(record.values["equipment_tag"]),
        "datasheet_id": _normalize_identifier(record.values["datasheet_id"]),
        "required_for_release": record.values["required_for_release"],
    }


def _normalized_equipment_datasheet_declaration(
    item: tuple[int, Mapping[str, Any]],
) -> dict[str, Any]:
    relationship = item[1]
    return {
        "equipment_tag": _normalize_identifier(relationship["source"]["identifier"]),
        "datasheet_id": _normalize_identifier(relationship["target"]["identifier"]),
        "required_for_release": relationship["required_for_release"],
    }


def _mapping_comparison_value(
    mappings: tuple[dict[str, Any], ...],
    *,
    missing_value: str,
) -> Any:
    if not mappings:
        return missing_value
    if len(mappings) == 1:
        return mappings[0]
    return list(mappings)


def _equipment_datasheet_reciprocity_evidence(
    *,
    manifest: LoadedPackageManifest,
    datasheet_records: tuple[StructuredSourceRecord, ...],
    equipment_tag: str,
    authoritative_records: tuple[StructuredSourceRecord, ...],
    declarations: tuple[tuple[int, Mapping[str, Any]], ...],
    expected_value: Any,
) -> tuple[EvidenceLocator, ...]:
    locators: list[EvidenceLocator] = []
    if authoritative_records:
        for record in authoritative_records:
            locators.extend(
                (
                    record.field_locator(
                        "equipment_tag",
                        normalized_value=equipment_tag,
                    ),
                    record.field_locator(
                        "datasheet_id",
                        normalized_value=_normalize_identifier(
                            record.values["datasheet_id"]
                        ),
                    ),
                )
            )
    else:
        locators.append(
            _datasheet_equipment_tag_search_locator(
                datasheet_records=datasheet_records,
                equipment_tag=equipment_tag,
                matching_records=(),
            )
        )

    if declarations:
        locators.extend(
            _manifest_item_locator(
                "relationship_declarations",
                item,
                normalized_value=_normalized_equipment_datasheet_declaration(item),
            )
            for item in declarations
        )
    else:
        locators.append(
            _manifest_collection_search_locator(
                manifest,
                "relationship_declarations",
                expected_value={
                    "relationship_type": "equipment_to_datasheet",
                    "equipment_tag": equipment_tag,
                    "authoritative_mapping": expected_value,
                    "required_for_release": True,
                },
            )
        )
    return tuple(locators)


def _datasheet_equipment_tag_search_locator(
    *,
    datasheet_records: tuple[StructuredSourceRecord, ...],
    equipment_tag: str,
    matching_records: tuple[StructuredSourceRecord, ...],
) -> EvidenceLocator:
    return EvidenceLocator(
        source_type="datasheet_spec_metadata",
        source_file="inputs/datasheet_spec_metadata.json",
        format="json",
        json_pointer="/datasheets",
        property_name="equipment_tag",
        original_value=[
            {
                "record_id": record.original_values["record_id"],
                "datasheet_id": record.original_values["datasheet_id"],
                "equipment_tag": record.original_values["equipment_tag"],
                "required_for_release": record.original_values[
                    "required_for_release"
                ],
            }
            for record in datasheet_records
        ],
        normalized_value={
            "equipment_tag": equipment_tag,
            "matching_record_ids": [
                _normalize_identifier(record.values["record_id"])
                for record in matching_records
            ],
            "matching_datasheet_ids": [
                _normalize_identifier(record.values["datasheet_id"])
                for record in matching_records
            ],
            "authoritative_record_count": len(matching_records),
            "searched_record_count": len(datasheet_records),
        },
    )


def _equipment_datasheet_authority_missing_finding(
    *,
    package_id: str,
    item_id: str,
    equipment_tag: str,
    actual_count: int,
    evidence: tuple[EvidenceLocator, EvidenceLocator],
) -> RelationshipFinding:
    result_state = "missing_authoritative_information"
    expected_value = "one authoritative datasheet"
    semantic = {
        "package_id": package_id,
        "check_id": EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE,
        "authority_rule_id": EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
        "item_id": item_id,
        "equipment_tag": equipment_tag,
        "result_state": result_state,
        "severity": "high",
        "release_hold": True,
        "expected_value": expected_value,
        "actual_value": actual_count,
    }
    digest = hashlib.sha256(
        json.dumps(
            semantic,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    ).hexdigest()[:16]
    if actual_count == 0:
        detail = "has no release-required authoritative datasheet record"
    else:
        detail = (
            f"has {actual_count} competing release-required authoritative "
            "datasheet records"
        )
    return RelationshipFinding(
        finding_id=f"FND-{digest.upper()}",
        check_id=EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
        message=(
            f"Release-required BOM equipment tag {equipment_tag} for "
            f"{item_id} {detail}."
        ),
        affected_identifiers=(item_id, equipment_tag),
        expected_value=expected_value,
        actual_value=actual_count,
        review_owner="mechanical_engineering",
        evidence=evidence,
    )


def _equipment_datasheet_mismatch_finding(
    *,
    package_id: str,
    item_id: str,
    equipment_tag: str,
    expected_value: str,
    actual_value: str,
    evidence: tuple[EvidenceLocator, EvidenceLocator],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": EQUIPMENT_DATASHEET_MISMATCH_CODE,
        "authority_rule_id": EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
        "item_id": item_id,
        "equipment_tag": equipment_tag,
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
        check_id=EQUIPMENT_DATASHEET_ASSOCIATION_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=EQUIPMENT_DATASHEET_MISMATCH_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
        message=(
            f"BOM datasheet {actual_value} conflicts with authoritative "
            f"datasheet {expected_value} for {item_id} / {equipment_tag}."
        ),
        affected_identifiers=(item_id, equipment_tag),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="mechanical_engineering",
        evidence=evidence,
    )


def _equipment_datasheet_reciprocity_finding(
    *,
    package_id: str,
    equipment_tag: str,
    expected_value: Any,
    actual_value: Any,
    evidence: tuple[EvidenceLocator, ...],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": EQUIPMENT_DATASHEET_RECIPROCITY_FAILED_CODE,
        "authority_rule_id": EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
        "equipment_tag": equipment_tag,
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
        check_id=EQUIPMENT_DATASHEET_MANIFEST_RECIPROCITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=EQUIPMENT_DATASHEET_RECIPROCITY_FAILED_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
        message=(
            f"Equipment tag {equipment_tag} is not reciprocal with the package "
            "manifest equipment-to-datasheet declarations."
        ),
        affected_identifiers=(equipment_tag,),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="mechanical_engineering",
        evidence=evidence,
    )
