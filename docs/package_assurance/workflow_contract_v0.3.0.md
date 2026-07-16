# v0.3.0 Mechanical Package Consistency Audit - Workflow Contract

**Status:** Accepted for P0.1 on 2026-07-15
**Release:** v0.3.0
**Scope:** Structured package metadata and controlled file references

## 1. Purpose

Evaluate whether a controlled mechanical document package is internally consistent enough to proceed to qualified human release review.

The workflow identifies deterministic discrepancies, missing authority, tool or parse failures, and unresolved engineering judgment. It does not approve engineering content, certify code or standards compliance, authenticate documents, or replace qualified review.

## 2. In-Scope Inputs

Every v0.3.0 package must contain these structured source files:

1. `package_manifest.json`
2. `inputs/drawing_register.csv`
3. `inputs/drawing_metadata.json`
4. `inputs/bom_or_equipment_list.csv`
5. `inputs/datasheet_spec_metadata.json`
6. `inputs/revision_history.csv`
7. `authority/authority_map.json`

The pilot accepts JSON and CSV source data only. Controlled file references may point to PDFs, drawings, spreadsheets, models, or other package artifacts, but v0.3.0 checks only declared existence, path control, identifiers, and metadata. It does not extract text, tables, geometry, CAD metadata, or drawing-image content from referenced files.

If a package has no records for an otherwise mandatory source family, the source file still exists and declares an empty record set with evidence for that condition. Missing mandatory files are not interpreted as empty files.

## 3. Package Directory Contract

```text
package/
  package_manifest.json
  inputs/
    drawing_register.csv
    drawing_metadata.json
    bom_or_equipment_list.csv
    datasheet_spec_metadata.json
    revision_history.csv
  files/
    ... controlled referenced artifacts ...
  authority/
    authority_map.json
  expected/                 # benchmark packages only; hidden from producer
    expected_findings.json
    expected_release_state.json
```

Generated data must be written outside the versioned case definition:

```text
runs/<run_id>/
  package_result.json
  issue_register.csv
  issue_register.md
  release_readiness.md
  logs/
```

The evaluator must reject path traversal and must not write generated reports, normalized intermediates, traces, or run results back into the versioned package directory.

## 4. Canonical Identifiers

Every relationship resolves through declared canonical IDs rather than filenames alone.

### 4.1 Identifier Scope

| Identifier | Required scope | Notes |
|---|---|---|
| `package_id` | Globally unique within the benchmark or run collection | The only v0.3.0 identifier assumed to be globally unique by itself. |
| `document_id` | Unique within `package_id` | Canonical package document identity independent of filename. |
| `drawing_number` | Unique within `package_id` unless an explicit duplicate policy permits otherwise | Drawing numbers are not assumed to be globally unique across packages or clients. |
| `revision_id` | Scoped to the owning `document_id`, `drawing_number`, `datasheet_id`, or `specification_id` | A revision value is never authoritative without its owning object. |
| `item_id` | Unique within `package_id` | BOM/equipment-list row identity. |
| `equipment_tag` | Unique within `package_id` unless an explicit duplicate policy permits otherwise | Duplicate tags require declared representation; accidental duplicates are release holds. |
| `datasheet_id` | Unique within `package_id` | Datasheet/specification identity independent of filename. |
| `specification_id` | Unique within `package_id` | Specification identity independent of filename. |
| `file_ref_id` | Unique within `package_id` | Controlled reference to a declared file path. |

Cross-package evidence references must qualify package-scoped identifiers as `package_id.identifier`.

### 4.2 Normalization

Normalization rules are declared and versioned by field. Normalization may trim surrounding whitespace and apply configured case rules. It must not silently remove meaningful punctuation, embedded spaces, leading zeroes, revision suffixes, tag separators, drawing-number structure, or unit-bearing text.

Each evidence record must preserve:

- original source value;
- normalized value;
- normalization profile or rule ID;
- source locator;
- parse or normalization failure if the value cannot be safely normalized.

When normalization is ambiguous, the evaluator fails closed and routes the finding to `evaluator_uncertainty` or `engineering_review_required` according to the authority rule. It must not fabricate a match.

## 5. Authority Model

Authority is package-specific and field-specific. The evaluator must not infer authority from file order, filename, modification time, row order, recency, source count, or model judgment.

`authority_map.json` declares, for each controlled field or relationship:

- controlled field or relationship path;
- authoritative source type;
- allowed secondary sources;
- precedence order only where explicitly permitted;
- required agreement rule;
- whether the field is required for release readiness;
- whether conflict or absence is a release hold;
- state routing for missing authority, missing values, conflicts, and ambiguity;
- review owner or discipline when human review is required;
- duplicate policy where duplicates may be intentional;
- revision scheme or normalization profile where relevant.

The reviewed example for this release is `docs/package_assurance/authority_map_example_v0.3.0.json`. It is an example contract for the synthetic pilot, not a universal engineering hierarchy.

### 5.1 Fields Requiring Authority Declarations

Authority declarations are required for every field or relationship consumed by a mandatory gate, deterministic check, release-hold rule, issue-register entry, or release-readiness summary.

Minimum controlled authority paths:

- package required source inventory;
- package boundary and allowed file-reference roots;
- document required-for-release status;
- document type, title, status, discipline, and owner where checked;
- drawing number, document mapping, current revision, revision scheme, title, status, and controlled file reference;
- revision history current/superseded state, revision order, release status, and effective date where checked;
- BOM/equipment item identity, equipment tag, item quantity, part/material identifier, drawing reference, datasheet/specification reference, and required release status;
- datasheet/specification identity, current revision, mapped equipment tag or item, controlled operating/design metadata where checked, and controlled file reference;
- duplicate tag/item/drawing policies;
- normalization profiles for every identifier used in relationships;
- state routing for missing authority, missing values, conflicts, unsupported rules, and review-required conditions.

### 5.2 Automatic Release Holds

These conflicts or control failures are automatic release holds in v0.3.0:

- required package manifest is missing, malformed, or unsupported;
- a mandatory structured source is missing, undeclared, inaccessible, or unparseable;
- a required authoritative source is absent for a release-critical decision;
- an authority map is missing, malformed, contradictory, or omits a required controlled field;
- required canonical identifiers are missing, structurally invalid, or duplicated without an explicit duplicate policy;
- a controlled file reference is missing, escapes the package boundary, or maps to the wrong controlled document;
- current revision conflicts with the authoritative source;
- a superseded or prohibited revision is selected as current;
- a required drawing, BOM/equipment item, datasheet, or specification mapping is missing or points to the wrong canonical object;
- a release-critical quantity, part/material identifier, tag, or document association conflicts with its authority rule;
- benchmark expected assets, expected findings, hidden fault labels, or held-out golden relationships are visible to a future producing agent.

All automatic release holds retain evidence even when a higher-level package state has already been determined.

### 5.3 Missing Values Routed to Review

Missing values route to `engineering_review_required` only when the authority map explicitly marks the field as reviewable and non-automatic-fail. Examples include:

- secondary-source metadata missing while the authoritative source is present and sufficient;
- optional descriptive fields such as non-critical title aliases, notes, or owner labels;
- technical values whose absence may be intentional and require discipline review, such as a design pressure or material note not used by a release-critical deterministic rule;
- ambiguous but bounded source mappings where the package owner must decide intent.

Missing authoritative information for a required decision routes to `missing_authoritative_information`, not review. Missing mandatory source files, parse failures, invalid identifiers, and required release-critical relationships do not route to review unless an accepted authority rule explicitly permits that behavior.

## 6. Revision Rules

Every controlled revision relationship declares a revision scheme in the manifest or authority map.

Permitted v0.3.0 schemes:

- `alpha_upper`: `A` through `Z`, then multi-letter uppercase values where explicitly allowed, matching `^[A-Z]{1,3}$`;
- `numeric_integer`: non-negative base-10 integer text matching `^[0-9]+$`;
- `numeric_zero_padded`: fixed-width non-negative integer text where the width is declared, such as `00`, `01`, `02`;
- `explicit_sequence`: a declared ordered list of accepted revision labels for a package or document family.

Mixed schemes are permitted only when declared per document type or canonical object. The evaluator must not infer sequence order for undeclared prefixes, suffixes, preliminary labels, construction status codes, or client-specific revision conventions.

Invalid revision format, impossible revision progression, conflicting current revision, or use of a superseded revision for a required current document is an automatic release hold unless the authority map routes a non-release-critical field to review.

## 7. Duplicate Tags, Items, and Documents

Duplicates are forbidden by default for canonical IDs.

Intentional duplicates must be represented explicitly with:

- a duplicate policy in `authority_map.json`;
- a stable canonical parent identifier;
- unique occurrence identifiers such as `item_id` or `duplicate_instance_id`;
- relationship role or scope, such as `spare`, `alternate`, `assembly_member`, or `parallel_equipment`;
- source evidence for the authority permitting the duplicate;
- release-hold behavior if required disambiguation is missing.

Two source rows with the same `equipment_tag`, `drawing_number`, `document_id`, `datasheet_id`, `specification_id`, or `file_ref_id` are not considered intentional duplicates merely because their filenames, titles, or descriptions differ.

## 8. Mandatory Package Gates

Gates execute before scored consistency checks and determine whether dependent checks may run.

| Gate | Required condition | Default state on failure |
|---|---|---|
| Manifest gate | `package_manifest.json` exists, parses, and declares a supported schema version | `extraction_or_tool_failure` if parsing prevents evaluation; otherwise `automatic_fail` |
| Source inventory gate | All mandatory source files are declared and loadable | `extraction_or_tool_failure` |
| Authority map gate | `authority_map.json` exists, parses, and declares required authority paths | `missing_authoritative_information` or `automatic_fail` for contradictory authority |
| Boundary gate | Declared source and controlled file paths remain inside the allowed package root | `automatic_fail` |
| Identifier gate | Required canonical IDs are present, normalized, and structurally valid | `automatic_fail` or `evaluator_uncertainty` for ambiguous normalization |
| Duplicate gate | Duplicate canonical IDs follow an explicit duplicate policy | `automatic_fail` |
| Revision gate | Revision values match declared schemes and current/superseded status is evaluable | `automatic_fail` or `engineering_review_required` if explicitly review-routed |
| Evidence-locator gate | Each source record has a CSV or JSON evidence locator sufficient for audit | `automatic_fail` |
| Expected-asset isolation gate | Benchmark expected assets are hidden from producer-visible inputs | `evaluator_uncertainty` for contaminated benchmark runs |
| Result-output gate | Generated outputs target a run directory outside the versioned package | `automatic_fail` |

Gate failures are findings with evidence. Dependent checks must not execute when their required inputs failed a gate.

## 9. Deterministic Check Families

### 9.1 Package Inventory

- required documents are present;
- unexpected, orphaned, or duplicate documents are identified;
- referenced files exist inside the package boundary;
- register entries and controlled files have reciprocal mappings.

### 9.2 Revision Consistency

- drawing register revision matches the authoritative declaration;
- drawing metadata and revision history agree where required;
- superseded revisions are not selected as current;
- revision progression follows the declared scheme;
- current revisions have evidence in the revision-history source when required.

### 9.3 Drawing and Register Relationships

- every required drawing maps to one canonical register entry;
- every register entry maps to the expected controlled file reference;
- title, tag, status, and discipline relationships match configured rules;
- filename-only matches are insufficient without canonical IDs.

### 9.4 BOM and Equipment Relationships

- required item or tag exists;
- duplicate tag/item relationships comply with explicit duplicate policy;
- quantity, part/material identifier, and revision relationships match authority rules;
- BOM/equipment records resolve to the correct drawing, datasheet, specification, and equipment scope.

### 9.5 Datasheet and Specification Relationships

- required datasheet/specification mappings exist;
- identifier and revision are current;
- controlled fields agree with authoritative metadata;
- missing or ambiguous mapping routes to review or missing authority rather than fabricated resolution.

### 9.6 Authority Conflicts

- secondary sources disagree with authority;
- multiple sources claim authority where only one is permitted;
- authority source is absent;
- authority rule is incomplete, contradictory, or unsupported.

## 10. Finding and Evidence Contract

Every finding includes:

- `finding_id`;
- `check_id` and check version;
- `package_id`;
- result state;
- severity;
- release-hold flag;
- affected canonical identifiers;
- authority rule ID;
- authoritative source reference;
- compared source reference or references;
- expected and actual values where applicable;
- original and normalized values;
- source file and row, record, or JSON-pointer location;
- concise rationale;
- reviewer requirement or owner where applicable;
- evaluator version.

No failure, review item, missing-authority item, or uncertainty item may rely only on a free-text statement without evidence references.

### 10.1 Evidence Locators

CSV evidence locators must include:

- `source_type`;
- package-relative `source_file`;
- `format: "csv"`;
- one-based `row_number` counted from the physical file, including the header row;
- `header_row_number`;
- `column_name` where field-specific;
- stable row key when available, such as `document_id`, `item_id`, or `equipment_tag`;
- original value and normalized value for compared fields.

JSON evidence locators must include:

- `source_type`;
- package-relative `source_file`;
- `format: "json"`;
- RFC 6901 `json_pointer`;
- record ID when available;
- property name where field-specific;
- original value and normalized value for compared fields.

File-reference evidence locators must include `file_ref_id`, declared relative path, resolved package-relative path, and boundary-check result.

## 11. Result States

### 11.1 Finding States

- `automatic_pass`
- `automatic_fail`
- `engineering_review_required`
- `missing_authoritative_information`
- `extraction_or_tool_failure`
- `evaluator_uncertainty`

### 11.2 Package State Precedence

The package state is selected by this precedence:

1. Any release-critical `automatic_fail` -> package `automatic_fail`.
2. Any unresolved `extraction_or_tool_failure` affecting required evidence -> package `extraction_or_tool_failure`.
3. Any `missing_authoritative_information` affecting a required decision -> package `missing_authoritative_information`.
4. Any `evaluator_uncertainty` affecting a required decision -> package `evaluator_uncertainty`.
5. Any `engineering_review_required` -> package `engineering_review_required`.
6. Package is `automatic_pass` only when all mandatory gates and required checks pass and no hold, review, missing-authority, tool-failure, or uncertainty state remains.

`package_result.json` must also retain all non-pass finding states in a blocking-state summary so precedence does not erase lower-priority evidence. A numeric score is supplementary and cannot override mandatory holds or state precedence.

## 12. Outputs and CLI Exit Codes

Required outputs:

- immutable `package_result.json`;
- evidence-linked issue register in CSV and Markdown;
- release-readiness summary;
- CLI exit code aligned to package state;
- benchmark metadata and evaluator version;
- pointers to preserved logs and failed artifacts.

`audit-package` package-state exit codes:

| Package state | Exit code |
|---|---:|
| `automatic_pass` | 0 |
| `automatic_fail` | 1 |
| `engineering_review_required` | 2 |
| `missing_authoritative_information` | 3 |
| `extraction_or_tool_failure` | 4 |
| `evaluator_uncertainty` | 5 |

Command usage errors, invalid command-line arguments, missing package path, or environment failures that occur before a package state can be produced are CLI errors rather than package states. They must use a distinct non-package exit code and must not be recorded as a successful package audit.

## 13. Human Review Boundary

The evaluator may identify inconsistencies and recommend review routing. A qualified human must decide:

- whether conflicting technical values are acceptable;
- whether a deviation is intentional;
- whether the package is released;
- whether engineering calculations, design intent, codes, standards, or safety requirements are satisfied;
- whether documents are authenticated, stamped, or contractually acceptable.

The evaluator output is an issue register, evidence package, release-readiness state, and draft review package. It is not engineering sign-off.

## 14. Explicit Exclusions for v0.3.0

- PDF text/table extraction;
- drawing-image interpretation;
- native CAD metadata extraction;
- GD&T or standards compliance;
- design optimization or generation;
- autonomous redlining or document issue;
- engineering sign-off or release approval;
- agent trajectory scoring;
- API, database, frontend, dashboard, or hosted deployment;
- RAG, reward models, LoRA, or RL.

## 15. P0.1 Review Question Resolutions

| Question | Resolution |
|---|---|
| 1. Which minimum source files are mandatory for every package? | The seven files in Section 2 are mandatory for every v0.3.0 package. |
| 2. Which canonical IDs are globally unique versus package-scoped? | Only `package_id` is globally unique by itself. All other canonical IDs are package-scoped, and `revision_id` is additionally scoped to its owning object. |
| 3. Which fields require authority declarations? | Every field or relationship used by gates, checks, release holds, issue registers, or release summaries requires an authority declaration; minimum paths are listed in Section 5.1. |
| 4. Which conflicts are automatic release holds? | The release-hold list in Section 5.2 is mandatory for v0.3.0. |
| 5. Which missing values route to review rather than fail? | Only authority-map-declared, non-release-critical, reviewable missing values route to `engineering_review_required`; required missing authority routes to `missing_authoritative_information`. |
| 6. What revision formats are permitted? | `alpha_upper`, `numeric_integer`, `numeric_zero_padded`, and `explicit_sequence`, only when declared. |
| 7. How are duplicate tags/items represented intentionally? | Duplicates require an explicit duplicate policy, unique occurrence IDs, role/scope, authority evidence, and release-hold behavior for missing disambiguation. |
| 8. What evidence locator is required for JSON and CSV records? | CSV locators require source type, relative file, one-based row, header row, column when applicable, row key, and original/normalized values. JSON locators require source type, relative file, RFC 6901 JSON pointer, record ID when available, property, and original/normalized values. |
| 9. Which package state maps to each CLI exit code? | Section 12 maps package states to exit codes 0 through 5. |
| 10. What data is hidden from a producing agent in a future benchmark run? | `expected/` assets, expected findings, expected release state, seeded fault IDs, hidden golden relationship graphs, held-out answer keys, prior result outputs, evaluator traces, and any benchmark-only notes not part of producer-visible task instructions. |

## 16. Acceptance Evidence and Next Gate

P0.1 deliverables:

- reviewed version of this contract;
- reviewed authority-map example;
- decision-register entry recording accepted scope, authority rules, state precedence, and hidden-data boundary;
- evidence-register entry linking the reviewed artifacts;
- explicit unresolved decisions, if any;
- no package-loader, schema, rule-engine, PDF, CAD, agent, API, database, RAG, or frontend implementation changes.

Unresolved P0.1 decisions: none within the structured-data scope defined here.

P0.2 must accept the benchmark protocol, fault matrix, and acceptance plan before any package-assurance implementation begins.
