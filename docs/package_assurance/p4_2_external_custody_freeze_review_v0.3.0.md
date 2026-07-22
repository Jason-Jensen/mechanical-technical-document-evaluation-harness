# P4.2 External-Custody Freeze Review

**Version:** 0.3.0

**Date:** 2026-07-22

**WBS:** P4.2 external held-out freeze

**Authority:** D-112

**Decision:** D-113 proposed for owner review

**Branch:** `codex/p4.2-external-held-out-freeze`

**Authorized main:** `0264db7d0c904452ffdec83c51f74103185a8e8d`

**Frozen evaluator behavior:** `4cf9fe8`

**Frozen evaluator source tree:** `d0c3f128ee13898cdcd6fc12c6d6ad5877649551`

## Executive Result

The external held-out family and its oracle-blind one-shot runner are ready for
an owner freeze decision. The family remains outside Git. No scenario has been
executed, no protected comparison has occurred, and the semantic execution
count is zero.

Family revision 2 passed 68 of 68 independent structural, oracle-contract,
hash, freeze, leakage, and matrix controls. Runner revision 6 passed 53 of 53
independent static controls, including one-shot execution, bounded environment,
read-only inputs, zero pre-existing artifacts, and pre/post hash identity.

This result proves readiness to run, not evaluator performance. The actual
held-out outcomes remain unknown.

## Frozen Family

- **Family:** `FAM-HO-CRANE-HOIST-901`
- **Benchmark revision:** `BR-D112-HOIST-001`
- **Accepted family revision:** `FR-D112-HOIST-002`
- **Scenarios:** 8 opaque packages
- **Complete files:** 163
- **Scenario-package files:** 152
- **Independent controls:** 68 passed, 0 failed
- **Producer SHA-256:**
  `b77f35e06e0400211264768a40a1b7bf7c9fe4fb842a691baf4566fcf48e10ab`
- **Protected SHA-256:**
  `1876455a0abb18a6a2ad10f9f57667a54a520201b209e16f8d9cc624654c280d`
- **Complete-family SHA-256:**
  `141f3d1b84691d9d87852e46754d139e5bd5d77b487b1b75c49964e969089190`
- **Pre/post family hash:** identical
- **Semantic executions:** 0

The aggregate expected matrix contains one automatic pass, five automatic
fails, one missing-authority state, one tool-failure state, and eight held
findings. Scenario assignments and protected values remain undisclosed.

## Oracle-Blind Runner

- **Producer capsule:** `PC-D112-HOIST-002`
- **Accepted runner:** `D-112-runner-revision-6`
- **Static files:** 186, all read-only
- **Staged inputs:** 181
- **Evaluator sources:** 27
- **Schemas:** 2
- **Package roots:** 8
- **Package files:** 152
- **Independent controls:** 53 passed, 0 failed across 7 categories
- **Complete runner-bundle SHA-256:**
  `54d01f7b9ef98893e9d1b05565829a7ac3d07eb58c8caf274465d944059598fb`
- **Runner script SHA-256:**
  `c2ab9b56e7fe81e9dda489fde83fbc3bf00e25a433e45a9cbdfdc75ffcc0beae`
- **Pre/post runner hash:** identical
- **Runtime, evidence, marker, result, report, and execution-freeze artifacts:** 0
- **Semantic executions:** 0

The runner rejects any pre-existing marker or evidence, verifies all input
hashes before invocation, writes durable global and per-scenario markers before
execution, invokes each package exactly once in sequence, and preserves command,
bounded environment, timestamps, exit, stdout, stderr, and either all four
outputs or complete failure evidence. It has no retry, reset, resume, overwrite,
oracle, comparison, tuning, or mutation path.

The child environment uses only six optional operating-system bootstrap keys
and five fixed Python values. It does not forward `PATH`, credentials, proxy
variables, user-profile values, or the full inherited environment.

## Failed Controls Preserved

The custody sequence failed closed several times before reaching the accepted
revisions:

- family revision 1 failed three independent oracle-contract categories;
- instruction-only staging exposed a generic protected-path entry without
  opening protected content;
- an early runner freeze used a noncanonical inventory order;
- runner revision 3 retained external control text and lacked read-only control
  attributes;
- runner revision 4 stopped before copying when its selected copy operation was
  unavailable; and
- runner revision 5 forwarded the full inherited environment.

Every failed family or runner revision remains preserved, unchanged, and
unexecuted. The failures did not change evaluator or producer bytes. They prove
that the independent gates stopped real custody defects before the first run.

## Claim Boundary

The repository may claim only that:

- a materially distinct synthetic external family is structurally frozen and
  independently verified;
- a matching oracle-blind one-shot runner is independently verified; and
- no semantic execution or protected comparison has occurred.

The repository may not yet claim held-out detection accuracy, false-positive
performance, release fitness, external validation, engineering approval, or
successful benchmark execution.

## Safe Repository Verification

Verification that does not enumerate or load a release-eligible held-out family
passed on the review branch:

- focused package benchmark, publication, CLI, and result tests: 40 passed;
- protected-safe full regression: 313 passed and 1 expected Windows skip;
- coverage: 88.57%, above the 80% floor;
- repository validation: 5/5 cases;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- portfolio demonstration: 2/2.

The protected held-out fixture test module remained excluded. Baseline and demo
replay evidence was written under generated `runs/` paths rather than tracked
historical evidence.

## Proposed Decision D-113

**Accept external family revision `FR-D112-HOIST-002` and runner revision
`D-112-runner-revision-6`; authorize exactly one semantic invocation for each
of the eight opaque packages against frozen evaluator behavior `4cf9fe8`; then
freeze all raw evidence and perform one separate protected comparison.**

Acceptance would authorize only this one-way sequence:

1. integrate this aggregate review and record exact `main`;
2. verify the external family, producer, runner, evaluator, and schema hashes;
3. invoke the frozen runner once, with any invocation or infrastructure failure
   consuming the affected scenario;
4. preserve all raw evidence before any protected access;
5. give immutable run evidence to a separate comparison custodian;
6. publish only aggregate comparison evidence; and
7. stop for owner review before import, tuning, rerun, or release claims.

D-113 would not authorize retries, evaluator or fixture changes, repository
family import, protected-fixture CI restoration, P4.3 work, public-package
reruns, or deferred product capabilities.

## Owner Review Point

The owner should accept or revise D-113. Until acceptance is recorded, the
runner remains inert and semantic execution remains prohibited.

The machine-readable aggregate evidence is
`p4_2_external_custody_freeze_evidence_v0.3.0.json`.
