# P4.2 External Benchmark Recovery Definition

**Version:** 0.3.0

**Date:** 2026-07-22

**Status:** D-116 complete; D-117 owner review required

**Predecessor:** D-114 publication stabilization accepted and verified

**Owner acceptance:** 2026-07-23

**Accepted predecessor main:** `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`

## Purpose

Define the smallest credible route to a new external semantic benchmark without
reusing the consumed D-113 family, weakening custody controls, or confusing a
publication test with evaluator-performance evidence.

## Decision D-116

Accept the D-114 publication correction and authorize preparation of one new,
materially distinct external held-out family and one oracle-blind runner under
independent custody. Do not authorize semantic execution until the complete
freeze package returns for a separate owner decision.

The project owner accepted this decision on 2026-07-23. PR #68 had already
merged at the exact predecessor commit above, both hosted checks were green,
and normal AI-governance validation passed with the intended `AIR-003` release
hold. This acceptance changes the preparation gate only; it does not authorize
the D-117 semantic invocation.

## Entry Criteria

The D-116 entry criteria were satisfied as follows:

1. PR #68 merged at exact `main`
   `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`;
2. the bounded publication sentinel passed locally and on hosted Linux CI;
3. focused and protected-safe full regression, repository validation, Ruff,
   frozen v0.2.0 baseline, portfolio demo, and AI-governance validation passed;
4. NC-001 corrective action is closed without removing the independent
   benchmark release hold; and
5. the consumed D-113 family, runner, raw evidence, and comparison remain
   unchanged and outside Git.

## Authorized Preparation

D-116 authorizes only:

- one materially distinct synthetic mechanical package family authored outside
  the ordinary repository;
- separate producer and protected records;
- independent structural, hash, authority, and oracle-contract verification;
- an oracle-blind runner with bounded environment and read-only static inputs;
- the accepted publication sentinel inside the final physical runner pattern;
- zero semantic executions during preparation; and
- a freeze review containing identities, hashes, controls, and the exact
  proposed one-shot command.

## Mandatory Freeze Controls

The freeze review must prove:

1. the family is materially distinct from development and all prior exposed or
   consumed families;
2. implementer-visible inputs contain no expected states, findings, severities,
   or comparison values;
3. all static files are byte-identified and read-only;
4. the sentinel runs under the same interpreter, bounded environment, output
   destination model, and atomic publication code as the future semantic run;
5. the sentinel publishes and schema-validates all four outputs while static
   hashes remain exact;
6. failure evidence captures exact publication stage and available lower-level
   classification;
7. the runner has no retry, resume, overwrite, tuning, or protected-comparison
   path; and
8. semantic execution count remains zero.

## Separate Execution Gate

After preparation, a proposed D-117 freeze decision must return to the owner.
Only D-117 may authorize one semantic invocation per opaque scenario followed
by immutable raw-evidence freeze and separate protected comparison.

## Explicit Exclusions

D-116 does not authorize:

- any D-113 rerun or reuse;
- semantic execution of the new family;
- repository import of protected or custody assets;
- evaluator semantic changes;
- public-package reruns;
- P4.3 release work;
- release, accuracy, false-positive, or false-negative claims; or
- deferred PDF, CAD, agent, API, database, RAG, or frontend work.

## Definition of Done

The recovery-preparation block is complete only when an independently verified,
zero-run freeze package and exact D-117 decision request are ready for owner
review. Polished documentation without the passing in-bundle sentinel is not
acceptable evidence.

## Closeout

The D-116 definition of done is satisfied by:

- `FAM-D116-CIM-20260723-01`, an eight-scenario synthetic family under
  separated external custody;
- `RUNNER-D116-CIM-20260723-04`, frozen at exact evaluator commit
  `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`;
- 8/8 mandatory and 51/51 detailed freeze controls;
- one development-only sentinel invocation with four schema-valid outputs;
- preserved failed runner revisions 1 through 3;
- zero opaque semantic executions, held-out publications, or protected
  comparisons; and
- an absent D-117 authorization file.

The controlling closeout records are:

- `docs/package_assurance/p4_2_external_benchmark_recovery_freeze_review_v0.3.0.md`;
- `docs/package_assurance/p4_2_external_benchmark_recovery_freeze_evidence_v0.3.0.json`;
  and
- `docs/package_assurance/p4_2_external_benchmark_execution_gate_v0.3.0.md`.
