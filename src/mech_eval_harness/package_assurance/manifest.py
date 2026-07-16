"""Load and validate the v0.3.0 package-manifest boundary."""

from __future__ import annotations

from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from mech_eval_harness.validator import RepositoryValidationError, load_json


PACKAGE_MANIFEST_SCHEMA_FILE = "schemas/package_manifest.schema.json"
PACKAGE_MANIFEST_FILENAME = "package_manifest.json"
SUPPORTED_PACKAGE_MANIFEST_VERSIONS = frozenset({"0.3.0"})

REQUIRED_SOURCE_DECLARATIONS = {
    "package_manifest": ("package_manifest.json", "json"),
    "drawing_register": ("inputs/drawing_register.csv", "csv"),
    "drawing_metadata": ("inputs/drawing_metadata.json", "json"),
    "bom_or_equipment_list": ("inputs/bom_or_equipment_list.csv", "csv"),
    "datasheet_spec_metadata": ("inputs/datasheet_spec_metadata.json", "json"),
    "revision_history": ("inputs/revision_history.csv", "csv"),
    "authority_map": ("authority/authority_map.json", "json"),
}


class PackageManifestError(RepositoryValidationError):
    """Raised when a package manifest violates the accepted v0.3.0 contract."""


@dataclass(frozen=True)
class LoadedPackageManifest:
    """Validated declarations and resolved paths from one package manifest."""

    manifest: dict[str, Any]
    manifest_path: Path
    package_root: Path
    source_paths: dict[str, Path]
    authority_map_path: Path
    allowed_file_roots: tuple[Path, ...]
    file_reference_paths: dict[str, Path]

    @property
    def package_id(self) -> str:
        return self.manifest["package_id"]


def load_package_manifest(
    repository_root: Path,
    manifest_path: Path,
    *,
    allowed_package_root: Path,
    supported_schema_versions: Collection[str] = SUPPORTED_PACKAGE_MANIFEST_VERSIONS,
) -> LoadedPackageManifest:
    """Load one package manifest without parsing its declared source records."""

    repository_root = repository_root.resolve()
    package_root = allowed_package_root.resolve()
    if not package_root.is_dir():
        raise PackageManifestError(f"Allowed package root not found: {package_root}")

    requested_manifest_path = Path(manifest_path)
    if not requested_manifest_path.is_absolute():
        requested_manifest_path = package_root / requested_manifest_path

    expected_manifest_path = package_root / PACKAGE_MANIFEST_FILENAME
    if requested_manifest_path.absolute() != expected_manifest_path.absolute():
        raise PackageManifestError(
            "Package manifest must be located at the allowed package root as "
            f"{PACKAGE_MANIFEST_FILENAME}: {requested_manifest_path}"
        )

    manifest_path = requested_manifest_path.resolve()
    if not _is_relative_to(manifest_path, package_root):
        raise PackageManifestError(
            f"Package manifest resolves outside the allowed package root: {manifest_path}"
        )

    supported_versions = frozenset(supported_schema_versions)
    if not supported_versions:
        raise ValueError("supported_schema_versions must not be empty")

    manifest = _load_manifest_json(manifest_path)
    schema_version = manifest.get("schema_version")
    if isinstance(schema_version, str) and schema_version not in supported_versions:
        supported = ", ".join(sorted(supported_versions))
        raise PackageManifestError(
            f"Unsupported package manifest schema_version: {schema_version}; "
            f"supported versions: {supported}"
        )

    schema = load_json(repository_root / PACKAGE_MANIFEST_SCHEMA_FILE)
    _validate_schema(manifest, schema, _display_path(repository_root, manifest_path))

    source_paths = _validate_source_inventory(manifest, package_root)
    authority_map_path = _resolve_declared_path(
        package_root,
        manifest["authority_map_ref"],
        "authority_map_ref",
    )
    if authority_map_path != source_paths["authority_map"]:
        raise PackageManifestError(
            "authority_map_ref must match the authority_map source declaration"
        )

    allowed_file_roots = tuple(
        _resolve_declared_path(package_root, path, "allowed file-reference root")
        for path in manifest["allowed_file_reference_roots"]
    )
    file_reference_paths = _validate_file_references(
        manifest["file_references"],
        package_root,
        allowed_file_roots,
    )
    _validate_document_inventory(manifest["document_inventory"], file_reference_paths)
    _validate_relationships(
        manifest["relationship_declarations"],
        manifest["document_inventory"],
        file_reference_paths,
    )

    return LoadedPackageManifest(
        manifest=manifest,
        manifest_path=manifest_path,
        package_root=package_root,
        source_paths=source_paths,
        authority_map_path=authority_map_path,
        allowed_file_roots=allowed_file_roots,
        file_reference_paths=file_reference_paths,
    )


def _load_manifest_json(path: Path) -> dict[str, Any]:
    try:
        return load_json(path)
    except RepositoryValidationError as exc:
        raise PackageManifestError(f"Package manifest error: {exc}") from exc
    except (OSError, UnicodeError) as exc:
        raise PackageManifestError(
            f"Package manifest could not be read: {path}: {exc}"
        ) from exc


def _validate_schema(data: dict[str, Any], schema: dict[str, Any], label: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if not errors:
        return

    messages: list[str] = []
    for error in errors:
        location = ".".join(str(part) for part in error.path) or "<root>"
        messages.append(f"{label}:{location}: {error.message}")
    raise PackageManifestError("; ".join(messages))


def _display_path(root: Path, path: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _resolve_declared_path(root: Path, value: str, label: str) -> Path:
    posix_path = PurePosixPath(value)
    windows_path = PureWindowsPath(value)
    raw_segments = value.split("/")
    if (
        posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
        or "\\" in value
        or any(segment in {"", ".", ".."} for segment in raw_segments)
    ):
        raise PackageManifestError(f"Invalid package-relative path for {label}: {value}")

    candidate = (root / Path(*posix_path.parts)).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise PackageManifestError(
            f"Declared path escapes allowed package root for {label}: {value}"
        ) from exc
    return candidate


def _require_unique(items: list[dict[str, Any]], key: str, label: str) -> None:
    seen: set[str] = set()
    for item in items:
        value = item[key]
        if value in seen:
            raise PackageManifestError(f"Duplicate {label}: {value}")
        seen.add(value)


def _validate_source_inventory(
    manifest: dict[str, Any],
    package_root: Path,
) -> dict[str, Path]:
    sources = manifest["source_inventory"]
    _require_unique(sources, "source_type", "source declaration")
    _require_unique(sources, "path", "source path")

    declared_types = {source["source_type"] for source in sources}
    required_types = set(REQUIRED_SOURCE_DECLARATIONS)
    if declared_types != required_types:
        missing = sorted(required_types - declared_types)
        unexpected = sorted(declared_types - required_types)
        raise PackageManifestError(
            "Source inventory must declare exactly the mandatory v0.3.0 sources; "
            f"missing={missing}, unexpected={unexpected}"
        )

    resolved: dict[str, Path] = {}
    for source in sources:
        source_type = source["source_type"]
        expected_path, expected_format = REQUIRED_SOURCE_DECLARATIONS[source_type]
        if source["path"] != expected_path:
            raise PackageManifestError(
                f"Source {source_type} must declare path {expected_path}: "
                f"{source['path']}"
            )
        if source["format"] != expected_format:
            raise PackageManifestError(
                f"Source {source_type} must declare format {expected_format}: "
                f"{source['format']}"
            )
        resolved[source_type] = _resolve_declared_path(
            package_root,
            source["path"],
            f"source {source_type}",
        )
    return resolved


def _validate_file_references(
    references: list[dict[str, Any]],
    package_root: Path,
    allowed_roots: tuple[Path, ...],
) -> dict[str, Path]:
    _require_unique(references, "file_ref_id", "file_ref_id")

    resolved: dict[str, Path] = {}
    for reference in references:
        file_ref_id = reference["file_ref_id"]
        candidate = _resolve_declared_path(
            package_root,
            reference["path"],
            f"file reference {file_ref_id}",
        )
        if not any(
            candidate != allowed_root and _is_relative_to(candidate, allowed_root)
            for allowed_root in allowed_roots
        ):
            raise PackageManifestError(
                f"File reference {file_ref_id} is outside allowed file-reference roots: "
                f"{reference['path']}"
            )
        resolved[file_ref_id] = candidate
    return resolved


def _validate_document_inventory(
    documents: list[dict[str, Any]],
    file_reference_paths: dict[str, Path],
) -> None:
    _require_unique(documents, "document_id", "document_id")
    for index, document in enumerate(documents):
        file_ref_id = document.get("file_ref_id")
        if file_ref_id is not None and file_ref_id not in file_reference_paths:
            raise PackageManifestError(
                f"document_inventory[{index}] references undeclared file_ref_id: "
                f"{file_ref_id}"
            )
        _validate_revision(
            document["current_revision"],
            f"document_inventory[{index}].current_revision",
        )


def _validate_relationships(
    relationships: list[dict[str, Any]],
    documents: list[dict[str, Any]],
    file_reference_paths: dict[str, Path],
) -> None:
    _require_unique(relationships, "relationship_id", "relationship_id")
    declared_ids = {
        "document_id": {document["document_id"] for document in documents},
        "file_ref_id": set(file_reference_paths),
    }
    for index, relationship in enumerate(relationships):
        for endpoint_name in ("source", "target"):
            endpoint = relationship[endpoint_name]
            identifier_type = endpoint["identifier_type"]
            if (
                identifier_type in declared_ids
                and endpoint["identifier"] not in declared_ids[identifier_type]
            ):
                raise PackageManifestError(
                    f"relationship_declarations[{index}].{endpoint_name} references "
                    f"undeclared {identifier_type}: {endpoint['identifier']}"
                )


def _validate_revision(revision: dict[str, Any], label: str) -> None:
    revision_id = revision["revision_id"]
    scheme = revision["scheme"]
    if scheme == "alpha_upper" and len(revision_id) > revision["max_letters"]:
        raise PackageManifestError(
            f"{label} revision_id exceeds declared max_letters: {revision_id}"
        )
    if scheme == "numeric_zero_padded" and len(revision_id) != revision["width"]:
        raise PackageManifestError(
            f"{label} revision_id must have declared width {revision['width']}: "
            f"{revision_id}"
        )
    if scheme == "explicit_sequence" and revision_id not in revision["allowed_values"]:
        raise PackageManifestError(
            f"{label} revision_id is not in allowed_values: {revision_id}"
        )


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
