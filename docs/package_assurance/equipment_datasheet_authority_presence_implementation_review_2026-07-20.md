# Equipment Datasheet Authority Presence Implementation Review

**Date:** 2026-07-20

**Decision authority:** D-102, accepted by the project owner

**Integrated predecessor:** `main` commit `b0b32bba95c24facbbcb23216d9bc7d0ea23e1e6`

**Implementation branch:** `codex/p2.3-equipment-datasheet-authority-presence`

## Executive Result

P2.3 check 8, `equipment_datasheet_authority_presence`, is implemented as the
eighth ordered relationship check.

For each release-required BOM equipment tag, it now requires exactly one
release-required datasheet metadata record under the exact accepted
`AUTH-SPEC-001` rule. Zero records or multiple competing records produce one
high-severity `missing_authoritative_information` finding and a release hold.

The accepted clean development package passes all eight checks. Removing one
datasheet record produces the exact expected hold, CLI exit `3`, and four
consistent outputs.

## Scope Preserved

This slice added no package loader, schema, generic rule engine, public-package
rerun, held-out execution, PDF/CAD extraction, agent behavior, API, database,
RAG, or frontend capability.

It did not change the accepted development package, held-out assets, authority
map, goldens, result schema, state precedence, exit mapping, or frozen v0.2.0
kernel.

Check 8 does not compare the BOM `datasheet_id` with the authoritative metadata
record. That separate agreement claim remains check 9.

## Implemented Contract

| Item | Implemented value |
| --- | --- |
| Check ID | `equipment_datasheet_authority_presence` |
| Position | eighth, after `bom_equipment_drawing_presence` |
| Finding code | `EQUIPMENT_DATASHEET_AUTHORITY_MISSING` |
| Required object | each release-required BOM `equipment_tag` |
| Authoritative source | `datasheet_spec_metadata.datasheets` |
| Exact authority | `AUTH-SPEC-001` with all behavior-critical fields matched |
| Passing condition | exactly one release-required matching datasheet record |
| Failure condition | zero or multiple matching records |
| Result state | `missing_authoritative_information` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |
| Evidence | BOM equipment-tag field plus deterministic datasheet collection search |

The implementation is isolated in a datasheet-domain module. Existing drawing
and BOM relationship behavior remains separate and unchanged.

## Deterministic Behavior

The check sorts release-required BOM records and datasheet records by normalized
semantic identifiers before comparison. Its finding identity excludes source
row order and physical JSON positions.

Tests prove:

- the clean two-equipment package passes with four exact evidence locators;
- removing `DSMETA-001` produces one finding for `ITEM-PUMP-001` / `P-101A`;
- redirecting the second datasheet to `P-101A` produces one missing and one
  ambiguous finding in stable equipment-tag order;
- reversing both BOM and datasheet source order preserves finding identity and
  substantive values;
- an altered `AUTH-SPEC-001` behavior field skips check 8 against authority;
- drawing or BOM authority changes do not suppress the independent datasheet
  check; and
- a blocking package gate returns the complete eight-check skipped sequence.

## Output Inspection

### Clean run

- Run: `RUN-20260721T025957813425Z-a7aee64f`
- State: `automatic_pass`
- Release hold: `false`
- Relationship checks: 8 passed, 0 failed, 0 skipped
- Findings: 0
- CLI exit: `0`
- Outputs: exactly four; schema-valid and exactly reproducible from the result

### Isolated missing-datasheet run

- Run: `RUN-20260721T025913235840Z-be4840eb`
- State: `missing_authoritative_information`
- Release hold: `true`
- Relationship checks: 7 passed, 1 failed, 0 skipped
- Finding: `FND-55D33CACFBF70823`
- Code: `EQUIPMENT_DATASHEET_AUTHORITY_MISSING`
- Affected identifiers: `ITEM-PUMP-001`, `P-101A`
- Expected / actual: `one authoritative datasheet` / `0`
- CLI exit: `3`
- Outputs: exactly four; schema-valid and exactly reproducible from the result

Both run directories are preserved under
`scratch/verification/check8-implementation-20260720/`.

## Preserved Failed Probe

The first manual fault-copy attempt used Windows PowerShell's BOM-writing UTF-8
mode. The evaluator correctly stopped at source parsing with
`extraction_or_tool_failure`, exit `4`, and four controlled outputs. That failed
run is preserved rather than overwritten. A fresh copy written explicitly as
BOM-free UTF-8 then produced the intended check-8 result above.

This was an evidence-preparation encoding issue, not an evaluator defect or an
accepted-package change. It also confirms that malformed source encoding fails
closed before relationship evaluation.

## Verification

- relationship, CLI, and readiness focused set: 64 passed;
- broader gate/relationship/result/report/CLI set: 111 passed;
- full regression suite: 295 passed, 1 expected Windows skip;
- full-suite coverage: 87.71%, above the 80% CI floor;
- repository case validation: 5/5;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- frozen portfolio demo replay: 2/2.

The clean and fault outputs were independently schema-validated and all three
report views reproduced exactly from their canonical `package_result.json`.

## Practical Value

The product can now distinguish between a package that has one controlled
datasheet authority record for each required equipment item and a package where
that authority is absent or ambiguous. This is useful release-review evidence,
especially when source records look complete but do not establish one clear
equipment-to-datasheet authority.

It still cannot claim the BOM points to the correct datasheet. Check 9 is the
next meaningful slice because it compares the BOM datasheet ID with the one
authoritative record established by check 8.

## Recommended Decision D-103

Accept check 8 as matching D-102 and merge this implementation. Authorize only
P2.3 check 9, `equipment_datasheet_association`, next under the same exact
`AUTH-SPEC-001` dependency.

Require check 9 to compare the BOM `datasheet_id` with the single authoritative
metadata `datasheet_id`, emit the accepted automatic-fail hold on mismatch,
publish the exact four outputs, and preserve all earlier check behavior.

Continue to keep checks 10-11, the six authority-gap claims, semantic held-out
execution, public-package reruns, and deferred multimodal/platform capabilities
blocked until their respective review gates.
