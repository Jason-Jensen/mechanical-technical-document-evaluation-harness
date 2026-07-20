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
- **P2.3:** Definition is authorized for the remaining BOM, equipment, datasheet, specification, and revision relationship slices. Implementation remains blocked pending definition acceptance.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

Define only the ordered P2.3 relationship slices, exact authority dependencies, evidence, states, holds, prerequisites, and negative tests. Do not implement a P2.3 rule, execute held-out semantics, or add deferred capabilities before definition acceptance.

## Active Work Block

- **WBS:** P2.3 relationship-expansion definition
- **Branch:** `codex/p2.3-relationship-expansion-definition` after the P3.3 integration closeout
- **Objective:** Freeze a small, ordered implementation sequence for BOM/equipment, datasheet/specification, and revision checks using the accepted authority map and runnable audit path.
- **Definition of done:** The definition states each check's exact source and target, accepted authority rule, prerequisites, pass/fail/skip behavior, finding fields, result state and hold, positive and negative development tests, implementation order, exclusions, and acceptance gate. It does not change code, schemas, fixtures, goldens, or held-out content.

Next action: review and accept the bounded P2.3 relationship-expansion definition before the first implementation slice. Semantic held-out execution and deferred capabilities remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
