# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Current Gate

- **P0.1:** Accepted. Workflow contract and authority-map boundary are frozen.
- **P0.2:** Reviewed and complete pending user acceptance.
- **P1 implementation:** Blocked until P0.2 acceptance is recorded.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Decision Required

Accept, revise, or reject `docs/package_assurance/acceptance_plan_v0.3.0.md` as the v0.3.0 benchmark policy.

Acceptance authorizes only P1.1. It does not authorize the full roadmap or any deferred capability.

## Next Work Block After Acceptance

- **WBS:** P1.1, package manifest schema and loader
- **Branch:** a separate package-manifest capability branch
- **Definition of done:** A versioned manifest contract validates package metadata, source inventory, identifiers, revisions, relationships, authority declarations, controlled file references, and stable missing/malformed failure behavior.

P1.1 must conform to the accepted P0.1 and P0.2 contracts. It may not silently change product or benchmark policy.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
