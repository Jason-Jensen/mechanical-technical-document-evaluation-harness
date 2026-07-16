# v0.3.0 Package Assurance Target Architecture

## Architectural Goal

Extend the v0.2.0 evaluator into one complete structured package workflow while preserving the existing model-independent kernel.

Do not introduce a parallel framework.

## Pipeline

```text
Versioned Package Case
        |
        v
Package Manifest Loader
        |
        v
Structured Source Adapters (JSON/CSV only)
        |
        v
Canonical Normalization + Evidence Locators
        |
        v
Mandatory Package Gates
        |
        v
Relationship Graph / Indexed Package Model
        |
        v
Deterministic Rule Families
        |
        v
Authority Resolver + Result-State Router
        |
        v
Immutable Package Result
       / \
      v   v
Issue Register   Release-Readiness Summary
```

## Component Responsibilities

### Package Manifest Loader

Inputs:

- package manifest path;
- allowed package root;
- supported schema versions.

Outputs:

- validated package declaration;
- declared source files;
- package metadata;
- authority-map reference;
- controlled file-reference policy.

Failure modes:

- missing/malformed manifest;
- unsupported schema;
- path traversal;
- duplicate source declarations;
- undeclared source type.

### Structured Source Adapters

Adapters parse JSON and CSV into typed internal records with source locators.

Each record retains:

- source file;
- row/index/JSON pointer;
- original values;
- parsed values;
- schema version.

Extraction and semantic interpretation are not adapter responsibilities in v0.3.0.

### Canonical Normalization

Normalization returns both original and canonical values. It is explicit, versioned, field-specific, and testable.

It must fail closed when a value cannot be safely normalized.

### Mandatory Package Gates

Gates verify package evaluability before relationship scoring. They produce evidence-rich gate results and determine whether downstream checks may execute.

### Relationship Graph / Indexed Package Model

The graph links controlled entities:

- documents;
- drawings;
- revisions;
- BOM/equipment items;
- tags;
- datasheets/specifications;
- file references;
- authority declarations.

This layer performs no release decision. It exposes deterministic queries to rule families.

### Deterministic Rule Families

Rules are narrow and versioned. Each rule consumes typed entities and authority declarations and emits check results with evidence.

Rules should be independently testable and avoid hidden global state.

### Authority Resolver

The resolver applies declared field/relationship authority. It does not invent source precedence.

Outputs include:

- resolved authoritative value;
- missing-authority condition;
- source conflict;
- unsupported/ambiguous rule;
- evidence references.

### Result-State Router

The router converts gate/check outcomes into explicit finding and package states. It enforces mandatory-hold precedence independently of weighted scoring.

### Result and Report Layer

One immutable machine-readable result is the source for all report views.

Report renderers produce:

- issue-register CSV;
- issue-register Markdown;
- release-readiness Markdown;
- optional portfolio/demo summary.

Report renderers must not recompute evaluation logic.

## Existing Kernel Integration

Reuse or extend the v0.2.0 concepts for:

- candidate/case loading patterns;
- stable errors;
- mandatory gates;
- deterministic check results;
- weighted scoring where relevant;
- failure evidence;
- immutable result persistence;
- CLI conventions;
- harness-version stamping.

Any v0.2.0 contract change requires a documented interface conflict and regression proof.

## Data Separation

### Versioned Benchmark Inputs

- package manifest;
- structured source files;
- authority map;
- expected findings and states;
- fixture notes.

### Generated Evidence

- candidate package output;
- run metadata;
- gate/check results;
- issue register;
- release summary;
- logs;
- traces when a future agent is integrated.

Generated evidence must never be written back into the versioned case directory.

## Proposed Module Boundaries

Names are provisional and should align with the existing package layout:

```text
src/mech_eval_harness/
  package_assurance/
    manifest.py
    models.py
    adapters/
      json_adapter.py
      csv_adapter.py
    normalize.py
    gates.py
    relationships.py
    authority.py
    rules/
      inventory.py
      revision.py
      document_tag.py
      bom_equipment.py
      datasheet_spec.py
    routing.py
    reports.py
    cli.py
```

Do not create all files at once. Add them only as each WBS requires.

## Future Adapter Boundary

v0.4.0 extraction adapters should emit the same structured records and evidence-locator contract used by v0.3.0.

Extraction results must include:

- extractor/tool version;
- source artifact/page/region;
- confidence or uncertainty where applicable;
- parse failures;
- original extracted text/value;
- normalized value.

Extraction failure must remain distinguishable from a genuine package inconsistency.

## Future Agent Boundary

A future agent may assemble, inspect, or propose corrections to a package. It remains a replaceable producer.

The evaluator receives only committed candidate artifacts and optional preserved traces. Final outcome quality and process quality are scored separately.
