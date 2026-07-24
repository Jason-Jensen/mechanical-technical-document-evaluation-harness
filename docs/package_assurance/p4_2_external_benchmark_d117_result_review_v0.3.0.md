# P4.2 D-117 External Benchmark Result Review

**Version:** 0.3.0

**Date:** 2026-07-23

**Status:** D-117 complete; D-118 owner review required

**Authority:** D-117 accepted by the project owner on 2026-07-23

**Branch:** `codex/p4.2-external-benchmark-first-run`

**Exact integrated main:** `04d919f98f412fd0951cc804ce1a95f2ce078920`

**Frozen evaluator:** `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`

## Executive Result

The D-117 one-shot sequence completed without an operational failure. The
frozen runner was invoked once, all eight opaque scenarios were attempted once,
and every attempt published a complete, schema-valid four-output audit package.
The raw evidence was frozen, independently verified without the oracle, and
then compared in a separate protected custodian context.

The comparison exposed a benchmark-family authoring defect. Every scenario's
authority map applied to the family ID instead of its package ID. The accepted
public contract explicitly requires a package-specific value. The evaluator
therefore correctly failed the mandatory authority gate in all eight packages
and skipped every downstream relationship check.

This is useful fail-closed product evidence, but it is not a valid benchmark of
the intended downstream checks. The family is consumed and may not be fixed and
rerun as fresh held-out evidence.

## Controlled Execution

- Execution ID: `EXEC-D117-R4-20260724-01`
- Family: `FAM-D116-CIM-20260723-01`
- Runner: `RUNNER-D116-CIM-20260723-04`
- Authorization SHA-256:
  `f7547399932cb819d2e99a970261203c28807452f7f5444a4dbf038191ead2e7`
- Runner invocations: 1
- Authorized and completed attempts: 8/8
- Runner process exit: `0`
- Child exits: eight exit `1` results
- Complete four-output publications: 8/8
- Retry, resume, repair, overwrite, tuning, or second invocation: none
- Oracle access inside the runner: none
- Protected comparison inside the runner: none
- Static evaluator and producer inputs changed: no

The child exit values are consistent with the eight observed
`automatic_fail` results. They are not, by themselves, evidence of benchmark
accuracy.

## Raw-Evidence Freeze

The frozen D-117 raw set contains 73 read-only files with aggregate SHA-256
`f9bc8135c1ee0d6a5d472eff7d438972811f31477f38de3678f8d8074790cb5c`.
It includes the exact authorization, permanent consumption marker, command,
stdout, stderr, exit, publication, environment, attempt order, and static
pre/post records.

Oracle-blind verifier revision 3 passed:

- controls: 14/14;
- attempts verified: 8/8;
- complete publications: 8/8;
- schema-valid package results: 8/8;
- raw aggregate reproduced exactly;
- static pre/post identity: exact;
- protected paths accessed: 0; and
- oracle values loaded: 0.

Verifier revisions 1 and 2 are preserved as improvement evidence. Revision 1
used the wrong field name for the frozen static count. Revision 2 treated a
parent runtime label as a recursive evidence scope, used the wrong documented
scenario-order encoding, and expected a different Markdown Boolean rendering.
Neither verifier failure changed the raw evidence or invoked the semantic
runner.

The accepted raw verification is `VER-D117-RAW-20260724-03`. Its JSON SHA-256
is `def6db6aac3f5c259e7b86d5a8d1780734b9c9e05882845f552925495bb9b250`.

## Oracle-Blind Actual Facts

Before protected comparison, the verified raw outputs contained:

- state distribution: 8 `automatic_fail`;
- total findings: 8;
- finding-code distribution: 8 `AUTHORITY_SCOPE_CONFLICT`; and
- relationship checks executed: 0.

These were observed results, not expected values or a performance conclusion.

## Protected Comparison

Comparison `CMP-D117-R4-20260724-01` bound the protected oracle to the exact
raw aggregate and accepted raw-verification hash. It reported:

- comparable scenarios: 8/8;
- not evaluable at the file/state-comparison level: 0/8;
- exact state matches: 7/8;
- exact finding matches: 0/8;
- expected finding true positives: 0/7;
- false negatives against intended target findings: 7/7;
- unexpected findings: 8/8 actual findings;
- clean-package false positives: 1/1;
- intended downstream target checks executed: 0/7; and
- exact combined state-and-finding matches: 0/8.

The apparent 7/8 state match is non-diagnostic. Seven expected failure
scenarios and the shared unintended authority failure all route to
`automatic_fail`, but none of the intended target findings was reached.

Raw, protected, producer, and complete-family pre/post hashes remained exact.
The public comparison JSON SHA-256 is
`742132ce03b6375fb8a6d0bfa11165cc59b1c36c70ae2ca5e2b6d55231387c19`.
No scenario-level protected condition or expected value enters Git.

## Root Cause

The public replacement-custodian contract states that each authority map must
set `applies_to` to its scenario package ID. All eight frozen authority maps
instead contain `FAM-D116-CIM-20260723-01`.

The D-116 author and freeze checks validated schemas, files, rights, hashes,
separation, and oracle coverage, but did not enforce this public semantic
contract. That omission allowed a shared baseline defect to pass 51/51 freeze
controls.

The evaluator behavior is not the defect. `GATE-PKG-AUTHORITY-001` correctly
identified the mismatch and failed closed before relationship checks.

## Nonconformity and Claims

`NC-002` records the ineffective benchmark-authoring freeze control. `AIR-003`
continues to hold release because no unconfounded external relationship
benchmark exists. `AIR-011` is reopened because a gate package was accepted
with an overstated readiness claim. D-118 remains pending.

The project may claim:

- one-shot execution, complete publication, raw freeze, independent raw
  verification, and separated protected comparison completed;
- the evaluator consistently caught the real authority-scope conflict; and
- the improvement loop identified why the intended benchmark was invalid.

The project may not claim:

- downstream relationship-check accuracy, sensitivity, specificity, or
  generalization from this family;
- release readiness;
- external independent assurance;
- engineering correctness or sign-off; or
- permission to repair, rerun, tune, or reuse the consumed family.

## Repository Verification

The closeout revision passed:

- AI-governance tests: 22/22;
- protected-safe full regression: 340 passed and one expected Windows skip at
  88.33% coverage;
- repository validation: 5/5 cases;
- Ruff;
- development benchmark: 22/22 scenarios;
- publication sentinel: four schema-valid outputs;
- frozen v0.2.0 baseline: 9/9 with generated evidence under `runs/`; and
- portfolio demo: 2/2.

The first full-suite invocation used an unnecessarily long Windows temp root.
Its nested development-benchmark publications crossed the tested path budget,
leaving 21 scenario results unpublished and producing one suite failure. That
run is preserved. The exact unchanged revision passed under the required short
`runs/t117f` temp root. `IMP-039` makes the short-root invocation a permanent
closeout control.

## Next Decision

The proposed
[D-118 corrective-action gate](p4_2_benchmark_authoring_corrective_action_gate_v0.3.0.md)
would accept D-117 as consumed evidence and authorize a bounded
benchmark-authoring quality correction. It would not authorize another
external family or semantic execution; those require a later separate gate.
