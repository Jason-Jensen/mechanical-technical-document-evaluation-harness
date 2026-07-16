# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Accepted on 2026-07-16. Benchmark and acceptance policy are frozen.
- **P1.1:** Accepted and locally integrated at commit `42ad037`.
- **P1.2:** Accepted at commit `f26ed27`; clean development fixture is the frozen predecessor baseline.
- **P1.3:** Complete and integrity-verified on `feature/package-fixtures`; user acceptance and pre-tuning freeze activation are pending.
- **P2.1 and later:** Blocked pending P1.3 acceptance and held-out freeze.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Current Authorization

The user explicitly accepted P1.2 and authorized P1.3. That work is complete locally, but the authorization does not extend to P2 evaluator behavior.

## Active Work Block

- **WBS:** P1.3, held-out package and fault variants
- **Branch:** `feature/package-fixtures`
- **Definition of done:** Met locally. `FAM-HO-INSTRUMENT-AIR-001` contains one clean package and seven controlled variants, including seven release-blocking variants, an `evaluator_uncertainty` case, and a compound precedence case. Exact protected oracles, 31 relationship goldens, per-scenario inventories, material-distinction and contamination controls, and freeze-set hash `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884` are verified. Focused tests passed 50 with one expected Windows symlink skip; the full suite passed 170 with the same skip.

Next action: review and accept P1.3, which activates the recorded pre-tuning freeze without editing protected content. Then authorize P2.1 as a separate package-gate work block. Source adapters, mandatory gates, evaluator behavior, and all deferred capabilities remain outside this work block until acceptance.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
