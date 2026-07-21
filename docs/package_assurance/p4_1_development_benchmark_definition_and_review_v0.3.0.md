# P4.1 Development Benchmark Definition and Review

**Date:** 2026-07-21

**WBS:** P4.1 - Add regression tests and fault-injection coverage

**Branch:** `codex/p4.1-development-benchmark`

**Starting main:** `b4399747fa1c54e0cebbed3694eb51edfcebae88`

**Benchmark implementation:** `4cf9fe8d36c689ea46f38300b0e7b88b31d74c1e`

**Decision:** D-109 accepted by the project owner on 2026-07-21

## Executive Result

The first complete development benchmark is implemented and passing.

- 22 controlled package scenarios were generated from the accepted clean
  pump-skid baseline.
- Every scenario ran twice, for 44 complete audits.
- All 44 audits published exactly four immutable outputs outside the versioned
  benchmark tree.
- All 22 scenario pairs were substantively identical after removing only run
  ID and run metadata.
- The clean scenario produced no findings.
- All eight mandatory gates have a direct failing scenario.
- All eleven accepted relationship checks have a direct failing scenario.
- Every observed state, CLI exit, hold, finding-code list, failed/skipped
  control list, and normalized four-output hash matched its frozen oracle.
- Producer-hidden `expected/` assets were not copied into any evaluator input.
- No held-out package content or oracle was read or executed by this runner.

The generated acceptance evidence is under
`runs/p4.1-development-acceptance-4cf9fe8-final/`. It names exact evaluator
commit `4cf9fe8d36c689ea46f38300b0e7b88b31d74c1e` and is intentionally ignored
runtime evidence, not a versioned benchmark definition. A prior invocation at
`runs/p4.1-development-acceptance-59bccca/` was stopped by the command host's
short timeout and remains preserved as non-authoritative failure evidence. The
completed `59bccca-final` local run was superseded after hosted CI exposed the
cross-platform issue described below.

## What Was Added

The versioned definition is
`benchmarks/package_assurance/development/pump_skid_clean_v1/development_benchmark_v1.json`.
It freezes:

- benchmark revision `P4.1-DEV-1`;
- accepted baseline hash
  `a4b278e5bd20f3b64a85d52c478747b1115e15bbaf63b19bf47f5dffddfaf31a`;
- 22 globally identified scenarios and package IDs;
- one exact, reviewed mutation per seeded condition;
- exact expected states, exits, holds, finding codes, and control statuses;
- one SHA-256 oracle over the complete normalized four-output publication for
  each scenario;
- two executions per scenario;
- the six P2.3 claims deferred by D-108; and
- the prohibition on P4.1 held-out semantic execution.

The runner is
`src/mech_eval_harness/package_assurance/development_benchmark.py`, with the
operator command in
`scripts/run_package_assurance_development_benchmark.py`.

The runner:

1. verifies the accepted clean package-tree hash before mutation;
2. stages a complete package without `expected/` assets;
3. assigns a unique scenario package ID;
4. applies only a named, code-reviewed development mutation;
5. runs the real package evaluator and publication path twice;
6. preserves the generated package and every raw run;
7. compares the exact normalized publications and declared expectations; and
8. writes JSON and Markdown benchmark reports.

It refuses to overwrite an existing output directory, rejects outputs inside
`benchmarks/`, and reports a selected scenario subset as unscored. There is no
command that rewrites or automatically blesses the versioned oracle.

## Scenario Coverage

| Coverage area | Result |
|---|---:|
| Clean full-package scenarios | 1/1 |
| Seeded fault scenarios | 21/21 |
| Mandatory gate failure coverage | 8/8 |
| Relationship check failure coverage | 11/11 |
| Repeated-run pairs identical | 22/22 |
| Exact normalized oracle matches | 22/22 |
| Required output publications | 44/44 |
| Hidden expected directories staged | 0 |

The scenario set includes malformed manifest, unsupported manifest version,
missing source, missing and contradictory authority, missing controlled file,
invalid canonical identifier, duplicate identifier, invalid revision,
incomplete evidence contract, and one direct failure for each relationship
check. The missing-drawing-metadata scenario intentionally expects both the
primary drawing finding and its dependent equipment-on-drawing finding; this
is recorded rather than treated as an unexpected false positive.

## Exact Oracle Boundary

The runner removes only root `run_id` and `run_metadata` from
`package_result.json`. It replaces the run ID token in the two Markdown views.
It does not remove package identity, versions, fingerprints, control results,
findings, evidence, messages, output declarations, CSV content, or report
semantics. The canonical SHA-256 therefore detects missing findings, extra
findings, evidence drift, ordering changes, classification changes, and output
rendering changes.

The readable expectations remain alongside the hash so a hash cannot hide an
incorrect state, exit, hold, finding family, or failed/skipped control list.
Any legitimate evaluator change must first fail this benchmark and then use a
separate reviewed oracle-change decision. A failing run is evidence; the
golden is never loosened merely to recover a pass.

## Cross-Platform Stabilization

The first hosted Linux execution failed only the malformed-manifest exact
oracle. The sanitized error path was `<package_root>\package_manifest.json` on
Windows and `<package_root>/package_manifest.json` on Linux, which changed the
stable finding ID and all three finding-bearing views. The evaluator outcome,
state, hold, finding code, controls, and evidence locator were otherwise the
same.

Commit `4cf9fe8` makes the existing portable-error boundary emit POSIX path
separators on every operating system, adds direct assertions for missing and
malformed manifests, and updates only that scenario's publication hash. The
complete matrix then passed under local Python 3.12 and 3.14, and both hosted
Linux CI jobs passed. `IMP-022` retains the rule that a one-platform oracle
pass is not sufficient evidence.

## Acceptance-Plan Variance

P0.2 originally required one complete package scenario for each of the six
result states. The accepted eight gates and eleven P2.3 checks can currently
produce four states through a real package audit:

- `automatic_pass`;
- `automatic_fail`;
- `missing_authoritative_information`; and
- `extraction_or_tool_failure`.

The result router and stable CLI contract support and test all six states, but
none of the accepted package gates or relationship checks emits a genuine
`engineering_review_required` or `evaluator_uncertainty` finding. Creating
such benchmark results by patching stored output, mocking the evaluator, or
using an unrelated generic error would be false evidence. Adding genuine
semantic triggers would reopen P0/P2 behavior after D-108 closed the pilot to
the eleven proven checks.

This difference was not hidden or solved by weakening an oracle. It is the
main P4.1 management decision.

## Accepted Decision D-109

The project owner accepted the following bounded v0.3.0 benchmark
interpretation on 2026-07-21:

1. require full-package development scenarios for the four states the accepted
   evaluator can genuinely produce;
2. require exhaustive router and CLI-exit regression for all six states;
3. disclose that `engineering_review_required` and `evaluator_uncertainty`
   have contract coverage but no v0.3.0 end-to-end semantic trigger;
4. prohibit claims that the pilot detects review-routed or ambiguity-routed
   engineering conditions;
5. defer new semantic triggers to a later, separately accepted authority and
   check expansion; and
6. freeze P4.1 only after the full regression suite and this implementation
   are accepted.

This was accepted over reopening P2 now. It keeps the first release honest,
small, and useful while preserving the two states for future capabilities.
It is a controlled variance from P0.2, not an assertion that the original
six-state full-package criterion was met.

The accepted claim boundary is now frozen for P4.1. Any future requirement for
six full-package semantic paths must reopen P0/P2 through a separate decision;
the benchmark must never manufacture those states.

## Verification

Completed during implementation:

- focused benchmark tests: 5 passed;
- development acceptance benchmark: 22/22 scenarios, 44/44 complete audit
  publications, 22/22 repeatable pairs, 22/22 exact oracle matches;
- full frozen regression suite: 319 passed, one expected Windows skip, 88.57%
  coverage;
- repository validation: 5/5 cases passed;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9 passed, with generated evidence kept
  under `runs/`;
- portfolio demonstration: 2/2 passed; and
- hosted Linux CI: both push and pull-request jobs passed after the
  cross-platform oracle correction; and
- original accepted package-tree hash: unchanged.

The final exact-commit acceptance report records status `passed` and evaluator
commit `4cf9fe8d36c689ea46f38300b0e7b88b31d74c1e`. Final diff review and workbook
closeout were completed before the branch was published for acceptance.

## Stop Boundary

D-109 and P4.1 are accepted and PR #61 is integrated at exact `main`
`5a4d57e`. Until P4.2 is separately authorized:

- do not execute protected held-out semantics;
- do not open protected held-out expected results for diagnosis;
- do not tune evaluator behavior against held-out outcomes;
- do not change the accepted clean fixture or its expected assets;
- do not implement any D-108 deferred claim; and
- do not execute P4.2 held-out semantics or begin release work.
