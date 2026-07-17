# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Accepted on 2026-07-16. Benchmark and acceptance policy are frozen.
- **P1.1:** Accepted and locally integrated at commit `42ad037`.
- **P1.2:** Accepted at commit `f26ed27`; clean development fixture is the frozen predecessor baseline.
- **P1.3:** Accepted at commit `4b7516e`; the recorded `frozen_pre_tuning` status is active without changing protected content.
- **P2.1:** Stabilization and implementation accepted by the user on 2026-07-17; accepted feature chain pushed on `codex/stabilization-improvement-loop`.
- **P2.2:** Three ordered drawing checks are integrated through PR #33 at exact `main` commit `8d7f314`. The fourth, `drawing_register_metadata_file_reference`, is defined at `d46d56f` on green draft PR #34 and was accepted on 2026-07-17; implementation remains sequenced behind PR #34 integration and exact merged-tree verification.
- **P2.3 and later:** Blocked pending the preceding gates.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

The three implemented drawing checks are integrated and verified on exact `main` commit `8d7f314`. The user accepted the `drawing_register_metadata_file_reference` v0.3.0 definition at `d46d56f` on 2026-07-17. Integrate PR #34 and verify exact merged `main`; only then implement that accepted fourth check on its dedicated branch. Every other relationship, package-state routing, report, CLI behavior, and semantic held-out evaluation remains blocked.

## Active Work Block

- **WBS:** P2.2 drawing file-reference definition integration
- **Branch:** `codex/p2.2-drawing-file-reference-definition`
- **Objective:** Integrate the accepted fourth-slice definition through PR #34 and establish the exact implementation baseline.
- **Definition of done:** Acceptance is recorded; PR #34 merges with green checks; exact merged-tree verification passes; protected assets remain unchanged; and the scoped implementation branch is created from that exact baseline.

Next action: merge PR #34, verify exact `main`, then implement only the accepted fourth check. No semantic held-out run or tuning is authorized.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
