# Project Context

**Updated:** 2026-07-16
**Repository:** `C:\Projects\mechanical-technical-document-evaluation-harness`
**Current branch:** `feature/package-fixtures`

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
- **Active WBS:** P1.3, held-out package and fault variants
- **Status:** P1.3 is complete and integrity-verified on `feature/package-fixtures`; user acceptance and pre-tuning freeze activation are pending
- **Implementation state:** The accepted development fixture and the new held-out freeze candidate are present; source adapters, gates, consistency rules, result routing, and reports remain unimplemented

P0.1 is accepted. Its reviewed workflow contract and authority-map example freeze the package boundary, identifiers, authority rules, result states, evidence contract, human-review boundary, and exclusions.

P0.2 is accepted. It freezes the development/held-out split, minimum scenario matrix, exact oracle matching, state and CLI routing, reproducibility, contamination handling, false-positive/false-negative review, bounded claims, and release stop conditions.

P1.1 is accepted and locally integrated at commit `42ad037`. It validates package metadata, mandatory source declarations, canonical manifest identifiers, document revisions, relationship declarations, authority-map references, and controlled paths. It resolves source and file declarations without parsing source records or assigning package result states; those behaviors remain in later gated work.

P1.2 is accepted at commit `f26ed27`. It provides `SCN-DEV-PUMP-SKID-CLEAN-001`, a clean, fully synthetic pump-skid package with all seven mandatory sources, nine controlled file references, 20 reviewed semantic relationships, exact hidden evidence locators, expected clean results, and a package-tree content hash. Its source layouts are fixture examples rather than accepted general schemas.

P1.3 provides `FAM-HO-INSTRUMENT-AIR-001`, a materially distinct synthetic instrument-air family with one clean scenario and seven controlled variants. The family contains 11 documents, 31 reviewed relationships, eight seeded fault records, seven release-blocking variants, an `evaluator_uncertainty` case, and a compound state-precedence case. Exact protected findings, evidence locators, check IDs, package states, per-scenario hashes, material-distinction evidence, contamination controls, and freeze-set hash `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884` are recorded. Focused verification passed 50 tests with one expected Windows symlink skip; the full suite passed 170 with the same skip. The family is a self-authored pre-tuning freeze candidate, not an independently blind benchmark. P2 evaluator implementation remains blocked until P1.3 is accepted.

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

Review and accept the verified P1.3 held-out freeze candidate. Acceptance activates the recorded pre-tuning freeze without changing protected fixture content. Do not begin P2 source adapters, mandatory gates, consistency rules, PDF/CAD, agent, API, database, RAG, or frontend implementation until P1.3 is accepted.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
