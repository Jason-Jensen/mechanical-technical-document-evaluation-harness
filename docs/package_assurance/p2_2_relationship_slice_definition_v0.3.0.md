# P2.2 Relationship Slice Definition v0.3.0

## Control Status

- **WBS:** P2.2, first document-relationship slice
- **Status:** Accepted 2026-07-17; narrow implementation authorized
- **Predecessor:** Accepted P2.1 package gates
- **Definition branch:** `codex/p2.2-relationship-slice-definition`
- **Implementation branch:** `codex/p2.2-relationship-slice-implementation`
- **Integration baseline:** PR #27 merged to `main` at `94d9117` after green CI
- **Decision:** D-049
- **Evidence:** EV-046

## Plain-Language Goal

Answer one question reliably:

> For a drawing that exists in both the drawing register and drawing metadata,
> does the metadata revision match the authoritative register revision?

The evaluator must show both source locations and the expected and actual
revision. It must not guess, use filenames as identity, or decide whether the
package may be released.

This is the first P2.2 slice, not all of P2.2. It proves one useful
cross-document comparison before more relationship rules are added.

## Frozen Slice Contract

| Item | Decision |
|---|---|
| Check ID | `drawing_register_metadata_revision` |
| Check version | `0.3.0` |
| Finding code | `DRAWING_REVISION_MISMATCH` |
| Business object | One drawing present in both controlled sources |
| Join key | Exact normalized `drawing_number` |
| Authoritative value | `drawing_register.revision_id` |
| Compared value | `drawing_metadata.revision_id` |
| Authority rule | `AUTH-DWG-001` |
| Normalization | `canonical_identifier_v1` for the join; declared drawing revision scheme for the compared values |
| Mismatch state | `automatic_fail` |
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
2. `inputs/drawing_metadata.json` as the compared source;
3. `authority/authority_map.json`, rule `AUTH-DWG-001`;
4. the package ID from the accepted manifest; and
5. exact evidence locators already produced by the structured-source adapters.

The slice does not read files directly, reopen the package, parse a new format,
or inspect expected or held-out assets.

## Prerequisite Boundary

The relationship evaluator receives a completed `PackageGateEvaluation`.

- It may run only when `dependent_checks_allowed` is true and the accepted
  manifest and structured sources are present.
- If P2.1 blocks dependent checks, this check is `skipped` and names the
  blocking gate or gates.
- It must not reinterpret a P2.1 failure or create a second finding for the same
  invalid input condition.
- P2.1 remains responsible for parseability, authority-map validity, boundary
  control, canonical identifier validity, duplicates, revision evaluability,
  and evidence-locator completeness.

## Relationship Selection

The first implementation selects only exact pairs that meet all of these
conditions:

1. the drawing-register record has a valid `drawing_number`;
2. one drawing-metadata record has the same normalized `drawing_number`;
3. both records contain an evaluable `revision_id`; and
4. P2.1 has already accepted the applicable authority and revision scheme.

Pair order is ascending normalized `drawing_number`. Source-file order and map
iteration order must not change outcomes.

This slice does not claim that all required drawings have a counterpart.
Missing register rows, missing metadata rows, extra records, title conflicts,
file-reference conflicts, status conflicts, discipline conflicts, and tag
relationships remain separate P2.2 checks. Until those checks exist, the
package-wide P2.2 family cannot claim complete relationship coverage.

## Deterministic Behavior

For each selected pair:

1. retain both original revision values;
2. normalize each value under the declared drawing revision scheme;
3. compare the normalized values exactly;
4. emit a pass outcome when they agree; or
5. emit exactly one `DRAWING_REVISION_MISMATCH` finding when they differ.

The evaluator must not:

- fuzzy-match drawing numbers;
- use title, filename, list position, or record order as identity;
- infer an undeclared revision sequence;
- choose the metadata value over the drawing register;
- downgrade a required conflict to review; or
- emit duplicate findings for one drawing and one authority rule.

## Exact Fault Outcome

The reviewed development fault changes only the metadata revision for
`DWG-PSK-1001` from `C` to `A` in a temporary test copy. Both values remain
structurally valid, so P2.1 must continue to pass and P2.2 owns the conflict.

The required finding is:

| Field | Required value |
|---|---|
| `check_id` | `drawing_register_metadata_revision` |
| `check_version` | `0.3.0` |
| `package_id` | `PKG-DEV-PUMP-SKID-001` |
| `code` | `DRAWING_REVISION_MISMATCH` |
| `result_state` | `automatic_fail` |
| `severity` | `high` |
| `release_hold` | `true` |
| `authority_rule_id` | `AUTH-DWG-001` |
| affected identifiers | `DOC-DWG-001`, `DWG-PSK-1001` |
| expected value | `C` from the drawing register |
| actual value | `A` from drawing metadata |
| review owner | `document_control` |

The rationale may use different wording, but it must state that drawing
metadata revision `A` conflicts with authoritative drawing-register revision
`C` for `DWG-PSK-1001`.

## Required Evidence

The finding contains both field-level locators.

### Authoritative CSV Locator

- source type: `drawing_register`;
- source file: `inputs/drawing_register.csv`;
- format: `csv`;
- physical row number: `2`;
- header row number: `1`;
- column name: `revision_id`;
- row key: `drawing_number = DWG-PSK-1001`;
- original value: `C`;
- normalized value: `C`.

### Compared JSON Locator

- source type: `drawing_metadata`;
- source file: `inputs/drawing_metadata.json`;
- format: `json`;
- JSON pointer: `/records/0/revision_id`;
- record ID: `DWMETA-001`;
- property name: `revision_id`;
- original value: `A`;
- normalized value: `A`.

No absolute path, temporary-directory path, free-text-only evidence, or expected
asset reference may appear in the finding.

## Stable Identity and Ordering

The finding ID must be derived from stable semantic content, including:

- package ID;
- check ID and version;
- authority rule ID;
- normalized drawing number;
- result state; and
- normalized expected and actual values.

It must not include timestamps, absolute paths, run IDs, process IDs, record
positions, or dictionary iteration order.

For unchanged inputs, repeated runs must produce the same substantive check
result, finding ID, finding order, affected identifiers, and evidence locators.

## Module Boundary

P2.2 implementation belongs in a new
`src/mech_eval_harness/package_assurance/relationships.py` module.

The module will:

- accept the completed P2.1 evaluation as input;
- enforce the prerequisite boundary;
- select exact source-record pairs;
- run deterministic relationship comparisons; and
- return relationship-check results and findings.

It will not:

- add relationship rules to `gates.py`;
- select a package-level state;
- write result files or reports;
- implement CLI behavior;
- read protected expected assets;
- change accepted source adapters, schemas, authority rules, or fixtures; or
- introduce a generic rule engine or provider-specific interface.

New result types may be added only when the implementation needs them. They
must preserve the accepted finding and evidence fields and remain separate from
P2.1 gate results.

## Downstream Handoff

Later accepted work must consume the finding without recomputing the comparison:

1. P2.4 retains `automatic_fail` as the package state because the finding is a
   mandatory release hold.
2. P3.1 creates one issue-register row containing the check, drawing, authority,
   expected value, actual value, and both evidence locators.
3. P3.2 shows the release hold in the release-readiness summary.
4. P3.3 returns package-state exit code `1`.

Reports and the CLI must be views of the immutable result. They must not rerun
or reinterpret this relationship rule.

## Acceptance Tests for the Implementation Block

Implementation is complete only when all of these pass:

1. the accepted clean development pair `DWG-PSK-1001` with `C` versus `C`
   produces a pass outcome and no non-pass finding;
2. a temporary copy with metadata revision `A` produces exactly the frozen
   mismatch finding and both exact locators;
3. all P2.1 gates still pass for that valid-but-conflicting mutation;
4. a blocked P2.1 evaluation causes a relationship-check skip with the blocking
   gate recorded and no relationship finding;
5. repeated evaluation produces identical substantive results and finding ID;
6. source-record reordering does not change semantic results or finding order;
7. focused relationship tests pass;
8. the full frozen regression suite, repository validation, Ruff, and the 80%
   coverage floor pass; and
9. accepted clean fixtures, goldens, held-out assets, and historical evidence
   remain byte-for-byte unchanged.

Focused tests may create a temporary package copy. They must never edit the
accepted development package in place. A versioned development fault scenario,
if later required for benchmark execution, needs its own reviewed fixture
decision and inventory update.

## Explicit Exclusions

This slice does not define or implement:

- missing or extra drawing detection;
- title, status, discipline, owner, file-reference, or equipment-tag agreement;
- revision-history comparison;
- BOM, equipment-list, datasheet, or specification relationships;
- authority-conflict routing beyond accepted rule `AUTH-DWG-001`;
- package-state routing;
- issue-register or release-summary rendering;
- an `audit-package` command;
- semantic held-out execution or tuning;
- PDF/CAD extraction or redlining;
- agents, APIs, databases, RAG, frontend, hosting, reward models, or RL.

## Review Decisions

| Question | Resolution |
|---|---|
| What user problem does the slice address? | Wrong drawing revisions crossing controlled sources before release review. |
| Which source wins? | The drawing register under `AUTH-DWG-001`. |
| How are records joined? | Exact normalized `drawing_number`; no fuzzy or filename matching. |
| What is compared? | The declared `revision_id` values. |
| When may the check run? | Only after every P2.1 prerequisite gate passes. |
| What is a clean result? | Equal normalized revisions and no non-pass finding. |
| What is the frozen fault? | Metadata `A` versus authoritative register `C` for `DWG-PSK-1001`. |
| How is the fault classified? | High-severity, release-holding `automatic_fail`. |
| What evidence is mandatory? | Exact register CSV and metadata JSON field locators with original and normalized values. |
| Where will code live? | A separate `relationships.py` module, not `gates.py`. |
| What may change in fixtures? | Only temporary test copies; no accepted or protected asset changes. |
| What remains blocked? | All P2.2 work outside this exact slice, plus all later WBS capabilities. |

## Definition of Done

This definition block is done when:

- this document is reviewed against the accepted workflow contract, authority
  map, acceptance plan, manifest contract, source layouts, and P2.1 boundary;
- the controlling workbook records D-049 and EV-046;
- the final diff proves that no executable P2.2 behavior or protected-asset
  change was added;
- the branch is committed and pushed; and
- the user accepts, revises, or rejects the definition before implementation.
