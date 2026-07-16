# Project Context

**Updated:** 2026-07-10
**Repository:** `C:\Projects\mechanical-technical-document-evaluation-harness`

## Frozen Release

Mechanical Technical Document Evaluation Harness **v0.2.0** is complete and frozen at accepted commit `45336a2`.

Verified release evidence:

- five reviewed mechanical cases;
- 121 passing tests;
- 9/9 harness-verification baseline;
- 2/2 deterministic portfolio demo;
- immutable result records;
- CI and release documentation;
- annotated `v0.2.0` tag.

Do not restart or replace this kernel.

## Product Direction

The strategic product is the **Mechanical Engineering Workflow Assurance Platform**.

The selected first post-MVP vertical is a **Mechanical Package Consistency Audit** over structured package manifests and controlled file references.

Target relationships:

`drawing register <-> drawing metadata <-> BOM/equipment list <-> datasheet/specification metadata <-> revision history`

Primary output:

- evidence-linked issue register;
- release-readiness summary;
- immutable machine-readable result.

## Active Release

**v0.3.0 — Package Assurance Pilot**

### Active WBS

P0.1 — Define workflow contract and authority map.

### Immediate Objective

Freeze scope, canonical IDs, authoritative fields and source precedence, result states, exclusions, human-review boundaries, and acceptance evidence before implementation.

### Expected Duration

2 focused hours.

### Definition of Done

The workflow contract is explicit, internally consistent, reviewable, and sufficient to author the acceptance plan without inventing missing product behavior.

### Next WBS

P0.2 — Define acceptance plan and benchmark protocol.

No pilot actual hours have been recorded yet.

## Product Interpretation

The existing release proves that the evaluation kernel works. It does not yet prove a realistic package-assurance workflow, external validity, commercial value, or agent performance.

v0.3.0 must add one complete vertical rather than more isolated checks.

## Required Package States

- automatic pass;
- automatic fail;
- engineering review required;
- missing authoritative information;
- extraction or tool failure;
- evaluator uncertainty.

A score may summarize non-critical quality but cannot override release-critical holds.

## Data Boundary

Use public, synthetic, self-authored, or explicitly authorized data only. Do not use confidential work-product details from Outlier, employers, clients, or private engineering packages.

## Deferred Until After v0.3.0

- PDF, image, drawing, table, and native CAD extraction;
- agent runtime integration;
- APIs, databases, and frontend work;
- observability dashboards;
- RAG;
- hosted deployment;
- reward models, LoRA, and RL.

## Source Hierarchy

1. Current project instructions
2. Current `gantt.xlsx`
3. `AGENTS.md` and this file
4. Repository architecture/workflow contracts
5. Accepted release and benchmark evidence
6. Research and market sources

Research informs design; it does not override the controlling Gantt or accepted contracts.
