# P4.2 External First-Run Result Review

**Version:** 0.3.0

**Date:** 2026-07-22

**WBS:** P4.2 external held-out first run

**Authority:** D-113 accepted by the project owner on 2026-07-22

**Decision:** D-114 accepted by the project owner on 2026-07-22

**Branch:** `codex/p4.2-external-held-out-first-run`

**Exact integrated main:** `6a74c74a8331f92342008bff8dd376124148eb36`

**Frozen evaluator behavior:** `4cf9fe8`

**Frozen evaluator source tree:** `d0c3f128ee13898cdcd6fc12c6d6ad5877649551`

## Executive Result

The D-113 one-shot sequence was followed exactly, but it did not produce a
usable semantic benchmark result. All frozen identities passed preflight. The
runner was invoked once, all eight scenarios were attempted once, and all eight
attempts ended with exit `70` before any complete four-output publication.

The independently verified failure class is an internal error in the atomic
publication layer. The lower-level cause is not available in the captured
failure evidence. All eight attempts are consumed and may not be rerun under
D-113.

The protected comparison therefore classified the benchmark as
`not_evaluable_due_to_output_publication_failure`. This is an operational
failure, not proof of a semantic evaluator mismatch. Accuracy, exact-state
performance, finding accuracy, false positives, and false negatives are all
undefined. A release hold is mandatory.

## Controlled Execution

- Preflight checks: 27 passed, 0 failed.
- Static files and read-only coverage: 186/186.
- Input identities: 181/181 matched.
- Runner invocations: 1.
- Scenarios expected, attempted, completed, and consumed: 8/8/8/8.
- Semantic process invocations: 8.
- Process exits: exit `70` for all eight attempts.
- Complete four-output sets: 0/8.
- Result states available: 0/8.
- Infrastructure/tool failures: 8/8.
- Retry, reset, resume, rerun, overwrite, deletion, and tuning: none.

The static runner, evaluator, schemas, and producer inputs remained unchanged
after execution.

## Raw-Evidence Freeze

The runner froze 40 raw-evidence files at
`2026-07-22T19:41:02.9651574Z`. Their aggregate SHA-256 is
`5d45bfa31299aeae5fa9bf7ea3084f8f86835713d709d08d0f91a98bb18d3b21`.

A fresh oracle-blind verifier reproduced the static identities, one-shot
markers, eight complete failure records, marker-before-invocation order,
absence of retries, output absence, and the raw-evidence hash. It found zero
aggregate mismatches with the execution summary and no post-freeze mutation.

The shared sanitized failure classification is:

- error class: `ERROR [INTERNAL]`;
- component: evaluator package-audit atomic publication layer; and
- category: internal output-publication tooling failure before complete atomic
  publication.

No lower-level exception type, operating-system error, or failing publication
operation was available in the captured evidence. Diagnosis must therefore use
non-held-out development evidence rather than speculation or a held-out rerun.

## Protected Comparison

Protected access began at `2026-07-22T20:06:34.0381290Z`, after the raw freeze
and independent verification. The comparison completed at
`2026-07-22T20:08:47.8323650Z`.

The protected benchmark contains eight scenarios with this aggregate expected
state distribution:

- `automatic_pass`: 1;
- `automatic_fail`: 5;
- `missing_authoritative_information`: 1;
- `extraction_or_tool_failure`: 1; and
- the remaining two result states: 0.

It contains eight exact high-severity findings across seven held scenarios.
All eight expectations mapped to one consumed raw attempt, but zero semantic
outputs existed to compare. Consequently:

- comparable scenarios: 0;
- not evaluable: 8;
- exact-state matches or mismatches: undefined;
- exact-finding matches or mismatches: undefined;
- false positives and false negatives: undefined; and
- accuracy: undefined.

The raw evidence, protected records, and complete family all had identical
pre/post hashes after comparison.

## Evidence Identities

- Static runner bundle:
  `54d01f7b9ef98893e9d1b05565829a7ac3d07eb58c8caf274465d944059598fb`
- Runner script:
  `c2ab9b56e7fe81e9dda489fde83fbc3bf00e25a433e45a9cbdfdc75ffcc0beae`
- Input inventory:
  `0b7b37b6f048d295b76bfd90877b52c00eef9ec617750bcc76585325b51c1f8f`
- Raw evidence:
  `5d45bfa31299aeae5fa9bf7ea3084f8f86835713d709d08d0f91a98bb18d3b21`
- Protected records:
  `1876455a0abb18a6a2ad10f9f57667a54a520201b209e16f8d9cc624654c280d`
- Complete family:
  `141f3d1b84691d9d87852e46754d139e5bd5d77b487b1b75c49964e969089190`

The public aggregate source records are frozen outside the repository:

- execution JSON: `502de2d8...b9574`;
- execution Markdown: `d67716a3...c5f5`;
- independent verification JSON: `ec2005f8...a50f0f`;
- independent verification Markdown: `ab4f2282...a7053`;
- protected comparison JSON: `20bdbf9d...ab70b7`; and
- protected comparison Markdown: `a6962ed3...55f6d1`.

## Claim Boundary

The project may claim that the controlled one-shot sequence, raw-evidence
freeze, independent verification, and separate protected comparison were
completed without retry or mutation.

The project may not claim held-out semantic performance, detection accuracy,
false-positive or false-negative performance, benchmark success, release
fitness, compliance, engineering approval, or external validation.

The family, runner, raw evidence, and comparison records remain outside Git and
must be preserved unchanged. The consumed family may not be rerun or reused as
fresh held-out evidence.

## Accepted Decision D-114

**Accept the D-113 evidence as a valid, immutable failed-run record; classify
the benchmark as not evaluable and release-held; prohibit any rerun or reuse of
the consumed family; and authorize a bounded development-only stabilization
block for the atomic publication failure.**

Acceptance authorizes only:

1. reproduce the publication failure using non-held-out development or public
   synthetic packages under the same bounded child environment;
2. identify the exact publication stage and lower-level failure cause;
3. add a non-held-out end-to-end publication sentinel that must create all four
   outputs before any future one-shot runner can be frozen;
4. improve sanitized failure evidence with an exact stage code and available
   exception or operating-system classification;
5. implement the smallest publication-layer correction without changing
   semantic gates, checks, state precedence, package fixtures, or protected
   expectations; and
6. return with regression evidence and a separate external-benchmark recovery
   definition.

D-114 does not authorize a held-out rerun, a new held-out family, protected
asset changes, semantic evaluator changes, P4.3 work, public-package reruns,
repository import of custody assets, or any release claim.

## Owner Acceptance

The project owner accepted D-114 on 2026-07-22 with the instruction to merge
PR #67, accept D-114, and continue working. This acceptance authorizes the
bounded development-only stabilization above. It does not alter or retry the
consumed D-113 evidence.

The resulting implementation and separate recovery definition are reviewed in
`p4_2_publication_stabilization_review_v0.3.0.md`.

The machine-readable aggregate evidence is
`p4_2_external_first_run_result_evidence_v0.3.0.json`.
