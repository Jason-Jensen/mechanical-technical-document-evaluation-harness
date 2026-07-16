# Project Context

**Updated:** 2026-07-16
**Repository:** `C:\Projects\mechanical-technical-document-evaluation-harness`
**Current branch:** `feature/package-assurance-contract`

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
- **Active WBS:** P1.1, package manifest schema and loader
- **Status:** P0.2 accepted on 2026-07-16; P1.1 authorized
- **Implementation state:** P1.1 begins only after the P0 branch is integrated and a dedicated capability branch is created

P0.1 is accepted. Its reviewed workflow contract and authority-map example freeze the package boundary, identifiers, authority rules, result states, evidence contract, human-review boundary, and exclusions.

P0.2 is accepted. It freezes the development/held-out split, minimum scenario matrix, exact oracle matching, state and CLI routing, reproducibility, contamination handling, false-positive/false-negative review, bounded claims, and release stop conditions.

P1.1 is authorized to implement only the package manifest schema and loader. P1.2 fixtures and all rule-engine work remain blocked by their own predecessor gates.

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

Integrate the accepted P0 branch, create `feature/package-manifest`, and implement P1.1 against the frozen P0.1 and P0.2 contracts. Do not begin P1.2 fixtures, consistency rules, PDF/CAD, agent, API, database, RAG, or frontend implementation.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
