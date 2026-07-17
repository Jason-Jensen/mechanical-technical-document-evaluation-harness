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
)

__all__ = [
    "LoadedPackageManifest",
    "PackageManifestError",
    "EvidenceLocator",
    "PackageGateEvaluation",
    "PackageGateFinding",
    "PackageGateResult",
    "PACKAGE_GATE_ORDER",
    "PACKAGE_GATE_VERSION",
    "load_package_manifest",
    "run_package_gates",
]
