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
- **P2.3:** The relationship-expansion definition is accepted through PR #41; check 6 is integrated through PR #42; the behavior-preserving relationship split is integrated through PR #44 at exact `main` `56ac9d1`; check 7 is verified and ready for integration. Six authority/source gaps and checks 8-11 remain unimplemented.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

Integrate verified check 7 after green CI. Then open a development-only real-package structured-trial decision and stop until the user identifies one public, synthetic, self-authored, or explicitly authorized sanitized package. Do not begin check 8, held-out semantics, authority-gap implementation, or deferred capabilities.

## Active Work Block

- **WBS:** P2.3 check 7 implementation review and integration
- **Branch:** `codex/p2.3-bom-equipment-drawing-presence`
- **Objective:** Require each release-required BOM equipment tag to appear in drawing metadata without overclaiming item-to-drawing authority.
- **Definition of done:** Exact `AUTH-BOM-002`; clean 7/7 pass; isolated missing-tag release hold; stable evidence and identity; unchanged predecessor behavior; 35 relationship tests, 80 focused tests, 283 full-suite passes with one expected skip, validation 5/5, Ruff, 87.25% coverage, and inspected four-output clean/fault runs.

Next action: integrate check 7, then stop at the real-package structured-trial input decision. Semantic held-out execution and deferred capabilities remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
