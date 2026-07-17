"""Structured package-assurance contracts for the v0.3.0 pilot."""

from mech_eval_harness.package_assurance.manifest import (
    LoadedPackageManifest,
    PackageManifestError,
    load_package_manifest,
)
from mech_eval_harness.package_assurance.gates import (
    PACKAGE_GATE_ORDER,
    PACKAGE_GATE_VERSION,
    run_package_gates,
)
from mech_eval_harness.package_assurance.models import (
    EvidenceLocator,
    PackageGateEvaluation,
    PackageGateFinding,
    PackageGateResult,
    PackageRelationshipEvaluation,
    RelationshipCheckResult,
    RelationshipFinding,
)
from mech_eval_harness.package_assurance.relationships import (
    DRAWING_METADATA_MISSING_CODE,
    DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID,
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    DRAWING_REVISION_AUTHORITY_RULE_ID,
    DRAWING_REVISION_MISMATCH_CODE,
    RELATIONSHIP_CHECK_ORDER,
    RELATIONSHIP_CHECK_VERSION,
    run_package_relationships,
)

__all__ = [
    "LoadedPackageManifest",
    "PackageManifestError",
    "EvidenceLocator",
    "PackageGateEvaluation",
    "PackageGateFinding",
    "PackageGateResult",
    "PackageRelationshipEvaluation",
    "RelationshipCheckResult",
    "RelationshipFinding",
    "PACKAGE_GATE_ORDER",
    "PACKAGE_GATE_VERSION",
    "DRAWING_METADATA_MISSING_CODE",
    "DRAWING_REGISTER_METADATA_PRESENCE_CHECK_ID",
    "DRAWING_REGISTER_METADATA_REVISION_CHECK_ID",
    "DRAWING_REVISION_AUTHORITY_RULE_ID",
    "DRAWING_REVISION_MISMATCH_CODE",
    "RELATIONSHIP_CHECK_ORDER",
    "RELATIONSHIP_CHECK_VERSION",
    "load_package_manifest",
    "run_package_gates",
    "run_package_relationships",
]
