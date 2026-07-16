# Project Modernization Decision — 2026-07-10

## Executive Decision

Continue the project. Freeze v0.2.0 as the accepted evaluation kernel and build one complete, economically meaningful workflow on top of it.

The active target is **v0.3.0 Package Assurance Pilot**, not a generic agent framework, generic LLM grader, or early SaaS product.

The selected vertical is a structured **Mechanical Package Consistency Audit** that reconciles drawing-register data, drawing metadata, BOM/equipment-list data, datasheet/specification metadata, revision history, and controlled file references.

## Why This Direction Is Stronger in the GPT-5.6 Era

GPT-5.6 materially improves long-horizon coding, professional knowledge work, computer use, tool coordination, and production of complete artifacts. This increases the amount of technical work one operator can execute. It also increases the value of independent verification because a stronger agent can produce larger and more convincing work products while still making authority, revision, completeness, tool-use, or accidental-success errors.

Therefore the product relationship is:

> The producer performs or assists the work. The independent harness verifies the committed artifacts, checks controlled requirements, preserves evidence, and routes unresolved engineering judgment to qualified humans.

The project should exploit stronger agent capability for implementation and future workflow execution without coupling the evaluator to one model.

## Current MVP Evaluation

### What v0.2.0 Proves

- A valid mechanical evaluation case can be loaded and validated.
- Candidate artifacts can fail cleanly when missing, malformed, or structurally invalid.
- Mandatory gates execute before scoring.
- Exact, Boolean, set, contains, and absolute-tolerance checks produce evidence.
- Weighted scoring, pass/fail, failure modes, and check-level evidence are stable.
- The CLI writes immutable result records.
- Five reviewed cases, 121 tests, a 9/9 baseline, and a 2/2 demo reproduce in a clean clone.
- Release documentation and an annotated tag establish a defensible frozen baseline.

### What v0.2.0 Does Not Prove

- A coherent multi-document package workflow.
- A declared authority hierarchy for conflicting sources.
- Cross-document relationship modelling.
- An evidence-linked issue register and release-readiness decision.
- A pristine external benchmark; the prior held-out case was historically visible before the split.
- Performance of any specific model or agent.
- PDF/CAD extraction reliability.
- Commercial value or customer willingness to pay.

### Product Assessment

| Dimension | Assessment |
|---|---|
| Evaluation-kernel correctness | Strong for the released scope |
| Architecture discipline | Strong and appropriate |
| Workflow completeness | Low; isolated cases rather than one package workflow |
| Benchmark external validity | Limited |
| Commercial readiness | Not ready |
| Strategic value | High if converted into package assurance |

The correct action is **vertical expansion**, not a rewrite.

## GPT-5.6 Operating Changes

### Adopt

- Longer coherent work blocks with explicit plans and acceptance gates.
- Repository-wide reconnaissance before implementation.
- Multi-file implementation inside an isolated branch or worktree.
- Independent verification passes, not self-attestation.
- Artifact inspection, exact test output, and Git-state evidence.
- Parallel agents only for independent workstreams with non-overlapping files and acceptance criteria.
- Reusable repository instructions in `AGENTS.md`.

### Do Not Adopt

- Unbounded autonomy.
- Automatic permission to modify goldens, held-out assets, or acceptance criteria.
- Destructive or external actions without approval.
- Multiple agents editing the same capability concurrently.
- “Completed” claims based on prose summaries.
- Provider-specific core architecture.

## Six-Week v0.3.0 Plan

| Phase | Planned Hours | Primary Gate |
|---|---:|---|
| P0 Definition & Control | 4 | Workflow contract and acceptance plan accepted |
| P1 Package Model & Fixtures | 8 | Two valid packages and frozen held-out split |
| P2 Consistency Rules | 14 | Deterministic audit core and result-state routing |
| P3 Issue Register & CLI | 8 | Reproducible issue register and package command |
| P4 Benchmark & Reliability | 8 | Held-out benchmark and clean-clone acceptance |
| P5 Portfolio & Commercial Proof | 4 | Auditable demo and bounded service specification |
| **Total** | **46** | **v0.3.0 release** |

The detailed controlling WBS is in `gantt.xlsx` -> `Pilot Gantt`.

## Immediate Work Block

### Active WBS

P0.1 — Define workflow contract and authority map.

### Objective

Freeze the package-audit product contract before implementation.

### Expected Duration

2 focused hours.

### Definition of Done

The contract explicitly defines:

- in-scope document/data types;
- canonical document, drawing, item, tag, and revision identifiers;
- source authority and precedence rules;
- mandatory gates;
- deterministic check families;
- issue evidence requirements;
- package and finding result states;
- release-critical holds;
- human-review boundaries;
- exclusions and deferred adapters;
- versioned input and output contracts.

### Next Action

Create and review `docs/package_assurance/workflow_contract_v0.3.0.md` on `feature/package-assurance-contract`. Do not implement loaders or checks in this work block.

## Release Metrics

These are benchmark acceptance criteria, not claims of real-world performance:

- 100% expected routing for curated mandatory-gate fixtures.
- 100% detection of seeded release-blocking faults in the frozen benchmark.
- No mandatory false hold on the curated clean development and held-out packages.
- Exact result-state routing for all benchmark cases.
- Evidence completeness for every failed or review-routed check.
- Two repeated runs produce the same normalized result.
- Development and held-out results are reported separately.
- Known false positives, false negatives, tool failures, authority gaps, and uncertainty are documented.

## Capability Sequence After v0.3.0

1. Add one controlled extraction adapter, likely a PDF/table metadata path.
2. Measure extraction accuracy separately from consistency-check accuracy.
3. Add a bounded producer or agent on the same frozen package tasks.
4. Preserve trajectories and score process quality separately from final outcome.
5. Compare direct-model, agent, deterministic, and human-created candidates under the same evaluator.
6. Productize only after repeated evidence of workflow value.

## Commercial Thesis

The first sellable outcome is a bounded **Mechanical Document Consistency Audit**, not software access.

The service should reduce coordinator/checker labour and expose wrong revisions, missing documents, tag mismatches, quantity inconsistencies, and unsupported datasheet/specification relationships before release.

The harness remains the internal production and verification engine. Each engagement should improve the reusable benchmark, validators, and failure taxonomy.

## Claim Boundaries

Do not claim that the system:

- validates all engineering correctness;
- replaces qualified review;
- approves a package for engineering release;
- performs code-compliance review;
- guarantees absence of errors;
- has proven production ROI;
- evaluates GPT-5.6 or any other agent until such a benchmark is actually run.
