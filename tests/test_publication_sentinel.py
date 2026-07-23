from pathlib import Path

import pytest

from scripts.run_package_assurance_publication_sentinel import (
    TARGET_RUNS_PATH_LENGTH,
    PublicationSentinelError,
    _bundle_root_for_target,
)


def test_bundle_root_uses_requested_stress_length_when_host_root_fits() -> None:
    bundle_root = _bundle_root_for_target(
        Path("evidence"),
        target_runs_path_length=TARGET_RUNS_PATH_LENGTH,
    )

    assert (
        len(str(bundle_root / "runtime" / "runs"))
        == TARGET_RUNS_PATH_LENGTH
    )


def test_bundle_root_adapts_upward_for_long_host_root() -> None:
    evidence_root = Path("e" * TARGET_RUNS_PATH_LENGTH)
    fixed_runs_dir = evidence_root / "bundle-" / "runtime" / "runs"

    bundle_root = _bundle_root_for_target(
        evidence_root,
        target_runs_path_length=TARGET_RUNS_PATH_LENGTH,
    )

    assert len(str(bundle_root / "runtime" / "runs")) == (
        len(str(fixed_runs_dir)) + 8
    )


def test_bundle_root_rejects_weaker_stress_length() -> None:
    with pytest.raises(
        PublicationSentinelError,
        match="below the minimum publication stress length",
    ):
        _bundle_root_for_target(
            Path("evidence"),
            target_runs_path_length=TARGET_RUNS_PATH_LENGTH - 1,
        )
