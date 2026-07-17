# Project Context

**Updated:** 2026-07-16
**Repository:** `C:\Projects\mechanical-technical-document-evaluation-harness`
**Current branch:** `feature/package-inventory-gates`

## Executive Summary

The repository contains two deliberately different assets:

- **v0.2.0 Mechanical Technical Document Evaluation Harness:** a frozen, verified evaluation kernel;
- **v0.3.0 Package Assurance Pilot:** the active effort to prove one complete structured Mechanical Package Consistency Audit.

The project is not building a generic AI platform or SaaS product. Its near-term goal is to prove that a bounded, deterministic-first workflow can identify package inconsistencies, preserve evidence, route uncertainty correctly, and support qualified human release review.

## Frozen Baseline

v0.2.0 is frozen at accepted commit `45336a2` and the annotated `v0.2.0` tag.

Accepted evidence:

- five reviewed mechanical cases;
- 121 passing tests;
- 9/9 harness-verification baseline;
- 2/2 deterministic portfolio demo;
- immutable result records, CI, release documentation, and clean-clone acceptance.

Do not rewrite this kernel or alter its protected evidence without an approved interface-conflict decision.

## Active Work

- **Release:** v0.3.0 Package Assurance Pilot
- **Active WBS:** P2.1, package inventory, parse, revision, and authority gates
- **Status:** P1.3 is accepted at commit `4b7516e`; the recorded `frozen_pre_tuning` status is active and P2.1 is in progress on `feature/package-inventory-gates`
- **Implementation state:** The manifest boundary and both fixture families are accepted. P2.1 package gates are authorized against development inputs only; relationship checks, package-state routing, issue/report generation, and held-out execution remain unimplemented

P0.1 is accepted. Its reviewed workflow contract and authority-map example freeze the package boundary, identifiers, authority rules, result states, evidence contract, human-review boundary, and exclusions.

P0.2 is accepted. It freezes the development/held-out split, minimum scenario matrix, exact oracle matching, state and CLI routing, reproducibility, contamination handling, false-positive/false-negative review, bounded claims, and release stop conditions.

P1.1 is accepted and locally integrated at commit `42ad037`. It validates package metadata, mandatory source declarations, canonical manifest identifiers, document revisions, relationship declarations, authority-map references, and controlled paths. It resolves source and file declarations without parsing source records or assigning package result states; those behaviors remain in later gated work.

P1.2 is accepted at commit `f26ed27`. It provides `SCN-DEV-PUMP-SKID-CLEAN-001`, a clean, fully synthetic pump-skid package with all seven mandatory sources, nine controlled file references, 20 reviewed semantic relationships, exact hidden evidence locators, expected clean results, and a package-tree content hash. Its source layouts are fixture examples rather than accepted general schemas.

P1.3 is accepted at commit `4b7516e`. It provides a materially distinct synthetic held-out family with exact protected findings, evidence locators, check IDs, package states, per-scenario hashes, material-distinction evidence, contamination controls, and freeze-set hash `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884`. Its recorded `frozen_pre_tuning` status is active without editing protected content. It is self-authored pre-tuning, not independently blind. P2 implementers must not inspect or execute the accepted held-out family before the controlled held-out run.

## Intended Outcome

The pilot audits structured relationships among:

`drawing register <-> drawing metadata <-> BOM/equipment list <-> datasheet/specification metadata <-> revision history <-> controlled file references`

Primary deliverables:

- immutable machine-readable package result;
- evidence-linked issue register;
- release-readiness summary;
- explicit package states and stable CLI exits;
- benchmark and clean-clone evidence;
- bounded service demonstration.

## Operating Decisions

- Use gate and evidence completion, not hours, to control progress. Prospective time tracking is waived; historical values remain archival context.
- Keep the evaluator independent of any producer, model, or agent runtime.
- Prefer deterministic, source-linked checks and fail closed on unsafe normalization or missing authority.
- Preserve failed runs and keep package definitions, expected assets, candidate artifacts, traces, and results separate.
- Use only public, synthetic, self-authored, or explicitly authorized data.
- Treat the first commercial offer as a bounded audit service, not software access.

## Document Authority

Read current project information in this order:

1. `gantt.xlsx` for active status, gates, decisions, risks, evidence, and next action;
2. accepted workflow and acceptance contracts for product behavior;
3. `AGENTS.md` for durable repository controls;
4. this file for the compact current handoff;
5. architecture, strategy, commercial, and release documents for supporting context.

Files under `docs/archive/` and dated modernization records are historical provenance, not current control.

## Current Authorized Action

Implement P2.1 inventory, structured-source parse, revision, authority, duplicate, evidence-locator, and controlled-file gates against accepted contracts and development inputs only. Stop for user acceptance before P2.2 document/tag relationship checks. Do not inspect the held-out family or begin package-state routing, CLI/reporting, PDF/CAD, agent, API, database, RAG, or frontend implementation.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
