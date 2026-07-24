# P4.2 New External Family Preparation Gate

**Version:** 0.3.0

**Date:** 2026-07-24

**Status:** D-119 accepted and complete; D-120 owner review required

**Predecessor:** D-118 benchmark-authoring corrective action complete

## Accepted Decision D-119

Authorize one genuinely new, materially distinct, entirely synthetic external
benchmark family to be authored and quality-controlled outside Git by isolated
custodian roles.

D-119 tests the effectiveness of the D-118 correction. It does not
authorize the official benchmark execution used for performance claims.

## Authorized Scope

D-119 authorizes only:

1. create one new family from accepted public contracts without reading or
   copying any prior family, protected asset, or expected value;
2. keep producer packages, protected target plans, authoring records, and
   scenario-level validation results outside Git and outside evaluator
   implementer access;
3. require distinct package IDs for every scenario and exact package-to-
   authority scope equality;
4. run `VAL-PKG-AUTHORING-001` on every scenario inside custody;
5. use `VER-PKG-TARGET-REACHABILITY-001` with the protected target plan;
6. require exactly one clean scenario to pass all mandatory gates;
7. require each fault scenario to reach every protected target with no earlier
   unplanned blocker;
8. preserve every rejected authoring or verification revision without repair
   in place;
9. freeze public, producer, protected, and verification inventories only after
   the controls pass;
10. return only public-safe aggregate hashes and the redacted reachability
    attestation to the implementation context;
11. obtain a fresh static reviewer who did not author the family or implement
    the evaluator; and
12. return a separate D-120 execution decision with exact identities and zero
    official benchmark invocations.

Any custodian authoring preflight is quality-control evidence only. It must be
counted and disclosed separately from the later official benchmark run, and
its scenario-level outputs may not be used to tune evaluator behavior.

## Definition of Done

D-119 is complete only when:

- rights, provenance, material distinction, and custody separation are
  documented;
- every package passes or is intentionally bounded by the public validator;
- clean-gate and protected target reachability pass;
- the exact D-117 authority-scope defect is absent from every scenario;
- all failed revisions and preflight counts are preserved;
- an independent reviewer reproduces public hashes and freeze controls;
- no protected target, expected finding, value, or scenario mapping enters Git
  or the implementation context;
- `NC-002` has effectiveness evidence but remains open until the later official
  run and owner closure review; and
- D-120 returns for explicit owner review before official execution.

## Explicit Exclusions

D-119 does not authorize:

- repair, rerun, reset, reuse, or reinterpretation of any consumed family;
- access to historical protected values by an author or implementer;
- evaluator gate, relationship, router, or oracle changes;
- tuning from authoring-preflight outcomes;
- import of the new family or protected records into Git;
- an official external benchmark invocation or performance comparison;
- P4.3 release work; or
- release, accuracy, generalization, conformity, certification, or engineering
  correctness claims.

## Owner Decision Record

The project owner accepted D-119 exactly as bounded above on 2026-07-24.
Acceptance authorizes the isolated preparation and quality-control work only.

Official execution still requires D-120. `AIR-003`, `AIR-008`, `AIR-011`,
`NC-002`, and the release hold remain open.
