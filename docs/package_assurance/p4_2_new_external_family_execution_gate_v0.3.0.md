# P4.2 New External Family Official Execution Gate

**Version:** 0.3.0

**Date:** 2026-07-24

**Status:** Proposed D-120 owner review

**Predecessor:** D-119 isolated preparation and static review complete

## Proposed Decision D-120

Authorize one controlled official benchmark batch for the exact D-119 family,
followed by immutable raw freeze, oracle-blind raw verification, one separate
protected comparison, and bounded owner review.

D-120 would convert the already quality-controlled family into official
benchmark evidence. It would not authorize retry, tuning, release, or P4.3.

## Exact Public Binding

The proposed authorization is limited to:

- evaluator commit
  `17830bd3aecfe6b51f6f8d983a67129757208b1c`;
- opaque family token `FAM-3178CBE96B77B3E6A998154C`;
- family content aggregate
  `69228bf06f9f1fd3035473082572e1e14b94ee3662bbcc136473f9cc19bbf69f`;
- inventory-set aggregate
  `39aa558fe14310b0f2a8be0968f097c03fc8ab28b3c00d51d016096e12f6afaf`;
- producer public handoff
  `6a89ba93934e42573a984573144d1f5dfde0efde89a99da01942663ecfc623e2`;
- D-119 public evidence
  `docs/package_assurance/p4_2_new_external_family_preparation_evidence_v0.3.0.json`;
  and
- the independent-review handoff hash recorded by the completed D-119 review.

Any identity mismatch voids D-120 before execution.

## Preconditions

Before an official invocation, the isolated custodian must:

1. reproduce all D-119 class, inventory, family, result-set, and public-handoff
   hashes;
2. confirm the frozen family and protected plan remain read-only;
3. confirm the official invocation count remains zero;
4. create one protected execution manifest that maps the eight opaque packages
   to exactly one official attempt each;
5. bind the manifest to the exact evaluator commit, output contract, bounded
   environment, and no-retry rule;
6. validate the manifest in a fresh oracle-blind context without executing a
   package;
7. publish only the manifest commitment, validation result, and zero-run count;
   and
8. stop without execution if any precondition fails.

The execution manifest, package mapping, and protected target plan remain
outside Git and outside evaluator-implementer access.

## Authorized Execution

If D-120 is accepted and every precondition passes, it authorizes only:

1. consume one write-once authorization record;
2. invoke the exact frozen evaluator once for each of the eight frozen
   packages;
3. publish exactly one four-output audit package per attempt;
4. preserve the exit, standard output, standard error, stage diagnostics, and
   output inventory for every attempt;
5. freeze all raw evidence immediately after the batch;
6. verify raw completeness, schemas, static pre/post identity, authorization
   consumption, and aggregate hashes in a separate oracle-blind context;
7. perform one protected comparison only after the raw freeze and raw
   verification pass; and
8. return a bounded result review for owner decision.

The official batch count is eight package attempts inside one consumed
authorization. No attempt may be retried, resumed, repaired, replaced, or
overwritten.

## Required Result Review

The post-run review must report, without publishing protected values:

- completed and comparable package counts;
- exact package-state agreement;
- exact finding-set agreement;
- expected finding true positives and false negatives;
- unexpected findings and clean-package false positives;
- protected target execution and reachability;
- shared blocker analysis;
- publication and tool failures separated from semantic results;
- raw, protected, and complete-family pre/post hash equality;
- every limitation and excluded claim; and
- the disposition of `NC-002`, `AIR-003`, `AIR-008`, and `AIR-011`.

Broad state agreement may not be presented without exact finding and target
metrics.

## Failure Rules

Any of these conditions stops the batch or review:

- identity, authorization, environment, or preflight mismatch;
- mutation of a frozen input;
- missing or duplicate attempt;
- incomplete four-output publication;
- schema-invalid or inconsistent result;
- protected value in raw or public evidence;
- retry, overwrite, or second authorization use;
- target blocked by an unintended earlier condition; or
- a required independent or qualified-human review is unavailable.

A stopped or failed batch is immutable evidence. D-120 never authorizes a
retry.

## Explicit Exclusions

D-120 would not authorize:

- editing, repairing, or regenerating the family or evaluator;
- using authoring-preflight results for performance claims;
- evaluator, gate, relationship, router, schema, or oracle changes;
- tuning from public or protected outcomes;
- importing packages, target plans, protected details, or raw results into
  Git;
- a second official batch;
- P4.3, release tagging, deployment, or production use;
- accuracy or generalization claims broader than the exact frozen benchmark;
  or
- engineering correctness, code compliance, independent external assurance,
  ISO/IEC 42001 conformity, or certification claims.

## Owner Review Question

Does the project owner accept D-120 exactly as bounded above?

Until acceptance, official benchmark invocations remain zero and
`AIR-003`, `AIR-008`, `AIR-011`, `NC-002`, and the release hold remain open.
