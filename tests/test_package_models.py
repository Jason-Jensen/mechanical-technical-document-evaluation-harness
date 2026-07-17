from __future__ import annotations

import pytest

from mech_eval_harness.package_assurance.models import EvidenceLocator


@pytest.mark.parametrize(
    "source_file",
    [
        "/absolute/source.json",
        "../outside/source.json",
        "inputs/../outside.json",
        "C:/absolute/source.json",
        "C:relative/source.json",
        r"C:\absolute\source.json",
        r"\\server\share\source.json",
        r"inputs\source.json",
    ],
)
def test_evidence_locator_rejects_non_package_relative_paths(
    source_file: str,
) -> None:
    with pytest.raises(ValueError, match="must be package-relative"):
        EvidenceLocator(
            source_type="drawing_metadata",
            source_file=source_file,
            format="json",
        )


def test_evidence_locator_accepts_posix_package_relative_path() -> None:
    locator = EvidenceLocator(
        source_type="drawing_metadata",
        source_file="inputs/drawing_metadata.json",
        format="json",
    )

    assert locator.source_file == "inputs/drawing_metadata.json"
