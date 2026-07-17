"""Deterministic P2.2 cross-document relationship checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from typing import Any, Mapping

from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
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
DRAWING_REVISION_MISMATCH_CODE = "DRAWING_REVISION_MISMATCH"
DRAWING_METADATA_MISSING_CODE = "DRAWING_METADATA_MISSING"
DRAWING_REVISION_AUTHORITY_RULE_ID = "AUTH-DWG-001"

RELATIONSHIP_CHECK_ORDER = (
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
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
    return PackageRelationshipEvaluation(
        package_id=gate_evaluation.package_id,
        checks=(revision_check, presence_check),
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
