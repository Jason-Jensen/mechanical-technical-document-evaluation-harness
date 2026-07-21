# P4.2 Replacement Freeze Review

**Version:** 0.3.0

**Date:** 2026-07-21

**WBS:** P4.2 held-out replacement freeze

**Authority:** D-110

**Proposed decision:** D-111

**Branch:** `codex/p4.2-held-out-replacement-freeze`

**Authorized base main:**
`ea45dcf30fa37d06de2816b6928ca91cec53df94`

**Frozen evaluator behavior:** `4cf9fe8`

## Executive Result

The materially distinct replacement held-out family is authored, structurally
verified, hash-frozen, independently verified, and imported as an exact opaque
copy. It contains eight scenarios in a synthetic industrial belt-conveyor
drive-station domain. The implementation context did not inspect protected
values or scenario package content.

No semantic evaluator execution has occurred. The family is not authorized
for execution until the project owner accepts D-111.

## Frozen Family

- **Family ID:** `FAM-HO-CONVEYOR-DRIVE-042`
- **Benchmark revision:** `P4.2-RF-20260721-01`
- **Repository root:**
  `benchmarks/package_assurance/held_out/conveyor_drive_station_v1`
- **Scenarios:** 8 opaque tokens
- **Family files:** 210
- **Scenario-package files:** 200, exactly 25 per scenario
- **Non-freeze inventory files:** 208
- **Producer bundle SHA-256:**
  `da154aed47e2f1b26625c40fa0987cf9f4bd872285e5fec13907d1b85f408867`
- **Protected bundle SHA-256:**
  `2b383800ad66625117febe883282392909ec9830286adb644006fc562e282c6e`
- **Complete-family SHA-256:**
  `e619c81854d9676b5d821a752e3b00e68d0072572cef64509d5cc9132a3e6ff6`
- **Contamination status:** `frozen_isolated_pre_execution`
- **Owner acceptance:** pending
- **Semantic execution count:** 0

## Custody Evidence

The custodian received bundle `P4.2-CUSTODIAN-EA45DCF-V1`, containing only
the approved public contracts and schemas. All nine declared input files
matched their individual hashes, the path-ordered inventory reproduced
`0339f3288b7d656369d8cbddb9664b3d1b434d857aa1ebaec66ad70f711152de`,
and the external manifest reproduced
`b78fc8afc3321938252accfdefebf8681e8cd8f62842deffd6912c8460229621`.

The initial authoring context stopped before the two freeze records were
complete. Its valid authored content was preserved. Isolated recovery
custodians working inside the same authorized root removed one temporary
validator placeholder, completed 326 structural and hash checks with zero
failures, wrote the protected inventory, and wrote the public freeze record
last. The public access and attestation records disclose that recovery.

No custodian accessed evaluator code, repository tests, prior held-out values,
generated results, external filesystem content, or the network. No custodian
ran the evaluator.

## Independent Verification

A separate fresh verifier completed all 14 required controls:

- 14 passed and 0 failed;
- all eight package manifests are structurally valid;
- all eleven accepted clean relationship contracts are satisfied;
- the protected matrix satisfies the public aggregate requirements;
- seven controlled fault scenarios and one compound scenario are present;
- all required result-state categories are represented within the D-109
  boundary;
- exact finding records are present with zero wildcards;
- public leakage findings: 0;
- hash mismatches: 0;
- freeze-order violations: 0; and
- semantic executions: 0.

The independent verifier did not modify the family. Its public evidence is:

- `p4_2_replacement_independent_verification_v0.3.0.json`; and
- `p4_2_replacement_independent_verification_v0.3.0.md`.

## Import Verification

An isolated import verifier compared the frozen source and repository copy by
relative path, raw bytes, and SHA-256 without reporting package contents:

- source files: 210;
- destination files: 210;
- byte-identical files: 210;
- missing or extra files: 0;
- mismatches: 0;
- source and destination complete-family hash:
  `e619c81854d9676b5d821a752e3b00e68d0072572cef64509d5cc9132a3e6ff6`;
  and
- semantic executions: 0.

The public evidence is
`p4_2_replacement_import_verification_v0.3.0.json`.

## Prior-Family Control

The contaminated `instrument_air_module_v1` family has no working-tree diff.
It remains preserved, unexecuted, and ineligible for release held-out claims.
It must not be relabeled, repaired, deleted, or substituted for the replacement.

## Safe Repository Verification

Checks that do not enumerate or load the new replacement passed:

- focused development-benchmark and repository tests: 32 passed;
- full regression through `python -m pytest`: 319 passed and 1 expected
  Windows skip;
- coverage: 88.57%, above the 80% floor;
- repository validation: 5/5 cases;
- Ruff: pass;
- frozen v0.2.0 baseline replay: 9/9; and
- portfolio demonstration: 2/2.

The first full-suite attempt used the standalone `pytest.exe` launcher and
failed collection because the repository root was absent from that launcher's
module path. The accepted `python -m pytest` invocation passed without a code
or fixture change. No replacement scenario or protected oracle was loaded by
these checks.

## Proposed Decision D-111

**Accept the replacement freeze and authorize one controlled first semantic
run of each opaque scenario against the frozen evaluator behavior.**

Acceptance authorizes only this one-way protocol:

1. merge the reviewed freeze package and record exact `main`;
2. verify the evaluator source still matches behavior commit `4cf9fe8` and the
   imported family still matches its complete-family hash;
3. use an isolated runner that cannot read the protected oracle during
   execution;
4. invoke each opaque scenario exactly once, with no retries or tuning;
5. preserve the raw result, issue register, release summary, CLI exit, command,
   environment, and hashes before any oracle comparison;
6. give the immutable run evidence to a separate custodian for exact protected
   comparison;
7. publish only aggregate comparison evidence until the release decision; and
8. stop after the first comparison for owner review.

An invocation or infrastructure failure is still a run and its evidence must
be preserved. No rerun is authorized by D-111. Any substantive mismatch,
protected-value exposure, input change, evaluator change, missing raw output,
or hash mismatch stops P4.2 and requires a separate decision.

## Owner Review

The requested owner action is to accept or reject D-111. Until acceptance,
held-out semantic execution, oracle comparison, evaluator changes, P4.3 work,
public reruns, and release claims remain blocked.
