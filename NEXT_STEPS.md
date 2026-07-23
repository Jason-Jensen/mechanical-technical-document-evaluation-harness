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
- **P4.2:** D-113 is integrated through PR #65 at exact `main` `6a74c74` and consumed. Preflight passed 27/27, then one runner invocation consumed all eight scenarios with exit `70` and zero complete output sets. Independent raw verification passed with zero mismatches. D-114 is accepted and implemented on `codex/p4.2-publication-stabilization`; the exact staging-path defect is corrected and guarded by a bounded four-output sentinel. The original benchmark remains not evaluable, and the consumed family remains prohibited from rerun or reuse.
- **G0.1:** D-115 is integrated through PR #67 at exact `main` `540a1f6`. It adopts an internal AI management and quality-control system as the highest-level repository governance. The system is ISO/IEC 42001-aligned at a public-guidance level, NIST-informed, machine validated, and explicitly not a conformity or certification claim.
- **Time tracking:** Waived prospectively; progress is gate- and evidence-based.

## Active Gate

D-115 is the active governance overlay. The D-113 one-shot sequence remains complete and immutable; its operational evidence is valid but its semantic benchmark result is not evaluable. D-114 is accepted and implemented pending integration review. Proposed D-116 is the next owner decision. The consumed family and raw evidence remain outside Git and may not be rerun.

## Active Work Block

- **WBS:** P4.2 D-114 publication stabilization
- **Branch:** `codex/p4.2-publication-stabilization`
- **Objective:** Reproduce the atomic publication failure using development-only evidence, identify its exact cause, make the smallest publication-layer correction, preserve sanitized diagnostics, and install a production-equivalent four-output sentinel.
- **Definition of done:** The pre-fix failure is reproduced without protected access; exact stage and lower-level cause are recorded; the bounded sentinel publishes four schema-valid outputs with unchanged read-only inputs; semantic behavior and protected evidence remain unchanged; regression passes; and a separate external-benchmark recovery definition returns for owner review.

Next action after D-114 closeout: review the publication correction and the proposed D-116 external-benchmark recovery gate. Held-out reruns, a new held-out family, semantic changes, P4.3 work, public reruns, imports, and release claims remain blocked until separately authorized.

## Delivery Sequence

1. P1: package model plus separate development and held-out fixtures.
2. P2: mandatory gates, relationship checks, authority resolution, and state routing.
3. P3: immutable package result, issue register, release summary, and CLI.
4. P4: fault-injection regression, benchmark execution, clean-clone acceptance, and release evidence.
5. P5: terminal-first demonstration, case study, and bounded service proof.

## Hard Stops

Do not add PDF/CAD extraction, redline editing, agent orchestration, API/database/frontend layers, observability, RAG, hosted deployment, reward models, or RL during v0.3.0.

Do not alter protected goldens, held-out packages, acceptance criteria, or failed-run evidence merely to obtain a pass.
