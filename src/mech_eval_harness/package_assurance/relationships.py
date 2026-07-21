"""Deterministic package-assurance cross-document relationship checks."""

from __future__ import annotations

from mech_eval_harness.package_assurance._relationship_common import (
    RELATIONSHIP_CHECK_VERSION,
    _skipped_check,
)
from mech_eval_harness.package_assurance.bom_relationships import (
    BOM_EQUIPMENT_AUTHORITY_RULE_ID,
    BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE,
    BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE,
    _evaluate_bom_equipment_drawing_presence,
    _evaluate_bom_item_equipment_manifest_reciprocity,
)
from mech_eval_harness.package_assurance.drawing_relationships import (
    DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE,
    DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID,
    DRAWING_FILE_REFERENCE_MISMATCH_CODE,
    DRAWING_METADATA_MISSING_CODE,
    DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    DRAWING_REGISTER_AUTHORITY_MISSING_CODE,
    DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    DRAWING_REVISION_AUTHORITY_RULE_ID,
    DRAWING_REVISION_MISMATCH_CODE,
    _drawing_file_reference_authority_rule,
    _drawing_metadata_register_authority_check,
    _drawing_register_manifest_file_reciprocity_check,
    _drawing_register_metadata_file_reference_check,
    _drawing_register_metadata_presence_check,
    _drawing_register_metadata_revision_check,
    _drawing_revision_authority_rule,
)
from mech_eval_harness.package_assurance.datasheet_relationships import (
    EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE,
    EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
    EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID,
    _evaluate_equipment_datasheet_authority_presence,
)
from mech_eval_harness.package_assurance.gates import AUTHORITY_GATE_ID
from mech_eval_harness.package_assurance.models import (
    PackageGateEvaluation,
    PackageRelationshipEvaluation,
)


__all__ = [
    "BOM_EQUIPMENT_AUTHORITY_RULE_ID",
    "BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID",
    "BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING_CODE",
    "BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID",
    "BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED_CODE",
    "DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED_CODE",
    "DRAWING_FILE_REFERENCE_AUTHORITY_RULE_ID",
    "DRAWING_FILE_REFERENCE_MISMATCH_CODE",
    "DRAWING_METADATA_MISSING_CODE",
    "DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID",
    "DRAWING_REGISTER_AUTHORITY_MISSING_CODE",
    "DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID",
    "DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID",
    "DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID",
    "DRAWING_REGISTER_METADATA_REVISION_CHECK_ID",
    "DRAWING_REVISION_AUTHORITY_RULE_ID",
    "DRAWING_REVISION_MISMATCH_CODE",
    "EQUIPMENT_DATASHEET_AUTHORITY_MISSING_CODE",
    "EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID",
    "EQUIPMENT_DATASHEET_AUTHORITY_RULE_ID",
    "RELATIONSHIP_CHECK_ORDER",
    "RELATIONSHIP_CHECK_VERSION",
    "run_package_relationships",
]


RELATIONSHIP_CHECK_ORDER = (
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    DRAWING_METADATA_REGISTER_AUTHORITY_CHECK_ID,
    DRAWING_REGISTER_METADATA_FILE_REFERENCE_CHECK_ID,
    DRAWING_REGISTER_MANIFEST_FILE_RECIPROCITY_CHECK_ID,
    BOM_ITEM_EQUIPMENT_MANIFEST_RECIPROCITY_CHECK_ID,
    BOM_EQUIPMENT_DRAWING_PRESENCE_CHECK_ID,
    EQUIPMENT_DATASHEET_AUTHORITY_PRESENCE_CHECK_ID,
)


def run_package_relationships(
    gate_evaluation: PackageGateEvaluation,
) -> PackageRelationshipEvaluation:
    """Run accepted relationship checks after the complete P2.1 gate boundary."""

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
        drawing_checks = tuple(
            _skipped_check(
                check_id=check_id,
                blocked_by=(AUTHORITY_GATE_ID,),
                summary=(
                    "Skipped because the accepted AUTH-DWG-001 drawing "
                    "revision authority rule is unavailable."
                ),
            )
            for check_id in RELATIONSHIP_CHECK_ORDER[:5]
        )
        bom_reciprocity_check = (
            _evaluate_bom_item_equipment_manifest_reciprocity(
                package_id=gate_evaluation.package_id,
                sources=gate_evaluation.sources,
                manifest=gate_evaluation.manifest,
            )
        )
        bom_drawing_presence_check = _evaluate_bom_equipment_drawing_presence(
            package_id=gate_evaluation.package_id,
            sources=gate_evaluation.sources,
        )
        datasheet_authority_presence_check = (
            _evaluate_equipment_datasheet_authority_presence(
                package_id=gate_evaluation.package_id,
                sources=gate_evaluation.sources,
            )
        )
        return PackageRelationshipEvaluation(
            package_id=gate_evaluation.package_id,
            checks=(
                *drawing_checks,
                bom_reciprocity_check,
                bom_drawing_presence_check,
                datasheet_authority_presence_check,
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
    bom_reciprocity_check = (
        _evaluate_bom_item_equipment_manifest_reciprocity(
            package_id=gate_evaluation.package_id,
            sources=gate_evaluation.sources,
            manifest=gate_evaluation.manifest,
        )
    )
    bom_drawing_presence_check = _evaluate_bom_equipment_drawing_presence(
        package_id=gate_evaluation.package_id,
        sources=gate_evaluation.sources,
    )
    datasheet_authority_presence_check = (
        _evaluate_equipment_datasheet_authority_presence(
            package_id=gate_evaluation.package_id,
            sources=gate_evaluation.sources,
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
            bom_reciprocity_check,
            bom_drawing_presence_check,
            datasheet_authority_presence_check,
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
