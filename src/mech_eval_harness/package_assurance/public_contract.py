"""Producer-visible validation of the accepted package authoring contract."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance.gates import run_package_gates
from mech_eval_harness.package_assurance.manifest import PACKAGE_MANIFEST_FILENAME
from mech_eval_harness.package_assurance.models import PackageGateEvaluation


PUBLIC_CONTRACT_VALIDATOR_ID = "VAL-PKG-AUTHORING-001"
PUBLIC_CONTRACT_VALIDATOR_VERSION = "0.3.0"


@dataclass(frozen=True)
class PublicContractGateResult:
    """One redacted mandatory-gate result suitable for authoring handoff."""

    gate_id: str
    status: str
    finding_codes: tuple[str, ...]
    blocked_by: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "gate_id": self.gate_id,
            "status": self.status,
            "finding_codes": list(self.finding_codes),
            "blocked_by": list(self.blocked_by),
        }


@dataclass(frozen=True)
class PackageContractValidation:
    """Deterministic public-contract validation without relationship execution."""

    package_id: str | None
    gates: tuple[PublicContractGateResult, ...]

    @property
    def public_contract_complete(self) -> bool:
        return bool(self.gates) and all(gate.status == "passed" for gate in self.gates)

    @property
    def failed_gate_ids(self) -> tuple[str, ...]:
        return tuple(gate.gate_id for gate in self.gates if gate.status == "failed")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": PUBLIC_CONTRACT_VALIDATOR_VERSION,
            "validator_id": PUBLIC_CONTRACT_VALIDATOR_ID,
            "validator_version": PUBLIC_CONTRACT_VALIDATOR_VERSION,
            "package_id": self.package_id,
            "status": "passed" if self.public_contract_complete else "failed",
            "public_contract_complete": self.public_contract_complete,
            "relationships_executed": False,
            "failed_gate_ids": list(self.failed_gate_ids),
            "gate_results": [gate.to_dict() for gate in self.gates],
            "claim_boundary": (
                "Validates producer-visible package authoring invariants only; "
                "it does not prove relationship accuracy, engineering correctness, "
                "or release readiness."
            ),
        }


def validate_package_contract(
    *,
    repository_root: Path,
    package_root: Path,
) -> PackageContractValidation:
    """Validate every public mandatory-gate invariant before benchmark freeze."""

    evaluation = run_package_gates(
        repository_root.resolve(),
        Path(PACKAGE_MANIFEST_FILENAME),
        allowed_package_root=package_root.resolve(),
    )
    return _public_validation(evaluation)


def _public_validation(
    evaluation: PackageGateEvaluation,
) -> PackageContractValidation:
    return PackageContractValidation(
        package_id=evaluation.package_id,
        gates=tuple(
            PublicContractGateResult(
                gate_id=gate.gate_id,
                status=gate.status,
                finding_codes=tuple(finding.code for finding in gate.findings),
                blocked_by=gate.blocked_by,
            )
            for gate in evaluation.gates
        ),
    )
