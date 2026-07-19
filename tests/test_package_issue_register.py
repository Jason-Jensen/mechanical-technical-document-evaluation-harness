from __future__ import annotations

import csv
import io
import json
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from mech_eval_harness.package_assurance import (
    DRAWING_REGISTER_METADATA_REVISION_CHECK_ID,
    ISSUE_REGISTER_CSV_FIELDS,
    IssueRegisterRenderError,
    build_package_result,
    render_issue_register_views,
    run_package_gates,
    run_package_relationships,
    write_package_result,
)
from mech_eval_harness.package_assurance.models import PackageRelationshipEvaluation
from mech_eval_harness.package_assurance.result_core import (
    RESULT_COMPLETENESS_CONTROL_ID,
)


ROOT = Path(__file__).resolve().parents[1]
RESULT_SCHEMA = ROOT / "schemas" / "package_result.schema.json"
DEVELOPMENT_PACKAGE = (
    ROOT
    / "benchmarks"
    / "package_assurance"
    / "development"
    / "pump_skid_clean_v1"
    / "package"
)
STARTED_AT = datetime(2026, 7, 19, 18, 0, 0, tzinfo=timezone.utc)
RUN_ID = "RUN-20260719T180000000000Z-deadbeef"


def _copy_package(tmp_path: Path) -> Path:
    package_root = tmp_path / "package"
    shutil.copytree(DEVELOPMENT_PACKAGE, package_root)
    return package_root


def _evaluate(package_root: Path):
    gates = run_package_gates(
        ROOT,
        Path("package_manifest.json"),
        allowed_package_root=package_root,
    )
    return gates, run_package_relationships(gates)


def _build_result(
    package_root: Path,
    *,
    relationships: PackageRelationshipEvaluation | None = None,
):
    gates, evaluated_relationships = _evaluate(package_root)
    return build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=STARTED_AT + timedelta(milliseconds=25),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=relationships or evaluated_relationships,
    )


def _write_result(tmp_path: Path, result) -> Path:
    return write_package_result(
        result=result,
        runs_dir=tmp_path / "runs",
        schema_path=RESULT_SCHEMA,
    )


def _csv_rows(csv_text: str) -> list[dict[str, str]]:
    return list(csv.DictReader(io.StringIO(csv_text)))


def test_clean_result_renders_header_only_and_non_approving_markdown(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    result_path = _write_result(tmp_path, _build_result(package_root))

    views = render_issue_register_views(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )

    assert views.csv_text.splitlines() == [",".join(ISSUE_REGISTER_CSV_FIELDS)]
    assert _csv_rows(views.csv_text) == []
    assert "# Package Issue Register" in views.markdown_text
    assert "No non-pass findings are recorded" in views.markdown_text
    assert "supports qualified human review" in views.markdown_text
    assert "ready for release" not in views.markdown_text.lower()
    assert "approved for release" not in views.markdown_text.lower()
    assert "certified" not in views.markdown_text.lower()


def test_relationship_finding_preserves_authority_and_structured_evidence(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["records"][0]["revision_id"] = "A"
    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    result = _build_result(package_root)
    result_path = _write_result(tmp_path, result)

    views = render_issue_register_views(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )
    rows = _csv_rows(views.csv_text)

    assert len(rows) == 1
    row = rows[0]
    assert tuple(row) == ISSUE_REGISTER_CSV_FIELDS
    assert row["finding_id"] == result.findings[0].finding_id
    assert row["result_state"] == "automatic_fail"
    assert row["release_hold"] == "true"
    assert row["control_type"] == "relationship_check"
    assert row["control_id"] == DRAWING_REGISTER_METADATA_REVISION_CHECK_ID
    assert row["authority_rule_id"] == "AUTH-DWG-001"
    assert row["governing_control_id"] == ""
    evidence = json.loads(row["evidence_json"])
    assert evidence[0]["source_file"] == "inputs/drawing_register.csv"
    assert evidence[1]["source_file"] == "inputs/drawing_metadata.json"
    assert str(tmp_path) not in views.csv_text
    assert str(tmp_path) not in views.markdown_text
    assert result.findings[0].finding_id in views.markdown_text
    assert "AUTH-DWG-001" in views.markdown_text


def test_gate_finding_uses_governing_control_without_fake_authority(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    (package_root / "package_manifest.json").write_text("{\n", encoding="utf-8")
    result = _build_result(package_root)
    result_path = _write_result(tmp_path, result)

    views = render_issue_register_views(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )
    gate_rows = [row for row in _csv_rows(views.csv_text) if row["control_type"] == "gate"]

    assert gate_rows
    assert all(row["authority_rule_id"] == "" for row in gate_rows)
    assert all(row["governing_control_id"] for row in gate_rows)
    assert all(row["package_id"] == "" for row in gate_rows)


def test_evaluator_completeness_finding_remains_explicit(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    gates, relationships = _evaluate(package_root)
    incomplete = PackageRelationshipEvaluation(
        package_id=relationships.package_id,
        checks=relationships.checks[:-1],
    )
    result = build_package_result(
        run_id=RUN_ID,
        started_at=STARTED_AT,
        completed_at=STARTED_AT + timedelta(milliseconds=25),
        package_root=package_root,
        gate_evaluation=gates,
        relationship_evaluation=incomplete,
    )
    result_path = _write_result(tmp_path, result)

    row = _csv_rows(
        render_issue_register_views(
            result_path=result_path,
            schema_path=RESULT_SCHEMA,
        ).csv_text
    )[0]

    assert row["result_state"] == "evaluator_uncertainty"
    assert row["control_type"] == "evaluator"
    assert row["authority_rule_id"] == ""
    assert row["governing_control_id"] == RESULT_COMPLETENESS_CONTROL_ID
    assert json.loads(row["evidence_json"]) == []
    assert json.loads(row["actual_value_json"])["issues"]


def test_views_are_byte_stable_and_preserve_canonical_finding_order(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["records"][0]["revision_id"] = "A"
    metadata["records"][1]["revision_id"] = "A"
    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    result = _build_result(package_root)
    result_path = _write_result(tmp_path, result)

    first = render_issue_register_views(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )
    second = render_issue_register_views(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )

    assert len(result.findings) == 2
    assert first == second
    assert [row["finding_id"] for row in _csv_rows(first.csv_text)] == [
        finding.finding_id for finding in result.findings
    ]
    markdown_positions = [
        first.markdown_text.index(finding.finding_id) for finding in result.findings
    ]
    assert markdown_positions == sorted(markdown_positions)
    assert "\r" not in first.csv_text
    assert "\r" not in first.markdown_text


def test_csv_quoting_and_markdown_escaping_preserve_finding_content(
    tmp_path: Path,
) -> None:
    package_root = _copy_package(tmp_path)
    metadata_path = package_root / "inputs" / "drawing_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["records"][0]["revision_id"] = "A"
    metadata_path.write_text(
        json.dumps(metadata, indent=2) + "\n",
        encoding="utf-8",
    )
    document = _build_result(package_root).to_dict()
    message = 'Review "A, B" | then\nreview C.'
    document["findings"][0]["message"] = message
    document["findings"][0]["expected_value"] = {"note": "A, B | C"}
    result_path = tmp_path / "package_result.json"
    result_path.write_text(
        json.dumps(document, indent=2) + "\n",
        encoding="utf-8",
    )

    views = render_issue_register_views(
        result_path=result_path,
        schema_path=RESULT_SCHEMA,
    )
    row = _csv_rows(views.csv_text)[0]

    assert row["message"] == message
    assert json.loads(row["expected_value_json"]) == {"note": "A, B | C"}
    assert "&#124;" in views.markdown_text
    assert "<br>" in views.markdown_text


@pytest.mark.parametrize(
    "raw",
    [
        "{\n",
        '{"schema_version":"0.3.0","schema_version":"0.3.0"}',
        '{"schema_version":"0.3.0"}',
        '{"schema_version":NaN}',
    ],
)
def test_malformed_or_schema_invalid_result_fails_closed(
    tmp_path: Path,
    raw: str,
) -> None:
    result_path = tmp_path / "package_result.json"
    result_path.write_text(raw, encoding="utf-8")

    with pytest.raises(IssueRegisterRenderError):
        render_issue_register_views(
            result_path=result_path,
            schema_path=RESULT_SCHEMA,
        )


def test_unreadable_result_path_fails_closed(tmp_path: Path) -> None:
    with pytest.raises(IssueRegisterRenderError, match="Could not read"):
        render_issue_register_views(
            result_path=tmp_path / "missing.json",
            schema_path=RESULT_SCHEMA,
        )
