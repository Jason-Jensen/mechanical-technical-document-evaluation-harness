# P4.2 Second Contamination and External-Custody Gate

**Status:** Accepted; PR #64 integration pending

**Date:** 2026-07-21

**Decision:** D-112 accepted by the project owner on 2026-07-22

**Exact integrated main:** `4d2c0f5f09950929ef057ef4f0efa3d75efdf0ed`

**Frozen evaluator behavior:** `4cf9fe8`

**Evaluator source-tree object:** `d0c3f128ee13898cdcd6fc12c6d6ad5877649551`

## Executive Summary

PR #63 integrated the accepted replacement family. During the local
fast-forward, Git printed a recursive change summary containing release-family
paths and comparative per-file insertion counts. No family file was
deliberately opened and no semantic audit ran, but the summary exposed
scenario-level structural differences before first execution.

An independent fresh governance review classified this as a pre-run semantic
side channel under D-110 and IMP-023. The replacement must therefore be
preserved unchanged and unexecuted, but it cannot support a v0.3.0 held-out
release claim. D-111 remains historically accepted; its execution authority
stopped unused.

## Preserved Facts

- PR #63 merged at exact `main` `4d2c0f5`.
- The evaluator source tree at exact `main` matches behavior commit `4cf9fe8`.
- Replacement semantic execution count is zero.
- No oracle comparison, retry, tuning, evaluator change, or fixture change
  occurred.
- The exposed instrument-air family and the conveyor-drive replacement remain
  unchanged and release-ineligible.

## Root Cause

Repository import happened before the first semantic run. This made ordinary
Git operations, pull-request diffs, checkout summaries, local tooling, and CI
potential metadata channels even when protected contents were not opened.
Suppressing one command's output would reduce one symptom but would not remove
the architectural exposure.

## Required External-Custody Design

A new materially distinct replacement must remain outside the ordinary
repository until first-run evidence is frozen:

1. A fresh authoring custodian receives only approved public contracts and
   creates the producer packages plus protected oracle.
2. A separate verifier reproduces inventories and hashes without publishing
   scenario mappings or protected values.
3. An oracle-blind staging custodian receives exact evaluator source and only
   the opaque producer packages. It receives no protected oracle.
4. A fresh runner invokes each opaque scenario exactly once and freezes the
   command, environment, exit, stdout, stderr, four outputs, and hashes.
5. A separate comparison custodian receives the frozen run evidence and
   protected oracle and publishes only aggregate results.
6. Only after the raw first-run evidence is preserved may archival family
   assets be imported into the repository under a separate reviewed decision.

The ordinary implementation checkout, its CI, and this agent context must not
receive a pristine family directory, path inventory, archive listing, diff
summary, or per-file statistics before the first run.

## Accepted Decision D-112

**Classify `FAM-HO-CONVEYOR-DRIVE-042` as contaminated for release held-out
claims after pre-run Git metadata exposure; preserve it unchanged and
unexecuted; and authorize one materially distinct replacement under the
external-custody design above.**

Acceptance authorizes replacement authoring, structural/hash verification,
oracle-blind staging, and preparation of a new freeze review. It does not
authorize semantic execution. A separate owner decision remains mandatory
after the new external freeze is independently verified.

## Execution Boundary

Acceptance authorizes the external-custody replacement sequence only after PR
#64 integration and exact-main verification:

- do not execute or further inspect either release-ineligible family;
- author the materially distinct replacement only in fresh isolated external
  custody;
- independently verify and hash-freeze it without repository import;
- prepare and independently verify an oracle-blind runner bundle without
  executing it;
- do not compare any protected oracle;
- do not retry, tune, or change evaluator behavior;
- do not restore protected-fixture tests to implementation CI; and
- do not begin P4.3 or make held-out release claims.

## Owner Acceptance

The project owner accepted D-112 on 2026-07-22. A separate owner decision is
still mandatory after the new external freeze and oracle-blind staging are
independently verified and before any semantic invocation.
