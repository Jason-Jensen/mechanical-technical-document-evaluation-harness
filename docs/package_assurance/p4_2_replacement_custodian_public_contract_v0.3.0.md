# P4.2 Replacement Custodian Public Contract

**Version:** 0.3.0

**Date:** 2026-07-21

**Authority:** D-110

**Authorized repository main:**
`ea45dcf30fa37d06de2816b6928ca91cec53df94`

**Frozen evaluator behavior:** `4cf9fe8`

## Purpose

This contract is the complete producer-visible input for an isolated benchmark
custodian. It permits creation and structural freeze of one materially distinct
replacement held-out family without exposing evaluator source, tests,
development package values or oracles, prior held-out content, or generated
audit results.

The custodian must not run the package evaluator. The output is not release
evidence until the owner separately accepts the freeze and authorizes a first
semantic run.

## Permitted Inputs

The custodian may read only the files copied into its isolated input bundle:

- this contract;
- `workflow_contract_v0.3.0.md`;
- `acceptance_plan_v0.3.0.md`;
- `p2_3_completion_and_claim_boundary_v0.3.0.md`;
- `p4_2_held_out_contamination_and_replacement_gate_v0.3.0.md`;
- `package_manifest.schema.json`;
- `package_result.schema.json`; and
- `authority_map_example_v0.3.0.json`.

The custodian must not access any repository path, evaluator implementation,
test, benchmark fixture, prior expected asset, result, report, or network
resource.

## Required Output Tree

The custodian writes only beneath `outbound/replacement_family/`:

```text
replacement_family/
  ACCESS_BOUNDARY.md
  family_metadata.public.json
  execution_index.public.json
  material_distinction.public.md
  custodian_attestation.public.md
  freeze_record.public.json
  scenarios/
    S01/package/...
    S02/package/...
    ...
  protected/
    oracle_bundle.json
    clean_relationship_golden.json
    authoring_record.json
    freeze_inventory.json
```

Scenario tokens and directories must be opaque sequential identifiers. Public
files must not reveal which token is clean, a fault, a compound case, or an
expected state. Fault names, mutations, expected states, and exact findings are
protected.

## Replacement Domain

Use a synthetic industrial belt-conveyor drive-station release package. It
must be materially distinct from a pump-skid package and an instrument-air
package in all of these dimensions:

- assembly and equipment domain;
- canonical identifiers and values;
- package size and relationship topology;
- record ordering and fault placement;
- controlled-file names and layout;
- revision convention; and
- authority-rule data shape within the accepted authority contract.

Do not copy or infer any existing benchmark value. All package content must be
newly authored from this public contract.

## Package Structure

Every scenario package contains exactly these required sources:

```text
package_manifest.json
authority_map.json
inputs/drawing_register.csv
inputs/drawing_metadata.json
inputs/bom_or_equipment_list.csv
inputs/datasheet_spec_metadata.json
inputs/revision_history.csv
files/...
```

All paths are package-relative POSIX-style paths. The allowed controlled-file
root is exactly `files`. Controlled files may be simple synthetic text
placeholders because v0.3.0 checks existence and declared identity only.

The clean scenario and every fault scenario must use a distinct `package_id`.
The family identity remains common across scenarios and is recorded outside
the package manifest.

## Structured Source Profiles

### Drawing Register CSV

Required columns, in this order:

```text
document_id,drawing_number,title,revision_id,revision_scheme,document_status,discipline,owner,required_for_release,file_ref_id
```

`required_for_release` is lowercase `true` or `false`.

### BOM Or Equipment List CSV

Required columns, in this order:

```text
item_id,equipment_tag,item_type,description,quantity,quantity_unit,part_or_material_id,drawing_number,datasheet_id,specification_id,required_for_release
```

`quantity` is a finite base-10 number. `required_for_release` is lowercase
`true` or `false`.

### Revision History CSV

Required columns, in this order:

```text
revision_record_id,document_id,owner_identifier_type,owner_identifier,revision_id,revision_scheme,sequence_index,revision_status,release_status,effective_date
```

`sequence_index` is a positive integer. `effective_date` is an ISO-8601 date.

### Drawing Metadata JSON

The top-level object contains:

- `schema_version`: exactly `0.3.0-fixture-example`;
- `source_type`: exactly `drawing_metadata`; and
- `records`: an array.

Every record contains:

```text
record_id, document_id, drawing_number, title, revision_id,
revision_scheme, document_status, discipline, owner, equipment_tags,
required_for_release, file_ref_id
```

`equipment_tags` is an array of strings and `required_for_release` is Boolean.

### Datasheet And Specification Metadata JSON

The top-level object contains:

- `schema_version`: exactly `0.3.0-fixture-example`;
- `source_type`: exactly `datasheet_spec_metadata`;
- `datasheets`: an array; and
- `specifications`: an array.

Every datasheet record contains:

```text
record_id, document_id, datasheet_id, equipment_tag, title, revision_id,
revision_scheme, revision_sequence, document_status, required_for_release,
file_ref_id
```

Every specification record contains:

```text
record_id, document_id, specification_id, equipment_tags, title,
revision_id, revision_scheme, revision_sequence, document_status,
required_for_release, file_ref_id
```

`equipment_tags` and `revision_sequence` are arrays of strings.
`required_for_release` is Boolean.

### Authority Map

Use the bundled authority-map example only as a public structural template.
Set `applies_to` to each scenario package ID. Preserve the accepted source,
state-precedence, CLI-exit, revision-scheme, duplicate-policy, and evidence
contracts. The clean scenario must include usable exact rules:

- `AUTH-DWG-001`;
- `AUTH-DWG-002`;
- `AUTH-BOM-002`;
- `AUTH-SPEC-001`; and
- `AUTH-SPEC-003`.

Do not add a rule for a D-108 deferred claim.

## Accepted Mandatory Gates

The clean package is authored to satisfy these gates in order:

1. `GATE-PKG-MANIFEST-001`;
2. `GATE-PKG-SOURCE-INVENTORY-001`;
3. `GATE-PKG-AUTHORITY-001`;
4. `GATE-PKG-BOUNDARY-001`;
5. `GATE-PKG-IDENTIFIER-001`;
6. `GATE-PKG-DUPLICATE-001`;
7. `GATE-PKG-REVISION-001`; and
8. `GATE-PKG-EVIDENCE-001`.

The package manifest must validate against the bundled schema. Every required
source and controlled file exists. Identifiers are nonblank and unique in
their accepted scope. Revisions are valid under the declared scheme. Evidence
requirements match the accepted authority contract.

## Accepted Relationship Checks

The clean package is authored to satisfy this exact ordered scope:

| Order | Check ID | Required clean relationship | Authority |
| ---: | --- | --- | --- |
| 1 | `drawing_register_metadata_revision` | Register and metadata revisions agree for each required drawing. | `AUTH-DWG-001` |
| 2 | `drawing_register_metadata_presence` | Every required register drawing has one metadata counterpart. | `AUTH-DWG-001` |
| 3 | `drawing_metadata_register_authority` | Every required metadata drawing resolves to the authoritative register. | `AUTH-DWG-001` |
| 4 | `drawing_register_metadata_file_reference` | Register and metadata use the same controlled `file_ref_id`. | `AUTH-DWG-002` |
| 5 | `drawing_register_manifest_file_reciprocity` | Required drawing rows and manifest `document_to_file` declarations agree in both directions. | `AUTH-DWG-002` |
| 6 | `bom_item_equipment_manifest_reciprocity` | Required BOM item/tag rows and manifest `item_to_equipment` declarations agree in both directions. | `AUTH-BOM-002` |
| 7 | `bom_equipment_drawing_presence` | Every required BOM equipment tag appears in at least one drawing-metadata `equipment_tags` array. | `AUTH-BOM-002` |
| 8 | `equipment_datasheet_authority_presence` | Every required BOM equipment tag has exactly one required authoritative datasheet record. | `AUTH-SPEC-001` |
| 9 | `equipment_datasheet_association` | BOM and authoritative metadata `datasheet_id` values agree. | `AUTH-SPEC-001` |
| 10 | `equipment_datasheet_manifest_reciprocity` | Required metadata associations and manifest `equipment_to_datasheet` declarations agree in both directions. | `AUTH-SPEC-001` |
| 11 | `specification_revision_history` | Every required specification revision matches exactly one current revision-history record by `specification_id`. | `AUTH-SPEC-003` |

Relationship types are exactly `document_to_file`, `item_to_equipment`, and
`equipment_to_datasheet` where those checks require manifest declarations.

## Scenario Matrix

Create exactly eight scenarios:

- one clean scenario;
- seven controlled fault scenarios;
- at least four release-blocking faults;
- at least one `missing_authoritative_information` scenario;
- at least one `extraction_or_tool_failure` scenario; and
- at least one compound scenario with two independently expected non-pass
  states that proves the accepted state precedence.

Use only the four package-level states accepted by D-109:

- `automatic_pass` with exit 0;
- `automatic_fail` with exit 1;
- `missing_authoritative_information` with exit 3; and
- `extraction_or_tool_failure` with exit 4.

Do not synthesize `engineering_review_required` or `evaluator_uncertainty`.

The custodian chooses all fault locations, values, and scenario-to-state
mapping. Those details must never appear in a public file.

## Protected Oracle Contract

`protected/oracle_bundle.json` contains one exact record per opaque scenario
token. Each record includes all fields required by Sections 9 through 12 of the
accepted acceptance plan:

- scenario, package, family, split, and benchmark identities;
- seeded-fault identity and scenario type;
- exact protected mutation description and source locator;
- affected canonical identifiers;
- required check ID or exact allowed check-ID set;
- expected finding state, severity, and release hold;
- expected package state and CLI exit;
- exact expected and actual values or missing/conflict condition;
- required evidence locators;
- expected gate and check outcomes, skips, and blocking gate;
- exact required findings and exact allowed incidental findings;
- reviewer and `frozen_pre_execution` status.

A clean scenario permits zero non-pass findings. Wildcards are prohibited.
Finding IDs need not be precomputed, but every semantic field from which the
evaluator derives a stable finding must be exact.

`protected/clean_relationship_golden.json` independently records every clean
required drawing, item/tag, file, datasheet, and specification relationship
with package-relative evidence locators.

## Public Execution Index

`execution_index.public.json` contains only:

- schema version;
- family ID;
- benchmark revision;
- opaque scenario tokens;
- package roots; and
- expected count of four output publications per scenario.

It must not contain scenario names, faults, states, exits, finding counts,
source mutations, or oracle paths beyond the single protected bundle path.

## Freeze And Hash Rules

Use SHA-256 over raw file bytes. Paths are relative POSIX paths and sorted by
ordinal byte order.

`protected/freeze_inventory.json` records every family file except the two
freeze records, with path, byte count, and SHA-256. It also records exact
per-scenario package-tree hashes.

The public freeze record contains only:

- schema version, family ID, benchmark revision, and creation date;
- custodian role and isolation attestation;
- authorized main and frozen evaluator behavior commits;
- scenario and file counts;
- producer-bundle SHA-256;
- protected-bundle SHA-256;
- complete-family SHA-256;
- contamination status `frozen_isolated_pre_execution`;
- semantic execution count `0`; and
- owner acceptance status `pending`.

Bundle hashes are SHA-256 of the UTF-8 inventory lines
`<file_sha256><two spaces><relative_posix_path><newline>` sorted by path.
The complete-family hash covers every non-freeze file.

## Custodian Verification

The custodian may use JSON parsing, CSV parsing, JSON Schema validation, file
existence checks, duplicate checks, cross-file reasoning, and SHA-256 hashing.
It must not import repository code, install dependencies, call a package CLI,
or execute any evaluator behavior.

Before completion, the custodian records:

- every path read from the input bundle;
- every path written beneath `outbound/replacement_family/`;
- commands used;
- schema and structural check results;
- exact file and bundle hashes;
- confirmation that no network or external path was accessed; and
- confirmation that semantic execution count is zero.

## Stop Boundary

The custodian stops after freeze creation. It must not publish expected values
outside `protected/`, run the evaluator, diagnose expected evaluator behavior,
or modify its output after the final hashes are written.
