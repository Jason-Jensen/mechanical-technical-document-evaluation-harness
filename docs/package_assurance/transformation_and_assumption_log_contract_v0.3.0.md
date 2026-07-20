# Transformation and Assumption Log Contract v0.3.0

## Control Status

- **WBS:** P2.3 controlled public-package mapping definition
- **Status:** Ready for CEO review
- **Applies to:** Public-package trial working copies
- **Template:** `transformation_and_assumption_log_template_v0.3.0.csv`

## Purpose

The log makes manual package preparation reviewable and reversible. It records
what the publisher supplied, what the preparation process changed or derived,
what authority supports the result, and where preparation stopped rather than
inventing a value.

The log is evidence about a working copy. It is not a substitute for publisher
source, an authority map, engineering review, or an audit result.

## Storage and Immutability

- Raw source archives remain unchanged, read-only in practice, and outside
  Git under the controlled local intake area.
- Every working package is created in a separate local directory.
- The populated log is stored beside the working package, not inside the raw
  source archive and not inside a benchmark `expected/` directory.
- Corrections append a superseding record; they do not erase an accepted or
  rejected record.
- Source and target paths use forward slashes and remain relative to their
  declared container. Absolute machine paths are prohibited.

## Mapping Classes

| Class | Meaning | Required record content |
|---|---|---|
| `direct` | Publisher value is retained without a semantic change. Representation-only changes such as CSV-to-JSON encoding are allowed. | Exact source locator/value, target locator/value, representation rule, and authority basis. |
| `derived` | Target value is produced by a deterministic, repeatable rule from preserved source values or an accepted trial-scope decision. | Every input locator/value, exact rule, output, authority basis, and review decision. |
| `missing` | A required or useful target value has no acceptable authoritative source. | Target locator, search/refusal evidence, blank target value, and explicit reason. |
| `not_applicable` | The target concept genuinely has no meaning for the accepted bounded configuration. | Reviewed scope reason and authority basis. |

`not_applicable` must not be used for a mandatory package source, a
release-critical authority field, or a relationship merely to avoid a hold.
Those conditions remain `missing` unless the controlling workflow contract is
changed through a separate accepted decision.

## CSV Column Contract

| Column | Requirement |
|---|---|
| `log_record_id` | Stable unique record ID. |
| `package_id` | Exact proposed working-package ID. |
| `source_container_sha256` | SHA-256 of the preserved source archive or separately preserved official artifact. |
| `source_artifact_path` | Relative path inside the source container; blank only for an accepted scope-only derivation or missing-value search record. |
| `source_locator` | CSV row/column, JSON Pointer, YAML path, Markdown heading/line evidence, ZIP path, or official release locator. |
| `source_value_json` | Exact source value encoded as JSON text; blank only for `missing` or scope-only derivation. |
| `target_artifact_path` | Relative working-package artifact path. |
| `target_locator` | CSV row/column, JSON Pointer, or manifest/authority field path. |
| `mapping_class` | One of `direct`, `derived`, `missing`, or `not_applicable`. |
| `transformation_rule` | Exact representation or derivation rule; `none` for an unchanged direct value. |
| `target_value_json` | Exact target value encoded as JSON text; blank for `missing`. |
| `authority_basis` | Publisher source, accepted authority rule, or accepted project decision supporting the mapping. |
| `assumption_or_refusal` | Trial-scope assumption or explicit reason a value was not created. |
| `review_status` | One of `proposed`, `accepted`, or `rejected`. |
| `reviewer_role` | Role that made the decision; blank while proposed. |
| `review_date` | ISO date; blank while proposed. |
| `evidence_note` | Short supporting note, including superseded record ID when applicable. |

JSON text is used inside value columns so numbers, strings, booleans, arrays,
objects, and nulls retain their types. A structured parser must be used when
the log is populated; comma splitting or ad hoc string replacement is not
acceptable.

## Recording Rules

1. Create at least one log record for every populated target field and every
   required target field classified as missing or not applicable.
2. Record source values before normalization or calculation.
3. Never derive identity from mutable row order alone.
4. A derived value must be reproducible from recorded inputs and the exact
   rule without engineering judgment.
5. One-to-many and many-to-one transformations use separate records so every
   target field remains traceable.
6. Preserve source precision. Decimal multiplication must not pass through a
   binary floating-point representation when exact decimal text is available.
7. Preserve punctuation, leading zeroes, case, units, and separators unless an
   accepted normalization rule explicitly changes them.
8. Missing values keep a blank target value. Placeholder text such as
   `UNKNOWN`, `TBD`, or `N/A` must not be written into a canonical field.
9. A publisher URL is evidence of a reference, not proof that the linked item
   is preserved, current, or authoritative.
10. Preparation cannot self-approve a proposed authority choice. The reviewer
    role and date are recorded only after the corresponding decision.

## Minimum Review

Before a prepared package may be audited, an independent review must confirm:

- all in-scope source rows/files have a disposition;
- every target value can be traced to direct source or an accepted derivation;
- missing authority remains visible;
- not-applicable decisions do not bypass mandatory controls;
- source and target hashes/paths identify the exact artifacts reviewed;
- no source file was overwritten;
- no protected benchmark or golden content was used; and
- the expected package state is stated before the evaluator result is seen.

## Human Boundary

Project/CEO review may accept package scope, trial-specific identifiers, and
source hierarchy for the experiment. A qualified engineer or document-control
owner is still required for engineering authority, applicability, release
acceptance, or technical conclusions. The evaluator and preparation agent do
not sign off the package.

## Definition of Done

This contract is ready when both package mapping definitions use the same four
classes, the CSV template matches every required column exactly, and project
controls require a populated-log review before either public package is run.
