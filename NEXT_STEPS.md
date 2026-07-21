# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

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
- **P4.1:** D-109 accepted on 2026-07-21. Revision `P4.1-DEV-1` at implementation `4cf9fe8` passes 22/22 development scenarios twice on Windows and the hosted Linux CI gate, covers all eight gates and eleven checks, and is ready for PR #61 integration.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Gate

P4.1 and D-109 are accepted. The executable matrix, exact normalized four-output oracles, two-run repeatability, failed-evidence preservation, development-only boundary, and bounded four-state claim are frozen pending PR #61 integration. P4.2 remains a separate protected gate.

## Active Work Block

- **WBS:** P4.1 acceptance and integration closeout
- **Branch:** `codex/p4.1-development-benchmark`
- **Objective:** Prove the accepted structured evaluator against one clean package and controlled development faults without exposing or tuning against held-out semantics.
- **Definition of done:** The clean baseline hash is verified; all eight gates and eleven checks have direct fault coverage; every scenario runs twice; exact states, exits, holds, control statuses, findings, evidence, and four-output publications match frozen oracles; generated and protected assets remain separated; regression is green; D-109 is accepted.

Next action: integrate PR #61, record the exact merged `main`, and define the separate P4.2 held-out execution gate. Held-out semantic execution, public reruns, protected-asset changes, and deferred capabilities remain blocked until that gate is accepted.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
