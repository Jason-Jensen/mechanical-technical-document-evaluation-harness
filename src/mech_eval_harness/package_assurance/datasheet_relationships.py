"""Datasheet-domain package relationship checks."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from mech_eval_harness.package_assurance._relationship_common import (
    RELATIONSHIP_CHECK_VERSION,
    _normalize_identifier,
    _skipped_check,
)
from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
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
