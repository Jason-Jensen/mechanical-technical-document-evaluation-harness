# Publication Resilience Stabilization Review

**Date:** 2026-07-21

**Decision authority:** D-104, accepted by the project owner

**Integrated predecessor:** `main` commit
`7146b232efafbc6994d1b7bcd71069f604fc6125`

**Implementation branch:** `codex/p2.3-publication-resilience`

## Executive Result

The final package-audit publication rename now tolerates a short-lived
permission or sharing lock without weakening immutable-run behavior.

Publication makes at most five final-rename attempts. The four waits are fixed
at 50, 100, 200, and 400 milliseconds, for a maximum added wait of 0.75
seconds. Only `PermissionError` qualifies for retry.

An existing final run, any other operating-system error, or a permission error
that outlasts the retry budget follows the existing fail-closed path. No final
run is overwritten, an incomplete publication is not presented as complete,
and retry exhaustion still returns CLI exit `70` with preserved evidence.

## Scope Preserved

This block changes only the final same-parent staging-directory rename and its
tests. It does not retry:

- package loading, gates, relationships, result routing, or serialization;
- output rendering or file writes;
- staging-directory creation;
- final-directory collisions; or
- non-permission operating-system failures.

It does not change the accepted result schema, output set, package-state exits,
authority map, fixtures, goldens, held-out assets, public-package results,
check behavior, or frozen v0.2.0 kernel.

Check 10 remains unimplemented.

## Implemented Boundary

| Condition | Behavior |
| --- | --- |
| First final rename succeeds | Publish immediately; no wait |
| Transient `PermissionError` | Retry using the next fixed delay |
| Final directory appears | Raise collision immediately; never retry or overwrite |
| Other `OSError` | Fail immediately; never retry |
| Fifth permission failure | Preserve failed publication and return the existing internal-error path |
| Retry later succeeds | Publish the original staged four-output set atomically |

The staging and final directories share the same resolved parent, so the retry
does not introduce cross-volume copying or a second publication mechanism.

## Injected Failure Proof

Four publication tests prove the retry boundary directly:

- two synthetic permission failures recover on the third attempt with the
  exact first two delays and no failed-publication directory;
- a persistent permission failure consumes all five attempts, preserves the
  staged result and failure marker, and publishes no final run;
- a final-directory collision is detected after one attempt with no wait and
  no overwrite; and
- a non-permission `OSError` fails after one attempt with no wait.

A separate CLI test injects persistent final-rename permission failures. It
proves exit `70`, no visible complete run, all four staged outputs plus
`publication_failure.txt`, and the exact `PermissionError` failure marker.

The publication and CLI focused set passes 24 tests.

## Windows Execution Proof

Twenty consecutive real `audit-package` commands ran on Microsoft Windows
against the unchanged clean development package.

- Successful commands: 20/20
- CLI exit: `0` for every command
- Package state: `automatic_pass` for every command
- Release hold: `false` for every command
- Mandatory gates: 8 passed for every command
- Relationship checks: 9 passed for every command
- Outputs: exactly four for every command
- Hidden staging or failed-publication directories: 0

The first run was `RUN-20260721T153603113434Z-ab8f3cbd`; the last was
`RUN-20260721T153614063468Z-b74ed8fd`. The compact execution summary is
preserved under
`scratch/verification/publication-resilience-20260721/`.

The real filesystem proof does not claim that the original transient lock was
reproduced. The injected tests prove the retry branches; the repeated commands
prove that the normal Windows path remains stable.

## Full Verification

- publication and CLI focused set: 24 passed;
- full regression suite: 304 passed, 1 expected Windows skip;
- full-suite coverage: 88.08%, above the 80% floor;
- repository validation: 5/5;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- frozen portfolio demo replay: 2/2.

The first and last repeated runs were inspected. Both contain exactly the four
accepted output files, `automatic_pass`, hold false, 8/8 passed gates, 9/9
passed relationships, and zero findings.

## Residual Boundary

This change reduces the chance that a short-lived Windows sharing lock blocks
a valid audit. It does not hide persistent access-control, disk, path, or
collision failures. Those continue to fail closed and require operator review.

This is the intended boundary: reliability improves without turning retries
into a substitute for diagnosing a real filesystem problem.

## Recommended Decision D-105

Accept the publication-resilience stabilization as matching D-104. Close
`I-005` as controlled and retain `IMP-019` as a permanent regression rule.

After integration, authorize only P2.3 check 10,
`equipment_datasheet_manifest_reciprocity`, under the already accepted
`AUTH-SPEC-001` contract. Keep check 11, the six authority/source gaps,
semantic held-out execution, public-package reruns, and deferred
multimodal/platform capabilities blocked until their respective gates.
