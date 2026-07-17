# P2.2 Drawing Metadata Register Authority Definition v0.3.0

## Control Status

- **WBS:** P2.2, third directional document-relationship slice
- **Status:** Proposed definition; implementation blocked pending user acceptance
- **Integration baseline:** `main` at PR #31 merge commit `36338c0`
- **Definition branch:** `codex/p2.2-drawing-metadata-orphan-definition`
- **Decisions:** D-059, D-060
- **Evidence:** EV-056, EV-057

This definition is the authorized next block after the accepted
`drawing_register_metadata_presence` implementation was integrated through PR
#31 and verified on the exact merged tree. It defines behavior only. No
executable relationship, package-state routing, fixture, schema, authority-map,
report, or CLI change is authorized until the user accepts this contract.

## Plain-Language Goal

Answer one release-control question:

> Does every drawing-metadata record have an authoritative drawing-register
> record with the same normalized drawing number?

Drawing metadata can claim that a drawing exists even when the controlled
drawing register contains no such drawing. The evaluator must identify the
exact metadata record, show the authoritative register collection that was
searched, and place a release hold for missing authority. It must not treat the
metadata record as self-authorizing, infer authority from a filename, or decide
whether the package may be released.

## Why This Is a Separate Direction

The accepted counterpart check starts from the authoritative register. A
registered drawing with no metadata counterpart is a missing required secondary
value and routes to `automatic_fail`.

This slice starts from metadata. A metadata drawing with no register row has no
authoritative source for a required release decision. Under `AUTH-DWG-001`,
that routes to `missing_authoritative_information`. Combining the directions
would hide different authority, result-state, evidence, and downstream routing
contracts.

## Narrow Authority Interpretation

`AUTH-DWG-001` controls `drawing.current_revision`, names the drawing register
as authoritative, and names drawing metadata as a secondary source. This slice
does not reinterpret that rule as universal register authority over every
drawing field or over package document inventory.

The check asks a narrower question: can the accepted metadata record's
`revision_id` claim be resolved to the authoritative source required by
`AUTH-DWG-001`? If no register row exists for the same normalized drawing
number, the required authority path for that revision claim cannot be resolved.
That is `missing_authoritative_information`. Title, status, ownership,
file-reference, manifest declaration, and drawing-existence policies remain
outside this slice unless a later accepted authority rule defines them.

## Frozen Slice Contract

| Item | Decision |
|---|---|
| Check ID | `drawing_metadata_register_authority` |
| Check version | `0.3.0` |
| Finding code | `DRAWING_REGISTER_AUTHORITY_MISSING` |
| Business object | One accepted drawing-metadata record |
| Join key | Exact normalized `drawing_number` |
| Required authority | Exactly one `drawing_register` record |
| Authority rule | `AUTH-DWG-001` |
| Normalization | `canonical_identifier_v1` |
| Missing-authority state | `missing_authoritative_information` |
| Severity | `high` |
| Release hold | `true` |
| Review owner | `document_control` |
| Future package state for the isolated fault | `missing_authoritative_information` |
| Future CLI exit for the isolated fault | `3` |

Package-state precedence is not implemented in P2.2. If a future package also
contains a higher-precedence state, P2.4 must select the package state from the
complete result while retaining this missing-authority finding.

## Controlled Inputs

The slice consumes only records already loaded and accepted by P2.1:

1. `inputs/drawing_metadata.json` as the source containing the claimed drawing;
2. `inputs/drawing_register.csv` as the authoritative source;
3. `authority/authority_map.json`, rule `AUTH-DWG-001`;
4. the package ID from the accepted manifest; and
5. exact source locators from the structured-source adapters.

The check does not reopen package files, parse another format, inspect expected
assets, or alter an accepted fixture.

## Prerequisite Boundary

The relationship evaluator receives a completed `PackageGateEvaluation`.

- It may run only when `dependent_checks_allowed` is true and the accepted
  manifest, drawing metadata, drawing register, and authority rule are present.
- If P2.1 blocks dependent checks, this check is `skipped` and names the
  blocking gate or gates.
- It must not reinterpret or duplicate P2.1 failures.
- P2.1 remains responsible for source presence and parseability, authority-map
  validity, identifier validity, duplicate drawing numbers, boundary control,
  revision evaluability, and evidence-locator completeness.
- A missing or malformed drawing-register file is a P2.1 source-inventory
  failure, not a P2.2 `DRAWING_REGISTER_AUTHORITY_MISSING` finding.
- An accepted register file that lacks a row for an accepted metadata drawing
  is the P2.2 condition owned by this check.

## Deterministic Selection

After P2.1 passes:

1. index valid drawing-metadata records by normalized `drawing_number`;
2. index valid drawing-register records by the same normalization;
3. select metadata drawing numbers that are absent from the register;
4. sort selected drawing numbers in ascending normalized order; and
5. emit one finding per selected metadata drawing.

P2.1 already rejects unapproved duplicate drawing numbers in either source.
This check therefore compares zero-or-one authority membership and does not
create another duplicate policy.

Source order, JSON position, CSV data-row position, dictionary order, filenames,
titles, and model judgment must not change the substantive outcome or finding
order.

## Clean Outcome

The check passes when every accepted drawing-metadata record has one exact
authoritative register counterpart. A pass contains:

- `check_id: drawing_metadata_register_authority`;
- `check_version: 0.3.0`;
- `status: passed`;
- no findings;
- a summary with the number of metadata records checked; and
- deterministic metadata drawing-number locators plus one register-membership
  locator.

An empty metadata collection is not automatically accepted as a complete
package. P2.1 and other accepted checks own source requirements and the opposite
counterpart direction. This check reports only the authority relationship it
owns.

## Exact Development Fault Outcome

The reviewed development fault removes only the
`DOC-DWG-001,DWG-PSK-1001` data row from a temporary copy of
`inputs/drawing_register.csv`. Metadata record `DWMETA-001` remains
unchanged.

The probe performed during definition review confirms:

- all eight P2.1 gates still pass;
- `drawing_register_metadata_revision` passes for the remaining exact pair;
- `drawing_register_metadata_presence` passes because each remaining register
  row has metadata; and
- only this new direction owns the missing authority for `DWG-PSK-1001`.

The required finding is:

| Field | Required value |
|---|---|
| `check_id` | `drawing_metadata_register_authority` |
| `check_version` | `0.3.0` |
| `package_id` | `PKG-DEV-PUMP-SKID-001` |
| `code` | `DRAWING_REGISTER_AUTHORITY_MISSING` |
| `result_state` | `missing_authoritative_information` |
| `severity` | `high` |
| `release_hold` | `true` |
| `authority_rule_id` | `AUTH-DWG-001` |
| affected identifiers | `DOC-DWG-001`, `DWG-PSK-1001` |
| expected value | `authoritative drawing_register record` |
| actual value | `missing` |
| review owner | `document_control` |

The rationale may use different wording, but it must state that metadata drawing
`DWG-PSK-1001` has no authoritative drawing-register record.

## Required Evidence

An authority-absence finding needs evidence of both the existing claim and the
complete authoritative membership that was searched.

### Metadata Drawing Locator

- source type: `drawing_metadata`;
- source file: `inputs/drawing_metadata.json`;
- format: `json`;
- JSON pointer: `/records/0/drawing_number`;
- record ID: `DWMETA-001`;
- property name: `drawing_number`;
- original value: `DWG-PSK-1001`;
- normalized value: `DWG-PSK-1001`.

### Authoritative Register Collection Locator

- source type: `drawing_register`;
- source file: `inputs/drawing_register.csv`;
- format: `csv`;
- physical row number: `1`;
- header row number: `1`;
- column name: `drawing_number`;
- no row key;
- original value: source-order drawing-number membership after the temporary
  removal, `["DWG-PSK-1002"]`;
- normalized value: sorted normalized membership,
  `["DWG-PSK-1002"]`.

The CSV locator is deliberately anchored to the physical
`drawing_number` header at row 1. It identifies the complete column that was
searched without inventing a data row for the missing drawing. The membership
arrays carry the observed collection contents. A row key is unavailable because
the locator describes a collection, not an existing register record.

This shape satisfies the workflow contract's CSV row and header requirements
and is supported by the accepted `EvidenceLocator` serialization. It must not
be replaced with a null row number, a fake data-row locator, a free-text
statement, an absolute temporary path, or a new evidence model during
implementation. A concrete incompatibility returns the slice to definition
review.

For an empty accepted register, both membership arrays are empty while the row
1 header anchor remains valid.

## Stable Identity and Ordering

The finding ID must derive from stable semantic content, including:

- package ID;
- check ID and version;
- finding code;
- authority rule ID;
- normalized drawing number;
- result state;
- release-hold value; and
- normalized expected and actual values.

It must not include timestamps, absolute paths, run IDs, process IDs, CSV data
row numbers, JSON positions, source order, or dictionary order.

For unchanged semantic inputs, repeated runs and source-record reordering must
produce the same finding IDs, finding order, affected identifiers, expected and
actual values, and normalized register membership. Physical JSON positions and
source-order membership may reflect the inspected temporary package.

Check-level evidence is ordered by normalized metadata drawing number, followed
by the register collection locator. Each finding contains its metadata field
locator first and the register collection locator second.

## Check Ordering and Existing Behavior

The accepted check order becomes:

1. `drawing_register_metadata_revision`;
2. `drawing_register_metadata_presence`;
3. `drawing_metadata_register_authority`.

The new check is appended. The existing checks keep their accepted semantics,
finding identities, evidence, and order.

- The revision check compares exact pairs only.
- The presence check owns registered drawings missing metadata.
- The authority check owns metadata drawings missing register authority.
- No check recomputes, suppresses, or reclassifies another check's finding.
- P2.4 later routes package state from the complete immutable result set.

## Downstream Handoff

Later accepted work must consume this finding without recomputing authority:

1. P2.4 retains the finding and applies the accepted package-state precedence;
2. for the isolated fault, the package state is
   `missing_authoritative_information`;
3. P3.1 writes one evidence-linked issue-register row;
4. P3.2 shows the release hold and missing authority in the release summary; and
5. P3.3 returns package-state exit code `3` for the isolated fault.

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

1. the clean development package checks both metadata records, passes all three
   ordered P2.2 checks, and emits no authority finding;
2. a temporary copy with only register row `DOC-DWG-001` removed leaves all
   eight P2.1 gates passing, leaves both accepted P2.2 checks passing, and emits
   exactly one frozen `DRAWING_REGISTER_AUTHORITY_MISSING` finding;
3. the finding contains the exact metadata locator and header-anchored register
   collection locator defined above, with no absolute temporary path;
4. removing both register data rows leaves P2.1 passing and emits one authority
   finding per metadata drawing in ascending normalized drawing-number order,
   with empty original and normalized register membership;
5. repeated evaluation preserves substantive results and finding IDs;
6. reversing metadata record order under the two-row fault preserves semantic
   finding identity and order, and reversing register rows in a clean copy
   preserves the normalized membership snapshot;
7. a blocked P2.1 evaluation returns all three P2.2 checks as skipped in stable
   order, with blocking gates recorded and no findings;
8. all accepted revision and metadata-presence tests continue to pass without
   changed semantics;
9. focused tests, the full frozen regression suite, repository validation,
   Ruff, and the 80% coverage floor pass; and
10. accepted fixtures, goldens, held-out assets, schemas, authority maps, and
    historical evidence remain unchanged.

Tests may mutate only temporary package copies. No versioned fault fixture or
semantic held-out evaluation is authorized by this definition.

## Explicit Exclusions

This slice does not define or implement:

- the accepted register-to-metadata revision or presence behaviors;
- drawing title, status, discipline, owner, file-reference, or tag agreement;
- manifest-to-drawing reciprocal declaration checks;
- revision-history relationships;
- BOM, equipment-list, datasheet, or specification relationships;
- package-state routing;
- issue-register or release-summary rendering;
- an `audit-package` command;
- semantic held-out execution or tuning;
- PDF/CAD extraction or redlining; or
- agents, APIs, databases, RAG, frontend, hosting, reward models, or RL.

## Review Decisions

| Question | Resolution |
|---|---|
| What user problem does the slice address? | Drawing metadata can claim a release-controlled drawing that has no authoritative register record. |
| Why is this separate from metadata presence? | The authority direction changes the result from missing secondary data to missing authoritative information. |
| Which source is authoritative? | The drawing register under `AUTH-DWG-001`. |
| Why does `AUTH-DWG-001` apply? | It makes the register authoritative for `drawing.current_revision` and metadata secondary; no matching register row leaves the metadata revision claim without that required authority. |
| How are records joined? | Exact normalized `drawing_number`; no fuzzy, filename, title, or position matching. |
| What counts as missing authority? | A metadata drawing number is absent from the accepted register record set. |
| How is the condition classified? | High-severity, release-holding `missing_authoritative_information`. |
| Why is it not `automatic_fail`? | The required authority record is absent; `AUTH-DWG-001` and the workflow contract reserve that condition for the missing-authority state. |
| What evidence is mandatory? | The metadata drawing-number field and a row-1 header-anchored snapshot of the complete register drawing-number membership. |
| Why may the collection locator omit a row key? | It identifies a searched column, not an existing or invented data row. |
| What is the frozen development fault? | Remove register row `DOC-DWG-001` from a temporary copy while retaining metadata record `DWMETA-001`. |
| How are duplicates handled? | P2.1 must pass first and already rejects unapproved duplicate drawing numbers. |
| What happens when the register file is missing? | P2.1 fails source inventory and all P2.2 checks skip. |
| Does this change accepted checks? | No. It appends one third check and preserves both existing behaviors. |
| What remains blocked? | Implementation pending acceptance, all other relationships, routing, reports, CLI, semantic held-out evaluation, and deferred capabilities. |

## Definition of Done

This definition block is done when:

- this document is reviewed against the accepted workflow contract, authority
  map, acceptance plan, source layouts, evidence model, and P2.1 boundary;
- the controlling workbook records PR #31 integration, exact merged-tree
  verification, this definition decision, and its review evidence;
- the final diff proves that no executable behavior or protected-asset change
  was added;
- the branch is committed, pushed, and opened as a draft definition PR; and
- the user accepts, revises, or rejects the definition before implementation.
