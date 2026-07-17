# P2.2 Drawing Metadata Presence Slice Definition v0.3.0

## Control Status

- **WBS:** P2.2, second document-relationship slice
- **Status:** Accepted and integrated definition; implementation ready for acceptance
- **Predecessor:** First P2.2 relationship slice integrated through PR #28
- **Definition branch:** `codex/p2.2-drawing-counterpart-definition`
- **Implementation branch:** `codex/p2.2-drawing-metadata-presence-implementation`
- **Implementation commit:** `b24ca65`
- **Integration baseline:** `main` at PR #30 merge commit `551200b`
- **Decisions:** D-054, D-055, D-056, D-057
- **Evidence:** EV-051, EV-052, EV-053, EV-054

The user accepted this definition on 2026-07-17. PR #30 merged it to `main` at
`551200b`, and the exact merged tree was verified. Implementation authorization
is limited to this exact directional check. Commit `b24ca65` implements it on
PR #31 and is pending user acceptance.

## Plain-Language Goal

Answer one question reliably:

> Does every authoritative drawing-register entry have one drawing-metadata
> record with the same normalized drawing number?

The drawing register says which drawings are authoritative. If a registered
drawing has no metadata record, the evaluator must identify that exact drawing,
show the register evidence and the searched metadata collection, and place a
release hold. It must not invent metadata, infer a match from a filename, or
decide whether the package may be released.

## Why This Is One Direction Only

Counterpart gaps look symmetrical but their authority outcomes are different:

- a register drawing with no metadata record is a required secondary value
  missing under `AUTH-DWG-001`, which routes to `automatic_fail`; and
- a metadata record with no register entry has no authoritative source record,
  which routes to `missing_authoritative_information` and requires a separate
  absence-evidence decision.

Combining both directions would hide that distinction. This slice therefore
defines only register-to-metadata presence. Metadata-only orphan detection is a
later P2.2 slice and remains unimplemented.

## Frozen Slice Contract

| Item | Decision |
|---|---|
| Check ID | `drawing_register_metadata_presence` |
| Check version | `0.3.0` |
| Finding code | `DRAWING_METADATA_MISSING` |
| Business object | One authoritative drawing-register entry |
| Join key | Exact normalized `drawing_number` |
| Required counterpart | Exactly one `drawing_metadata` record |
| Authority rule | `AUTH-DWG-001` |
| Normalization | `canonical_identifier_v1` |
| Missing-counterpart state | `automatic_fail` |
| Severity | `high` |
| Release hold | `true` |
| Review owner | `document_control` |
| Future package state | `automatic_fail` |
| Future CLI exit | `1` |

The future package state and CLI exit describe the required downstream handoff.
They are not implemented in P2.2. Package-state routing remains P2.4 and the
package CLI remains P3.3.

## Controlled Inputs

The slice consumes only records already loaded and accepted by P2.1:

1. `inputs/drawing_register.csv` as the authoritative source;
2. `inputs/drawing_metadata.json` as the required secondary source;
3. `authority/authority_map.json`, rule `AUTH-DWG-001`;
4. the package ID from the accepted manifest; and
5. exact record and source locators from the structured-source adapters.

The slice does not read files directly, reopen the package, parse another
format, inspect expected assets, or alter an accepted fixture.

## Prerequisite Boundary

The relationship evaluator receives a completed `PackageGateEvaluation`.

- It may run only when `dependent_checks_allowed` is true and the accepted
  manifest and both structured sources are present.
- If P2.1 blocks dependent checks, this check is `skipped` and names the
  blocking gate or gates.
- It must not reinterpret or duplicate P2.1 failures.
- P2.1 remains responsible for source presence and parseability, authority-map
  validity, canonical identifier validity, duplicate drawing numbers, boundary
  control, revision evaluability, and field-locator completeness.
- A missing `drawing_metadata.json` file is a P2.1 source-inventory failure, not
  a P2.2 `DRAWING_METADATA_MISSING` finding.

## Deterministic Selection

After P2.1 passes:

1. index valid drawing-register records by normalized `drawing_number`;
2. index valid drawing-metadata records by the same normalization;
3. select drawing numbers in the register that are absent from metadata;
4. sort selected drawing numbers in ascending normalized order; and
5. emit one finding per selected drawing.

P2.1 already forbids unapproved duplicate drawing numbers in either source.
This check therefore compares zero-or-one counterpart membership and does not
create a second duplicate policy.

Source-file order, JSON record order, dictionary order, filenames, titles, and
record positions must not change the substantive outcome or finding order.

## Clean Outcome

The check passes when every authoritative register drawing has one exact
metadata counterpart. A pass contains:

- `check_id: drawing_register_metadata_presence`;
- `check_version: 0.3.0`;
- `status: passed`;
- no findings;
- a summary with the number of authoritative register entries checked; and
- deterministic register and metadata membership evidence.

A package with zero register entries is not automatically accepted by this
check. P2.1 and later accepted package requirements decide whether an empty
authoritative source is allowed. This check reports only the relationship it
owns.

## Exact Development Fault Outcome

The reviewed development fault removes only metadata record `DWMETA-001` for
`DWG-PSK-1001` from a temporary copy of
`inputs/drawing_metadata.json`. The authoritative register row remains.

Every P2.1 gate must continue to pass. The required P2.2 finding is:

| Field | Required value |
|---|---|
| `check_id` | `drawing_register_metadata_presence` |
| `check_version` | `0.3.0` |
| `package_id` | `PKG-DEV-PUMP-SKID-001` |
| `code` | `DRAWING_METADATA_MISSING` |
| `result_state` | `automatic_fail` |
| `severity` | `high` |
| `release_hold` | `true` |
| `authority_rule_id` | `AUTH-DWG-001` |
| affected identifiers | `DOC-DWG-001`, `DWG-PSK-1001` |
| expected value | `drawing_metadata counterpart` |
| actual value | `missing` |
| review owner | `document_control` |

The rationale may use different wording, but it must state that authoritative
register drawing `DWG-PSK-1001` has no drawing-metadata counterpart.

## Required Evidence

Negative relationship findings need evidence of both the existing authority
record and the collection searched for the missing counterpart.

### Authoritative Register Locator

- source type: `drawing_register`;
- source file: `inputs/drawing_register.csv`;
- format: `csv`;
- physical row number: `2`;
- header row number: `1`;
- column name: `drawing_number`;
- row key: `drawing_number = DWG-PSK-1001`;
- original value: `DWG-PSK-1001`;
- normalized value: `DWG-PSK-1001`.

### Compared Collection Locator

- source type: `drawing_metadata`;
- source file: `inputs/drawing_metadata.json`;
- format: `json`;
- JSON pointer: `/records`;
- property name: `records`;
- original value: source-order drawing-number membership after the temporary
  removal, `['DWG-PSK-1002']`;
- normalized value: sorted normalized drawing-number membership,
  `['DWG-PSK-1002']`.

The collection locator deliberately has no `record_id`: it proves the searched
collection rather than claiming a nonexistent record. It remains
package-relative and contains no temporary path, timestamp, expected-asset
reference, or free-text-only evidence.

Implementation review must confirm that this collection-level JSON locator is
compatible with the accepted `EvidenceLocator` serialization before behavior
is accepted. A concrete incompatibility returns this slice to definition
review; it does not authorize an ad hoc evidence type or workflow-contract
rewrite.

## Stable Identity and Ordering

The finding ID must derive from stable semantic content, including:

- package ID;
- check ID and version;
- finding code;
- authority rule ID;
- normalized drawing number;
- result state; and
- normalized expected and actual values.

It must not include timestamps, absolute paths, run IDs, process IDs, CSV row
numbers, JSON positions, source order, or dictionary order.

For unchanged semantic inputs, repeated runs and source-record reordering must
produce the same finding IDs, finding order, affected identifiers, expected and
actual values, and normalized collection membership. Physical evidence
positions may reflect the inspected temporary package.

## Check Ordering and Existing Behavior

The accepted `drawing_register_metadata_revision` check remains first in
`RELATIONSHIP_CHECK_ORDER`. The new presence check is appended second. This
preserves the accepted output order while adding one independent completeness
result.

- The revision check continues to compare exact pairs only.
- The presence check owns missing metadata counterparts.
- One check must not recompute, suppress, or reinterpret the other's finding.
- A missing counterpart may leave the revision check passed for the remaining
  exact pairs while the presence check fails. P2.4 will later route the package
  from the complete immutable result set.

## Module Boundary

The implementation extends only
`src/mech_eval_harness/package_assurance/relationships.py` and the smallest
supporting result exports or tests required by this check.

It must not:

- add relationship logic to `gates.py`;
- change P2.1 gate meaning or order;
- select a package-level state;
- write reports or result files;
- implement CLI behavior;
- change schemas, authority rules, or accepted fixtures;
- inspect protected expected or held-out content;
- add a generic rule engine; or
- add provider-specific interfaces.

## Implementation Acceptance Tests

Implementation is complete only when all of these pass:

1. the clean development package checks both authoritative register entries,
   passes, and emits no presence finding;
2. a temporary copy with `DWMETA-001` removed leaves all P2.1 gates passing and
   emits exactly one frozen `DRAWING_METADATA_MISSING` finding;
3. the finding contains the exact register locator and metadata collection
   locator defined above;
4. removing both metadata records emits one finding per register drawing in
   ascending normalized drawing-number order;
5. repeated runs preserve substantive results and finding IDs;
6. reversing register and metadata record order preserves semantic findings
   and normalized collection membership;
7. a blocked P2.1 evaluation returns both accepted P2.2 checks as skipped in
   stable check order, with the blocking gates recorded and no findings;
8. all accepted revision-check tests continue to pass without changed finding
   semantics;
9. focused tests, the full frozen regression suite, repository validation,
   Ruff, and the 80% coverage floor pass; and
10. accepted fixtures, goldens, held-out assets, schemas, authority maps, and
    historical evidence remain unchanged.

Tests may mutate only temporary package copies. No versioned fault fixture or
semantic held-out evaluation is authorized by this definition.

## Explicit Exclusions

This slice does not define or implement:

- drawing-metadata records with no authoritative register entry;
- missing register rows relative to the package manifest;
- revision mismatch behavior already owned by the first P2.2 slice;
- title, status, discipline, owner, file-reference, or tag agreement;
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
| What user problem does the slice address? | A controlled drawing can be registered for release while its required metadata record is absent. |
| Why is this not bidirectional? | The opposite direction has a different authority state and needs its own absence-evidence contract. |
| Which source is authoritative? | The drawing register under `AUTH-DWG-001`. |
| How are records joined? | Exact normalized `drawing_number`; no fuzzy, filename, title, or position matching. |
| What counts as missing? | A register drawing number is absent from the accepted metadata record set. |
| Why is the result an automatic fail? | `AUTH-DWG-001` is required for release and routes a missing required secondary value to `automatic_fail`. |
| Is it a release hold? | Yes, with high severity and `document_control` ownership. |
| What evidence is mandatory? | The authoritative register drawing-number field and the searched metadata `/records` membership snapshot. |
| How are duplicates handled? | P2.1 must pass first and already rejects unapproved duplicate drawing numbers. |
| What happens when the metadata file is missing? | P2.1 fails source inventory and both P2.2 checks skip. |
| Does this change the first relationship check? | No. The accepted revision check remains first and retains its behavior. |
| What remains blocked? | Acceptance and integration, reverse orphan detection, all other relationships, routing, reports, CLI, semantic held-out evaluation, and deferred capabilities. |

## Definition of Done

This definition block is done when:

- this document is reviewed against the accepted workflow contract,
  authority-map example, development authority map, acceptance plan, source
  layouts, first P2.2 slice, evidence model, and P2.1 boundary;
- the controlling workbook records the PR #28 integration and this directional
  slice decision and evidence;
- the final diff proves that no executable behavior, schema, accepted fixture,
  golden, held-out asset, or historical evidence changed;
- definition-block verification passes;
- the branch is committed, pushed, and opened for review; and
- the user accepts, revises, or rejects the definition before implementation.

All definition-block criteria are satisfied. The user accepted the definition
on 2026-07-17, and PR #30 integration is verified. The scoped implementation
block is authorized.

Implementation commit `b24ca65` satisfies the accepted implementation criteria:
35 focused tests pass, the full suite passes 206 tests with one expected skip,
repository validation passes 5/5, Ruff passes, coverage is 84.93%, and two PR
#31 CI runs pass. No accepted fixture, golden, held-out asset, schema, authority
map, or historical evidence changed. User acceptance remains pending.
