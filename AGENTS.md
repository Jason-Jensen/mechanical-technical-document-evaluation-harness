# Repository Agent Instructions

## Repository Identity

This repository contains the frozen **Mechanical Technical Document Evaluation Harness v0.2.0** and the active **Mechanical Engineering Workflow Assurance Platform v0.3.0 Package Assurance Pilot**.

The v0.2.0 release is an evaluation kernel. Preserve accepted commit `45336a2`, the annotated `v0.2.0` tag, historical benchmark evidence, golden references, and release documentation.

## Controlling Work

Read, in order:

1. `gantt.xlsx` — `Start Here`
2. `gantt.xlsx` — `AI Context`
3. `gantt.xlsx` — active and next rows in `Pilot Gantt`
4. `PROJECT_CONTEXT.md`
5. relevant architecture and workflow documents

The workbook, not this file, defines the active WBS. Do not implement package loaders, schemas, fixtures, or rules unless `gantt.xlsx` records P0.2 acceptance and authorizes P1.

## Change Discipline

- Use one branch per coherent capability.
- Use the capability branch or worktree named in the active `Pilot Gantt` row.
- Do not modify unrelated files.
- Do not rewrite the v0.2.0 kernel unless an explicit interface conflict is demonstrated and approved.
- Keep package case definitions, golden relationships, candidate artifacts, traces, and run results separate.
- Never edit a held-out or golden asset to satisfy a failing test.
- Preserve failed runs and failure evidence.
- Do not add provider-specific assumptions to core evaluator contracts.

## Protected Assets

Treat these as read-only unless the active WBS explicitly authorizes a reviewed change:

- `v0.2.0` tag and release evidence;
- golden/reference case content;
- held-out benchmark packages;
- accepted schemas and acceptance criteria;
- historical result records;
- Gantt history and prior work-block records.

## Allowed Autonomous Actions

Within an approved branch and scoped worktree, an agent may:

- read repository files;
- create or edit files within the active WBS scope;
- run local tests, linters, formatters, and CLI commands;
- generate local synthetic fixtures and reports in approved paths;
- inspect Git diffs and status.

Explicit approval is required before:

- deleting or overwriting protected assets;
- changing acceptance criteria, goldens, or held-out cases;
- using credentials or personal accounts;
- enabling network access not required by the task;
- sending messages, publishing, purchasing, deploying, or making external changes;
- rebasing or rewriting shared history;
- merging, tagging, or pushing a release.

## Verification Contract

A completion claim must include:

- active WBS and acceptance criteria;
- changed files;
- commands executed;
- focused and regression test results;
- generated artifact paths;
- review of expected/actual evidence;
- unresolved limitations or blockers;
- Git branch, commit, and clean/dirty state.

Polished output is not evidence. A task is not complete until its acceptance checks pass and generated artifacts are inspected.

## Architecture

Maintain strict separation among:

- task;
- agent/producer;
- environment;
- trace/artifacts;
- evaluator;
- results.

For v0.3.0, the pipeline is:

`package manifest -> normalization -> mandatory gates -> relationship graph -> deterministic rules -> result-state router -> immutable result -> issue register/release summary`

The evaluator must remain independently executable without the producing agent.

## Result States

Use explicit states:

- `automatic_pass`
- `automatic_fail`
- `engineering_review_required`
- `missing_authoritative_information`
- `extraction_or_tool_failure`
- `evaluator_uncertainty`

Mandatory holds override aggregate scores.

## Scope Guardrails

v0.3.0 is structured-data first. Do not add:

- PDF/CAD extraction;
- redline editing;
- generic agent orchestration;
- API/database/frontend layers;
- observability platforms;
- RAG;
- reward models or RL.

These require later gate decisions.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
