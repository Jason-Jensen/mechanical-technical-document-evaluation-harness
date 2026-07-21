# Specification Revision History Implementation Review

**Date:** 2026-07-21

**Decision authority:** D-106, accepted by the project owner

**Integrated predecessor:** `main` commit
`761ac76a62bea26e63952613d9269435e6324605`

**Implementation branch:** `codex/p2.3-specification-revision-history`

## Executive Result

P2.3 check 11, `specification_revision_history`, is implemented as the
eleventh ordered relationship check.

It compares every release-required authoritative specification-metadata
revision with exactly one current revision-history record joined by normalized
`specification_id` under exact `AUTH-SPEC-003`. A missing current record,
multiple current records, or a revision mismatch produces the frozen
high-severity automatic-fail release hold.

The clean development package passes all eleven checks. Changing only
`SPMETA-001.revision_id` from `A` to valid explicit-sequence value `B`, while
revision history remains `A`, produces one `SPECIFICATION_REVISION_MISMATCH`
finding, release hold, CLI exit `1`, and the same exact four-output publication
contract.

## Scope Preserved

This slice adds no loader, adapter, schema, fixture, authority-map change,
generic rule engine, public-package rerun, held-out semantic execution,
PDF/CAD extraction, agent behavior, API, database, RAG, or frontend capability.

It does not reinterpret checks 1-10, result-state precedence, the result
schema, CLI exit mapping, publication behavior, or the frozen v0.2.0 kernel.

Only release-required specification metadata is authoritative for this check.
Unmatched revision-history records and the six accepted authority/source gaps
remain outside its release claim.

## Implemented Contract

| Item | Implemented value |
| --- | --- |
| Check ID | `specification_revision_history` |
| Position | eleventh, after `equipment_datasheet_manifest_reciprocity` |
| Finding code | `SPECIFICATION_REVISION_MISMATCH` |
| Authoritative source | release-required specification metadata |
| Compared source | current revision-history records |
| Join key | normalized `specification_id` |
| Expected cardinality | exactly one current history record per required specification |
| Exact authority | `AUTH-SPEC-003` with every behavior-critical field matched |
| Conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `document_control` |
| Evidence | specification ID and revision followed by current-history join, status, and revision locators, or a bounded history-search locator when missing |

## Deterministic Behavior

Required specification records are sorted by normalized specification ID and
record ID. Revision-history records are sorted by normalized owner type,
owner identifier, sequence index, document ID, and revision-record ID.

Finding identity includes the package, check, specification ID, exact
authority rule, expected revision, and stable actual condition. It excludes
run IDs, timestamps, absolute paths, CSV row positions, source iteration
order, and process state.

Tests prove:

- the clean two-specification package passes with exact bounded evidence;
- the accepted wrong-valid metadata revision produces one frozen finding;
- missing and multiple current records produce one stable finding per affected
  specification;
- reversing metadata and revision-history source order preserves finding IDs
  and substantive expected/actual values;
- every behavior-critical `AUTH-SPEC-003` field is required;
- an unrelated `AUTH-SPEC-001` change does not suppress check 11;
- a blocking package gate returns the complete eleven-check skipped sequence;
  and
- every prior isolated relationship fault retains its original finding while
  check 11 passes independently.

## Output Inspection

### Clean run

- Run: `RUN-20260721T164400783739Z-e5fdce3c`
- State: `automatic_pass`
- Release hold: `false`
- Mandatory gates: 8 passed
- Relationship checks: 11 passed, 0 failed, 0 skipped
- Findings: 0
- CLI exit: `0`
- Outputs: exactly `package_result.json`, `issue_register.csv`,
  `issue_register.md`, and `release_readiness.md`

### Wrong-specification-revision run

- Run: `RUN-20260721T164405746563Z-8ccbbbf1`
- State: `automatic_fail`
- Release hold: `true`
- Mandatory gates: 8 passed
- Relationship checks: 10 passed, 1 failed, 0 skipped
- Finding: `FND-C74035C8B9E5C4E7`
- Code: `SPECIFICATION_REVISION_MISMATCH`
- Affected identifier: `SPEC-PUMP-001`
- Expected / actual: `B` / `A`
- Authority / owner: `AUTH-SPEC-003` / `document_control`
- CLI exit: `1`
- Outputs: the same exact four files

The canonical result, CSV issue row, Markdown issue view, readiness summary,
terminal state, hold, and exit were inspected and agree. No output contains
the temporary package's absolute path. Verification evidence is preserved
under `scratch/verification/check11-implementation-20260721/`.

## Verification

- relationship/result/report/CLI focused set: 99 passed;
- full regression suite: 314 passed, 1 expected Windows skip;
- full-suite coverage: 88.48%, above the 80% CI floor;
- repository case validation: 5/5;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- frozen portfolio demo replay: 2/2.

No accepted fixture, schema, authority map, golden, held-out asset, public
package, historical result, or v0.2.0 behavior changed.

## Practical Value

The audit now catches a specification that claims a valid but different
revision from the package's current revision history. This closes the final
relationship check supportable by the pilot's accepted sources and authority
rules.

## Residual Boundary

The six authority/source gaps remain real product limitations: quantity,
part/material, BOM-to-drawing, equipment-to-specification, datasheet revision,
and controlled technical-value reconciliation. They must not be represented
as implemented assurance.

Semantic held-out execution, public-package reruns, and every deferred
multimodal/platform capability also remain blocked.

## Recommended Decision D-107

Accept check 11 as matching D-106 and merge this implementation.

Then authorize only a P2.3 authority-gap disposition and completion-definition
block. The recommended pilot decision is to explicitly defer the six
unsupported claims, narrow the v0.3.0 release claims to the eleven proven
checks, and then proceed to P4 fault-injection and benchmark planning. Do not
invent comparison sources or authority rules merely to mark P2.3 complete.
