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
- **Status:** P2.1 implementation is committed at `e1ada72` and verified on `feature/package-inventory-gates`; user acceptance is pending
- **Implementation state:** Structured JSON/CSV adapters and eight deterministic package gates now cover manifest, source inventory/parse, authority, boundary/file references, identifiers, duplicates, revisions, and evidence locators. P2.2 relationships, P2.3 consistency rules, P2.4 state routing, reports, and semantic held-out evaluation remain unimplemented

P0.1 is accepted. Its reviewed workflow contract and authority-map example freeze the package boundary, identifiers, authority rules, result states, evidence contract, human-review boundary, and exclusions.

P0.2 is accepted. It freezes the development/held-out split, minimum scenario matrix, exact oracle matching, state and CLI routing, reproducibility, contamination handling, false-positive/false-negative review, bounded claims, and release stop conditions.

P1.1 is accepted and locally integrated at commit `42ad037`. It validates package metadata, mandatory source declarations, canonical manifest identifiers, document revisions, relationship declarations, authority-map references, and controlled paths. It resolves source and file declarations without parsing source records or assigning package result states; those behaviors remain in later gated work.

P1.2 is accepted at commit `f26ed27`. It provides `SCN-DEV-PUMP-SKID-CLEAN-001`, a clean, fully synthetic pump-skid package with all seven mandatory sources, nine controlled file references, 20 reviewed semantic relationships, exact hidden evidence locators, expected clean results, and a package-tree content hash. Its source layouts are fixture examples rather than accepted general schemas.

P1.3 is accepted at commit `4b7516e`. It provides a materially distinct synthetic held-out family with exact protected findings, evidence locators, check IDs, package states, per-scenario hashes, material-distinction evidence, contamination controls, and freeze-set hash `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884`. Its recorded `frozen_pre_tuning` status is active. It is self-authored pre-tuning, not independently blind. During P2.1, tracked held-out path names were inadvertently enumerated and the full suite exercised opaque integrity checks; protected source and oracle content was not opened or used to tune evaluator behavior. The first semantic held-out evaluation remains gated.

P2.1 implementation is committed at `e1ada72`. It adds fail-closed structured-source adapters, deterministic evidence models, eight ordered package gates, stable findings, and explicit prerequisite skips without selecting a package-level result state. Focused verification passed 60 tests with one expected Windows symlink skip; the full suite passed 187 tests with the same skip. An approved EOL-only repair adds byte-preserving Git attributes so raw benchmark inventories remain reproducible on Windows; no fixture JSON value, oracle, expected state, or accepted hash changed.

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

Review and accept the verified P2.1 package-gate implementation. Do not begin P2.2 document/tag relationship checks until that acceptance is recorded. Semantic held-out execution, package-state routing, CLI/reporting, PDF/CAD, agent, API, database, RAG, and frontend implementation remain blocked.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
