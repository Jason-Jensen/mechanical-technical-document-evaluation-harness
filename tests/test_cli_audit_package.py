from __future__ import annotations

import csv
import io
import json
import shutil
from pathlib import Path

import pytest

from mech_eval_harness.cli import main
from mech_eval_harness.package_assurance import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
    PACKAGE_STATE_EXIT_CODES,
    package_state_exit_code,
)


ROOT = Path(__file__).resolve().parents[1]
DEVELOPMENT_PACKAGE = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "development"
    / "pump_skid_clean_v1"
    / "package"
)


def _copy_package(tmp_path: Path) -> Path:
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    return package_root


def _only_run_directory(runs_dir: Path) -> Path:
    run_directories = [
        path
        for path in runs_dir.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ]
    assert len(run_directories) == 1
    return run_directories[0]


def _run_cli(package_root: Path, runs_dir: Path) -> int:
    return main(
        [
            "audit-package",
            str(ROOT),
            str(package_root),
            "--runs-dir",
            str(runs_dir),
        ]
    )


def test_clean_package_cli_publishes_complete_non_approving_audit(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    assert exit_code == 0
    assert captured.err == ""
    assert "PACKAGE STATE: automatic_pass" in captured.out
    assert "RELEASE HOLD: false" in captured.out
    assert "ISSUE COUNT: 0" in captured.out
    assert "RESULT PATH:" in captured.out
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )

    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    assert document["package_state"] == "automatic_pass"
    assert document["release_hold"] is False
    assert document["output_generation"]["output_names"] == list(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )
    issue_rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )
    assert issue_rows == []
    readiness = (run_directory / "release_readiness.md").read_text(
        encoding="utf-8"
    )
    assert "qualified human must decide" in readiness
    assert "does not approve release" in readiness


def test_removed_required_mapping_cli_preserves_exact_fault(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    manifest_path = package_root / "package_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["relationship_declarations"] = [
        relationship
        for relationship in manifest["relationship_declarations"]
        if relationship["relationship_id"] != "REL-DOC-FILE-001"
    ]
    manifest_path.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    rows = list(
        csv.DictReader(
            io.StringIO(
                (run_directory / "issue_register.csv").read_text(
                    encoding="utf-8"
                )
            )
        )
    )
    assert exit_code == 1
    assert "PACKAGE STATE: automatic_fail" in captured.out
    assert "RELEASE HOLD: true" in captured.out
    assert document["package_state"] == "automatic_fail"
    assert document["release_hold"] is True
    assert [item["status"] for item in document["relationship_results"]] == [
        "passed",
        "passed",
        "passed",
        "passed",
        "failed",
    ]
    assert len(rows) == 1
    assert rows[0]["code"] == "DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED"
    for report_name in (
        "issue_register.csv",
        "issue_register.md",
        "release_readiness.md",
    ):
        report = (run_directory / report_name).read_text(encoding="utf-8")
        assert str(package_root) not in report


def test_malformed_manifest_cli_persists_controlled_failure(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")
    runs_dir = tmp_path / "runs"

    exit_code = _run_cli(package_root, runs_dir)

    captured = capsys.readouterr()
    run_directory = _only_run_directory(runs_dir)
    document = json.loads(
        (run_directory / "package_result.json").read_text(encoding="utf-8")
    )
    assert exit_code == 4
    assert "PACKAGE ID: not established" in captured.out
    assert "PACKAGE STATE: extraction_or_tool_failure" in captured.out
    assert document["package_id"] is None
    assert document["package_state"] == "extraction_or_tool_failure"
    assert document["input_fingerprint"]["status"] == "partial"
    assert {path.name for path in run_directory.iterdir()} == set(
        AUDIT_PACKAGE_OUTPUT_FILENAMES
    )


def test_unchanged_repeated_runs_preserve_substantive_outputs(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    runs_dir = tmp_path / "runs"

    assert _run_cli(package_root, runs_dir) == 0
    assert _run_cli(package_root, runs_dir) == 0

    run_directories = sorted(
        path for path in runs_dir.iterdir() if not path.name.startswith(".")
    )
    assert len(run_directories) == 2
    documents = [
        json.loads(
            (run_directory / "package_result.json").read_text(encoding="utf-8")
        )
        for run_directory in run_directories
    ]
    for document in documents:
        document.pop("run_id")
        document.pop("run_metadata")
    assert documents[0] == documents[1]
    assert (run_directories[0] / "issue_register.csv").read_bytes() == (
        run_directories[1] / "issue_register.csv"
    ).read_bytes()


@pytest.mark.parametrize(
    "argv",
    [
        ["audit-package"],
        ["audit-package", "missing-repository", "missing-package"],
    ],
)
def test_audit_package_usage_errors_return_64_without_result(
    argv: list[str],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    assert main(argv) == 64
    assert not (tmp_path / "runs").exists()


def test_output_inside_package_is_a_usage_error(tmp_path: Path) -> None:
    package_root = _copy_package(tmp_path)

    exit_code = main(
        [
            "audit-package",
            str(ROOT),
            str(package_root),
            "--runs-dir",
            str(package_root / "generated"),
        ]
    )

    assert exit_code == 64
    assert not (package_root / "generated").exists()


def test_pre_result_internal_failure_returns_70_without_result(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    incomplete_repository = tmp_path / "incomplete-repository"
    incomplete_repository.mkdir()
    runs_dir = tmp_path / "runs"

    exit_code = main(
        [
            "audit-package",
            str(incomplete_repository),
            str(package_root),
            "--runs-dir",
            str(runs_dir),
        ]
    )

    assert exit_code == 70
    assert not runs_dir.exists()


def test_every_package_state_has_the_accepted_stable_exit() -> None:
    assert PACKAGE_STATE_EXIT_CODES == {
        "automatic_pass": 0,
        "automatic_fail": 1,
        "engineering_review_required": 2,
        "missing_authoritative_information": 3,
        "extraction_or_tool_failure": 4,
        "evaluator_uncertainty": 5,
    }
    for state, expected_exit in PACKAGE_STATE_EXIT_CODES.items():
        assert package_state_exit_code(state) == expected_exit
