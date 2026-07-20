"""BOM and equipment-domain package relationship checks."""

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


BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID = (
    "bom_item_equipment_manifest_reciprocity"
)
BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE = (
    "BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED"
)
BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID = "bom_equipment_drawing_presence"
BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE = (
    "BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING"
)
BOM_EQUIPMENT_AUTHORITY_RULE_ID = "AUTH-BOM-002"


def _bom_equipment_authority_rule(
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
        if rule.get("rule_id") != BOM_EQUIPMENT_AUTHORITY_RULE_ID:
            continue
        if (
            rule.get("field") == "bom.equipment_tag"
            and rule.get("authoritative_source")
            == "bom_or_equipment_list"
            and rule.get("secondary_sources")
            == ["datasheet_spec_metadata", "drawing_metadata"]
            and rule.get("agreement_rule")
            == (
                "equipment tag relationships must resolve to one canonical "
                "equipment scope unless duplicate policy applies"
            )
            and rule.get("normalization_profile")
            == "canonical_identifier_v1"
            and rule.get("duplicate_policy") == "equipment_tag"
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


def _evaluate_bom_item_equipment_manifest_reciprocity(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
    manifest: LoadedPackageManifest | None,
) -> RelationshipCheckResult:
    if _bom_equipment_authority_rule(sources) is None:
        return _skipped_check(
            check_id=BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-BOM-002 equipment-tag "
                "authority rule is unavailable."
            ),
        )
    if manifest is None:
        return _skipped_check(
            check_id=BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
            blocked_by=("package_gate_evaluation",),
            summary=(
                "Skipped because the accepted loaded package manifest is "
                "unavailable."
            ),
        )
    return _bom_item_equipment_manifest_reciprocity_check(
        package_id=package_id,
        sources=sources,
        manifest=manifest,
    )


def _evaluate_bom_equipment_drawing_presence(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    if _bom_equipment_authority_rule(sources) is None:
        return _skipped_check(
            check_id=BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-BOM-002 equipment-tag "
                "authority rule is unavailable."
            ),
        )
    return _bom_equipment_drawing_presence_check(
        package_id=package_id,
        sources=sources,
    )


def _bom_item_equipment_manifest_reciprocity_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
    manifest: LoadedPackageManifest,
) -> RelationshipCheckResult:
    bom_by_item = {
        _normalize_identifier(record.values["item_id"]): record
        for record in sources.records_of_type("equipment_item")
        if record.values["required_for_release"] is True
    }
    mappings_by_item = _required_item_equipment_mappings(manifest)
    item_ids = sorted(bom_by_item.keys() | mappings_by_item.keys())

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for item_id in item_ids:
        bom_record = bom_by_item.get(item_id)
        mappings = mappings_by_item.get(item_id, ())
        expected_value: Any
        if bom_record is None:
            expected_value = "authoritative release-required BOM item"
        else:
            expected_value = {
                "item_id": item_id,
                "equipment_tag": _normalize_identifier(
                    bom_record.values["equipment_tag"]
                ),
                "required_for_release": True,
            }

        normalized_mappings = tuple(
            _normalized_item_equipment_mapping(item) for item in mappings
        )
        if not normalized_mappings:
            actual_value: Any = "missing"
        elif len(normalized_mappings) == 1:
            actual_value = normalized_mappings[0]
        else:
            actual_value = list(normalized_mappings)

        item_evidence = _bom_item_equipment_reciprocity_evidence(
            manifest=manifest,
            item_id=item_id,
            bom_record=bom_record,
            mappings=mappings,
            expected_value=expected_value,
        )
        evidence.extend(item_evidence)

        reciprocal = (
            bom_record is not None
            and len(normalized_mappings) == 1
            and normalized_mappings[0] == expected_value
        )
        if reciprocal:
            continue

        findings.append(
            _bom_item_equipment_reciprocity_finding(
                package_id=package_id,
                item_id=item_id,
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=item_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Checked {len(item_ids)} authoritative or declared BOM "
                f"item(s) and found {len(findings)} non-reciprocal "
                "item/equipment mapping(s)."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(item_ids)} release-required BOM item(s) have one "
            "reciprocal manifest item/equipment mapping."
        ),
        evidence=tuple(evidence),
    )


def _bom_equipment_drawing_presence_check(
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
    metadata_records = sources.records_of_type("drawing_metadata_record")

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for bom_record in bom_records:
        item_id = _normalize_identifier(bom_record.values["item_id"])
        equipment_tag = _normalize_identifier(
            bom_record.values["equipment_tag"]
        )
        matching_record_ids = tuple(
            sorted(
                _normalize_identifier(record.values["record_id"])
                for record in metadata_records
                if equipment_tag
                in {
                    _normalize_identifier(tag)
                    for tag in record.values["equipment_tags"]
                }
            )
        )
        item_evidence = (
            bom_record.field_locator(
                "equipment_tag",
                normalized_value=equipment_tag,
            ),
            _drawing_metadata_equipment_tag_search_locator(
                metadata_records=metadata_records,
                equipment_tag=equipment_tag,
                matching_record_ids=matching_record_ids,
            ),
        )
        evidence.extend(item_evidence)
        if matching_record_ids:
            continue
        findings.append(
            _bom_equipment_drawing_reference_missing_finding(
                package_id=package_id,
                item_id=item_id,
                equipment_tag=equipment_tag,
                evidence=item_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Checked {len(bom_records)} release-required BOM equipment "
                f"tag(s) and found {len(findings)} without drawing-metadata "
                "representation."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(bom_records)} release-required BOM equipment tag(s) "
            "appear in drawing metadata."
        ),
        evidence=tuple(evidence),
    )


def _required_item_equipment_mappings(
    manifest: LoadedPackageManifest,
) -> dict[str, tuple[tuple[int, Mapping[str, Any]], ...]]:
    relationships = manifest.manifest.get("relationship_declarations")
    if not isinstance(relationships, list):
        return {}

    grouped: dict[str, list[tuple[int, Mapping[str, Any]]]] = {}
    for index, item in enumerate(relationships):
        if (
            not isinstance(item, Mapping)
            or item.get("relationship_type") != "item_to_equipment"
            or item.get("required_for_release") is not True
            or not isinstance(item.get("source"), Mapping)
            or item["source"].get("identifier_type") != "item_id"
            or not isinstance(item["source"].get("identifier"), str)
            or not isinstance(item.get("target"), Mapping)
            or item["target"].get("identifier_type") != "equipment_tag"
            or not isinstance(item["target"].get("identifier"), str)
        ):
            continue
        item_id = _normalize_identifier(item["source"]["identifier"])
        grouped.setdefault(item_id, []).append((index, item))

    return {
        item_id: tuple(sorted(items, key=_relationship_id))
        for item_id, items in grouped.items()
    }


def _normalized_item_equipment_mapping(
    item: tuple[int, Mapping[str, Any]],
) -> dict[str, Any]:
    relationship = item[1]
    source = relationship["source"]
    target = relationship["target"]
    return {
        "item_id": _normalize_identifier(source.get("identifier")),
        "equipment_tag": _normalize_identifier(target.get("identifier")),
        "required_for_release": relationship.get("required_for_release"),
    }


def _bom_item_equipment_reciprocity_evidence(
    *,
    manifest: LoadedPackageManifest,
    item_id: str,
    bom_record: StructuredSourceRecord | None,
    mappings: tuple[tuple[int, Mapping[str, Any]], ...],
    expected_value: Any,
) -> tuple[EvidenceLocator, ...]:
    locators: list[EvidenceLocator] = []
    if bom_record is not None:
        locators.extend(
            (
                bom_record.field_locator(
                    "item_id",
                    normalized_value=item_id,
                ),
                bom_record.field_locator(
                    "equipment_tag",
                    normalized_value=expected_value["equipment_tag"],
                ),
            )
        )

    if mappings:
        locators.extend(
            _manifest_item_locator(
                "relationship_declarations",
                item,
                normalized_value=_normalized_item_equipment_mapping(item),
            )
            for item in mappings
        )
    else:
        locators.append(
            _manifest_collection_search_locator(
                manifest,
                "relationship_declarations",
                expected_value={
                    "relationship_type": "item_to_equipment",
                    "item_id": item_id,
                    "required_for_release": True,
                },
            )
        )
    return tuple(locators)


def _drawing_metadata_equipment_tag_search_locator(
    *,
    metadata_records: tuple[StructuredSourceRecord, ...],
    equipment_tag: str,
    matching_record_ids: tuple[str, ...],
) -> EvidenceLocator:
    ordered_records = sorted(
        metadata_records,
        key=lambda record: _normalize_identifier(record.values["record_id"]),
    )
    return EvidenceLocator(
        source_type="drawing_metadata",
        source_file="inputs/drawing_metadata.json",
        format="json",
        json_pointer="/records",
        property_name="equipment_tags",
        original_value=[
            {
                "record_id": record.original_values["record_id"],
                "equipment_tags": record.original_values["equipment_tags"],
            }
            for record in ordered_records
        ],
        normalized_value={
            "equipment_tag": equipment_tag,
            "matching_record_ids": list(matching_record_ids),
            "searched_record_count": len(metadata_records),
        },
    )


def _bom_item_equipment_reciprocity_finding(
    *,
    package_id: str,
    item_id: str,
    expected_value: Any,
    actual_value: Any,
    evidence: tuple[EvidenceLocator, ...],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE,
        "authority_rule_id": BOM_EQUIPMENT_AUTHORITY_RULE_ID,
        "item_id": item_id,
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
        check_id=BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=BOM_EQUIPMENT_AUTHORITY_RULE_ID,
        message=(
            f"BOM item {item_id} is not reciprocal with the package manifest "
            "item-to-equipment declarations."
        ),
        affected_identifiers=(item_id,),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="mechanical_engineering",
        evidence=evidence,
    )


def _bom_equipment_drawing_reference_missing_finding(
    *,
    package_id: str,
    item_id: str,
    equipment_tag: str,
    evidence: tuple[EvidenceLocator, EvidenceLocator],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    expected_value = "at least one drawing_metadata equipment_tags reference"
    actual_value = "missing"
    semantic = {
        "package_id": package_id,
        "check_id": BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE,
        "authority_rule_id": BOM_EQUIPMENT_AUTHORITY_RULE_ID,
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
        check_id=BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=BOM_EQUIPMENT_AUTHORITY_RULE_ID,
        message=(
            f"Release-required BOM equipment tag {equipment_tag} for "
            f"{item_id} does not appear in drawing metadata."
        ),
        affected_identifiers=(item_id, equipment_tag),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="mechanical_engineering",
        evidence=evidence,
    )
