# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Accepted on 2026-07-16. Benchmark and acceptance policy are frozen.
- **P1.1:** Accepted and locally integrated at commit `42ad037`.
- **P1.2:** Accepted at commit `f26ed27`; clean development fixture is the frozen predecessor baseline.
- **P1.3:** Accepted at commit `4b7516e`; the recorded `frozen_pre_tuning` status is active without changing protected content.
- **P2.1:** Stabilization and implementation accepted by the user on 2026-07-17; accepted feature chain pushed on `codex/stabilization-improvement-loop`.
- **P2.2:** The revision slice is integrated at `5866212`; the metadata-presence slice is integrated at `36338c0`; the reverse metadata-without-register authority definition was accepted on 2026-07-17 and awaits PR #32 integration.
- **P2.3 and later:** Blocked pending the preceding gates.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

The accepted `drawing_register_metadata_revision` and `drawing_register_metadata_presence` v0.3.0 slices are implemented, integrated, and verified on exact `main` commit `36338c0`. The user accepted `drawing_metadata_register_authority` v0.3.0 on 2026-07-17. Integrate PR #32 and verify the exact merged tree before beginning only that implementation. Every other relationship, package-state routing, report, CLI behavior, and semantic held-out evaluation remains blocked.

## Active Work Block

- **WBS:** P2.2 reverse drawing-metadata authority definition integration
- **Branch:** `codex/p2.2-drawing-metadata-orphan-definition`
- **Objective:** Integrate the accepted reverse-authority definition through PR #32 and establish an exact verified implementation baseline.
- **Definition of done:** Acceptance is recorded; PR #32 merges with green checks; exact merged-tree verification passes; protected assets remain unchanged; and only the scoped implementation branch is created.

Next action: merge PR #32, verify exact `main`, then implement only `drawing_metadata_register_authority` v0.3.0 on a fresh branch. The accepted slice routes an unbacked metadata revision claim to `missing_authoritative_information`, uses exact metadata evidence plus a header-anchored drawing-register membership snapshot, and appends one third relationship check. No semantic held-out run or tuning is authorized.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
