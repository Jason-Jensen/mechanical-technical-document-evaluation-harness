# P2.2 Drawing File Reference Definition v0.3.0

## Control Status

- **WBS:** P2.2, fourth document-relationship slice
- **Status:** Definition proposed; explicit user acceptance pending
- **Integration baseline:** `main` at PR #33 merge commit `8d7f314`
- **Definition branch:** `codex/p2.2-drawing-file-reference-definition`
- **Proposed implementation branch:**
  `codex/p2.2-drawing-file-reference-implementation`
- **Decisions:** D-065, D-066
- **Evidence:** EV-062, EV-063

PR #33 integrated the accepted `drawing_metadata_register_authority` check and
its acceptance record to `main` at `8d7f314`. Exact merged-tree verification
passed before this branch was created.

This document defines the next bounded relationship behavior only. It does not
authorize executable behavior, package-state routing, fixture, schema,
authority-map, report, CLI, semantic held-out, or protected-asset changes.

## Plain-Language Goal

Answer one release-control question:

> When the drawing register and drawing metadata describe the same drawing, do
> they point to the same controlled file reference?

Two file references can both be well formed, declared, inside the package, and
individually valid while one drawing record points to another drawing's file.
That error is easy to miss if validation stops at file existence. This check
compares the two controlled identifiers and shows exactly what each one
resolves to.

## Why This Slice Is Next

The slice reuses the smallest proven relationship boundary:

- both source types are already loaded by P2.1;
- both records are already paired by exact normalized `drawing_number`;
- both `file_ref_id` fields and their source locators already exist;
- manifest file-reference resolution already passed the P2.1 boundary gate;
- `AUTH-DWG-002` already declares the register authoritative; and
- no new schema, source type, duplicate policy, or evidence model is needed.

A temporary development-package copy proved the current gap. Changing only
metadata record `DWMETA-001.file_ref_id` from `FILE-DWG-001` to the existing
and valid `FILE-DWG-002` left all eight P2.1 gates and all three accepted P2.2
checks passing. The proposed fourth check owns that escaped conflict.

## Narrow Authority Interpretation

`AUTH-DWG-002` controls `drawing.file_ref_id`, names `drawing_register` as the
authoritative source, names `drawing_metadata` as a secondary source, and
routes a conflict to `automatic_fail` with a release hold.

This slice implements only cross-source agreement for exact drawing pairs. It
does not claim that matching file-reference IDs alone prove the complete
manifest-to-document relationship. Reciprocal manifest declarations, a shared
undeclared identifier repeated by both sources, file contents, filenames, and
the semantic identity of an extracted PDF or CAD file remain separate controls.

## Frozen Slice Contract

| Item | Decision |
|---|---|
| Check ID | `drawing_register_metadata_file_reference` |
| Check version | `0.3.0` |
| Finding code | `DRAWING_FILE_REFERENCE_MISMATCH` |
| Business object | One exact register/metadata drawing pair |
| Join key | Exact normalized `drawing_number` |
| Authoritative value | Drawing-register `file_ref_id` |
| Compared value | Drawing-metadata `file_ref_id` |
| Authority rule | `AUTH-DWG-002` |
| Normalization | `canonical_identifier_v1` |
| Conflict state | `automatic_fail` |
| Severity | `high` |
| Release hold | `true` |
| Review owner | `document_control` |
| Future package state for the isolated fault | `automatic_fail` |
| Future CLI exit for the isolated fault | `1` |

Package-state precedence is not implemented in P2.2. P2.4 must later retain
this finding and select package state from the complete immutable result set.

## Controlled Inputs

The check consumes only accepted in-memory P2.1 outputs:

1. `drawing_register_record` values and locators;
2. `drawing_metadata_record` values and locators;
3. `authority/authority_map.json`, exact rule `AUTH-DWG-002`;
4. the accepted loaded manifest and resolved file-reference paths for evidence;
5. the package ID from the accepted manifest.

The check does not reopen package files, parse another format, inspect expected
assets, or alter an accepted fixture.

## Prerequisite Boundary

The relationship evaluator receives a completed `PackageGateEvaluation`.

- It may run only when all P2.1 prerequisites passed and the accepted manifest,
  source records, and authority rule are available.
- If P2.1 blocks dependent checks, all four P2.2 checks are `skipped` in stable
  order and name the blocking gate or gates.
- P2.1 remains responsible for source presence and parsing, authority-map
  validity, structural identifier validity, duplicate drawing numbers,
  controlled file existence and boundary checks, revision evaluability, and
  evidence-locator completeness.
- The two accepted directional checks remain responsible for a register drawing
  with no metadata record and metadata with no register authority.
- This check compares exact pairs only. It emits no absence finding and does not
  reinterpret another check's result.

## Deterministic Selection and Comparison

After P2.1 passes:

1. index register and metadata records by normalized `drawing_number`;
2. select the intersection of those drawing-number sets;
3. sort selected drawing numbers in ascending normalized order;
4. normalize each source's `file_ref_id` with `canonical_identifier_v1`;
5. compare the authoritative register value with the metadata value; and
6. emit one finding for each unequal pair.

P2.1 already rejects unapproved duplicate drawing numbers. Source order, JSON
position, CSV position, titles, filenames, dictionary order, and model judgment
must not change the substantive result or finding order.

## Clean Outcome

The check passes when every exact drawing pair has the same normalized
`file_ref_id`. A pass contains:

- the frozen check ID and version;
- `status: passed`;
- no findings;
- a summary with the number of exact drawing pairs compared; and
- deterministic field and file-resolution evidence for each pair.

Check-level evidence is ordered by normalized drawing number. For each pair it
contains the register field locator, metadata field locator, and one manifest
file-reference locator for the shared value. The same resolution locator is not
duplicated merely because both fields agree.

## Exact Development Fault Outcome

The reviewed fault changes only
`inputs/drawing_metadata.json#/records/0/file_ref_id` in a temporary package
copy:

`FILE-DWG-001` -> `FILE-DWG-002`

The authoritative register row remains unchanged. Both file references remain
declared, inside the package boundary, and resolvable. The probe confirms:

- all eight P2.1 gates pass;
- `drawing_register_metadata_revision` passes;
- `drawing_register_metadata_presence` passes;
- `drawing_metadata_register_authority` passes; and
- the exact pair is `DWG-PSK-1001`, register `FILE-DWG-001`, metadata
  `FILE-DWG-002`.

The required finding is:

| Field | Required value |
|---|---|
| `check_id` | `drawing_register_metadata_file_reference` |
| `check_version` | `0.3.0` |
| `package_id` | `PKG-DEV-PUMP-SKID-001` |
| `code` | `DRAWING_FILE_REFERENCE_MISMATCH` |
| `result_state` | `automatic_fail` |
| `severity` | `high` |
| `release_hold` | `true` |
| `authority_rule_id` | `AUTH-DWG-002` |
| affected identifiers | `DOC-DWG-001`, `DWG-PSK-1001`, `FILE-DWG-001`, `FILE-DWG-002` |
| expected value | `FILE-DWG-001` |
| actual value | `FILE-DWG-002` |
| review owner | `document_control` |

The rationale may use different wording, but it must identify the drawing, both
file-reference IDs, and the fact that metadata conflicts with the authoritative
register value.

## Required Evidence

The fault finding contains four locators in this order.

### 1. Authoritative Register Field

- source type: `drawing_register`;
- source file: `inputs/drawing_register.csv`;
- format: `csv`;
- physical row number: `2`;
- header row number: `1`;
- column: `file_ref_id`;
- row key: `document_id = DOC-DWG-001`;
- original and normalized value: `FILE-DWG-001`.

### 2. Compared Metadata Field

- source type: `drawing_metadata`;
- source file: `inputs/drawing_metadata.json`;
- format: `json`;
- JSON pointer: `/records/0/file_ref_id`;
- record ID: `DWMETA-001`;
- property: `file_ref_id`;
- original and normalized value: `FILE-DWG-002`.

### 3. Authoritative File Resolution

- source type: `package_manifest`;
- source file: `package_manifest.json`;
- format: `file_reference`;
- file reference: `FILE-DWG-001`;
- declared and resolved package-relative path:
  `files/drawings/DWG-PSK-1001_rev_C.txt`;
- boundary check: `inside_allowed_root`.

### 4. Compared File Resolution

- source type: `package_manifest`;
- source file: `package_manifest.json`;
- format: `file_reference`;
- file reference: `FILE-DWG-002`;
- declared and resolved package-relative path:
  `files/drawings/DWG-PSK-1002_rev_B.txt`;
- boundary check: `inside_allowed_root`.

The two structured locators prove the conflicting source claims. The two
file-reference locators prove that this is a wrong-but-valid mapping rather
than a missing file or boundary failure. Evidence must not contain an absolute
temporary path.

## Stable Identity and Ordering

The finding ID derives from stable semantic content, including:

- package ID;
- check ID and version;
- finding code;
- authority rule ID;
- normalized drawing number;
- normalized expected and actual file-reference IDs;
- result state; and
- release-hold value.

It must not include timestamps, absolute paths, run IDs, process IDs, row
numbers, JSON positions, source order, filenames, or dictionary order.

Repeated runs and source-record reordering must preserve substantive results,
finding IDs, finding order, affected identifiers, expected and actual values,
and normalized evidence. Physical locators may reflect the inspected package.

## Check Ordering and Existing Behavior

The accepted check order becomes:

1. `drawing_register_metadata_revision`;
2. `drawing_register_metadata_presence`;
3. `drawing_metadata_register_authority`;
4. `drawing_register_metadata_file_reference`.

The new check is appended. The first three retain their accepted semantics,
identities, evidence, and order. No check suppresses or reclassifies another
check's finding.

## Known Adjacent Gap

P2.1 currently proves that manifest-declared file references are structurally
valid, inside the allowed boundary, and resolvable. It does not yet prove that
every source-level `file_ref_id` is declared in the manifest.

This slice therefore does not claim complete `AUTH-DWG-002` coverage. In
particular, two sources repeating the same undeclared identifier would agree
with each other but still require a separate declaration/reciprocity control.
That gap must be defined and tested before the package can claim complete
drawing-to-file assurance. It must not be silently folded into this check
during implementation.

## Downstream Handoff

Later accepted work must consume this finding without recomputing the conflict:

1. P2.4 retains the finding and applies package-state precedence;
2. for the isolated fault, package state is `automatic_fail`;
3. P3.1 writes one evidence-linked issue-register row;
4. P3.2 shows the release hold and both resolved file paths; and
5. P3.3 returns package-state exit code `1` for the isolated fault.

Reports and the CLI remain views of the immutable result.

## Module Boundary

Implementation may extend only
`src/mech_eval_harness/package_assurance/relationships.py` and the smallest
supporting exports and tests required by this check.

It must not:

- add relationship logic to `gates.py`;
- change P2.1 gate meaning or order;
- create another evidence model;
- select a package-level state;
- write reports or result files;
- implement CLI behavior;
- change schemas, authority rules, accepted fixtures, or protected assets;
- inspect semantic held-out content;
- add a generic rule engine; or
- add provider-specific interfaces.

## Implementation Acceptance Tests

Implementation is complete only when all of these pass:

1. the clean development package passes all four ordered P2.2 checks, compares
   both exact drawing pairs, and emits no file-reference finding;
2. a temporary copy with only `DWMETA-001.file_ref_id` changed to the existing
   `FILE-DWG-002` leaves all eight P2.1 gates and the first three P2.2 checks
   passing, then emits exactly one frozen mismatch finding;
3. that finding contains the four exact locators defined above and no absolute
   temporary path;
4. swapping both metadata file-reference values emits two findings in ascending
   normalized drawing-number order;
5. repeated evaluation and reversed metadata source order preserve substantive
   results and finding IDs;
6. a blocked P2.1 evaluation returns all four P2.2 checks as skipped in stable
   order, with blocking gates recorded and no findings;
7. the exact accepted `AUTH-DWG-002` rule is required and no other authority
   rule is substituted;
8. all accepted relationship tests continue to pass without changed semantics;
9. focused tests, the full frozen regression suite, repository validation,
   Ruff, and the 80% coverage floor pass; and
10. accepted fixtures, goldens, held-out assets, schemas, authority maps, and
    historical evidence remain unchanged.

Tests may mutate only temporary development-package copies. No versioned fault
fixture or semantic held-out evaluation is authorized.

## Explicit Exclusions

This slice does not define or implement:

- undeclared source-level file-reference detection;
- manifest document-to-file reciprocal declarations;
- inspection of file contents, filenames, PDFs, or CAD;
- drawing title, status, discipline, owner, or equipment-tag agreement;
- revision-history relationships;
- BOM, equipment-list, datasheet, or specification relationships;
- package-state routing;
- issue-register or release-summary rendering;
- an `audit-package` command;
- semantic held-out execution or tuning;
- agents, APIs, databases, RAG, frontend, hosting, reward models, or RL.

## Ten Review Decisions

| Question | Resolution |
|---|---|
| 1. What user problem does the slice address? | A drawing can point to another drawing's valid controlled file while ordinary presence and boundary checks still pass. |
| 2. Which source is authoritative? | The drawing register under exact rule `AUTH-DWG-002`; metadata is the compared secondary source. |
| 3. How are records selected and compared? | Join exact normalized `drawing_number` pairs, then compare normalized `file_ref_id` values in sorted drawing-number order. |
| 4. How is a mismatch classified? | `automatic_fail`, high severity, release hold true, owned by `document_control`. |
| 5. What evidence is mandatory? | Both source-field locators plus manifest file-resolution locators for the authoritative and conflicting references. |
| 6. Why include file-resolution evidence? | It proves the isolated fault is a wrong-but-valid mapping, not a missing file or boundary failure. |
| 7. What happens to missing counterparts? | The two accepted directional checks retain ownership; this check compares exact pairs only. |
| 8. What is the frozen development fault? | Change only `DWMETA-001.file_ref_id` from `FILE-DWG-001` to valid `FILE-DWG-002` in a temporary copy. |
| 9. What does this slice not prove? | It does not prove source-to-manifest declaration or full document-to-file reciprocity when both sources repeat the same bad identifier. |
| 10. What remains blocked? | Implementation until user acceptance and definition integration, plus all other relationships, routing, reports, CLI, held-out semantics, and deferred capabilities. |

## Definition of Done

This definition block is done when:

- this document is reviewed against the workflow contract, exact authority
  rule, accepted source layouts, P2.1 boundary, evidence model, and three
  integrated P2.2 checks;
- the controlling workbook records PR #33 integration, exact merged-tree
  verification, this definition decision, and its review evidence;
- the final diff proves no executable behavior or protected-asset change was
  added;
- the branch is committed, pushed, and opened as a draft definition PR; and
- the user accepts, revises, or rejects the definition before implementation.

The document and evidence review are complete. Implementation remains blocked
until explicit user acceptance and integration of this definition.
