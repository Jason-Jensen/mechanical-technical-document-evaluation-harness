# AI Impact Assessment

**Assessment ID:** AIMS-IA-001

**Version:** 0.3.0

**Date:** 2026-07-22

## 1. Scope and Systems

This assessment covers:

- `AIS-001`: generative-AI assistance used for project planning, research,
  coding, testing, documentation, and repository operations;
- `AIS-002`: the deterministic package-assurance evaluator that constrains and
  evaluates candidate artifacts but does not call an AI model; and
- `AIS-003`: future model-based extraction or agent capabilities, currently
  prohibited and not implemented.

## 2. Intended Benefits

- reduce repetitive review and implementation effort;
- find structured package inconsistencies earlier;
- produce traceable evidence for qualified human review;
- preserve failure states and reduce unsupported confidence;
- improve project learning through durable tests and controls; and
- support a bounded future audit service if technical and human evidence is
  sufficient.

## 3. Affected Parties

- project owner and maintainers;
- qualified engineering reviewers;
- future clients and document-control personnel;
- engineers, fabricators, operators, and others who could rely on package
  release information; and
- data or intellectual-property owners whose material could enter the workflow.

No current output is authorized to make an autonomous safety-critical decision.

## 4. Material Adverse Impacts

| Impact | Mechanism | Current control |
|---|---|---|
| Unsafe reliance on a wrong or incomplete result | Hallucination, false negative, missing authority, or automation bias | Human sign-off boundary, evidence-linked findings, explicit states, release holds |
| Unnecessary delay or review burden | False positives or low-value findings | Clean-package tests, exact evidence, reviewer feedback objectives |
| Loss of accountability | AI action presented as human or engineering approval | Named roles, immutable records, no autonomous release |
| Confidentiality, privacy, or IP harm | Unauthorized material uploaded, retained, or reproduced | Source authorization gate, data classification, stop condition, no supplied standard in Git |
| Security compromise or manipulated output | Prompt injection, untrusted artifacts, credentials, dependencies, or tools | Treat content as data, least privilege, bounded tools, CI and review |
| Inability to reproduce or contest a result | Model/provider/environment changes or missing evidence | Versioned changes, fingerprints, stable paths, preservation, challenge route |
| Misleading performance claim | Contaminated benchmark or tool failure reported as semantic accuracy | Isolated custody, failed-run preservation, separate failure states, claim boundary |
| Unequal or inaccessible treatment | Review priority or future model behavior disadvantages a group | Stakeholder review requirement, fairness/accessibility assessment before external use |

## 5. System Decisions

### AIS-001: active with controls

Generative AI may assist work within accepted scope. It cannot accept its own
high-risk work, release the product, make engineering sign-off, invent source
authority, or use restricted data without authorization. Material output is
verified through tests, evidence inspection, and human review.

### AIS-002: active deterministic control component

The package evaluator is not represented as AI. Its deterministic behavior,
explicit result states, immutable outputs, and independent execution reduce
AI-producer risk. The open D-113 publication failure means benchmark and release
claims remain held.

### AIS-003: prohibited pending a new gate

PDF/CAD extraction, generic agents, RAG, hosted APIs, databases, autonomous
redlining, reward models, and production model use remain outside v0.3.0.
Authorization requires a new impact assessment, threat model, data and supplier
review, benchmark, monitoring plan, and owner decision.

## 6. Residual Impact Decision

Current internal development use is acceptable only with the recorded controls
and human authority. External release is not acceptable while `NC-001` and its
associated high residual publication risk remain open.

The assessment is reviewed after any material system, provider, data,
deployment, affected-party, incident, or regulatory change and before every
release candidate.
