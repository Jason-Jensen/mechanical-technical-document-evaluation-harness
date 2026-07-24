# P4.2 Benchmark-Authoring Corrective-Action Review

**Version:** 0.3.0

**Date:** 2026-07-23

**Status:** D-118 implementation complete; D-119 owner review required

**Accepted predecessor main:** `2246d1a`

## Executive Result

D-118 is implemented without changing evaluator behavior and without creating
or executing another external family.

The exact D-117 authority-scope defect is now rejected by a deterministic
public package-contract command. A separate custodian verifier proves that the
clean scenario clears every mandatory gate and that each protected target can
execute without an unintended earlier blocker. Its public output contains no
scenario-to-target mapping or expected value.

`NC-002` remains contained rather than closed. The corrective control exists
and works on development-only synthetic evidence, but effectiveness must still
be demonstrated on a genuinely new, isolated family under a later gate.

## Implemented Controls

### Public validator

`VAL-PKG-AUTHORING-001`:

- reuses the accepted eight-gate implementation;
- runs no relationship check;
- reports deterministic, path-safe JSON;
- rejects package/authority scope mismatch with
  `AUTHORITY_SCOPE_CONFLICT`;
- exposes source, file, reference, identifier, revision, duplicate, and
  evidence-contract failures before freeze; and
- returns stable pass, fail, and usage exits.

### Custodian reachability

`VER-PKG-TARGET-REACHABILITY-001`:

- confines all result inputs to one custody root;
- requires schema-valid canonical package results;
- verifies exact gate and check order;
- requires all gates to pass for the clean scenario;
- identifies root failed gates rather than counting downstream skips;
- verifies protected gate or relationship targets are not skipped;
- binds public index, protected plan, result set, and protected detail by
  SHA-256;
- preserves public and protected outputs separately; and
- refuses to overwrite existing evidence.

### Operating proof

`PROOF-D118-AUTHORING-CONTROLS-001` passed all six development-only controls:

- clean public contract passed;
- relationship-fault public contract passed;
- exact D-117 scope defect rejected;
- relationship target reachable;
- unintended authority blocker rejected; and
- public attestations redacted.

The proof excluded the development expected directory and performed zero
held-out semantic executions. Generated evidence is under
`runs/d118-proof-b/`.

## Focused Verification

- New authoring-control tests: 14 passed.
- Package boundary, manifest, gate, relationship, and audit-CLI regression:
  118 passed with one expected Windows skip.
- Ruff on the new and changed implementation: passed.
- Generated proof report: passed.
- Public reachability attestation: one of one target reachable, zero blockers.
- Negative reachability attestation: zero of one target reachable, one
  unintended authority blocker, as required.
- Full protected-safe regression: 354 passed, one expected Windows skip, and
  88.02 percent coverage.
- AI governance tests: 22 passed; normal governance validation passed and
  strict release-ready validation correctly remained held.
- Repository validation: 5/5 cases passed.
- Full Ruff check: passed.
- Publication sentinel: `automatic_pass`, four outputs, 193-character runs
  path.
- Development benchmark: 22/22 scenarios passed.
- Frozen v0.2.0 baseline: 9/9 passed using a new generated evidence directory.
- Portfolio demo: 2/2 scenarios passed.

Workbook inspection and hosted Linux CI are recorded separately at work-block
closeout.

## Search-Scope Incident

During D-118 discovery, a command intended to search one governance JSON file
unexpectedly returned repository-wide matches, including protected text from a
tracked, already-consumed and release-ineligible historical held-out family.
The command was stopped from further use. No protected file was modified, no
protected fixture test was run, no external D-117 custody asset was accessed,
and no disclosed value informed the implementation or tests.

This is a recurrence of the search-scope hazard already described by
`IMP-032`, so process-only guidance was not sufficient. `IMP-040` strengthens
the prevention rule: exact-file inspection uses literal-path readers, scoped
searches name only approved roots, and future release-eligible families remain
physically outside the implementation repository through authoring,
reachability verification, and first official execution.

The incident does not restore validity to any consumed family and creates no
permission to use historical protected content.

## Nonconformity Status

`NC-002` containment is verified:

- D-116 and D-117 evidence remains unchanged;
- the consumed family remains prohibited from repair, rerun, or reuse;
- no new family was created;
- the exact defect has a repeatable rejection test; and
- the public/protected reachability separation has operating proof.

Closure requires:

1. D-119 owner authorization for a genuinely new isolated family;
2. successful public validation and protected reachability attestation for
   that family;
3. independent reproduction of the freeze controls;
4. a separate later execution decision;
5. preserved first official run and comparison evidence; and
6. owner review confirming that the corrective controls were effective.

Until then, `NC-002`, `AIR-003`, `AIR-008`, and `AIR-011` remain release holds.

## Claims Boundary

D-118 proves the corrective controls operate on development-only synthetic
evidence. It does not prove external benchmark accuracy, generalization,
engineering correctness, product release readiness, independent assurance,
ISO/IEC 42001 conformity, or certification.

## Next Decision

The proposed
`p4_2_new_external_family_preparation_gate_v0.3.0.md` requests only isolated
preparation and corrective-control verification for one genuinely new family.
It does not authorize an official benchmark execution, tuning, P4.3, or
release.
