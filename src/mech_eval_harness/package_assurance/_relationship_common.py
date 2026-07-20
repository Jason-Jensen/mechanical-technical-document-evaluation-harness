"""Shared primitives for deterministic relationship checks."""

from __future__ import annotations

from typing import Any, Mapping

from mech_eval_harness.package_assurance.manifest import (
    PACKAGE_MANIFEST_FILENAME,
    LoadedPackageManifest,
)
from mech_eval_harness.package_assurance.models import (
    EvidenceLocator,
    RelationshipCheckResult,
)


RELATIONSHIP_CHECK_VERSION = "0.3.0"

def _normalize_identifier(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("P2.1 accepted identifiers must be strings")
    return value.strip()


def _normalize_revision(value: Any) -> str:
    if not isinstance(value, str):
        raise TypeError("P2.1 accepted drawing revisions must be strings")
    return value.strip()


def _relationship_id(item: tuple[int, Mapping[str, Any]]) -> str:
    return str(item[1].get("relationship_id", ""))


def _manifest_item_locator(
    collection_name: str,
    item: tuple[int, Mapping[str, Any]],
    *,
    normalized_value: Any,
) -> EvidenceLocator:
    index, document = item
    record_id = document.get("relationship_id") or document.get("document_id")
    return EvidenceLocator(
        source_type="package_manifest",
        source_file=PACKAGE_MANIFEST_FILENAME,
        format="json",
        json_pointer=f"/{collection_name}/{index}",
        record_id=str(record_id) if record_id is not None else None,
        property_name=collection_name,
        original_value=dict(document),
        normalized_value=normalized_value,
    )


def _manifest_collection_search_locator(
    manifest: LoadedPackageManifest,
    collection_name: str,
    *,
    expected_value: Mapping[str, Any],
) -> EvidenceLocator:
    collection = manifest.manifest.get(collection_name)
    original_value = collection if isinstance(collection, list) else []
    return EvidenceLocator(
        source_type="package_manifest",
        source_file=PACKAGE_MANIFEST_FILENAME,
        format="json",
        json_pointer=f"/{collection_name}",
        property_name=collection_name,
        original_value=original_value,
        normalized_value={
            "expected": dict(expected_value),
            "searched_count": len(original_value),
        },
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
