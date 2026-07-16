# v0.3.0 Mechanical Package Consistency Audit — Workflow Contract

**Status:** Draft for P0.1 review
**Release:** v0.3.0
**Scope:** Structured package metadata and controlled file references

## 1. Purpose

Evaluate whether a controlled mechanical document package is internally consistent enough to proceed to human release review.

The workflow identifies deterministic discrepancies, missing authority, tool failures, and unresolved engineering judgment. It does not approve engineering content or replace qualified review.

## 2. In-Scope Inputs

A package contains versioned structured representations of:

1. package manifest;
2. drawing register;
3. drawing metadata records;
4. BOM or equipment-list records;
5. datasheet or specification metadata;
6. revision-history records;
7. controlled file references.

The pilot accepts JSON and CSV data. File references may point to PDFs, drawings, spreadsheets, or other artifacts, but v0.3.0 checks reference existence and declared metadata only. It does not extract content from those files.

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

## 4. Canonical Identifiers

Every relationship must resolve through declared canonical IDs rather than filenames alone.

Minimum identifiers:

- `package_id`
- `document_id`
- `drawing_number`
- `revision_id`
- `item_id`
- `equipment_tag`
- `datasheet_id`
- `specification_id`
- `file_ref_id`

Normalization rules must be declared and versioned. Normalization may trim whitespace and apply configured case rules, but it must not silently remove meaningful punctuation, leading zeroes, revision suffixes, or tag structure.

An original source value and normalized value must both remain available in evidence.

## 5. Authority Model

Authority is package- and field-specific. The evaluator must not infer authority from file order, filename, modification time, or model judgment.

`authority_map.json` declares, for each controlled field or relationship:

- authoritative source type;
- allowed secondary sources;
- precedence order where explicitly permitted;
- required agreement rule;
- escalation behavior when authority is missing or contradictory;
- human owner or discipline for review where applicable.

Example:

```json
{
  "schema_version": "0.3.0",
  "rules": [
    {
      "field": "drawing.current_revision",
      "authoritative_source": "drawing_register",
      "secondary_sources": ["drawing_metadata", "revision_history"],
      "on_missing_authority": "missing_authoritative_information",
      "on_conflict": "automatic_fail"
    },
    {
      "field": "equipment.required_operating_pressure",
      "authoritative_source": "datasheet_spec_metadata",
      "secondary_sources": ["bom_or_equipment_list"],
      "on_missing_authority": "engineering_review_required",
      "on_conflict": "engineering_review_required"
    }
  ]
}
```

The example is not a universal engineering hierarchy. Each benchmark package must define its own reviewed authority map.

## 6. Mandatory Package Gates

Gates execute before scored consistency checks.

Minimum gates:

1. package manifest exists and parses;
2. schema versions are supported;
3. required source files are declared and loadable;
4. canonical identifiers are present and structurally valid;
5. declared authoritative sources exist;
6. required file references resolve inside the allowed package boundary;
7. revisions use declared formats;
8. duplicate canonical IDs are rejected unless explicitly allowed;
9. source rows include evidence locations;
10. benchmark expected assets remain isolated from candidate/producer access.

A gate failure produces evidence and routes to automatic fail, missing authoritative information, extraction/tool failure, or evaluator uncertainty as defined by the contract.

## 7. Deterministic Check Families

### 7.1 Package Inventory

- required documents present;
- unexpected/duplicate documents identified;
- referenced files exist;
- orphan files and orphan register entries reported.

### 7.2 Revision Consistency

- drawing register revision matches authoritative declaration;
- drawing metadata and revision history agree where required;
- superseded revisions are not selected as current;
- impossible or malformed revision progression is flagged.

### 7.3 Drawing and Register Relationships

- every required drawing maps to one canonical register entry;
- every register entry maps to the expected controlled file reference;
- title/tag/status relationships match configured rules.

### 7.4 BOM and Equipment Relationships

- required item/tag exists;
- duplicate tag/item relationships are flagged;
- quantity, part/material identifier, and revision relationships match authority rules;
- BOM references resolve to the correct drawing or equipment scope.

### 7.5 Datasheet and Specification Relationships

- required datasheet/specification mapping exists;
- identifier and revision are current;
- controlled fields agree with authoritative metadata;
- missing or ambiguous mapping routes to review or missing authority rather than fabricated resolution.

### 7.6 Authority Conflicts

- secondary sources disagree with authority;
- multiple sources claim authority;
- authority source is absent;
- authority rule is incomplete or not applicable.

## 8. Finding Contract

Every finding includes:

- `finding_id`
- `check_id` and check version
- `package_id`
- result state
- severity
- release-hold flag
- affected canonical identifiers
- authoritative source reference
- compared source reference(s)
- expected and actual values where applicable
- source file and row/record location
- normalized and original values
- concise rationale
- reviewer requirement
- evaluator version

No failure may rely only on a free-text statement without evidence references.

## 9. Result States

### Finding States

- `automatic_pass`
- `automatic_fail`
- `engineering_review_required`
- `missing_authoritative_information`
- `extraction_or_tool_failure`
- `evaluator_uncertainty`

### Package State Precedence

1. Any release-critical `automatic_fail` -> package `automatic_fail`.
2. Any unresolved `extraction_or_tool_failure` affecting required evidence -> package `extraction_or_tool_failure`.
3. Any `missing_authoritative_information` affecting a required decision -> package `missing_authoritative_information`.
4. Any `engineering_review_required` -> package `engineering_review_required` unless a higher-precedence state applies.
5. Any `evaluator_uncertainty` affecting a required decision -> package `evaluator_uncertainty` unless a higher-precedence state applies.
6. Package is `automatic_pass` only when all mandatory gates and required checks pass and no hold/review/uncertainty state remains.

A numeric score is supplementary and cannot override this precedence.

## 10. Outputs

Required outputs:

- immutable `package_result.json`;
- evidence-linked issue register in CSV and Markdown;
- release-readiness summary;
- CLI exit code aligned to package state;
- benchmark metadata and evaluator version;
- pointers to preserved logs and failed artifacts.

## 11. Human Review Boundary

The evaluator may identify inconsistencies and recommend review routing. A qualified human must decide:

- whether conflicting technical values are acceptable;
- whether a deviation is intentional;
- whether the package is released;
- whether engineering calculations, design intent, codes, standards, or safety requirements are satisfied;
- whether documents are authenticated or stamped.

## 12. Explicit Exclusions for v0.3.0

- PDF text/table extraction;
- drawing-image interpretation;
- native CAD metadata extraction;
- GD&T or standards compliance;
- design optimization or generation;
- autonomous redlining or document issue;
- engineering sign-off;
- agent trajectory scoring;
- API, database, frontend, or hosted deployment.

## 13. P0.1 Review Questions

P0.1 is not accepted until these are resolved:

1. Which minimum source files are mandatory for every package?
2. Which canonical IDs are globally unique versus package-scoped?
3. Which fields require authority declarations?
4. Which conflicts are automatic release holds?
5. Which missing values route to review rather than fail?
6. What revision formats are permitted?
7. How are duplicate tags/items represented intentionally?
8. What evidence locator is required for JSON and CSV records?
9. Which package state maps to each CLI exit code?
10. What data is hidden from a producing agent in a future benchmark run?

## 14. Acceptance Evidence

P0.1 deliverables:

- reviewed version of this contract;
- reviewed authority-map example;
- decision-register entry recording accepted scope and state precedence;
- explicit unresolved decisions, if any;
- no implementation changes.
