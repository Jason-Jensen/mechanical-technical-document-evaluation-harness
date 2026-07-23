# P4.2 Publication Stabilization Review

**Version:** 0.3.0

**Date:** 2026-07-22

**WBS:** P4.2 D-114 publication stabilization

**Authority:** D-114 accepted by the project owner on 2026-07-22

**Branch:** `codex/p4.2-publication-stabilization`

**Starting main:** `540a1f6`

## Executive Result

D-114 is implemented within its development-only boundary. The exact failure
class was reproduced without opening, listing, importing, changing, or
rerunning any held-out family.

The root cause was a Windows path-length defect in the internal staging name,
not a semantic evaluator result. The immutable final run path fit, but the
former temporary sibling repeated the full run ID and added a UUID. Under the
external-bundle output layout, that made the first staged output path 263-264
characters. Python failed the write with `FileNotFoundError` and errno `2`, and
the CLI returned `70`.

The correction shortens only internal temporary and failed-evidence sibling
names. Final immutable run IDs, output names, gates, checks, result-state
precedence, schemas, package fixtures, and protected evidence are unchanged.

## Controlled Reproduction

The reproduction used only the accepted development pump-skid package.

- The package was copied into a disposable external-bundle layout.
- Staged input files were read-only.
- The child environment omitted inherited `PATH`, credentials, proxies, and
  user-profile values.
- The output root was exactly 193 characters.
- Before correction, the full child audit returned exit `70` with no output.
- A direct probe of the first legacy staged output path at 263 characters
  returned `FileNotFoundError` with errno `2`.
- During reproduction, no protected fixture test or held-out family path was
  accessed.

This matches the D-113 operational failure class without making a new semantic
benchmark observation.

## Minimal Correction

The publication layer now:

1. uses `.tmp-<8 hex>` for the same-parent staging directory instead of
   embedding the run ID;
2. uses `.failed-<8 hex>` for incomplete staged evidence while preserving the
   run ID inside `package_result.json` and `publication_failure.txt`;
3. records the exact controlled stage code, exception type, errno, and Windows
   error when available;
4. includes the same sanitized diagnostics in the CLI error;
5. writes a short parent-level fallback failure marker if a nested marker
   cannot be created; and
6. retains the existing bounded final-rename retry policy without adding any
   new retry or overwrite behavior.

The correction affects publication mechanics only.

## Production-Equivalent Sentinel

`scripts/run_package_assurance_publication_sentinel.py` stages:

- current evaluator sources and the two required schemas;
- the producer-visible development package with `expected/` excluded;
- all static inputs as read-only files;
- a child environment limited to optional operating-system bootstrap values
  and five fixed Python values; and
- a runs-directory path of at least 193 characters that makes the former
  staged output path at least 260 characters. The accepted local evidence uses
  exactly 193 characters; longer hosted checkout roots adapt upward without
  weakening the stress condition.

The sentinel requires:

- unchanged pre/post static-input hashes and file counts;
- no inherited `PATH`, credential, or proxy values;
- child exit `0`;
- exactly one immutable run and no failed publication;
- exactly four expected outputs;
- a schema-valid `automatic_pass` result with no release hold; and
- preserved machine-readable evidence under `runs/`.

CI runs this sentinel before the protected-safe regression suite.

## Verification

- focused publication, CLI, governance, and sentinel-helper tests: 53 passed;
- publication module coverage: 91%;
- governance module coverage: 84%;
- protected-safe full regression: 340 passed, 1 expected skip, 88.48%
  coverage;
- repository validation: 5/5;
- Ruff: passed;
- P4.1-DEV-1 development benchmark: 22/22;
- frozen v0.2.0 baseline replay with a generated evidence directory: 9/9;
- portfolio demo: 2/2;
- normal AI-governance validation: passed; and
- strict release-ready validation: exit 2 as required on `AIR-003` and pending
  D-116.

Machine-readable details and generated evidence hashes are in
`p4_2_publication_stabilization_evidence_v0.3.0.json`.

## Final Scope-Audit Finding

During final status cleanup, one repository-wide `rg` command omitted the
required held-out exclusion. It traversed tracked historical held-out folders
and surfaced path names and matching hash lines from families already
contaminated and ineligible for a release benchmark.

No external D-113 custody evidence or future D-116 family was accessed, no
protected fixture test ran, and no semantic execution occurred. This does not
restore or weaken any benchmark claim. `IMP-032` now requires implementer-side
searches to exclude `benchmarks/package_assurance/held_out/**` explicitly.

## Claim Boundary

This block proves the identified publication defect is corrected under a
production-equivalent non-held-out sentinel. It does not recover or reinterpret
the D-113 semantic benchmark. The eight consumed attempts remain
`not_evaluable_due_to_output_publication_failure`.

D-114 does not authorize:

- rerunning or reusing the consumed family;
- creating or running a replacement held-out family;
- changing semantic gates, checks, precedence, schemas, or accepted fixtures;
- rerunning NASA/JPL or OpenFlexure;
- importing custody assets;
- beginning P4.3; or
- making a release or held-out performance claim.

## Next Review Gate

The separate recovery definition is
`p4_2_external_benchmark_recovery_definition_v0.3.0.md`. Its proposed D-116
decision requires owner review before any new external family work begins.
