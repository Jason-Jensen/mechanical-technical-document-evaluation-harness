from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

import pytest

from mech_eval_harness.package_assurance import (
    PackageManifestError,
    load_package_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def _valid_manifest() -> dict[str, object]:
    return {
        "schema_version": "0.3.0",
        "package_id": "PKG-SYNTHETIC-001",
        "package_title": "Synthetic pump package",
        "created_date": "2026-07-16",
        "synthetic": True,
        "source_inventory": [
            {
                "source_type": "package_manifest",
                "path": "package_manifest.json",
                "format": "json",
                "required_for_release": True,
            },
            {
                "source_type": "drawing_register",
                "path": "inputs/drawing_register.csv",
                "format": "csv",
                "required_for_release": True,
            },
            {
                "source_type": "drawing_metadata",
                "path": "inputs/drawing_metadata.json",
                "format": "json",
                "required_for_release": True,
            },
            {
                "source_type": "bom_or_equipment_list",
                "path": "inputs/bom_or_equipment_list.csv",
                "format": "csv",
                "required_for_release": True,
            },
            {
                "source_type": "datasheet_spec_metadata",
                "path": "inputs/datasheet_spec_metadata.json",
                "format": "json",
                "required_for_release": True,
            },
            {
                "source_type": "revision_history",
                "path": "inputs/revision_history.csv",
                "format": "csv",
                "required_for_release": True,
            },
            {
                "source_type": "authority_map",
                "path": "authority/authority_map.json",
                "format": "json",
                "required_for_release": True,
            },
        ],
        "authority_map_ref": "authority/authority_map.json",
        "allowed_file_reference_roots": ["files"],
        "document_inventory": [
            {
                "document_id": "DOC-001",
                "document_type": "drawing",
                "drawing_number": "DWG 1001-A",
                "title": "Pump arrangement",
                "required_for_release": True,
                "current_revision": {
                    "revision_id": "A",
                    "scheme": "alpha_upper",
                    "max_letters": 1,
                },
                "file_ref_id": "FILE-001",
            }
        ],
        "file_references": [
            {
                "file_ref_id": "FILE-001",
                "path": "files/drawings/Pump Arrangement.pdf",
                "artifact_type": "drawing_pdf",
                "required_for_release": True,
            }
        ],
        "relationship_declarations": [
            {
                "relationship_id": "REL-DOC-FILE-001",
                "relationship_type": "document_to_file",
                "source": {
                    "identifier_type": "document_id",
                    "identifier": "DOC-001",
                },
                "target": {
                    "identifier_type": "file_ref_id",
                    "identifier": "FILE-001",
                },
                "required_for_release": True,
            }
        ],
    }


def _write_manifest(package_root: Path, manifest: dict[str, object]) -> Path:
    package_root.mkdir(parents=True, exist_ok=True)
    manifest_path = package_root / "package_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def _load(package_root: Path, manifest: dict[str, object]):
    manifest_path = _write_manifest(package_root, manifest)
    return load_package_manifest(
        ROOT,
        manifest_path,
        allowed_package_root=package_root,
    )


def test_load_package_manifest_returns_validated_declarations(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    loaded = _load(package_root, _valid_manifest())

    assert loaded.package_id == "PKG-SYNTHETIC-001"
    assert loaded.manifest_path == (package_root / "package_manifest.json").resolve()
    assert loaded.source_paths["drawing_register"] == (
        package_root / "inputs" / "drawing_register.csv"
    ).resolve()
    assert loaded.authority_map_path == (
        package_root / "authority" / "authority_map.json"
    ).resolve()
    assert loaded.allowed_file_roots == ((package_root / "files").resolve(),)
    assert loaded.file_reference_paths["FILE-001"] == (
        package_root / "files" / "drawings" / "Pump Arrangement.pdf"
    ).resolve()


def test_loader_defers_declared_source_and_file_io(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    loaded = _load(package_root, _valid_manifest())

    assert not loaded.source_paths["drawing_register"].exists()
    assert not loaded.file_reference_paths["FILE-001"].exists()


@pytest.mark.parametrize(
    "revision",
    [
        {"revision_id": "AB", "scheme": "alpha_upper", "max_letters": 2},
        {"revision_id": "12", "scheme": "numeric_integer"},
        {"revision_id": "02", "scheme": "numeric_zero_padded", "width": 2},
        {
            "revision_id": "IFC",
            "scheme": "explicit_sequence",
            "allowed_values": ["IFA", "IFB", "IFC"],
        },
    ],
)
def test_load_package_manifest_accepts_supported_revision_schemes(
    tmp_path: Path,
    revision: dict[str, object],
) -> None:
    manifest = _valid_manifest()
    documents = manifest["document_inventory"]
    assert isinstance(documents, list)
    documents[0]["current_revision"] = revision

    loaded = _load(tmp_path / "package", manifest)

    assert loaded.manifest["document_inventory"][0]["current_revision"] == revision


def test_load_package_manifest_rejects_missing_manifest(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()

    with pytest.raises(PackageManifestError, match="Package manifest error: File not found"):
        load_package_manifest(
            ROOT,
            package_root / "package_manifest.json",
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_malformed_json(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()
    manifest_path = package_root / "package_manifest.json"
    manifest_path.write_text("{not valid json}", encoding="utf-8")

    with pytest.raises(PackageManifestError, match="Invalid JSON"):
        load_package_manifest(
            ROOT,
            manifest_path,
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_invalid_utf8(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()
    manifest_path = package_root / "package_manifest.json"
    manifest_path.write_bytes(b"{\"schema_version\": \"0.3.0\", \"bad\": \xff}")

    with pytest.raises(PackageManifestError, match="could not be read"):
        load_package_manifest(
            ROOT,
            manifest_path,
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_manifest_directory(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()
    manifest_path = package_root / "package_manifest.json"
    manifest_path.mkdir()

    with pytest.raises(PackageManifestError, match="could not be read"):
        load_package_manifest(
            ROOT,
            manifest_path,
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_non_object_json(tmp_path: Path) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()
    manifest_path = package_root / "package_manifest.json"
    manifest_path.write_text("[]", encoding="utf-8")

    with pytest.raises(PackageManifestError, match="Top-level JSON value must be an object"):
        load_package_manifest(
            ROOT,
            manifest_path,
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_missing_required_field(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    del manifest["package_id"]

    with pytest.raises(PackageManifestError, match="'package_id' is a required property"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_invalid_created_date(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    manifest["created_date"] = "2026-02-30"

    with pytest.raises(PackageManifestError, match="is not a 'date'"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_unsupported_version(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    manifest["schema_version"] = "0.4.0"

    with pytest.raises(
        PackageManifestError,
        match="Unsupported package manifest schema_version: 0.4.0",
    ):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_manifest_outside_allowed_root(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()
    other_root = tmp_path / "other"
    manifest_path = _write_manifest(other_root, _valid_manifest())

    with pytest.raises(PackageManifestError, match="must be located at the allowed package root"):
        load_package_manifest(
            ROOT,
            manifest_path,
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_manifest_symlink_escape(
    tmp_path: Path,
) -> None:
    package_root = tmp_path / "package"
    package_root.mkdir()
    outside_manifest = _write_manifest(tmp_path / "outside", _valid_manifest())
    manifest_path = package_root / "package_manifest.json"
    try:
        manifest_path.symlink_to(outside_manifest)
    except OSError:
        pytest.skip("symlink creation is not available")

    with pytest.raises(PackageManifestError, match="resolves outside"):
        load_package_manifest(
            ROOT,
            manifest_path,
            allowed_package_root=package_root,
        )


def test_load_package_manifest_rejects_duplicate_source_type(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    sources = manifest["source_inventory"]
    assert isinstance(sources, list)
    sources[-1] = deepcopy(sources[1])

    with pytest.raises(PackageManifestError, match="Duplicate source declaration"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_undeclared_source_type(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    sources = manifest["source_inventory"]
    assert isinstance(sources, list)
    sources[-1]["source_type"] = "pdf_extract"

    with pytest.raises(PackageManifestError, match="is not one of"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_authority_map_reference_mismatch(
    tmp_path: Path,
) -> None:
    manifest = _valid_manifest()
    manifest["authority_map_ref"] = "authority/other_authority_map.json"

    with pytest.raises(PackageManifestError, match="must match the authority_map"):
        _load(tmp_path / "package", manifest)


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("path", "inputs/register.csv", "must declare path"),
        ("format", "json", "must declare format"),
    ],
)
def test_load_package_manifest_rejects_wrong_source_contract(
    tmp_path: Path,
    field: str,
    value: str,
    message: str,
) -> None:
    manifest = _valid_manifest()
    sources = manifest["source_inventory"]
    assert isinstance(sources, list)
    sources[1][field] = value

    with pytest.raises(PackageManifestError, match=message):
        _load(tmp_path / "package", manifest)


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("files/../../outside.pdf", "Invalid package-relative path"),
        ("inputs/not-controlled.pdf", "outside allowed file-reference roots"),
        ("C:/outside.pdf", "does not match"),
        ("files\\outside.pdf", "does not match"),
    ],
)
def test_load_package_manifest_rejects_unsafe_file_reference_paths(
    tmp_path: Path,
    path: str,
    message: str,
) -> None:
    manifest = _valid_manifest()
    references = manifest["file_references"]
    assert isinstance(references, list)
    references[0]["path"] = path

    with pytest.raises(PackageManifestError, match=message):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_duplicate_file_ref_id(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    references = manifest["file_references"]
    assert isinstance(references, list)
    references.append(deepcopy(references[0]))

    with pytest.raises(PackageManifestError, match="Duplicate file_ref_id: FILE-001"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_undeclared_document_file_ref(
    tmp_path: Path,
) -> None:
    manifest = _valid_manifest()
    documents = manifest["document_inventory"]
    assert isinstance(documents, list)
    documents[0]["file_ref_id"] = "FILE-999"

    with pytest.raises(PackageManifestError, match="undeclared file_ref_id: FILE-999"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_duplicate_document_id(tmp_path: Path) -> None:
    manifest = _valid_manifest()
    documents = manifest["document_inventory"]
    assert isinstance(documents, list)
    documents.append(deepcopy(documents[0]))

    with pytest.raises(PackageManifestError, match="Duplicate document_id: DOC-001"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_undeclared_relationship_endpoint(
    tmp_path: Path,
) -> None:
    manifest = _valid_manifest()
    relationships = manifest["relationship_declarations"]
    assert isinstance(relationships, list)
    relationships[0]["source"]["identifier"] = "DOC-999"

    with pytest.raises(PackageManifestError, match="undeclared document_id: DOC-999"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_duplicate_relationship_id(
    tmp_path: Path,
) -> None:
    manifest = _valid_manifest()
    relationships = manifest["relationship_declarations"]
    assert isinstance(relationships, list)
    relationships.append(deepcopy(relationships[0]))

    with pytest.raises(
        PackageManifestError,
        match="Duplicate relationship_id: REL-DOC-FILE-001",
    ):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_zero_padded_width_mismatch(
    tmp_path: Path,
) -> None:
    manifest = _valid_manifest()
    documents = manifest["document_inventory"]
    assert isinstance(documents, list)
    revision = documents[0]["current_revision"]
    revision.clear()
    revision.update(
        {
            "revision_id": "01",
            "scheme": "numeric_zero_padded",
            "width": 3,
        }
    )

    with pytest.raises(PackageManifestError, match="must have declared width 3"):
        _load(tmp_path / "package", manifest)


def test_load_package_manifest_rejects_revision_outside_explicit_sequence(
    tmp_path: Path,
) -> None:
    manifest = _valid_manifest()
    documents = manifest["document_inventory"]
    assert isinstance(documents, list)
    revision = documents[0]["current_revision"]
    revision.clear()
    revision.update(
        {
            "revision_id": "C",
            "scheme": "explicit_sequence",
            "allowed_values": ["A", "B"],
        }
    )

    with pytest.raises(PackageManifestError, match="is not in allowed_values: C"):
        _load(tmp_path / "package", manifest)
