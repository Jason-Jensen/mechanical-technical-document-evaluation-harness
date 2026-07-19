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
- **P3.1:** Authorized next for pure CSV and Markdown issue-register views of `package_result.json`.
- **P2.3 and later:** Broad relationship expansion remains blocked until the first runnable audit through P3.3 is accepted.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

Implement only deterministic CSV and Markdown issue-register views from the accepted immutable package result. Do not add the release summary, CLI integration, P2.3 expansion, held-out semantics, or deferred capabilities.

## Active Work Block

- **WBS:** P3.1 evidence-linked issue register
- **Branch:** `codex/p3.1-issue-register` after the P2.4 integration closeout
- **Objective:** Render deterministic CSV and Markdown issue registers as pure views of the accepted immutable package result.
- **Definition of done:** Both views contain only canonical non-pass findings in accepted order; a clean result writes headers and zero issue rows; evidence remains machine-readable; reports do not rerun gates, checks, authority, state, or holds; malformed result input fails closed; focused/full tests, validation, Ruff, coverage, and control evidence pass.

Next action: implement only the bounded P3.1 CSV and Markdown issue-register views. P3.2 release summary, P3.3 CLI, P2.3 expansion, and deferred capabilities remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
