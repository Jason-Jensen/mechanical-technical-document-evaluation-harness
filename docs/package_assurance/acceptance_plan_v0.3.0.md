# v0.3.0 Package Assurance Pilot - Acceptance Plan and Benchmark Protocol

**Status:** Reviewed for P0.2 acceptance
**Release:** v0.3.0
**Predecessor:** Accepted P0.1 workflow contract and authority-map boundary
**Scope:** Structured package assurance only

## 1. Acceptance Objective

Demonstrate that the structured Mechanical Package Consistency Audit:

- detects every curated release-blocking fault in the frozen benchmark;
- routes every curated pass, fail, review, missing-authority, tool-failure, and uncertainty condition exactly as declared;
- produces complete source-linked evidence;
- preserves failed runs and protected benchmark inputs;
- reproduces the same substantive result over unchanged inputs; and
- leaves engineering release decisions with qualified humans.

This plan validates one bounded structured-data workflow. It does not establish population-level real-world accuracy, engineering correctness, production readiness, or performance of a model or agent.

## 2. Controlling Contracts

Acceptance is subordinate to:

1. `docs/package_assurance/workflow_contract_v0.3.0.md`;
2. `docs/package_assurance/authority_map_example_v0.3.0.json`;
3. the active P0.2 row and accepted decisions in `gantt.xlsx`;
4. the frozen v0.2.0 release and its regression evidence.

If this plan exposes an ambiguity in an accepted P0.1 rule, work stops until a recorded P0 gate decision resolves it. A benchmark fixture must not silently define new product behavior.

## 3. Acceptance Roles and Boundaries

| Role | Permitted knowledge and action |
|---|---|
| Package producer | Receives only producer-visible package inputs and task instructions. It must not receive expected findings, hidden fault labels, or prior result outputs. |
| Evaluator | Executes independently from the producer and emits gates, findings, package state, evidence, and immutable outputs. It must not read golden answers to determine its result. |
| Benchmark runner | Invokes the evaluator, preserves raw runs, and compares normalized outputs to protected expected results after evaluation. |
| Benchmark custodian/reviewer | May author and review fixtures and protected expected results. It records hashes, freeze status, contamination, and any replacement decision. |

The same person may fill more than one role in the pilot, but access and claim limitations must be disclosed. A self-authored held-out package may be described as newly authored and frozen before rule tuning; it must not be described as independently blind unless a genuinely independent author and execution boundary are documented.

## 4. Benchmark Units and Identifiers

A **package family** is one coherent mechanical release package design. A **scenario** is one executable package instance derived from a family. Each scenario has:

- globally unique `scenario_id`;
- globally unique `package_id`;
- `package_family_id` in benchmark metadata;
- split: `development` or `held_out`;
- scenario type: `clean`, `single_fault`, `compound_fault`, or `operational_failure`;
- benchmark revision and content hash;
- protected expected package state and findings.

Fault variants may be materialized copies or reproducibly generated from a frozen clean baseline. The evaluator always receives a complete package that satisfies the P0.1 directory contract; it never receives a mutation descriptor as a substitute for package input.

A single-fault scenario contains one intentional semantic fault. Mechanically necessary changes, such as assigning the variant a unique `package_id`, are recorded and are not counted as additional faults. A compound scenario declares every intentional fault and the precedence behavior being tested.

## 5. Required Benchmark Assets

### 5.1 Development Package Family

The development family is visible during implementation and may be used for rule tuning. It must include:

- one reviewed clean baseline;
- controlled fault variants sufficient to cover every mandatory gate;
- at least one passing and one failing relationship for every deterministic check family;
- at least one scenario for each of the six package states;
- explicit expected findings, expected package states, and expected CLI exits;
- source and mutation notes sufficient to audit every seeded condition.

### 5.2 Held-Out Package Family

The held-out family is newly authored, materially distinct, and frozen before P2 rule implementation or tuning begins. It must include:

- one reviewed clean baseline;
- at least six controlled fault variants;
- at least four release-blocking fault variants;
- at least one non-`automatic_fail` blocking or review state;
- at least one compound scenario that tests package-state precedence;
- protected expected findings and expected package states;
- a freeze record, content hashes, reviewer, and contamination status.

### 5.3 Material Distinction

The held-out family must differ from the development family in all of these dimensions:

- package and canonical identifiers;
- record ordering and source row placement;
- file names and controlled relative paths;
- at least one revision scheme or explicit revision sequence;
- relationship topology among drawings, items/tags, and datasheets/specifications;
- fault location and affected canonical objects.

It must also differ in at least one of these dimensions:

- package size or record counts;
- intentional duplicate policy;
- optional/review-routed authority rule;
- document type mix.

Renaming a copied development package is not a materially distinct held-out package.

## 6. Minimum Acceptance Scenario Matrix

The following development scenarios are mandatory. Exact fixture IDs and source locations are frozen when P1 fixtures are accepted.

| Scenario requirement | Seeded condition | Expected package state | CLI exit |
|---|---|---|---:|
| Clean development baseline | All mandatory gates and required relationships pass | `automatic_pass` | 0 |
| Malformed required structured source | A required JSON or CSV input cannot be parsed | `extraction_or_tool_failure` | 4 |
| Missing mandatory source | A declared required source is absent or inaccessible | `extraction_or_tool_failure` | 4 |
| Missing required authority | A release-critical decision has no authoritative source | `missing_authoritative_information` | 3 |
| Contradictory authority | Authority declarations conflict for a required field | `automatic_fail` | 1 |
| Duplicate canonical identity | A forbidden duplicate ID or tag exists without a valid duplicate policy | `automatic_fail` | 1 |
| Ambiguous normalization | A required relationship cannot be safely normalized | `evaluator_uncertainty` | 5 |
| Review-routed condition | A non-release-critical field is missing or conflicting under an explicit review rule | `engineering_review_required` | 2 |
| Missing controlled file | A required file reference is absent, escapes the package boundary, or resolves to the wrong document | `automatic_fail` | 1 |
| Wrong or superseded revision | A required object selects a non-current or prohibited revision | `automatic_fail` | 1 |
| Orphan relationship | A required drawing, item/tag, datasheet, or specification mapping is missing or wrong | `automatic_fail` | 1 |
| Quantity or identifier mismatch | A release-critical quantity, part/material ID, tag, or association conflicts with authority | `automatic_fail` | 1 |
| Unsupported declared behavior | A parsed manifest schema or authority rule is unsupported | Exact state declared by the P0.1 gate rule: `automatic_fail` for unsupported manifest schema, `evaluator_uncertainty` for unsupported authority interpretation | 1 or 5 |

The held-out scenario catalog remains protected from the producer. It must satisfy the counts and state coverage in Section 5.2 without copying the same record positions or canonical values used by development scenarios.

Across the two package families, the frozen benchmark must contain at least ten distinct release-blocking seeded faults, including at least four in the held-out split. Focused gate fixtures may supplement the package variants, but they do not replace the clean development and clean held-out package runs.

## 7. Mandatory Gate Acceptance

Each P0.1 mandatory gate requires:

- one curated passing fixture;
- one curated failing fixture;
- exact expected gate state and release-hold behavior;
- exact evidence source and failure location;
- an expected list of dependent checks that must be skipped;
- proof that independent gates may still preserve useful evidence;
- proof that a failed gate is not counted as a passed or scored check.

The expected-asset isolation gate must prove that protected oracle files are not supplied to the package producer or consumed by the evaluator as package evidence. The result-output gate must prove that generated results and reports are written outside the versioned scenario directory.

## 8. Deterministic Check-Family Acceptance

Each required check family in the workflow contract needs at least one passing and one failing relationship in the development suite:

- package inventory and reciprocal file mapping;
- revision consistency;
- drawing/register relationships;
- document and equipment-tag relationships;
- BOM/equipment identity, quantity, part/material, and drawing relationships;
- datasheet/specification identity, revision, and equipment relationships;
- authority absence, conflict, ambiguity, and unsupported-rule handling.

Every required check has a stable check ID and check version before its expected fixture is frozen. A generic parse error, generic package failure, or unrelated finding does not count as detection of a seeded relationship fault.

## 9. Fault Matrix Contract

Every scenario fault-matrix record includes:

- `scenario_id`, `package_id`, `package_family_id`, split, and benchmark revision;
- `seeded_fault_id` and scenario type;
- source file, record, field, and protected mutation description;
- affected canonical identifiers;
- required check ID or explicitly allowed check-ID set;
- expected finding state;
- expected severity value and release-hold flag;
- expected package state and CLI exit code;
- required evidence locators and expected/actual or missing-condition evidence;
- expected skipped checks and blocking gate, when applicable;
- exact required findings;
- exact allowed incidental findings, if any;
- reviewer and fixture-freeze status.

Held-out fault IDs, mutations, and expected records are hidden from the package producer. Wildcards such as "any revision error" or "any package failure" are prohibited in release-blocking oracle entries.

## 10. Finding and Oracle Matching

A seeded fault is detected only when a required finding matches all applicable semantic fields:

- check ID and compatible check version;
- result state;
- release-hold flag;
- affected canonical identifiers;
- authority rule ID where applicable;
- authoritative and compared source references;
- expected/actual value or exact missing/conflict condition;
- required evidence locator fields.

Human-readable rationale may vary without failing acceptance if the structured fields match and the rationale remains accurate. Severity must match the exact value frozen in the fault matrix; severity does not override package-state precedence.

### 10.1 Unexpected Findings

- A clean scenario permits no non-pass finding.
- A fault scenario permits only its required findings and explicitly enumerated incidental findings.
- An unexpected release hold, review item, missing-authority item, tool failure, or uncertainty is a false positive.
- An incidental finding must have an exact check/state/identifier pattern; broad wildcards are not allowed.
- A skipped check is neither a pass nor a failure. It must identify the blocking gate or unavailable prerequisite.

Finding order must be deterministic. Reordering source records must not change semantic findings or package state.

## 11. Result States and CLI Expectations

Package states and package-state exits are exact:

| Package state | CLI exit |
|---|---:|
| `automatic_pass` | 0 |
| `automatic_fail` | 1 |
| `engineering_review_required` | 2 |
| `missing_authoritative_information` | 3 |
| `extraction_or_tool_failure` | 4 |
| `evaluator_uncertainty` | 5 |

For v0.3.0 benchmark fixtures, every `automatic_fail` is release-blocking. A non-blocking discrepancy that needs human action routes to `engineering_review_required`; an advisory observation does not use a non-pass finding state.

CLI invocation errors that occur before a package audit can be established use exit 64 and do not masquerade as a package result. An unexpected unhandled evaluator failure before a controlled package state can be written uses exit 70. Controlled parse, tool, or environment failures after a valid package context exists must produce an immutable `extraction_or_tool_failure` package result and exit 4.

The package-state router is tested against every ordered pair of states and at least two full-list input-order permutations. The exact precedence from the workflow contract must hold, and the result must retain every observed non-pass state in its blocking-state summary.

## 12. Evidence Completeness

Every non-pass finding must satisfy the P0.1 finding contract. Acceptance additionally requires:

- package-relative source paths only;
- exact CSV physical row and column or JSON RFC 6901 pointer;
- original and normalized values for compared fields;
- stable canonical row or record key where available;
- authority rule and authoritative source when authority is involved;
- expected/actual values or an exact missing, inaccessible, unsupported, or conflict condition;
- evaluator version, check ID, and check version;
- review owner for review-routed findings;
- skip reason for every unexecuted dependent check.

Reports are views of `package_result.json`. The CSV and Markdown issue registers and release-readiness summary must not recompute state, authority, or check logic.

## 13. Reproducibility Protocol

Run every accepted clean and fault scenario twice from unchanged inputs using the same evaluator commit and configuration. The normalized substantive result must be identical.

Only these volatile fields may differ between runs:

- run ID;
- start and completion timestamps;
- elapsed duration;
- explicitly declared host or process metadata;
- output-directory path outside the versioned scenario.

The following must remain identical:

- package state, exit code, and blocking-state summary;
- gate and check outcomes;
- finding IDs, check IDs, check versions, and order;
- affected identifiers, evidence locators, expected/actual values, and normalization details;
- authority resolution and skipped-check reasons;
- issue-register rows and release-summary semantics.

Finding IDs must be deterministic for unchanged semantic findings. Machine-specific absolute paths, temporary-directory names, and nondeterministic map or file ordering are prohibited from substantive result fields.

## 14. Development and Held-Out Freeze Protocol

### 14.1 Development Freeze

Development fixtures may change during P1 and P2, but every change must be reviewed and versioned. Before the first held-out execution:

1. all development acceptance scenarios pass;
2. evaluator behavior and configuration are committed;
3. development fixture and expected-result hashes are recorded;
4. open false positives, false negatives, and unsupported cases are documented;
5. rule tuning stops.

### 14.2 Held-Out Freeze

Before P2 rule tuning begins:

1. author the materially distinct held-out clean package and fault variants;
2. validate fixture structure and intended relationships;
3. review the expected findings and package states;
4. record benchmark revision, file hashes, author/reviewer, and split commit;
5. mark all held-out inputs and expected assets read-only;
6. record contamination status as `frozen_pre_tuning` or a more conservative disclosed status.

The evaluator implementation must not be tuned against held-out outcomes. The held-out package may be inspected only for recorded fixture-validity review before the split is frozen.

### 14.3 Held-Out Execution

1. Run only after the development gate passes and the evaluator commit is frozen.
2. Stage only producer/evaluator-visible package inputs; retain protected expected assets outside that input boundary.
3. Preserve the first raw held-out run before comparison or diagnosis.
4. Compare through the benchmark runner after evaluation completes.
5. Report clean, seeded-fault, state-routing, and evidence results separately from development results.

## 15. Contamination and Replacement Rules

A held-out family is contaminated for release claims if, after the split is frozen:

- its expected findings, hidden mutations, or answer keys are exposed to the producer or rule implementer;
- rules, tolerances, normalization, or authority behavior are changed in response to its substantive outcomes;
- a held-out fixture or golden is edited to match evaluator output;
- prior result outputs are supplied as implementation guidance;
- the package is repeatedly probed to infer hidden expected behavior.

When contamination occurs:

1. preserve the failed run and original fixture hashes;
2. mark the benchmark revision and evidence as contaminated;
3. move the exposed scenario to development/regression use if still valuable;
4. author and freeze a materially distinct replacement held-out family;
5. do not count the contaminated result as release held-out evidence.

A rerun of the same held-out package is allowed without replacement only for a documented infrastructure or invocation failure when the oracle remained hidden, no evaluator behavior changed, inputs and evaluator commit are unchanged, and the failed run is preserved.

## 16. False-Positive and False-Negative Review

Definitions:

- **False negative:** a required finding is absent, is matched only by an unrelated generic error, or has the wrong affected identifiers, state, or release-hold behavior.
- **False positive:** an unexpected non-pass finding appears outside the exact required or allowed-incidental oracle.
- **Misclassification:** the seeded condition is found but state, hold, severity, authority rule, package state, exit, or required evidence is wrong.
- **Fixture defect:** the package does not contain the intended condition or its expected result conflicts with an accepted contract.

Before release:

1. review every clean relationship for unexpected findings;
2. review every seeded fault for detection and exact classification;
3. record every false positive, false negative, and misclassification;
4. classify root cause as evaluator defect, fixture defect, authority ambiguity, normalization defect, unsupported scope, operational failure, or evaluator uncertainty;
5. preserve the first failing evidence;
6. correct the product or replace an invalid fixture through change control;
7. never loosen a golden, tolerance, state, or hold solely to improve the reported result.

Release acceptance requires zero false negatives for curated release-blocking faults, zero unexpected non-pass findings on clean packages, exact routing for every curated scenario, and no unresolved fixture defect that affects a release claim.

## 17. Reporting Requirements

Report separately:

- development and held-out splits;
- clean and fault scenarios;
- mandatory gates and deterministic check families;
- each package state and CLI exit;
- seeded faults detected, missed, or misclassified;
- unexpected findings and allowed incidental findings;
- evidence-completeness failures;
- repeated-run reproducibility;
- contamination status and benchmark revision;
- known limitations and unsupported scope;
- v0.2.0 regression results.

Do not collapse development and held-out results into one headline score. If percentages are shown, include exact numerators and denominators and keep release-blocking detection separate from review/tool/uncertainty routing.

## 18. Test and Acceptance Layers

### 18.1 Unit Tests

- schema and structured-source validation;
- field-specific normalization;
- authority resolution;
- relation construction and indexing;
- individual gate and check behavior;
- all ordered state-precedence pairs and order permutations;
- evidence and result serialization.

### 18.2 Integration Tests

- package input through immutable result;
- gate dependency and skip behavior;
- issue-register and release-summary derivation;
- package-state and non-package CLI exit codes;
- failed-run preservation;
- output-directory separation from protected inputs.

### 18.3 Regression Tests

- frozen v0.2.0 suite remains passing;
- development fixtures reproduce frozen expectations;
- exposed former held-out failures become development regressions only after contamination is recorded;
- previously fixed package-assurance defects remain covered.

### 18.4 Clean-Clone Acceptance

A fresh clone at the release candidate commit must:

- install from documented instructions;
- validate all versioned benchmark definitions;
- run the full test suite, including the frozen v0.2.0 tests;
- execute clean and failing package-audit demos;
- run development and protected held-out benchmark protocols;
- generate versioned immutable results and report views outside case directories;
- reproduce normalized results on the repeated-run sample;
- remain clean except for documented ignored/generated-output locations.

## 19. Stop Conditions and Release Gate

Implementation must not begin until P0.2 is accepted. Once implementation begins, release work stops and the gate remains closed if any of these conditions exists:

- an accepted P0.1 rule is ambiguous for a required fixture;
- the held-out split is not frozen before rule tuning;
- held-out contamination lacks a materially distinct replacement;
- a curated release-blocking fault is missed or detected only generically;
- a clean package receives any non-pass finding;
- package state, CLI exit, hold precedence, or skipped-check routing is wrong;
- required evidence is incomplete or points to the wrong source location;
- unchanged repeated runs differ substantively;
- a failed run was deleted, overwritten, or rewritten as a pass;
- a protected case, golden, or expected result was changed without recorded review;
- generated output modifies a versioned package definition;
- the frozen v0.2.0 regression suite fails;
- benchmark or report claims exceed the evidence.

v0.3.0 may be tagged only when P0 through P4 gates are accepted, the complete release matrix passes, the exact commit and benchmark revision are recorded, limitations are explicit, and clean-clone acceptance succeeds.

## 20. Allowed and Prohibited Claims

Allowed claims must name the benchmark revision, evaluator commit, split, and exact counts. Examples include:

- all curated release-blocking faults in benchmark revision X were detected;
- both curated clean packages produced no non-pass findings;
- all curated package-state routes and evidence requirements passed;
- two unchanged runs produced the same normalized result.

Do not claim:

- zero real-world false negatives or false positives;
- complete engineering correctness;
- code, standard, safety, or design compliance;
- universal authority resolution;
- autonomous package approval or engineering release;
- production readiness across arbitrary client packages;
- an independently blind benchmark when the author or implementer knew the held-out design;
- superiority to GPT-5.6, ChatGPT file review, another model, an agent, or a human without a controlled comparison.

## 21. P0.2 Review Question Resolutions

| Question | Resolution |
|---|---|
| 1. What is the benchmark unit? | A globally identified scenario containing one complete package instance, linked to a development or held-out package family and protected expected results. |
| 2. What minimum benchmark is required? | One clean development family plus its gate/check variants, and one materially distinct clean held-out family plus at least six fault variants; at least ten release-blocking faults overall and four held-out. |
| 3. Which state coverage is mandatory? | Every one of the six package states in development, with pass, automatic fail, at least one other non-pass state, and a compound precedence case in held-out. |
| 4. What counts as detecting a seeded fault? | An exact structured match on the required check, state, hold, affected IDs, authority/source relationship, values or condition, and evidence locator; a generic or unrelated error does not count. |
| 5. Are extra findings allowed? | Clean scenarios allow none. Fault scenarios allow only exact required findings and explicitly enumerated incidental findings; unexpected non-pass findings are false positives. |
| 6. What are the state and CLI expectations? | Package states map exactly to exits 0-5; pre-package usage errors use 64 and unhandled pre-result evaluator failures use 70. State precedence is tested exhaustively. |
| 7. What must be reproducible? | All substantive states, findings, stable IDs, ordering, evidence, authority results, and report semantics; only declared run/time/host/output-path metadata may vary. |
| 8. How is held-out status established? | Author a materially distinct family, review it, hash it, freeze it before P2 tuning, protect its oracle, and execute it only after the development gate and evaluator commit are frozen. |
| 9. What happens after held-out exposure or tuning? | Preserve evidence, mark contamination, move exposed cases to development if useful, and replace them with a materially distinct held-out family before release. |
| 10. What closes or stops the release gate? | Exact scenario routing, evidence, reproducibility, clean behavior, fault detection, protected-asset integrity, v0.2.0 regression, and bounded claims must all pass; any listed stop condition keeps the gate closed. |

## 22. P0.2 Acceptance Evidence and Next Gate

P0.2 deliverables:

- this reviewed acceptance plan and benchmark protocol;
- decision-register entry freezing the benchmark split, minimum matrix, exact oracle rules, state/exit expectations, contamination protocol, and stop conditions;
- evidence-register entry linking the reviewed plan and P0.1 predecessor;
- Gantt update showing P0.2 complete and P1.1 blocked pending user acceptance;
- no package loader, schema, rule engine, fixture, PDF/CAD, agent, API, database, RAG, or frontend implementation.

Unresolved P0.2 decisions: none within the structured-data pilot boundary.

After user acceptance of P0.2, P1.1 may begin with the versioned package-manifest schema and loader. P1 implementation must conform to this plan and the accepted P0.1 contracts; it may not change benchmark policy implicitly.
