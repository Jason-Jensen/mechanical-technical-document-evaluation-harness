"""Deterministic issue-register views of an immutable package result."""

from __future__ import annotations

import csv
import html
import io
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mech_eval_harness.package_assurance.result_view import (
    PackageResultViewInputError,
    load_package_result_for_reporting,
)


ISSUE_REGISTER_CSV_FILENAME = "issue_register.csv"
ISSUE_REGISTER_MARKDOWN_FILENAME = "issue_register.md"
ISSUE_REGISTER_CSV_FIELDS: tuple[str, ...] = (
    "finding_id",
    "result_state",
    "release_hold",
    "severity",
    "review_owner",
    "control_type",
    "control_id",
    "control_version",
    "code",
    "authority_rule_id",
    "governing_control_id",
    "package_id",
    "affected_identifiers_json",
    "expected_value_json",
    "actual_value_json",
    "evidence_json",
    "message",
    "evaluator_version",
)


class IssueRegisterRenderError(RuntimeError):
    """Raised when a package result cannot be rendered without ambiguity."""


@dataclass(frozen=True)
class IssueRegisterViews:
    """The two P3.1 text views prepared from one validated package result."""

    csv_text: str
    markdown_text: str


def render_issue_register_views(
    *,
    result_path: Path,
    schema_path: Path,
) -> IssueRegisterViews:
    """Load one canonical result and render its CSV and Markdown issue views."""

    try:
        document = load_package_result_for_reporting(result_path, schema_path)
    except PackageResultViewInputError as exc:
        raise IssueRegisterRenderError(str(exc)) from exc
    return IssueRegisterViews(
        csv_text=_render_csv(document),
        markdown_text=_render_markdown(document),
    )


def _render_csv(document: dict[str, Any]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output,
        fieldnames=ISSUE_REGISTER_CSV_FIELDS,
        lineterminator="\n",
    )
    writer.writeheader()
    for finding in document["findings"]:
        writer.writerow(
            {
                "finding_id": finding["finding_id"],
                "result_state": finding["result_state"],
                "release_hold": _boolean_text(finding["release_hold"]),
                "severity": finding["severity"],
                "review_owner": finding["review_owner"],
                "control_type": finding["control_type"],
                "control_id": finding["control_id"],
                "control_version": finding["control_version"],
                "code": finding["code"],
                "authority_rule_id": finding["authority_rule_id"] or "",
                "governing_control_id": finding["governing_control_id"] or "",
                "package_id": finding["package_id"] or "",
                "affected_identifiers_json": _compact_json(
                    finding["affected_identifiers"]
                ),
                "expected_value_json": _compact_json(finding["expected_value"]),
                "actual_value_json": _compact_json(finding["actual_value"]),
                "evidence_json": _compact_json(finding["evidence"]),
                "message": finding["message"],
                "evaluator_version": finding["evaluator_version"],
            }
        )
    return output.getvalue()


def _render_markdown(document: dict[str, Any]) -> str:
    package_id = document["package_id"]
    lines = [
        "# Package Issue Register",
        "",
        f"- Package ID: {_inline_code(package_id) if package_id else 'not established'}",
        f"- Run ID: {_inline_code(document['run_id'])}",
        "",
        f"> {_markdown_text(document['engineering_review_limitation'])}",
        "",
        "## Findings",
        "",
    ]

    findings = document["findings"]
    if not findings:
        lines.extend(
            [
                "No non-pass findings are recorded in this package result.",
                "",
            ]
        )
        return "\n".join(lines)

    for finding in findings:
        lines.extend(_markdown_finding(finding))
    return "\n".join(lines)


def _markdown_finding(finding: dict[str, Any]) -> list[str]:
    authority_rule = finding["authority_rule_id"]
    governing_control = finding["governing_control_id"]
    lines = [
        f"### Finding {finding['finding_id']}",
        "",
        "| Field | Value |",
        "| --- | --- |",
        f"| Result state | {_inline_code(finding['result_state'])} |",
        f"| Release hold | {_inline_code(_boolean_text(finding['release_hold']))} |",
        f"| Severity | {_inline_code(finding['severity'])} |",
        f"| Review owner | {_inline_code(finding['review_owner'])} |",
        f"| Control type | {_inline_code(finding['control_type'])} |",
        f"| Control ID | {_inline_code(finding['control_id'])} |",
        f"| Control version | {_inline_code(finding['control_version'])} |",
        f"| Finding code | {_inline_code(finding['code'])} |",
        f"| Authority rule ID | {_optional_inline_code(authority_rule)} |",
        f"| Governing control ID | {_optional_inline_code(governing_control)} |",
        "| Package ID | "
        f"{_optional_inline_code(finding['package_id'], absent_text='not established')} |",
        f"| Evaluator version | {_inline_code(finding['evaluator_version'])} |",
        f"| Message | {_markdown_text(finding['message'])} |",
        "",
        "**Affected identifiers**",
        "",
        _fenced_json(finding["affected_identifiers"]),
        "",
        "**Expected value or condition**",
        "",
        _fenced_json(finding["expected_value"]),
        "",
        "**Actual value or condition**",
        "",
        _fenced_json(finding["actual_value"]),
        "",
        "**Evidence**",
        "",
        _fenced_json(finding["evidence"]),
        "",
    ]
    return lines


def _compact_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def _fenced_json(value: Any) -> str:
    encoded = json.dumps(
        value,
        indent=2,
        sort_keys=True,
        ensure_ascii=False,
        allow_nan=False,
    )
    longest_run = max(
        (len(run) for run in re.findall(r"`+", encoded)),
        default=0,
    )
    fence = "`" * max(3, longest_run + 1)
    return f"{fence}json\n{encoded}\n{fence}"


def _boolean_text(value: bool) -> str:
    return "true" if value else "false"


def _inline_code(value: Any) -> str:
    return f"<code>{_markdown_text(value)}</code>"


def _optional_inline_code(value: Any, *, absent_text: str = "not applicable") -> str:
    return _inline_code(value) if value is not None else absent_text


def _markdown_text(value: Any) -> str:
    normalized = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return (
        html.escape(normalized, quote=False)
        .replace("|", "&#124;")
        .replace("\n", "<br>")
    )
