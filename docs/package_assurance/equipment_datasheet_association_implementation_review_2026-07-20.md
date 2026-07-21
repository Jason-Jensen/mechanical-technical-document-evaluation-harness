# Equipment Datasheet Association Implementation Review

**Date:** 2026-07-20

**Decision authority:** D-103, accepted by the project owner

**Integrated predecessor:** `main` commit `fb0113d1550a1e5f55e5987ec3b33b5f960416a3`

**Implementation branch:** `codex/p2.3-equipment-datasheet-association`

## Executive Result

P2.3 check 9, `equipment_datasheet_association`, is implemented as the ninth
ordered relationship check.

For each release-required BOM equipment tag with exactly one authoritative
datasheet record, it compares the BOM `datasheet_id` with the authoritative
metadata `datasheet_id` under exact `AUTH-SPEC-001`. A mismatch produces one
high-severity `automatic_fail` finding and a release hold.

The clean development package passes all nine checks. Changing only the pump
BOM reference from `DS-P-101` to the existing valid `DS-M-101` produces the
exact expected hold, CLI exit `1`, and four consistent outputs.

## Scope Preserved

This slice added no package loader, schema, generic rule engine, protected
fixture change, public-package rerun, held-out execution, PDF/CAD extraction,
agent behavior, API, database, RAG, or frontend capability.

It did not alter checks 1-8, the accepted authority map, result-state
precedence, result schema, exit mapping, or frozen v0.2.0 kernel.

Check 9 does not test manifest reciprocity. That separate claim remains check
10.

## Implemented Contract

| Item | Implemented value |
| --- | --- |
| Check ID | `equipment_datasheet_association` |
| Position | ninth, after `equipment_datasheet_authority_presence` |
| Finding code | `EQUIPMENT_DATASHEET_MISMATCH` |
| Join key | normalized `equipment_tag` |
| Authoritative value | datasheet metadata `datasheet_id` |
| Compared value | BOM `datasheet_id` |
| Exact authority | `AUTH-SPEC-001` with every behavior-critical field matched |
| Conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |
| Evidence | authoritative metadata field, then compared BOM field |

Check 8 retains ownership of tags with zero or multiple authoritative records.
Check 9 compares only tags with exactly one authoritative record and does not
duplicate the missing-authority finding.

## Deterministic Behavior

The check sorts BOM and datasheet records by normalized semantic identifiers.
Finding identity includes the package, item, equipment tag, authority rule,
expected ID, and actual ID, but excludes physical row order and machine paths.

Tests prove:

- the clean two-equipment package passes with four exact field locators;
- the wrong-but-valid pump reference produces one exact mismatch;
- two swapped references produce findings in stable equipment-tag order;
- reversing BOM and metadata source order preserves finding identity and
  substantive values;
- missing or ambiguous authority stays owned by check 8;
- an altered `AUTH-SPEC-001` behavior field skips checks 8 and 9 against the
  authority prerequisite;
- unrelated drawing and BOM authority changes do not suppress checks 8 or 9;
  and
- a blocking package gate returns the complete nine-check skipped sequence.

## Output Inspection

### Clean run

- Run: `RUN-20260721T034251280706Z-6efeff51`
- State: `automatic_pass`
- Release hold: `false`
- Relationship checks: 9 passed, 0 failed, 0 skipped
- Findings: 0
- CLI exit: `0`
- Outputs: exactly four; schema-valid and exactly reproducible from the result

### Wrong-ID run

- Run: `RUN-20260721T034329189347Z-dc3cd02a`
- State: `automatic_fail`
- Release hold: `true`
- Relationship checks: 8 passed, 1 failed, 0 skipped
- Finding: `FND-91304712BCB20CEE`
- Code: `EQUIPMENT_DATASHEET_MISMATCH`
- Affected identifiers: `ITEM-PUMP-001`, `P-101A`
- Expected / actual: `DS-P-101` / `DS-M-101`
- CLI exit: `1`
- Outputs: exactly four; schema-valid and exactly reproducible from the result

Both successful run directories and their compact verification summary are
preserved under `scratch/verification/check9-implementation-20260720/`.

## Publication Reliability Finding

The first wrong-ID command generated the correct canonical result and three
report views, then Windows denied the final staging-directory rename with a
`PermissionError`. The workflow correctly returned internal exit `70`, did
not publish an apparently complete final run, and preserved the staged files
and `publication_failure.txt` under:

`.RUN-20260721T034252120538Z-fa89f942.publication-failed-2f10bb08`

An immediate fresh invocation against the unchanged verification package
succeeded with the exact expected check-9 result. This isolates a transient
Windows publication-finalization risk, not an evaluator or check-9 defect.

The event is recorded as `IMP-019`. It should be resolved before check 10 by a
separate bounded stabilization decision rather than hidden inside this rule
slice.

## Verification

- relationship/result/report/CLI focused set: 88 passed;
- full regression suite: 299 passed, 1 expected Windows skip;
- full-suite coverage: 87.86%, above the 80% CI floor;
- repository case validation: 5/5;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- frozen portfolio demo replay: 2/2.

The clean and successful fault outputs were independently schema-validated,
and all three report views reproduced exactly from their canonical
`package_result.json`.

## Practical Value

The product can now distinguish a package that merely contains one datasheet
record per equipment tag from a package whose BOM actually points to that
authoritative record. This catches a realistic wrong-but-valid reference that
all structural gates and check 8 correctly allow through.

## Recommended Decision D-104

Accept check 9 as matching D-103 and merge this implementation.

Before check 10, authorize one narrow Windows publication-resilience block.
It should retry only the final same-volume staging rename after a transient
permission/sharing failure, never retry or overwrite a final-directory
collision, retain bounded failure behavior after retry exhaustion, and add
injected failure tests plus a repeated Windows command proof.

Continue to keep check 10, check 11, the six authority-gap claims, semantic
held-out execution, public-package reruns, and deferred multimodal/platform
capabilities blocked until their respective review gates.
