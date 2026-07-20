# Dual Public-Package Audit Failure Review

**Date:** 2026-07-20
**WBS:** P2.3 - Controlled public-package audit execution
**Branch:** `codex/p2.3-dual-public-package-audit-execution`
**Execution authority:** accepted D-098
**Integrated preparation baseline:** PR #50, exact `main` `7009fe2`
**Status:** stopped for stabilization review; OpenFlexure audit not executed

## Executive Conclusion

The first real-package audit exposed an evaluator defect before any report was
published. The NASA/JPL package was unchanged and structurally loadable, but
the evaluator could not serialize its own findings for intentionally blank BOM
references. It returned internal exit `70` instead of the expected
`missing_authoritative_information` exit `3`.

This is useful failure evidence. The strict result schema prevented malformed
findings from becoming an apparently valid audit record. The correct response
is a narrow evaluator stabilization, not changing the public packages or
weakening the result schema.

## Controlled Execution

The accepted NASA/JPL package tree was reverified immediately before execution:

`52aedc3eaf6753305dbf29d01366f324dd959fe57e14ace6295e62f3801fd8ce`

The accepted 1,144-row mapping log was also frozen at:

`d1d910f02a89830f551e9daf949e48931471320e3764551fe3718a441125a9ec`

The unchanged command was:

```text
mech-eval audit-package . scratch/prep/osr-v4/package --runs-dir scratch/public-package-audit-runs/osr-v4
```

Expected result:

- package state `missing_authoritative_information`;
- release hold `true`;
- CLI exit `3`;
- four immutable outputs.

Actual result:

- internal CLI exit `70`;
- package-result schema validation failure;
- zero published outputs;
- OpenFlexure execution stopped.

Local ignored evidence is preserved under
`scratch/public-package-audit-runs/osr-v4-failed-20260720`.

## Root Cause

The accepted package mappings explicitly require unavailable BOM
`drawing_number`, `datasheet_id`, and `specification_id` values to remain blank.
They must not be replaced with invented identifiers.

The P2.1 identifier gate currently treats all three columns as required
canonical identifiers whenever a BOM row exists. For NASA/JPL, 58 rows times
three blank references produced 174 `CANONICAL_IDENTIFIER_INVALID` findings in
the `automatic_fail` state.

Those findings then used the invalid blank value itself as an
`affected_identifier`. The canonical package-result schema correctly rejects
blank affected identifiers. Atomic publication therefore stopped before it
could create any result or report file.

The defect has two connected parts:

1. **Presence semantics:** an absent optional relationship reference is being
   treated as a malformed present identifier.
2. **Finding representation:** an invalid source value is being copied into a
   result field reserved for valid canonical identifiers.

The raw invalid or missing value already has a precise evidence locator. It
does not need to be promoted into `affected_identifiers`.

## Cross-Package Confirmation

The OpenFlexure audit was not executed. A read-only gate diagnostic confirmed
the same deterministic defect before result construction:

| Observation | NASA/JPL | OpenFlexure |
| --- | ---: | ---: |
| BOM rows | 58 | 33 |
| Expected missing-authority findings | 1 | 1 |
| Blank-identifier findings | 174 | 99 |
| Relationship checks skipped | 7 | 7 |
| Audit executed | Yes, stopped internally | No |

The OpenFlexure package tree remains unchanged at:

`71656da77b469ec3f688b0d936201fbd7be5218edda5a99fc59edcce4a87b29b`

## What Must Not Be Done

- Do not add placeholder or sentinel drawing, datasheet, or specification IDs.
- Do not delete the blank fields from the accepted traceability record.
- Do not weaken the canonical result schema to permit blank identifiers.
- Do not change the authority map to suppress the missing-authority hold.
- Do not rerun NASA/JPL or execute OpenFlexure before a reviewed fix is merged.

Each of those actions would hide the real source gap or weaken accepted result
quality.

## Recommended Stabilization

Make the smallest evaluator change that restores the accepted distinction
between a missing optional reference and a malformed present identifier:

1. Explicitly classify the three BOM relationship-reference fields as optional
   at the identifier-syntax gate.
2. Skip syntax validation only when those optional values are exactly blank.
3. Continue to fail any nonblank malformed value automatically.
4. Never place an invalid source value in canonical
   `affected_identifiers`; use a valid parent row identifier when available or
   an empty list, while preserving the raw value in evidence.
5. Add synthetic public-shape regression coverage through the full CLI and all
   four outputs.
6. Keep every existing package, authority map, schema, check, and result-state
   precedence rule unchanged.

## Stabilization Acceptance Criteria

The fix is reviewable only when all of the following pass:

- blank optional BOM references do not fail the identifier gate;
- mandatory `item_id` and `equipment_tag` values remain strict;
- a nonblank malformed optional reference still produces an automatic hold;
- every invalid-identifier finding remains valid under the package-result
  schema and preserves the raw value in evidence;
- a synthetic missing-authority package publishes exactly four outputs with
  state `missing_authoritative_information` and exit `3`;
- all existing focused and full regression tests remain green; and
- both accepted public package tree hashes remain unchanged.

## Recommended Decision D-099

Accept this failed run and root-cause classification as valid learning
evidence. Authorize a separate narrow identifier/result-contract stabilization
block using the acceptance criteria above. Require review and integration of
that fix before authorizing a NASA/JPL rerun or the first OpenFlexure audit.

Checks 8-11, held-out semantics, PDF/CAD extraction, public-package content
changes, and deferred platform capabilities remain blocked.
