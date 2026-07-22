# Execution Handoff

The detailed sequence, status, evidence, and next action are controlled in `gantt.xlsx`. This file is intentionally short so it cannot become a second schedule.

## Accepted Gates

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
- **P2.3:** Complete. D-107 accepted check 11 and PR #59 merged it at exact `main` `69c0d1b`. D-108 explicitly defers the six unsupported authority/source claims and limits v0.3.0 to the eleven proven relationship checks.
- **P4.1:** Accepted and integrated through PR #61 at exact `main` `5a4d57e`. Revision `P4.1-DEV-1` at implementation `4cf9fe8` passes 22/22 development scenarios twice on Windows and hosted Linux CI and freezes the D-109 claim boundary.
- **P4.2:** D-111 integrated through PR #63 at exact `main` `4d2c0f5`. Its Git change summary exposed scenario-level path and file-statistics metadata before first execution. Semantic execution count remains zero. The replacement is preserved unchanged and release-ineligible; D-112 external-custody recovery is proposed for owner review.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Active Gate

P4.1 is integrated and frozen. D-111 remains historically accepted, but its execution authority stopped unused when PR #63 integration exposed pre-run family metadata. Proposed D-112 preserves the second release-ineligible family and moves any new replacement to external custody through the raw first-run freeze.

## Active Work Block

- **WBS:** P4.2 second contamination and external-custody gate
- **Branch:** `codex/p4.2-held-out-second-recovery`
- **Objective:** Record the zero-run metadata exposure, preserve the affected family, and replace repository-first custody with an external first-run design.
- **Definition of done:** Exact `main` and zero-run evidence are recorded; an independent review confirms disposition; D-112 defines the external custody, staging, execution, comparison, and post-run import boundaries; project controls are current; no family content or evaluator behavior changes.

Next action: owner accepts or rejects D-112 in `p4_2_second_contamination_and_external_custody_gate_v0.3.0.md`. Another replacement, semantic execution, oracle comparison, evaluator changes, P4.3 work, public reruns, and release claims remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
