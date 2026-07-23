"""Run a production-equivalent, non-held-out package publication sentinel."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from jsonschema import Draft202012Validator

from mech_eval_harness.package_assurance import (
    AUDIT_PACKAGE_OUTPUT_FILENAMES,
    PACKAGE_RESULT_FILENAME,
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
SCHEMA_FILENAMES = (
    "package_manifest.schema.json",
    "package_result.schema.json",
)
OPTIONAL_OS_BOOTSTRAP_KEYS = (
    "SYSTEMROOT",
    "WINDIR",
    "COMSPEC",
    "PATHEXT",
    "TEMP",
    "TMP",
)
TARGET_RUNS_PATH_LENGTH = 193


class PublicationSentinelError(RuntimeError):
    """Raised when the bounded publication sentinel does not pass."""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Stage the development package and evaluator in an external-bundle "
            "layout, run one bounded child audit, and require four valid outputs."
        )
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "runs" / "package-assurance-publication-sentinel",
    )
    parser.add_argument(
        "--target-runs-path-length",
        type=int,
        default=TARGET_RUNS_PATH_LENGTH,
    )
    args = parser.parse_args(argv)

    try:
        summary_path, summary = run_publication_sentinel(
            output_dir=args.output_dir,
            target_runs_path_length=args.target_runs_path_length,
        )
    except PublicationSentinelError as exc:
        print(f"FAIL publication sentinel: {exc}", file=sys.stderr)
        return 1

    print(
        "PASS publication sentinel | "
        f"state={summary['result']['package_state']} | "
        f"outputs={summary['publication']['output_count']} | "
        f"runs_path_length={summary['paths']['runs_dir_length']} | "
        f"evidence={summary_path}"
    )
    return 0


def run_publication_sentinel(
    *,
    output_dir: Path,
    target_runs_path_length: int = TARGET_RUNS_PATH_LENGTH,
) -> tuple[Path, dict[str, Any]]:
    output_dir = output_dir.resolve()
    sentinel_id = (
        datetime.now(timezone.utc).strftime("SENTINEL-%Y%m%dT%H%M%SZ-")
        + uuid4().hex[:8]
    )
    evidence_root = output_dir / sentinel_id
    evidence_root.mkdir(parents=True, exist_ok=False)
    bundle_root = _bundle_root_for_target(
        evidence_root,
        target_runs_path_length=target_runs_path_length,
    )
    evaluator_root = bundle_root / "eval"
    evaluator_source = evaluator_root / "src"
    package_root = bundle_root / "inputs" / "package"
    runs_dir = bundle_root / "runtime" / "runs"

    summary: dict[str, Any] = {
        "schema_version": "0.3.0",
        "sentinel_id": sentinel_id,
        "status": "failed",
        "purpose": (
            "Development-only, production-equivalent atomic publication sentinel."
        ),
        "protected_or_held_out_inputs_used": False,
        "paths": {
            "runs_dir_length": len(str(runs_dir)),
            "target_runs_path_length": target_runs_path_length,
            "host_root_adapted": (
                len(str(runs_dir)) > target_runs_path_length
            ),
        },
    }
    summary_path = evidence_root / "sentinel_summary.json"

    try:
        _stage_evaluator(evaluator_root)
        _stage_producer_visible_package(package_root)
        if (package_root / "expected").exists():
            raise PublicationSentinelError(
                "Producer-hidden expected assets entered the sentinel package."
            )

        static_roots = {
            "evaluator": evaluator_root,
            "package": package_root,
        }
        static_sha256_before, static_file_count = _aggregate_roots_sha256(
            static_roots
        )
        readonly_file_count = _make_files_read_only(static_roots.values())

        environment = _bounded_child_environment(evaluator_source)
        command = (
            str(Path(sys.executable).resolve()),
            "-m",
            "mech_eval_harness",
            "audit-package",
            str(evaluator_root),
            str(package_root),
            "--runs-dir",
            str(runs_dir),
        )
        completed = subprocess.run(
            command,
            cwd=evaluator_root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        static_sha256_after, post_file_count = _aggregate_roots_sha256(
            static_roots
        )
        if static_sha256_after != static_sha256_before:
            raise PublicationSentinelError(
                "Staged evaluator or package inputs changed during execution."
            )
        if post_file_count != static_file_count:
            raise PublicationSentinelError(
                "Staged evaluator or package file count changed during execution."
            )
        if completed.returncode != 0:
            raise PublicationSentinelError(
                "Bounded child audit returned "
                f"{completed.returncode}: {completed.stderr.strip()}"
            )

        run_directories = sorted(
            (
                path
                for path in runs_dir.iterdir()
                if path.is_dir() and not path.name.startswith(".")
            ),
            key=lambda path: path.name.encode("utf-8"),
        )
        failed_directories = sorted(
            (
                path
                for path in runs_dir.iterdir()
                if path.is_dir() and path.name.startswith(".")
            ),
            key=lambda path: path.name.encode("utf-8"),
        )
        if len(run_directories) != 1 or failed_directories:
            raise PublicationSentinelError(
                "Sentinel must produce one complete run and no failed publication."
            )

        run_directory = run_directories[0]
        output_names = tuple(
            sorted(
                (path.name for path in run_directory.iterdir() if path.is_file()),
                key=lambda name: name.encode("utf-8"),
            )
        )
        if set(output_names) != set(AUDIT_PACKAGE_OUTPUT_FILENAMES):
            raise PublicationSentinelError(
                "Sentinel did not publish the exact four-output contract."
            )

        result_path = run_directory / PACKAGE_RESULT_FILENAME
        result_document = json.loads(result_path.read_text(encoding="utf-8"))
        schema_document = json.loads(
            (evaluator_root / "schemas" / "package_result.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator.check_schema(schema_document)
        Draft202012Validator(schema_document).validate(result_document)
        if result_document["package_state"] != "automatic_pass":
            raise PublicationSentinelError(
                "Clean sentinel package did not reach automatic_pass."
            )
        if result_document["release_hold"] is not False:
            raise PublicationSentinelError(
                "Clean sentinel package unexpectedly produced a release hold."
            )

        longest_output_name = max(
            AUDIT_PACKAGE_OUTPUT_FILENAMES,
            key=len,
        )
        legacy_staging_path = (
            runs_dir
            / f".{result_document['run_id']}.12345678.tmp"
            / longest_output_name
        )
        output_sha256 = {
            name: _file_sha256(run_directory / name) for name in output_names
        }
        summary.update(
            {
                "status": "passed",
                "environment": {
                    "keys": sorted(environment),
                    "path_forwarded": "PATH" in environment,
                    "credential_or_proxy_keys_forwarded": any(
                        key.upper().endswith(("TOKEN", "SECRET", "PASSWORD"))
                        or "PROXY" in key.upper()
                        for key in environment
                    ),
                },
                "static_inputs": {
                    "file_count": static_file_count,
                    "readonly_file_count": readonly_file_count,
                    "aggregate_sha256_before": static_sha256_before,
                    "aggregate_sha256_after": static_sha256_after,
                    "producer_hidden_expected_assets_absent": True,
                },
                "child": {
                    "exit_code": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                },
                "publication": {
                    "run_directory_name": run_directory.name,
                    "output_count": len(output_names),
                    "output_names": list(output_names),
                    "output_sha256": output_sha256,
                    "legacy_staging_output_path_length": len(
                        str(legacy_staging_path)
                    ),
                },
                "result": {
                    "run_id": result_document["run_id"],
                    "package_id": result_document["package_id"],
                    "package_state": result_document["package_state"],
                    "release_hold": result_document["release_hold"],
                    "finding_count": len(result_document["findings"]),
                    "schema_valid": True,
                },
            }
        )
        if summary["publication"]["legacy_staging_output_path_length"] < 260:
            raise PublicationSentinelError(
                "Sentinel path is too short to exercise the former staging defect."
            )
    except Exception as exc:
        summary["error"] = {
            "type": type(exc).__name__,
            "message": str(exc),
        }
        _write_summary(summary_path, summary)
        if isinstance(exc, PublicationSentinelError):
            raise
        raise PublicationSentinelError(str(exc)) from exc

    _write_summary(summary_path, summary)
    return summary_path, summary


def _bundle_root_for_target(
    evidence_root: Path,
    *,
    target_runs_path_length: int,
) -> Path:
    if target_runs_path_length < TARGET_RUNS_PATH_LENGTH:
        raise PublicationSentinelError(
            "Requested runs path is below the minimum publication stress length."
        )
    fixed_bundle_name = "bundle-"
    fixed_runs_dir = evidence_root / fixed_bundle_name / "runtime" / "runs"
    effective_runs_path_length = max(
        target_runs_path_length,
        len(str(fixed_runs_dir)) + 8,
    )
    padding_length = effective_runs_path_length - len(str(fixed_runs_dir))
    bundle_root = evidence_root / (fixed_bundle_name + ("x" * padding_length))
    runs_dir = bundle_root / "runtime" / "runs"
    if len(str(runs_dir)) != effective_runs_path_length:
        raise PublicationSentinelError(
            "Could not construct the requested publication path length."
        )
    return bundle_root


def _stage_evaluator(evaluator_root: Path) -> None:
    source_target = evaluator_root / "src" / "mech_eval_harness"
    source_target.parent.mkdir(parents=True, exist_ok=False)
    shutil.copytree(
        ROOT / "src" / "mech_eval_harness",
        source_target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    schema_target = evaluator_root / "schemas"
    schema_target.mkdir()
    for filename in SCHEMA_FILENAMES:
        shutil.copy2(ROOT / "schemas" / filename, schema_target / filename)


def _stage_producer_visible_package(target: Path) -> None:
    def ignore_hidden(current: str, names: list[str]) -> set[str]:
        if Path(current).resolve() == DEVELOPMENT_PACKAGE.resolve():
            return {"expected"} & set(names)
        return set()

    shutil.copytree(DEVELOPMENT_PACKAGE, target, ignore=ignore_hidden)


def _bounded_child_environment(evaluator_source: Path) -> dict[str, str]:
    environment = {
        key: os.environ[key]
        for key in OPTIONAL_OS_BOOTSTRAP_KEYS
        if key in os.environ
    }
    environment.update(
        {
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONIOENCODING": "utf-8",
            "PYTHONUTF8": "1",
            "PYTHONPATH": str(evaluator_source),
        }
    )
    return environment


def _make_files_read_only(roots: Any) -> int:
    count = 0
    for root in roots:
        for path in root.rglob("*"):
            if path.is_file():
                path.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
                count += 1
    return count


def _aggregate_roots_sha256(roots: dict[str, Path]) -> tuple[str, int]:
    entries: list[tuple[bytes, Path]] = []
    for label, root in roots.items():
        for path in root.rglob("*"):
            if path.is_file():
                relative = f"{label}/{path.relative_to(root).as_posix()}"
                entries.append((relative.encode("utf-8"), path))
    entries.sort(key=lambda entry: entry[0])

    digest = hashlib.sha256()
    for relative, path in entries:
        digest.update(relative)
        digest.update(b"\0")
        digest.update(bytes.fromhex(_file_sha256(path)))
        digest.update(b"\n")
    return digest.hexdigest(), len(entries)


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )


if __name__ == "__main__":
    raise SystemExit(main())
