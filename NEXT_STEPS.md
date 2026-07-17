# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Accepted on 2026-07-16. Benchmark and acceptance policy are frozen.
- **P1.1:** Accepted and locally integrated at commit `42ad037`.
- **P1.2:** Accepted at commit `f26ed27`; clean development fixture is the frozen predecessor baseline.
- **P1.3:** Accepted at commit `4b7516e`; the recorded `frozen_pre_tuning` status is active without changing protected content.
- **P2.1:** Stabilization and implementation accepted by the user on 2026-07-17; accepted feature chain pushed on `codex/stabilization-improvement-loop`.
- **P2.2:** The revision slice is integrated at `5866212`; the metadata-presence slice is integrated at `36338c0`; the reverse metadata-without-register authority definition is integrated at `6d1f2f2`, and implementation `8eb431d` is ready for review on draft PR #33.
- **P2.3 and later:** Blocked pending the preceding gates.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

The accepted `drawing_register_metadata_revision` and `drawing_register_metadata_presence` v0.3.0 slices are implemented and integrated. The accepted `drawing_metadata_register_authority` definition was integrated through PR #32 at exact `main` commit `6d1f2f2`; its narrow implementation is complete at `8eb431d` and awaits user review. Every other relationship, package-state routing, report, CLI behavior, and semantic held-out evaluation remains blocked.

## Active Work Block

- **WBS:** P2.2 drawing-metadata register-authority implementation review
- **Branch:** `codex/p2.2-drawing-metadata-register-authority-implementation`
- **Objective:** Implement and prove only the accepted `drawing_metadata_register_authority` v0.3.0 behavior.
- **Definition of done:** The third check and exact evidence are implemented; temporary-copy faults prove clean, one-missing, all-missing, repeatability, ordering, and prerequisite behavior; the full verification contract passes; protected assets remain unchanged; and a review PR is ready for explicit acceptance.

Next action: review and accept, revise, or reject draft PR #33 and implementation commit `8eb431d`. The new third check routes an unbacked metadata revision claim to `missing_authoritative_information`, places a release hold, and preserves exact claim plus searched-register evidence. Verification passes 40 focused tests, 211 full-suite tests with one expected skip, repository validation 5/5, Ruff, 85.18% coverage, and two green GitHub CI runs. No semantic held-out run or tuning occurred.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
