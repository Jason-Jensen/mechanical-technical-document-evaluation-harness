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
- **P2.3:** The relationship-expansion definition is accepted through PR #41. Check 6 is accepted and integrated through PR #42 at exact `main` `559bb81`; six authority/source gaps and checks 7-11 remain unimplemented.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

Complete a bounded behavior-preserving maintainability stabilization of the relationship implementation and focused tests. After exact regression proof, implement only check 7, `bom_equipment_drawing_presence`, under the accepted P2.3 contract. Do not alter evaluator meaning, accepted assets, authority-gap decisions, held-out semantics, or deferred capabilities.

## Active Work Block

- **WBS:** P2.3 relationship maintainability stabilization
- **Branch:** `codex/p2.3-relationship-maintainability`
- **Objective:** Reduce review and regression risk before adding checks 7-11, without changing accepted audit behavior.
- **Definition of done:** Split relationship implementation and focused tests into clear domain boundaries, preserve all six accepted checks and exact outputs, and pass focused/full regression, validation, Ruff, and coverage.

Next action: complete and integrate the no-behavior stabilization, then implement only check 7. A sanitized real-package development trial follows check 7 and requires an explicitly authorized package. Semantic held-out execution and deferred capabilities remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
