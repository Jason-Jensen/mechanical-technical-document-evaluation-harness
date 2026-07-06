# Limitations and Claim Boundaries

## Purpose

This document defines what the Mechanical Technical Document Evaluation Harness version `0.2.0` does not establish.

It is part of the release contract. Claims about the system should remain inside these boundaries.

## Artifact scope

The MVP evaluates structured JSON candidate artifacts only.

It does not ingest or interpret:

- PDF documents;
- scanned drawings;
- images;
- spreadsheets as native workbooks;
- CAD files or native CAD metadata;
- redlines;
- handwritten markups;
- email or document-management systems.

The repository may contain CSV and Markdown source inputs for cases, but candidate evaluation is JSON-first.

## Workflow scope

The five included cases are narrow, synthetic, self-authored examples intended to verify the evaluation architecture.

They do not represent exhaustive coverage of mechanical engineering, fabrication, inspection, commissioning, quality management, or document-control workflows.

Passing the benchmark does not establish general engineering competence, production readiness, regulatory compliance, or suitability for every organization.

## Benchmark limitation

The benchmark contains four development cases and one held-out case.

`MECH-003` is frozen from the current benchmark version forward and has no committed candidate-example directory. However, it was authored and reviewed before the split was established.

Therefore:

- it is not a pristine blind case;
- its result must be reported separately;
- it must not be used for iterative tuning;
- current evidence must not be described as uncontaminated generalization performance.

Future benchmark versions should add newly authored cases that are frozen before candidate generation or evaluator tuning.

## Baseline limitation

The MVP v1 baseline uses reference-equivalent oracle artifacts and a small curated set of known faults.

It establishes that:

- expected valid artifacts can pass;
- selected known faults can fail as intended;
- scoring and evidence are reproducible for those scenarios.

It does not establish:

- AI-model accuracy;
- agent reliability;
- production defect-detection rates;
- false-positive or false-negative rates across a representative population;
- statistical generalization;
- robustness to adversarial or malformed real-world documents;
- complete coverage of the failure taxonomy.

## Portfolio-demo limitation

The portfolio demo reuses committed `MECH-002` candidate fixtures.

It proves the observable CLI, scoring, failure-evidence, exit-code, and persistence contract for two predetermined scenarios.

It is not an independent benchmark, model comparison, customer validation, or blind evaluation.

## Evaluator limitation

The current evaluator supports bounded deterministic checks defined by the versioned case and evaluator specifications.

The system does not infer engineering intent beyond those encoded checks.

A pass means the candidate satisfied the configured gates and checks within their stated tolerances. It does not mean the artifact is correct in every engineering respect.

A failure means at least one configured requirement failed. It does not prove the entire artifact is unusable.

## Failure-evidence limitation

Failure modes and evidence are generated from deterministic rules and configured mappings.

They are intended to support audit and diagnosis, but they are not a complete root-cause analysis.

The current failure taxonomy is bounded and may require expansion for additional workflows.

## Result-record limitation

Result records are written as local JSON evidence.

They are immutable by repository convention because each run receives a unique directory. They are not:

- cryptographically signed;
- protected by an append-only external store;
- independently timestamped;
- tamper-evident after filesystem access;
- retained by a managed database or records-management policy.

Generated run data must remain separate from versioned benchmark inputs.

## Model and agent limitation

Version `0.2.0` does not execute, orchestrate, or compare AI models or agents.

It contains no:

- direct-model baseline;
- agent runtime;
- tool-use environment;
- trajectory capture;
- process-quality score;
- cost or latency comparison;
- model-based judge;
- reward model;
- training or adaptation loop.

The architecture permits later expansion, but those capabilities are not part of the released MVP.

## Security limitation

The MVP is intended for local execution with public, synthetic, self-authored, or authorized data.

It has not undergone a formal security assessment, penetration test, threat-model review, or production hardening.

It must not be run with:

- production credentials;
- unrestricted external permissions;
- confidential client data without authorization and appropriate controls;
- destructive tool access;
- autonomous external-action authority.

Prompt injection and malicious-document handling are future concerns, not solved capabilities.

## Interface and deployment limitation

The supported interface is a local CLI.

Version `0.2.0` does not provide:

- REST or GraphQL APIs;
- database services;
- authentication or authorization;
- multi-user access;
- web or desktop UI;
- container or cloud deployment;
- service-level objectives;
- operational monitoring;
- telemetry or observability infrastructure;
- automated release deployment.

The package is installed from the repository. No public package-registry distribution is claimed.

## Compatibility limitation

The project requires Python 3.12 or newer.

It has been exercised locally on Windows and in GitHub Actions on Ubuntu with Python 3.12. Compatibility with all operating systems, shells, filesystems, locales, and later Python versions is not guaranteed.

## Engineering and legal boundary

The harness is an engineering workflow-assurance aid.

It does not provide or replace:

- professional engineering judgment;
- engineering sign-off;
- stamping or sealing;
- code or regulatory compliance opinions;
- safety-critical approval;
- autonomous design release;
- unreviewed operational control;
- qualified human verification.

All outputs require review by an appropriately qualified person.

## Release claim

The defensible version `0.2.0` claim is:

> The repository contains a runnable, deterministic, JSON-first mechanical technical-document evaluation kernel with five synthetic cases, mandatory gates, deterministic checks, weighted scoring, structured failure evidence, immutable local result records, automated regression tests, CI, a reproducible harness-verification baseline, and a terminal portfolio demo.

Claims beyond that statement require new evidence.
