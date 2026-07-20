"""Concise release-readiness view of an immutable package result."""

from __future__ import annotations

import html
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from mech_eval_harness.package_assurance.result_view import (
    PackageResultViewInputError,
    load_package_result_for_reporting,
)


RELEASE_READINESS_MARKDOWN_FILENAME = "release_readiness.md"
CONTROL_STATUS_ORDER: tuple[str, ...] = ("passed", "failed", "skipped")
FINDING_STATE_ORDER: tuple[str, ...] = (
    "automatic_fail",
    "extraction_or_tool_failure",
    "missing_authoritative_information",
    "evaluator_uncertainty",
    "engineering_review_required",
)


class ReleaseReadinessRenderError(RuntimeError):
    """Raised when a package result cannot support a readiness summary."""


def render_release_readiness_summary(
    *,
    result_path: Path,
    schema_path: Path,
) -> str:
    """Render one non-approving Markdown view of a validated stored result."""

    try:
        document = load_package_result_for_reporting(result_path, schema_path)
    except PackageResultViewInputError as exc:
        raise ReleaseReadinessRenderError(str(exc)) from exc
    return _render_markdown(document)


def _render_markdown(document: dict[str, Any]) -> str:
    package_id = document["package_id"]
    gate_counts = _status_counts(document["gate_results"])
    relationship_counts = _status_counts(document["relationship_results"])
    finding_counts = Counter(
        finding["result_state"] for finding in document["findings"]
    )
    blocking_states = document["blocking_states"]

    lines = [
        "# Package Release-Readiness Summary",
        "",
        "## Audit Identity",
        "",
        f"- Package ID: {_inline_code(package_id) if package_id else 'not established'}",
        f"- Run ID: {_inline_code(document['run_id'])}",
        "",
        "## Stored Result",
        "",
        "| Field | Stored value |",
        "| --- | --- |",
        f"| Package state | {_inline_code(document['package_state'])} |",
        f"| Release hold | {_inline_code(_boolean_text(document['release_hold']))} |",
        f"| Blocking states | {_blocking_state_text(blocking_states)} |",
        "| Output generation status | "
        f"{_inline_code(document['output_generation']['status'])} |",
        "",
        "## Evaluation Counts",
        "",
        "| Evaluation group | Passed | Failed | Skipped |",
        "| --- | ---: | ---: | ---: |",
        _count_row("Mandatory gates", gate_counts),
        _count_row("Relationship checks", relationship_counts),
        "",
        "## Finding Counts",
        "",
        "| Stored finding state | Count |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| {_inline_code(state)} | {finding_counts[state]} |"
        for state in FINDING_STATE_ORDER
    )
    lines.extend(
        [
            f"| **Total** | **{sum(finding_counts.values())}** |",
            "",
            "## Known Outputs",
            "",
        ]
    )
    lines.extend(
        f"- [{_markdown_text(name)}]({_markdown_text(name)})"
        for name in document["output_generation"]["output_names"]
    )
    lines.extend(
        [
            "",
            "## Required Qualified-Human Decision",
            "",
            "A qualified human must decide whether this package may proceed under "
            "the applicable engineering and release process.",
            "",
            f"> {_markdown_text(document['engineering_review_limitation'])}",
            "",
            "This summary does not approve release, certify compliance, or state "
            "that the engineering work is correct.",
            "",
        ]
    )
    return "\n".join(lines)


def _status_counts(results: Iterable[dict[str, Any]]) -> Counter[str]:
    return Counter(result["status"] for result in results)


def _count_row(label: str, counts: Counter[str]) -> str:
    values = (counts[status] for status in CONTROL_STATUS_ORDER)
    return f"| {label} | " + " | ".join(str(value) for value in values) + " |"


def _blocking_state_text(states: list[str]) -> str:
    if not states:
        return "none observed"
    return ", ".join(_inline_code(state) for state in states)


def _boolean_text(value: bool) -> str:
    return "true" if value else "false"


def _inline_code(value: Any) -> str:
    return f"<code>{_markdown_text(value)}</code>"


def _markdown_text(value: Any) -> str:
    normalized = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return (
        html.escape(normalized, quote=False)
        .replace("|", "&#124;")
        .replace("\n", "<br>")
    )
