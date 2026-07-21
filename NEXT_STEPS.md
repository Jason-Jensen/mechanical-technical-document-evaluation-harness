# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Accepted Gates

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Accepted on 2026-07-16. Benchmark and acceptance policy are frozen.
- **P1.1:** Accepted and locally integrated at commit `42ad037`.
- **P1.2:** Accepted at commit `f26ed27`; clean development fixture is the frozen predecessor baseline.
- **P1.3:** Accepted at commit `4b7516e`; the recorded `frozen_pre_tuning` status is active without changing protected content.
- **P2.1:** Stabilization and implementation accepted by the user on 2026-07-17; accepted feature chain pushed on `codex/stabilization-improvement-loop`.
- **P2.2:** Complete for the accepted vertical slice. Five ordered drawing checks are integrated through PRs #35 and #37; the exact accepted main baseline is `5571d2a`.
- **First usable audit definition:** Accepted and integrated through PR #36 at `5b32b6d`.
- **P2.4:** Accepted and integrated through PR #39 at exact `main` commit `cd9b52e`.
- **P3.1:** Accepted and integrated at exact `main` commit `8f66b12`; exact-main verification is green.
- **P3.2:** Accepted and integrated at exact `main` commit `4b848b9`; exact-main verification is green.
- **P3.3:** Accepted and integrated through PR #40 at exact `main` commit `e4080fd`; exact-main verification is green.
- **P2.3:** Complete. D-107 accepted check 11 and PR #59 merged it at exact `main` `69c0d1b`. D-108 explicitly defers the six unsupported authority/source claims and limits v0.3.0 to the eleven proven relationship checks.
- **P4.1:** Accepted and integrated through PR #61 at exact `main` `5a4d57e`. Revision `P4.1-DEV-1` at implementation `4cf9fe8` passes 22/22 development scenarios twice on Windows and hosted Linux CI and freezes the D-109 claim boundary.
- **P4.2:** D-110 integrated through PR #62 at exact `main` `ea45dcf`. Replacement `FAM-HO-CONVEYOR-DRIVE-042` is isolated, hash-frozen, independently verified 14/14, and imported byte-exact at 210/210 files. Semantic execution count is zero. D-111 owner review is pending.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Active Gate

P4.1 is integrated and frozen. D-110 recovery is complete. The replacement family reproduces complete-family hash `e619c81854d9676b5d821a752e3b00e68d0072572cef64509d5cc9132a3e6ff6`; D-111 must be accepted before one controlled first run per opaque scenario.

## Active Work Block

- **WBS:** P4.2 replacement freeze review
- **Branch:** `codex/p4.2-held-out-replacement-freeze`
- **Objective:** Publish the independently verified replacement freeze and obtain a separate owner decision before semantic execution.
- **Definition of done:** The isolated family is frozen; independent verification and byte-exact import pass; public decision/evidence records are current; the exposed prior family is unchanged; D-111 is ready for owner review; semantic execution remains zero.

Next action: owner accepts or rejects D-111 in `p4_2_replacement_freeze_review_v0.3.0.md`. Until acceptance, held-out semantic execution, oracle comparison, evaluator changes, P4.3 work, public reruns, and deferred capabilities remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
