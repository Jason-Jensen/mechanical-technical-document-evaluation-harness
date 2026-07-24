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
- **P4.2:** PR #71 merged D-118 at exact `main` `17830bd`. D-119 is accepted and complete on `codex/p4.2-new-external-family-preparation`: one new isolated synthetic family passed 8/8 public validations and 7/7 protected targets, and a fresh reviewer reproduced the 322-file freeze and redaction. Official invocations remain zero. Proposed D-120 controls the one-shot official batch.
- **G0.1:** D-115 is integrated through PR #67 at exact `main` `540a1f6`. It adopts an internal AI management and quality-control system as the highest-level repository governance. The system is ISO/IEC 42001-aligned at a public-guidance level, NIST-informed, machine validated, and explicitly not a conformity or certification claim.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Active Gate

D-115 is the active governance overlay. D-113 and D-117 are consumed evidence. D-119 proves the D-118 authoring controls on one new isolated family without changing evaluator semantics. `AIR-003`, `AIR-008`, `AIR-011`, `NC-002`, and proposed D-120 hold release.

## Active Work Block

- **WBS:** P4.2 D-119 isolated new-family preparation
- **Branch:** `codex/p4.2-new-external-family-preparation`
- **Objective:** Prove the D-118 authoring controls on one genuinely new family while keeping all packages, targets, results, and authoring records outside Git and implementer access.
- **Definition of done:** Rights and custody pass; 8/8 public validations and all protected targets pass; rejected revisions are preserved; a fresh reviewer reproduces the read-only freeze and redaction; official invocations remain zero; and D-120 returns for owner review.

Next action: review and merge PR #72, whose two hosted validation jobs pass, then accept or revise proposed D-120. No official benchmark execution, evaluator tuning, P4.3, release, or performance claim is authorized before D-120 acceptance.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
