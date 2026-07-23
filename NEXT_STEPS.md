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
- **P4.2:** D-113 remains consumed and not evaluable. D-114 is integrated through PR #68 at exact `main` `3a6766f`. D-116 then prepared a materially distinct eight-scenario synthetic family and oracle-blind runner outside Git. Runner revision 4 passed 8/8 mandatory and 51/51 detailed freeze controls, including one four-output development sentinel; opaque semantic executions remain zero. D-117 is pending.
- **G0.1:** D-115 is integrated through PR #67 at exact `main` `540a1f6`. It adopts an internal AI management and quality-control system as the highest-level repository governance. The system is ISO/IEC 42001-aligned at a public-guidance level, NIST-informed, machine validated, and explicitly not a conformity or certification claim.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Active Gate

D-115 is the active governance overlay. D-113 remains complete, immutable, and not evaluable. D-114 is integrated. D-116 is complete with a verified zero-run freeze. Proposed D-117 is the next owner decision. Neither the consumed D-113 family nor the new D-116 opaque family may be executed without its exact gate authority.

## Active Work Block

- **WBS:** P4.2 D-116 external benchmark recovery freeze
- **Branch:** `codex/p4.2-external-benchmark-recovery-preparation`
- **Objective:** Prepare one materially distinct external family and one oracle-blind runner under separated custody, prove publication in the final physical pattern, and preserve zero opaque executions.
- **Definition of done:** The family, runner, hashes, rights, authority/oracle contract, leakage controls, read-only state, one-shot behavior, and development sentinel are independently verified; failed revisions are preserved; D-117 returns with an exact command; and no opaque scenario is executed.

Next action: review this branch and proposed D-117. Do not create the authorization file or run the exact command until D-117 is explicitly accepted. P4.3, public reruns, semantic changes, imports, and release claims remain blocked.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
