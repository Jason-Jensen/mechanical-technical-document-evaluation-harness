# Execution Plan From Here

## Work Block P0.1 — Workflow Contract and Authority Map

**Objective:** Freeze what the package audit evaluates and how authority is resolved.
**Expected duration:** 2 focused hours.
**Branch:** `feature/package-assurance-contract`
**Definition of done:** The reviewed contract specifies inputs, canonical IDs, source precedence, gates, checks, result states, release holds, evidence, exclusions, and human-review boundaries.

Actions:

1. Integrate the modernization package and updated Gantt.
2. Review `docs/package_assurance/workflow_contract_v0.3.0.md` line by line.
3. Resolve the ten P0.1 review questions.
4. Create an accepted `authority_map.json` example after the hierarchy is agreed.
5. Record decisions in the Gantt Decision Register.
6. Do not write package-loader or rule-engine code yet.

## Work Block P0.2 — Acceptance Plan and Benchmark Protocol

**Objective:** Define how v0.3.0 will be proven before implementation.
**Expected duration:** 2 focused hours.
**Definition of done:** Development and held-out split, fault matrix, release gates, evidence requirements, false-negative review, claim boundaries, and stop conditions are frozen.

Actions:

1. Review and finalize `acceptance_plan_v0.3.0.md`.
2. Define the minimum fault matrix.
3. Define package-state and CLI-exit-code expectations.
4. Establish the newly authored held-out package protocol.
5. Record the release-gate decision.

## Work Blocks P1.1–P1.3 — Package Model and Fixtures

Build only after P0 is accepted:

1. Versioned package manifest schema and loader.
2. Development synthetic package with clean and corrupted variants.
3. Materially distinct held-out package frozen before rule tuning.

The package model must preserve source locators, original values, normalized values, authority declarations, and controlled file references.

## Work Blocks P2.1–P2.4 — Consistency Rules

Implement in this order:

1. inventory, parse, revision, file-reference, and authority gates;
2. document/tag relationship checks;
3. BOM/equipment/datasheet/specification checks;
4. authority conflicts and explicit result-state routing.

Do not add a broad scoring system before state precedence and release holds work correctly.

## Work Blocks P3.1–P3.3 — Audit Deliverables

Produce one immutable result, then render:

- issue register;
- release-readiness summary;
- stable `audit-package` CLI behavior.

Report views must not recompute evaluation logic.

## Work Blocks P4.1–P4.3 — Reliability and Release

- fault-injection regression tests;
- development and held-out benchmark;
- false-positive/false-negative review;
- clean-clone acceptance;
- v0.3.0 release evidence and annotated tag.

## Work Blocks P5.1–P5.2 — Portfolio and Commercial Proof

- terminal-first clean/failing demo;
- evidence-linked case study;
- bounded Mechanical Document Consistency Audit service specification;
- no SaaS, integration, or engineering-sign-off claims.

## Explicitly Deferred

Until v0.3.0 passes its frozen benchmark:

- PDF/CAD extraction;
- agent runtime integration;
- API/database/frontend;
- observability platform;
- RAG;
- hosted deployment;
- reward models, LoRA, or RL.
