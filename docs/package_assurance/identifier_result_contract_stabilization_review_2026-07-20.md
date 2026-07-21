# Identifier and Result Contract Stabilization Review

**Date:** 2026-07-20
**WBS:** P2.3 - Identifier/result-contract stabilization
**Branch:** `codex/p2.3-identifier-result-stabilization`
**Decision authority:** accepted D-099
**Integrated baseline:** PR #51, exact `main` `624acce`
**Status:** implementation and synthetic proof complete; public reruns not executed

## Executive Conclusion

The first public-package failure has been corrected without changing either
public package, weakening the result schema, or relaxing malformed-identifier
handling.

The identifier gate now distinguishes an absent optional BOM relationship
reference from a malformed present identifier. Exact blanks are permitted only
for `equipment_item.drawing_number`, `equipment_item.datasheet_id`, and
`equipment_item.specification_id`. Any nonblank malformed value still creates
an `automatic_fail` release hold.

Invalid raw values remain in exact evidence locators. They are no longer copied
into the canonical `affected_identifiers` field. A valid parent row identifier
is used when one exists; otherwise the affected-identifier list is empty. The
strict package-result schema is unchanged.

## Implemented Behavior

| Input condition | Identifier gate | Result representation |
| --- | --- | --- |
| Exact blank in one of the three approved optional BOM fields | No syntax failure | Blank remains visible in source evidence |
| Whitespace-only or padded optional value | `automatic_fail` | Valid parent `item_id` is affected; raw value remains in evidence |
| Nonblank malformed optional value | `automatic_fail` | Valid parent `item_id` is affected; raw value remains in evidence |
| Invalid required row identifier | `automatic_fail` | Empty affected-identifier list; raw value remains in evidence |
| Invalid identifier inside a JSON identifier list | `automatic_fail` | Valid record identifier is affected; raw value remains in evidence |

No placeholder identifiers, sentinel values, schema exceptions, or authority
shortcuts were introduced.

## Synthetic End-to-End Proof

A temporary copy of the accepted development package was shaped like the
public inputs by blanking all three optional BOM references. One required
authority rule was then removed to create a controlled missing-authority state.

The complete `audit-package` path produced:

- package state `missing_authoritative_information`;
- release hold `true`;
- CLI exit `3`;
- exactly four published outputs;
- a passed identifier gate; and
- one schema-valid `AUTHORITY_REQUIRED_RULE_MISSING` finding.

A second temporary package used a padded, nonblank `datasheet_id`. The complete
CLI path produced:

- package state `automatic_fail`;
- release hold `true`;
- CLI exit `1`;
- exactly four published outputs;
- one `CANONICAL_IDENTIFIER_INVALID` finding;
- affected identifier `ITEM-PUMP-001`; and
- the original and normalized malformed values in evidence.

Both executions used temporary synthetic copies. Neither accepted public
package was audited.

## Changed Implementation Surface

- `src/mech_eval_harness/package_assurance/gates.py`
- `tests/test_package_gates.py`
- `tests/test_cli_audit_package.py`

No package schema, result schema, authority map, fixture, golden, held-out
asset, relationship check, state precedence rule, CLI exit mapping, or
publication contract changed.

## Verification

- focused gates/result/publication/CLI tests: 47 passed;
- full regression suite: 289 passed, 1 expected Windows skip;
- repository case validation: 5/5;
- full-suite coverage: 87.57%, above the 80% CI floor;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9;
- frozen portfolio demo replay: 2/2; and
- tracked diff check: passed.

The accepted public-package evidence was reverified after implementation:

| Package | Package files | Package tree SHA-256 | Accepted log rows | Accepted log SHA-256 |
| --- | ---: | --- | ---: | --- |
| NASA/JPL Open Source Rover v4.0.0 | 133 | `52aedc3eaf6753305dbf29d01366f324dd959fe57e14ace6295e62f3801fd8ce` | 1,144 | `d1d910f02a89830f551e9daf949e48931471320e3764551fe3718a441125a9ec` |
| OpenFlexure Microscope v7.0.0-beta5 | 58 | `71656da77b469ec3f688b0d936201fbd7be5218edda5a99fc59edcce4a87b29b` | 620 | `a8ba53e53e2d77ce742264c29aed6938c9ba89150f050e5c66da456aef1b4566` |

No new public-package run directory exists. The original NASA/JPL failure
evidence remains preserved and Git-ignored.

## Remaining Limits

This stabilization proves the corrected interface on synthetic package copies.
It does not prove that either public package will complete exactly as predicted.
Issue `I-004` therefore remains open until a controlled NASA/JPL rerun publishes
and its four outputs are inspected.

Checks 8-11, six unresolved authority/source claims, held-out semantic
execution, PDF/CAD extraction, and deferred platform capabilities remain
blocked.

## Recommended Decision D-100

Accept the D-099 implementation and synthetic proof. Merge the stabilization
PR, then authorize exactly one controlled NASA/JPL rerun from its unchanged
accepted package tree and log. Stop on any result other than the predeclared
`missing_authoritative_information` state, exit `3`, release hold `true`, and
four schema-valid outputs.

Require review of the NASA/JPL result before authorizing the first OpenFlexure
audit. Do not change either package, its authority map, expected state, or the
evaluator during that observation block.
