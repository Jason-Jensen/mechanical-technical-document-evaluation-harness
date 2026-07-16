# v0.3.0 Package Assurance Pilot — Acceptance Plan

**Status:** Draft for P0.2
**Predecessor:** Accepted P0.1 workflow contract

## 1. Acceptance Objective

Demonstrate that the structured Mechanical Package Consistency Audit detects its defined discrepancy classes, routes uncertain or unresolvable conditions correctly, preserves evidence, and reproduces results without changing frozen references.

This plan validates the workflow implementation. It does not establish population-level real-world accuracy.

## 2. Benchmark Assets

### Development Package

A realistic synthetic package used during implementation. It contains:

- a clean baseline;
- controlled fault variants;
- explicit authority map;
- reviewed expected findings;
- expected package states.

### Held-Out Package

A materially distinct, newly authored package frozen before rule tuning. It must differ in identifiers, package structure, record ordering, and fault placement.

The held-out package may be inspected for fixture validity but must not be used to tune implementation behavior after the split without recording contamination and replacing it.

## 3. Required Scenario Families

1. Clean package — expected automatic pass.
2. Missing required document or register entry.
3. Duplicate document, drawing, item, or tag.
4. Wrong or superseded revision.
5. Orphan relationship between drawing, BOM/equipment, and datasheet/specification.
6. Quantity or identifier mismatch.
7. Missing authoritative source.
8. Conflicting authority declarations.
9. Malformed structured input.
10. Missing or inaccessible referenced file.
11. Ambiguous normalization case.
12. Evaluator-configuration or unsupported-schema case.

## 4. Fault Matrix

Each fault fixture records:

- seeded fault ID;
- source file and record;
- affected canonical IDs;
- expected finding state;
- expected severity and hold behavior;
- expected evidence references;
- expected package state;
- whether the fault is release-critical;
- whether additional incidental findings are permitted.

At least six distinct release-blocking faults must exist across the development and held-out packages.

## 5. Deterministic Acceptance Criteria

### Gates

- Every curated gate fixture routes exactly as expected.
- Required gate failures stop dependent scoring.
- Gate evidence names the source and failure location.

### Seeded Fault Detection

- All seeded release-blocking faults in the frozen benchmark are detected.
- A seeded fault is not considered detected by an unrelated or generic error.
- Evidence must identify the affected canonical relationship.

### Clean Package Behavior

- The curated clean development package has no release hold.
- The curated clean held-out package has no release hold.
- Any allowed informational finding is explicitly declared in expected results.

### State Routing

- Finding states match expected values.
- Package-state precedence is exact.
- Numeric scores never override mandatory holds.

### Evidence Integrity

Every non-pass finding includes:

- check version;
- source references;
- expected/actual or missing-condition evidence;
- affected identifiers;
- state and severity;
- review requirement.

### Reproducibility

- Two runs over unchanged inputs produce the same normalized result.
- Run IDs and timestamps may differ; substantive findings, states, and evidence must not.
- Result records are immutable and stored outside case definitions.

### Failure Preservation

- Malformed inputs and tool/configuration failures leave inspectable records.
- Failed runs are not deleted or rewritten as passes.

## 6. False-Positive and False-Negative Review

Before release:

1. Review every expected clean relationship for unexpected findings.
2. Review every seeded fault for missed or misclassified findings.
3. Record known false positives and false negatives.
4. Classify each as rule defect, fixture defect, authority ambiguity, normalization defect, unsupported scope, or evaluator uncertainty.
5. Do not alter goldens or tolerances solely to improve the reported result.

## 7. Development/Held-Out Reporting

Report separately:

- development package results;
- held-out package results;
- clean scenarios;
- seeded faults;
- malformed/tool-failure scenarios;
- state-routing accuracy;
- evidence-completeness results;
- known limitations.

Do not aggregate development and held-out results into one flattering score.

## 8. Test Layers

### Unit Tests

- schema validation;
- normalization rules;
- authority resolution;
- relation construction;
- individual check behavior;
- state precedence;
- evidence serialization.

### Integration Tests

- package load through immutable result;
- issue-register and release-summary generation;
- CLI exit codes;
- failed-run persistence.

### Regression Tests

- frozen v0.2.0 suite remains passing;
- package fixtures reproduce expected findings;
- previously fixed defects remain covered.

### Clean-Clone Acceptance

A fresh clone must:

- install from documented instructions;
- run the full test suite;
- validate both benchmark packages;
- execute clean and failing audit demos;
- generate versioned result/report artifacts;
- remain clean except for documented generated-output locations.

## 9. Release Gate

v0.3.0 may be tagged only when:

- P0 through P4 gates are accepted;
- all curated release-blocking faults are detected;
- clean packages have no mandatory false hold;
- held-out results are reported separately;
- state routing and evidence completeness pass;
- v0.2.0 regression tests remain passing;
- clean-clone acceptance passes;
- limitations and human-review boundaries are explicit;
- exact commit and generated artifact versions are recorded.

## 10. Prohibited Release Claims

Do not claim:

- zero real-world false negatives;
- complete engineering correctness;
- universal authority resolution;
- production readiness across arbitrary client packages;
- autonomous package approval;
- superiority to GPT-5.6, ChatGPT file review, or another tool without a controlled comparison.
