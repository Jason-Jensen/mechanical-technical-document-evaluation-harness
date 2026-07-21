"""Specification-domain package relationship checks."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from mech_eval_harness.package_assurance._relationship_common import (
    RELATIONSHIP_CHECK_VERSION,
    _normalize_identifier,
    _normalize_revision,
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


SPECIFICATION_REVISION_HISTORY_CHECK_ID = "specification_revision_history"
SPECIFICATION_REVISION_MISMATCH_CODE = "SPECIFICATION_REVISION_MISMATCH"
SPECIFICATION_REVISION_AUTHORITY_RULE_ID = "AUTH-SPEC-003"


def _specification_revision_authority_rule(
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
        if rule.get("rule_id") != SPECIFICATION_REVISION_AUTHORITY_RULE_ID:
            continue
        if (
            rule.get("field") == "specification.current_revision"
            and rule.get("authoritative_source") == "datasheet_spec_metadata"
            and rule.get("secondary_sources") == ["revision_history"]
            and rule.get("agreement_rule")
            == (
                "specification revision must match the declared current "
                "metadata and revision history"
            )
            and rule.get("normalization_profile")
            == "canonical_identifier_v1"
            and rule.get("revision_scheme") == "spec_explicit_sequence_v1"
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


def _evaluate_specification_revision_history(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    if _specification_revision_authority_rule(sources) is None:
        return _skipped_check(
            check_id=SPECIFICATION_REVISION_HISTORY_CHECK_ID,
            blocked_by=(AUTHORITY_GATE_ID,),
            summary=(
                "Skipped because the accepted AUTH-SPEC-003 specification "
                "revision authority rule is unavailable."
            ),
        )
    return _specification_revision_history_check(
        package_id=package_id,
        sources=sources,
    )


def _specification_revision_history_check(
    *,
    package_id: str,
    sources: LoadedStructuredSources,
) -> RelationshipCheckResult:
    specification_records = tuple(
        sorted(
            (
                record
                for record in sources.records_of_type("specification_record")
                if record.values["required_for_release"] is True
            ),
            key=lambda record: (
                _normalize_identifier(record.values["specification_id"]),
                _normalize_identifier(record.values["record_id"]),
            ),
        )
    )
    history_records = tuple(
        sorted(
            sources.records_of_type("revision_history_record"),
            key=_revision_history_sort_key,
        )
    )
    current_by_specification = _current_history_by_specification(history_records)

    findings: list[RelationshipFinding] = []
    evidence: list[EvidenceLocator] = []
    for specification_record in specification_records:
        specification_id = _normalize_identifier(
            specification_record.values["specification_id"]
        )
        expected_value = _normalize_revision(
            specification_record.values["revision_id"]
        )
        current_records = current_by_specification.get(specification_id, ())
        actual_value = _current_revision_value(current_records)
        comparison_evidence = _specification_revision_evidence(
            specification_record=specification_record,
            specification_id=specification_id,
            expected_value=expected_value,
            history_records=history_records,
            current_records=current_records,
        )
        evidence.extend(comparison_evidence)
        if len(current_records) == 1 and actual_value == expected_value:
            continue
        findings.append(
            _specification_revision_mismatch_finding(
                package_id=package_id,
                specification_id=specification_id,
                expected_value=expected_value,
                actual_value=actual_value,
                evidence=comparison_evidence,
            )
        )

    if findings:
        return RelationshipCheckResult(
            check_id=SPECIFICATION_REVISION_HISTORY_CHECK_ID,
            check_version=RELATIONSHIP_CHECK_VERSION,
            status="failed",
            summary=(
                f"Compared {len(specification_records)} release-required "
                f"specification revision(s) and found {len(findings)} "
                "missing, ambiguous, or mismatched current history record(s)."
            ),
            findings=tuple(findings),
            evidence=tuple(evidence),
        )

    return RelationshipCheckResult(
        check_id=SPECIFICATION_REVISION_HISTORY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        status="passed",
        summary=(
            f"All {len(specification_records)} release-required specification "
            "revision(s) match exactly one current revision-history record."
        ),
        evidence=tuple(evidence),
    )


def _revision_history_sort_key(
    record: StructuredSourceRecord,
) -> tuple[str, str, int, str, str]:
    return (
        _normalize_identifier(record.values["owner_identifier_type"]),
        _normalize_identifier(record.values["owner_identifier"]),
        record.values["sequence_index"],
        _normalize_identifier(record.values["document_id"]),
        _normalize_identifier(record.values["revision_record_id"]),
    )


def _current_history_by_specification(
    history_records: tuple[StructuredSourceRecord, ...],
) -> dict[str, tuple[StructuredSourceRecord, ...]]:
    grouped: dict[str, list[StructuredSourceRecord]] = {}
    for record in history_records:
        if (
            record.values["owner_identifier_type"] != "specification_id"
            or record.values["revision_status"] != "current"
        ):
            continue
        specification_id = _normalize_identifier(record.values["owner_identifier"])
        grouped.setdefault(specification_id, []).append(record)
    return {
        specification_id: tuple(records)
        for specification_id, records in grouped.items()
    }


def _current_revision_value(
    current_records: tuple[StructuredSourceRecord, ...],
) -> Any:
    if not current_records:
        return "missing"
    if len(current_records) == 1:
        return _normalize_revision(current_records[0].values["revision_id"])
    return [_normalized_history_record(record) for record in current_records]


def _normalized_history_record(record: StructuredSourceRecord) -> dict[str, str]:
    return {
        "revision_record_id": _normalize_identifier(
            record.values["revision_record_id"]
        ),
        "document_id": _normalize_identifier(record.values["document_id"]),
        "owner_identifier_type": _normalize_identifier(
            record.values["owner_identifier_type"]
        ),
        "specification_id": _normalize_identifier(
            record.values["owner_identifier"]
        ),
        "revision_id": _normalize_revision(record.values["revision_id"]),
        "revision_status": _normalize_identifier(record.values["revision_status"]),
    }


def _specification_revision_evidence(
    *,
    specification_record: StructuredSourceRecord,
    specification_id: str,
    expected_value: str,
    history_records: tuple[StructuredSourceRecord, ...],
    current_records: tuple[StructuredSourceRecord, ...],
) -> tuple[EvidenceLocator, ...]:
    locators = [
        specification_record.field_locator(
            "specification_id",
            normalized_value=specification_id,
        ),
        specification_record.field_locator(
            "revision_id",
            normalized_value=expected_value,
        ),
    ]
    if not current_records:
        locators.append(
            _revision_history_search_locator(
                history_records=history_records,
                specification_id=specification_id,
                current_records=current_records,
            )
        )
        return tuple(locators)

    for record in current_records:
        locators.extend(
            (
                record.field_locator(
                    "owner_identifier",
                    normalized_value=specification_id,
                ),
                record.field_locator(
                    "revision_status",
                    normalized_value="current",
                ),
                record.field_locator(
                    "revision_id",
                    normalized_value=_normalize_revision(
                        record.values["revision_id"]
                    ),
                ),
            )
        )
    return tuple(locators)


def _revision_history_search_locator(
    *,
    history_records: tuple[StructuredSourceRecord, ...],
    specification_id: str,
    current_records: tuple[StructuredSourceRecord, ...],
) -> EvidenceLocator:
    specification_history = tuple(
        record
        for record in history_records
        if record.values["owner_identifier_type"] == "specification_id"
    )
    return EvidenceLocator(
        source_type="revision_history",
        source_file="inputs/revision_history.csv",
        format="csv",
        row_number=1,
        header_row_number=1,
        column_name="owner_identifier",
        original_value=[
            {
                "revision_record_id": record.original_values["revision_record_id"],
                "document_id": record.original_values["document_id"],
                "owner_identifier_type": record.original_values[
                    "owner_identifier_type"
                ],
                "owner_identifier": record.original_values["owner_identifier"],
                "revision_id": record.original_values["revision_id"],
                "revision_status": record.original_values["revision_status"],
            }
            for record in specification_history
        ],
        normalized_value={
            "specification_id": specification_id,
            "matching_current_record_ids": [
                _normalize_identifier(record.values["revision_record_id"])
                for record in current_records
            ],
            "current_record_count": len(current_records),
            "searched_record_count": len(specification_history),
        },
    )


def _specification_revision_mismatch_finding(
    *,
    package_id: str,
    specification_id: str,
    expected_value: str,
    actual_value: Any,
    evidence: tuple[EvidenceLocator, ...],
) -> RelationshipFinding:
    result_state = "automatic_fail"
    semantic = {
        "package_id": package_id,
        "check_id": SPECIFICATION_REVISION_HISTORY_CHECK_ID,
        "check_version": RELATIONSHIP_CHECK_VERSION,
        "code": SPECIFICATION_REVISION_MISMATCH_CODE,
        "authority_rule_id": SPECIFICATION_REVISION_AUTHORITY_RULE_ID,
        "specification_id": specification_id,
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
        check_id=SPECIFICATION_REVISION_HISTORY_CHECK_ID,
        check_version=RELATIONSHIP_CHECK_VERSION,
        package_id=package_id,
        code=SPECIFICATION_REVISION_MISMATCH_CODE,
        result_state=result_state,
        severity="high",
        release_hold=True,
        authority_rule_id=SPECIFICATION_REVISION_AUTHORITY_RULE_ID,
        message=(
            f"Specification {specification_id} authoritative revision "
            f"{expected_value} does not agree with exactly one current "
            "revision-history record."
        ),
        affected_identifiers=(specification_id,),
        expected_value=expected_value,
        actual_value=actual_value,
        review_owner="document_control",
        evidence=evidence,
    )
