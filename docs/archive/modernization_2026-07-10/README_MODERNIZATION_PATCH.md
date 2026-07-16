# Mechanical Engineering Workflow Assurance Platform

> Historical README patch. Its relevant project-status content was incorporated into the repository README during the 2026-07-16 management cleanup.

> A model-agnostic assurance system for evaluating mechanical technical deliverables with deterministic gates, evidence-linked findings, explicit uncertainty, and human-controlled release decisions.

## Current State

The released **Mechanical Technical Document Evaluation Harness v0.2.0** is the frozen evaluation kernel. It validates structured candidate artifacts, executes mandatory gates and deterministic checks, applies weighted scoring, records check-level failure evidence, exposes a CLI, and writes immutable result records.

Release evidence includes five reviewed cases, 121 passing tests, a 9/9 verification baseline, a 2/2 deterministic demo, CI, release documentation, and an annotated release tag.

## Active Release: v0.3.0 Package Assurance Pilot

The next release turns the kernel into one economically meaningful workflow: a structured **Mechanical Package Consistency Audit**.

It will check relationships among:

- drawing registers;
- drawing metadata;
- BOMs and equipment lists;
- datasheet and specification metadata;
- revision history;
- controlled file references.

The pilot will produce:

- an immutable machine-readable package result;
- an evidence-linked issue register;
- a release-readiness summary;
- explicit states for automatic pass/fail, engineering review, missing authority, tool failure, and evaluator uncertainty.

v0.3.0 is deliberately structured-data first. PDF/CAD extraction, agent runtimes, APIs, databases, dashboards, RAG, and RL remain deferred until the workflow passes a frozen held-out benchmark.

## Why This Exists

Stronger AI agents can create more technical work, but they do not remove the need for controlled inputs, authoritative-source mapping, deterministic validation, evidence provenance, release gates, and qualified human approval.

The producer is replaceable. The evaluator remains independent.

## Architecture

The project keeps these concerns separate:

`Task -> Agent/Producer -> Environment -> Trace/Artifacts -> Evaluator -> Results`

For v0.3.0:

`Package Manifest -> Normalization -> Mandatory Gates -> Relationship Graph -> Deterministic Rules -> State Router -> Issue Register and Release Summary`

## Boundaries

This project provides workflow assistance, consistency checking, evaluation, and review evidence. It does not provide engineering sign-off, stamped deliverables, autonomous release, code-compliance opinions, or safety-critical final decisions.

## Project Control

The controlling plan is `gantt.xlsx`. Read `Start Here`, `AI Context`, and the active row in `Pilot Gantt` before beginning work.

---

## Integration Note

This file is a README modernization patch because the existing top-level README was not available in this environment. Integrate the sections above into the current README rather than blindly replacing working setup, CLI, demo, and release instructions.
