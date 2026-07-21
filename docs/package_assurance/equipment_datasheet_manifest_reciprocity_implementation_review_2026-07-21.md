# Equipment Datasheet Manifest Reciprocity Implementation Review

**Date:** 2026-07-21

**Decision authority:** D-105, accepted by the project owner

**Integrated predecessor:** `main` commit
`dbcd242e027ae4e40ea9738adda3f8b02be07c6a`

**Implementation branch:**
`codex/p2.3-equipment-datasheet-manifest-reciprocity`

## Executive Result

P2.3 check 10, `equipment_datasheet_manifest_reciprocity`, is implemented as
the tenth ordered relationship check.

It compares release-required authoritative equipment-to-datasheet mappings in
datasheet metadata with release-required `equipment_to_datasheet` declarations
in the package manifest under exact `AUTH-SPEC-001`. The comparison works in
both directions: missing, extra, conflicting, or multiple declarations do not
pass as reciprocal.

The clean development package passes all ten checks. Changing only
`REL-EQ-DS-001` from `DS-P-101` to the existing valid `DS-M-101` produces one
high-severity `automatic_fail` finding, a release hold, CLI exit `1`, and the
same exact four-output publication contract.

## Scope Preserved

This slice adds no loader, adapter, schema, generic rule engine, fixture,
authority-map change, public-package rerun, held-out semantic execution,
PDF/CAD extraction, agent behavior, API, database, RAG, or frontend capability.

It does not alter checks 1-9, result-state precedence, the result schema, CLI
exit mapping, publication behavior, or the frozen v0.2.0 kernel.

Check 9 retains ownership of BOM-versus-metadata agreement. Check 10 compares
metadata with the package manifest and does not reinterpret the BOM value.

## Implemented Contract

| Item | Implemented value |
| --- | --- |
| Check ID | `equipment_datasheet_manifest_reciprocity` |
| Position | tenth, after `equipment_datasheet_association` |
| Finding code | `EQUIPMENT_DATASHEET_RECIPROCITY_FAILED` |
| Authoritative source | release-required datasheet metadata |
| Compared declaration | release-required manifest `equipment_to_datasheet` relationship |
| Semantic key | normalized `equipment_tag -> datasheet_id` |
| Exact authority | `AUTH-SPEC-001` with every behavior-critical field matched |
| Conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |
| Evidence | authoritative metadata fields followed by the manifest item or collection-search locator |

For a release-required BOM equipment tag with zero or multiple authoritative
records, check 8 retains ownership. Check 10 records that ownership in its
summary and does not create a duplicate finding. Declarations outside that BOM
scope must still resolve to authoritative metadata, so the reverse direction
cannot disappear silently.

## Deterministic Behavior

Authoritative records and declarations are grouped by normalized equipment
tag and sorted by normalized semantic mapping. Relationship IDs are used only
as a stable tie-breaker and as evidence identity.

Finding identity includes the package, check, equipment tag, authority rule,
expected mapping, and actual mapping. It excludes run IDs, timestamps,
absolute paths, source list positions, and process state.

Tests prove:

- the clean two-equipment package passes with six bounded field/manifest
  locators;
- the exact wrong-valid pump target produces one frozen finding;
- missing and multiple declarations produce one stable finding per affected
  equipment tag;
- reversing source and declaration order preserves finding IDs and substantive
  expected/actual values;
- check 8 retains missing/ambiguous-authority ownership;
- an altered behavior-critical `AUTH-SPEC-001` field skips checks 8-10 against
  the authority prerequisite;
- unrelated drawing and BOM authority failures do not suppress check 10; and
- a blocking package gate returns the complete ten-check skipped sequence.

## Output Inspection

### Clean run

- Run: `RUN-20260721T161152356249Z-a4995c89`
- State: `automatic_pass`
- Release hold: `false`
- Mandatory gates: 8 passed
- Relationship checks: 10 passed, 0 failed, 0 skipped
- Findings: 0
- CLI exit: `0`
- Outputs: exactly `package_result.json`, `issue_register.csv`,
  `issue_register.md`, and `release_readiness.md`

### Wrong-manifest-target run

- Run: `RUN-20260721T161152970951Z-ace6c987`
- State: `automatic_fail`
- Release hold: `true`
- Mandatory gates: 8 passed
- Relationship checks: 9 passed, 1 failed, 0 skipped
- Finding: `FND-7D92758E4EE968AE`
- Code: `EQUIPMENT_DATASHEET_RECIPROCITY_FAILED`
- Affected identifier: `P-101A`
- Expected / actual: `P-101A -> DS-P-101` /
  `P-101A -> DS-M-101`
- Authority / owner: `AUTH-SPEC-001` / `mechanical_engineering`
- CLI exit: `1`
- Outputs: the same exact four files

The canonical result, CSV issue row, Markdown issue view, readiness summary,
terminal state, hold, and exit were inspected and agree. Verification evidence
is preserved under
`scratch/verification/check10-implementation-20260721/`.

## Verification

- relationship/result/report/CLI focused set: 93 passed;
- full regression suite: 308 passed, 1 expected Windows skip;
- full-suite coverage: 88.27%, above the 80% CI floor;
- repository case validation: 5/5;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- frozen portfolio demo replay: 2/2.

No accepted fixture, schema, authority map, golden, held-out asset, public
package, historical result, or v0.2.0 behavior changed.

## Practical Value

The audit can now distinguish a manifest that merely names valid equipment and
datasheet identifiers from one that declares the authoritative pairing. This
catches a realistic package-assembly error that structural validation and the
BOM-versus-metadata check cannot own.

## Residual Boundary

Check 11, `specification_revision_history`, remains unimplemented. The six
authority/source gaps, semantic held-out execution, public-package reruns, and
all deferred multimodal/platform capabilities remain blocked.

## Recommended Decision D-106

Accept check 10 as matching D-105 and merge this implementation.

After integration, authorize only P2.3 check 11,
`specification_revision_history`, under exact `AUTH-SPEC-003`. Keep the six
authority-gap claims and every later capability behind their separate review
gates.
