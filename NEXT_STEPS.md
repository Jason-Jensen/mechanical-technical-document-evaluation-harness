# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Accepted on 2026-07-16. Benchmark and acceptance policy are frozen.
- **P1.1:** Accepted and locally integrated at commit `42ad037`.
- **P1.2:** Accepted at commit `f26ed27`; clean development fixture is the frozen predecessor baseline.
- **P1.3:** Accepted at commit `4b7516e`; the recorded `frozen_pre_tuning` status is active without changing protected content.
- **P2.1:** Stabilization and implementation accepted by the user on 2026-07-17; accepted feature chain pushed on `codex/stabilization-improvement-loop`.
- **P2.2:** Three ordered drawing checks are integrated through PR #33 at exact `main` commit `8d7f314`. The fourth, `drawing_register_metadata_file_reference`, is defined for review only; no fourth-check implementation is authorized.
- **P2.3 and later:** Blocked pending the preceding gates.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

The three accepted drawing checks are implemented, integrated, and verified on exact `main` commit `8d7f314`. Review only the proposed `drawing_register_metadata_file_reference` v0.3.0 definition. It compares exact register/metadata drawing pairs under `AUTH-DWG-002` and does not authorize executable behavior. Every other relationship, package-state routing, report, CLI behavior, and semantic held-out evaluation remains blocked.

## Active Work Block

- **WBS:** P2.2 drawing file-reference agreement definition
- **Branch:** `codex/p2.2-drawing-file-reference-definition`
- **Objective:** Freeze one deterministic check for exact drawing pairs whose drawing-register and drawing-metadata `file_ref_id` values disagree under `AUTH-DWG-002`.
- **Definition of done:** The ten review decisions, exact wrong-but-valid development fault, evidence, exclusions, implementation acceptance tests, and adjacent declaration/reciprocity gap are reviewed; the controlling workbook is current; the diff contains no executable or protected-asset change; and a draft definition PR is ready for explicit user acceptance.

Next action: review and accept, revise, or reject the fourth-slice definition. Implementation may begin only after explicit acceptance and definition integration. No semantic held-out run or tuning is authorized.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
