# P4.2 Held-Out Contamination and Replacement Gate

**Date:** 2026-07-21

**WBS:** P4.2 definition and held-out control recovery

**Branch:** `codex/p4.2-held-out-benchmark-definition`

**Frozen evaluator main:** `5a4d57e534bd5e900abac3c455cd484ef083e972`

**Decision status:** D-110 accepted by the project owner on 2026-07-21

**Integration:** PR #62 at exact `main`
`ea45dcf30fa37d06de2816b6928ca91cec53df94`

## Executive Result

P4.1 and D-109 are accepted and integrated through PR #61 at exact `main`
`5a4d57e`. P4.2 semantic execution has not begun.

While preparing the P4.2 execution definition, the current implementation
agent enumerated held-out path names and opened the top-level
`freeze_record.json` and `family_review.md`. Those records disclose scenario
conditions, expected package states, fault identifiers, and protected-asset
references. No value from `protected/` or a scenario `expected/` file was
surfaced to or inspected by the implementation context, no held-out package
was evaluated, and no evaluator behavior changed.

Section 15 of the accepted acceptance plan nevertheless classifies expected
condition or answer-key exposure to a rule implementer after freeze as
contamination for release claims. The existing instrument-air family must
therefore remain unchanged and unexecuted for release evidence. A materially
distinct replacement family is required before P4.2 can continue.

## Exposure Record

### Exposed

- repository path names beneath the existing held-out family;
- `ACCESS_CONTROL.md`;
- `family_metadata.json`;
- `freeze_record.json`;
- `family_review.md`; and
- `material_distinction.md`.

The exposed records included scenario names, expected state classes, fault
labels and identifiers, package hashes, and protected-asset names and hashes.

### Not Exposed Or Changed

- no `protected/*.json` value was surfaced to or inspected by the
  implementation context;
- no scenario `package/expected/*.json` value was surfaced to or inspected by
  the implementation context;
- no held-out package input file was opened for diagnosis;
- no held-out audit or comparison was run;
- no result from this family exists;
- no evaluator, gate, check, authority, normalization, schema, fixture, or
  oracle was changed after exposure; and
- the accepted freeze-set hash remains
  `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884`.

This is a governance contamination event, not evidence of an evaluator
failure or a fixture defect.

After this record was created, the repository's existing hosted CI ran
`tests/test_held_out_package_fixtures.py`. Those legacy integrity tests load
protected fixture JSON internally but do not print or otherwise expose its
values to the implementation context, and they do not invoke the package
evaluator. This opaque automated access does not restore or worsen the already
conservative release classification. Future release-eligible replacement
families must be excluded from implementation-branch CI that loads protected
assets until their first raw semantic run is preserved.

## Required Classification

The existing family `FAM-HO-INSTRUMENT-AIR-001` must be treated as:

- preserved and read-only;
- unexecuted;
- contaminated for v0.3.0 release held-out claims due to pre-run oracle
  metadata exposure;
- ineligible for P4.2 release acceptance percentages or pass/fail claims; and
- optionally reusable later as disclosed development regression material only
  through a separate decision.

Its files, hashes, and historical P1.3 acceptance record must not be edited to
hide the exposure or restore a held-out label.

## Accepted Decision D-110

The project owner accepted the following recovery path on 2026-07-21:

1. record the existing family as contaminated for release claims without
   editing or executing it;
2. keep evaluator behavior frozen at exact integrated `main` `5a4d57e` while
   the replacement is authored and frozen;
3. authorize a fresh, isolated benchmark-custodian task to author a materially
   distinct replacement family from public contracts only;
4. prohibit that custodian task from reading evaluator implementation,
   development oracles, prior held-out oracle content, or generated results;
5. require one clean package, at least six controlled fault packages, at least
   four release-blocking faults, and one compound precedence package using
   only the four genuine semantic states accepted by D-109;
6. keep producer-visible package inputs and protected expected assets in
   separate paths and roles;
7. freeze exact family, scenario, package, and oracle hashes before any
   execution;
8. require project-owner acceptance of the replacement freeze record before
   the first semantic run; and
9. execute each replacement scenario once at the frozen evaluator commit,
   preserving raw outputs before a custodian-only exact comparison.

This is required by the accepted contamination policy. Waiving the policy or
running the exposed family as though it remained held out is not recommended.

## Replacement Family Boundary

The replacement must be materially distinct from both the development pump
skid and the exposed instrument-air family in:

- equipment or assembly domain;
- canonical identifiers and values;
- package size and relationship topology;
- record ordering and fault placement;
- controlled-file layout and naming;
- revision convention; and
- authority-rule data shape within the already accepted contract.

It must not add a new evaluator rule, authority meaning, schema feature, or
deferred D-108 claim. It may only exercise the accepted eight gates, eleven
relationship checks, state router, four publications, and D-109 claim
boundary.

## Role Separation

The replacement authoring task must be a fresh isolated context with these
permissions:

- read accepted workflow, schema, authority, and acceptance contracts;
- create synthetic package inputs and protected expected assets in an isolated
  worktree;
- run structural fixture validation that does not invoke the evaluator; and
- produce hashes and a freeze record for project-owner review.

It must not:

- read evaluator source or tests;
- read development or exposed held-out expected assets;
- run the package evaluator before freeze acceptance;
- enter implementation-branch CI or tests that load protected replacement
  assets before the first raw run is preserved;
- receive prior benchmark output as guidance; or
- change the frozen evaluator.

The implementation agent may build a generic execution wrapper before the
replacement oracle is visible, but may not author or inspect the replacement
oracle. The benchmark custodian may compare results only after the first raw
run is complete and preserved.

## First-Run Protocol

After replacement freeze acceptance:

1. verify the evaluator commit, replacement freeze-set hash, clean worktree,
   and unchanged protected assets;
2. rerun the accepted P4.1 development benchmark at the same evaluator commit;
3. stage only producer/evaluator-visible files for each replacement scenario;
4. execute each scenario exactly once and preserve all raw packages, logs,
   exits, and four-output publications before comparison;
5. after every raw run exists, let the benchmark custodian compare exact
   expected and actual states, holds, findings, controls, evidence, and output
   hashes;
6. report clean, fault, state-routing, false-positive, false-negative,
   misclassification, and evidence-completeness results separately; and
7. stop before any evaluator or fixture change.

A rerun is permitted only for a documented infrastructure or invocation
failure when the oracle remained hidden, no behavior or input changed, and the
failed run is preserved. A substantive mismatch contaminates the replacement
for further held-out release use; it becomes development evidence and another
materially distinct replacement is required after any fix.

## Acceptance Criteria For This Definition Block

- PR #61 integration and exact `main` are recorded.
- The exposure and non-exposure boundaries are explicit.
- The existing family remains byte-unchanged and unexecuted.
- D-110 records the required release-claim classification.
- Replacement authority, isolation, minimum matrix, freeze, run count,
  comparison, failure, and rerun rules are explicit.
- D-109's four-state semantic boundary remains unchanged.
- D-110 is accepted and integrated. D-111 was accepted but its execution
  authority stopped unused after the replacement's repository integration
  exposed pre-run metadata. P4.2 semantic execution remains blocked pending
  proposed recovery decision D-112.

## Stop Boundary

The replacement freeze package is reviewed in
`p4_2_replacement_freeze_review_v0.3.0.md`. PR #63 integrated it at exact
`main` `4d2c0f5`, but Git's change summary exposed scenario-level structural
metadata before execution. The independent governance disposition and proposed
external-custody recovery are controlled in
`p4_2_second_contamination_and_external_custody_gate_v0.3.0.md`. Until D-112 is
accepted:

- do not execute the exposed held-out family;
- do not open any additional file in its `protected/` or `expected/` paths;
- keep `tests/test_held_out_package_fixtures.py` excluded from implementation-branch
  CI until the replacement first-run evidence is frozen;
- do not edit, relabel, delete, or move either exposed family;
- do not implement or tune evaluator behavior;
- do not author or import another replacement; and
- do not begin P4.2 semantic execution, P4.3 release work, or held-out claims.
