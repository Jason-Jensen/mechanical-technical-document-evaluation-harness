# Mechanical MVP v1 Baseline Report

## Purpose

This is a harness-verification baseline. It demonstrates that the deterministic evaluators accept reference-equivalent structured artifacts and reject a small curated set of known defects. It is not evidence of AI-model or agent performance.

## Benchmark controls

- Benchmark: `MECHANICAL-MVP-V1`
- Executed at: `2026-07-05T23:16:20.198892+00:00`
- Development cases: 4/4 oracle checks passed
- Held-out cases: 1/1 oracle checks passed
- Fault injections detected as expected: 4/4
- Raw result records: `runs/baseline-mvp-v1/BASELINE-20260705T231620Z`

MECH-003 is reported separately as held-out. It was historically seen during case authoring and is not claimed to be a pristine blind test case.

## Oracle verification suite

| Scenario | Split | Case | Score | Evaluator result |
|---|---|---|---:|---|
| `oracle-development-mech-001` | development | MECH-001 | 1.00 | pass |
| `oracle-development-mech-002` | development | MECH-002 | 1.00 | pass |
| `oracle-development-mech-004` | development | MECH-004 | 1.00 | pass |
| `oracle-development-mech-005` | development | MECH-005 | 1.00 | pass |
| `oracle-held_out-mech-003` | held_out | MECH-003 | 1.00 | pass |

## Fault-injection suite

| Scenario | Case | Score | Failure modes | Expectation |
|---|---|---:|---|---|
| `mech-002-unit-error` | MECH-002 | 0.75 | UNIT_ERROR | met |
| `mech-002-incomplete` | MECH-002 | 0.00 | INCOMPLETE_DELIVERABLE | met |
| `mech-004-revision-error` | MECH-004 | 0.80 | WRONG_REVISION | met |
| `mech-005-unit-error` | MECH-005 | 0.65 | UNIT_ERROR, FAILURE_TO_VERIFY | met |

## Interpretation

The oracle suite establishes an evaluator-integrity upper bound: reference-equivalent artifacts can traverse the candidate contract, deterministic gates, weighted checks, and immutable result-record path successfully.

The fault-injection suite demonstrates intended detection for unit conversion, incomplete deliverable, revision, and verification failures. The sample is deliberately small and curated; no statistical generalization is claimed.

## Limitations

- No model or agent generated the oracle artifacts.
- Fault coverage is representative, not exhaustive.
- MECH-003 was frozen only after initial authoring and review.
- Engineering outputs still require qualified human review.
