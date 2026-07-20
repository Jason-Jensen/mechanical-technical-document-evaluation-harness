# P2.3 Relationship Expansion Definition v0.3.0

## Control Status

- **WBS:** P2.3, BOM/equipment/datasheet/specification relationship expansion
- **Status:** Accepted; checks 6-7 integrated, practical-use trial gate awaiting CEO input
- **Baseline:** definition integrated through PR #41 at exact `main` `a855d99`
- **Definition branch:** `codex/p2.3-relationship-expansion-definition`
- **Accepted predecessor:** P3.3 through PR #40 at exact `main` commit `e4080fd`
- **Decision:** D-085 proposed; D-086 accepted
- **Evidence:** EV-082 reviewed; EV-083 accepted
- **Protected assets changed:** None
- **Time tracking:** Waived; progress is gate- and evidence-based

## Plain-Language Goal

Expand the first runnable audit beyond drawing controls without claiming more
than the structured package can prove.

P2.3 will add small deterministic checks for BOM item/equipment declarations,
equipment references on drawings, equipment-to-datasheet authority and
agreement, manifest reciprocity, and specification revision history. Each
check must identify the exact source, authority rule, evidence, result state,
release hold, and test fault before implementation.

The current package cannot honestly reconcile several planned fields because
only one source supplies them or the accepted authority map has no exact rule.
Those gaps stay visible and blocked instead of being converted into weak
"present therefore correct" checks.

## Management Decision

P2.3 is divided into two tracks:

1. **Existing-authority implementation track:** six checks supported by the
   accepted source layouts and exact authority rules.
2. **Authority-gap track:** six planned claims that require a separate reviewed
   authority/source decision before implementation.

The first track may proceed one check at a time after this definition is
accepted. The second track may not be implemented by analogy, broad wording,
or a convenient fixture value.

## Definition Probe

Before freezing the sequence, six temporary copies of the accepted development
package were created under ignored `scratch/` output. Each copy applied only
the isolated fault proposed for one new check:

1. wrong-but-valid item/equipment manifest target;
2. missing drawing representation for one BOM equipment tag;
3. missing authoritative datasheet record;
4. wrong-but-valid BOM datasheet association;
5. wrong-but-valid equipment/datasheet manifest target; and
6. valid-but-conflicting specification metadata revision.

For every probe, all eight P2.1 gates passed, all five accepted drawing checks
passed, and the current evaluator emitted zero findings. This confirms that
the proposed checks own real uncovered conditions and do not duplicate an
existing gate or relationship check. The probes changed temporary development
copies only; accepted fixtures, goldens, and held-out content were untouched.

## Existing Accepted Boundary

Every P2.3 check reuses the accepted pipeline:

`manifest -> adapters -> eight P2.1 gates -> ordered relationship checks -> canonical result -> reports -> audit-package publication`

P2.3 does not add another loader, result model, report model, CLI path, or
publication path. The package result remains the only source for report views.

P2.1 already owns:

- required source presence and structured parsing;
- required CSV/JSON field presence and type conversion;
- canonical identifier validity;
- source-local duplicate detection;
- revision-scheme evaluability;
- authority-map structural validity;
- controlled file boundary and existence checks; and
- complete evidence-locator construction.

For example, P2.1 already rejects a nonnumeric BOM quantity. P2.3 must not emit
a second relationship finding for the same parse failure.

## Exact Check Order

The five accepted drawing checks retain their identities, behavior, and order.
P2.3 appends these checks in order:

| Order | Check ID | Exact authority | Purpose |
|---:|---|---|---|
| 6 | `bom_item_equipment_manifest_reciprocity` | `AUTH-BOM-002` | Reconcile required BOM item-to-equipment mappings with manifest declarations. |
| 7 | `bom_equipment_drawing_presence` | `AUTH-BOM-002` | Require each release-required BOM equipment tag to appear in drawing metadata. |
| 8 | `equipment_datasheet_authority_presence` | `AUTH-SPEC-001` | Require one unambiguous authoritative datasheet record for each release-required BOM equipment tag. |
| 9 | `equipment_datasheet_association` | `AUTH-SPEC-001` | Compare the BOM datasheet ID with the authoritative metadata datasheet ID for the same equipment tag. |
| 10 | `equipment_datasheet_manifest_reciprocity` | `AUTH-SPEC-001` | Reconcile authoritative equipment-to-datasheet mappings with manifest declarations. |
| 11 | `specification_revision_history` | `AUTH-SPEC-003` | Compare specification metadata revision with the current revision-history record. |

Each check is a separate implementation and acceptance slice. A later slice
must not alter an earlier accepted check except for an explicitly demonstrated
interface conflict.

## Common Prerequisites

All six checks receive the completed `PackageGateEvaluation` and use only its
accepted in-memory manifest and structured-source records.

- If any P2.1 gate blocks dependent checks, every relationship check is
  `skipped` in the exact accepted order and names the blocking gate IDs.
- If an exact authority rule required by a check is unavailable or differs in
  a behavior-critical field, that check and only its dependent later checks
  are skipped against `authority_resolution`.
- A check does not reopen files, load expected assets, inspect held-out
  content, or infer authority from similar field names.
- Existing drawing findings are retained. New checks do not suppress,
  combine, or reclassify them.
- Source records and declarations are sorted by normalized semantic keys before
  comparison. Input order cannot change results or finding IDs.

## Check 6: BOM Item/Equipment Manifest Reciprocity

### Contract

| Item | Decision |
|---|---|
| Check ID | `bom_item_equipment_manifest_reciprocity` |
| Finding code | `BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED` |
| Authoritative source | `bom_or_equipment_list` |
| Contract declaration | Manifest `item_to_equipment` relationships |
| Join key | Exact normalized `item_id` |
| Expected target | BOM `equipment_tag` |
| Authority rule | Exact `AUTH-BOM-002` |
| Conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |

For every release-required BOM row, the manifest must contain exactly one
release-required `item_to_equipment` declaration with the same normalized
`item_id` and `equipment_tag`. A declaration for a nonexistent BOM item, a
missing declaration, or a wrong target produces one finding per affected item.

The finding contains the BOM `item_id` and `equipment_tag` field locators plus
the matching or collection-level manifest locator. Expected value is the
authoritative BOM mapping; actual value is the declared mapping or `missing`.

### Development Proof

- Clean package: two mappings pass in `item_id` order.
- Fault: change only `REL-ITEM-EQ-001` target from `P-101A` to the existing
  valid `M-101A` in a temporary copy.
- Expected: all P2.1 gates and the five accepted drawing checks pass; check 6
  emits exactly one finding for `ITEM-PUMP-001` with expected `P-101A` and
  actual `M-101A`; package state is `automatic_fail`, hold is true, CLI exit is
  1, and all four run outputs are preserved.

## Check 7: BOM Equipment Drawing Presence

### Contract

| Item | Decision |
|---|---|
| Check ID | `bom_equipment_drawing_presence` |
| Finding code | `BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING` |
| Authoritative source | `bom_or_equipment_list` |
| Compared source | `drawing_metadata` |
| Join key | Exact normalized `equipment_tag` |
| Authority rule | Exact `AUTH-BOM-002` |
| Missing state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |

Each release-required BOM equipment tag must occur in at least one drawing
metadata `equipment_tags` collection. This is a presence check, not proof that
the BOM row's `drawing_number` is authoritative.

The finding contains the authoritative BOM equipment-tag locator and a stable
collection-search locator for drawing metadata. It does not invent a specific
drawing when no accepted rule controls the BOM `drawing_number` field.

### Development Proof

- Clean package: `P-101A` and `M-101A` are both represented.
- Fault: remove only `M-101A` from `DWMETA-001.equipment_tags` in a temporary
  copy; all remaining identifiers stay valid.
- Expected: preceding checks pass; check 7 emits exactly one release-holding
  automatic-fail finding for `ITEM-MOTOR-001` / `M-101A`.

## Check 8: Equipment Datasheet Authority Presence

### Contract

| Item | Decision |
|---|---|
| Check ID | `equipment_datasheet_authority_presence` |
| Finding code | `EQUIPMENT_DATASHEET_AUTHORITY_MISSING` |
| Required object | Each release-required BOM `equipment_tag` |
| Authoritative source | `datasheet_spec_metadata.datasheets` |
| Join key | Exact normalized `equipment_tag` |
| Authority rule | Exact `AUTH-SPEC-001` |
| Missing/ambiguous state | `missing_authoritative_information` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |

Exactly one release-required datasheet record must identify each
release-required BOM equipment tag. Zero records or multiple competing records
means the evaluator has no single authoritative datasheet mapping.

The finding contains the BOM equipment-tag locator and a datasheet collection
search locator. It reports expected condition `one authoritative datasheet`
and actual count. It must not select a record by list order or title.

### Development Proof

- Clean package: one datasheet record for each of `P-101A` and `M-101A`.
- Fault: remove the `DSMETA-001` datasheet object in a temporary copy while the
  source remains valid JSON.
- Expected: preceding checks pass; check 8 emits exactly one
  `missing_authoritative_information` finding, hold true, package state 3, and
  CLI exit 3 for the isolated fault.

## Check 9: Equipment/Datasheet Association

### Contract

| Item | Decision |
|---|---|
| Check ID | `equipment_datasheet_association` |
| Finding code | `EQUIPMENT_DATASHEET_MISMATCH` |
| Join key | Exact normalized `equipment_tag` |
| Authoritative value | Datasheet metadata `datasheet_id` |
| Compared value | BOM `datasheet_id` |
| Authority rule | Exact `AUTH-SPEC-001` |
| Conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |

This check runs only for equipment tags that passed check 8 with one
authoritative datasheet record. It compares normalized IDs exactly and emits
one finding per mismatch with both field locators.

### Development Proof

- Clean package: `P-101A -> DS-P-101` and `M-101A -> DS-M-101` pass.
- Fault: change only the pump BOM row `datasheet_id` to existing valid
  `DS-M-101` in a temporary copy.
- Expected: P2.1 and checks 1-8 pass; check 9 emits exactly one finding with
  expected `DS-P-101`, actual `DS-M-101`, package state `automatic_fail`, hold
  true, and CLI exit 1.

## Check 10: Equipment/Datasheet Manifest Reciprocity

### Contract

| Item | Decision |
|---|---|
| Check ID | `equipment_datasheet_manifest_reciprocity` |
| Finding code | `EQUIPMENT_DATASHEET_RECIPROCITY_FAILED` |
| Authoritative source | Datasheet metadata |
| Contract declaration | Manifest `equipment_to_datasheet` relationships |
| Semantic key | Exact normalized `equipment_tag -> datasheet_id` |
| Authority rule | Exact `AUTH-SPEC-001` |
| Conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `mechanical_engineering` |

Every release-required authoritative equipment-to-datasheet mapping must have
one equal manifest declaration, and every release-required declaration must
resolve to that authoritative mapping. Check 9 retains ownership of BOM versus
metadata agreement; check 10 does not recompute it.

### Development Proof

- Clean package: two reciprocal declarations pass in equipment-tag order.
- Fault: change only `REL-EQ-DS-001` target to existing valid `DS-M-101` in a
  temporary copy.
- Expected: checks 1-9 pass; check 10 emits one exact reciprocity finding for
  `P-101A`, expected `DS-P-101`, actual `DS-M-101`, automatic fail, hold true,
  and CLI exit 1.

## Check 11: Specification Revision History

### Contract

| Item | Decision |
|---|---|
| Check ID | `specification_revision_history` |
| Finding code | `SPECIFICATION_REVISION_MISMATCH` |
| Join key | Exact normalized `specification_id` |
| Authoritative value | Specification metadata `revision_id` |
| Compared value | Current revision-history `revision_id` |
| Authority rule | Exact `AUTH-SPEC-003` |
| Missing secondary / conflict state | `automatic_fail` |
| Severity / hold | `high` / `true` |
| Review owner | `document_control` |

For every release-required specification record, revision history must contain
one current record with `owner_identifier_type = specification_id`, the same
normalized `specification_id`, and an equal revision under the declared
explicit sequence. A missing current record or mismatch is an automatic fail
under the accepted rule.

### Development Proof

- Clean package: both specification revision `A` relationships pass.
- Fault: change only `SPMETA-001.revision_id` from `A` to valid sequence value
  `B` in a temporary copy; revision history remains `A`.
- Expected: P2.1 and checks 1-10 pass; check 11 emits exactly one finding with
  specification metadata and revision-history locators, expected `B`, actual
  `A`, automatic fail, hold true, and CLI exit 1.

## Finding and Evidence Contract

Every non-pass P2.3 finding uses the accepted `RelationshipFinding` fields:

- stable finding ID;
- check ID and version `0.3.0`;
- package ID and code;
- result state, severity, and release hold;
- exact authority rule ID;
- stable affected identifiers;
- expected and actual values or conditions;
- accepted review owner; and
- ordered package-relative CSV/JSON/manifest evidence locators.

Finding identity excludes timestamps, run IDs, process IDs, absolute paths,
row positions, JSON list positions, and source iteration order. Physical row
or JSON pointer may appear as evidence but not as semantic identity.

Pass evidence is bounded and deterministic. It records the compared mapping or
pair once and does not duplicate the same source locator merely to increase
evidence volume.

## Result and Publication Handoff

Each implementation slice updates the shared `RELATIONSHIP_CHECK_ORDER`. The
accepted result completeness check must then require the new exact sequence.
No new package state, result schema variant, report path, or CLI command is
needed.

For an isolated fault:

- the canonical result retains the new finding and selects the accepted state
  by existing precedence;
- `issue_register.csv` and `issue_register.md` show the exact finding;
- `release_readiness.md` shows the state, hold, and updated check counts;
- `audit-package` publishes the same exact four-output set; and
- the process exits with the accepted state code.

Reports and CLI behavior must not reinterpret the new relationship.

## Authority-Gap Register

The following planned claims are not authorized for implementation by this
definition:

| Planned claim | Why it is not currently supportable | Required next decision |
|---|---|---|
| Cross-document quantity reconciliation | Quantity appears only in the BOM; `AUTH-BOM-001` requires presence and numeric parsing but names no comparison source. | Add a reviewed authoritative comparison source/rule, or narrow the release claim to BOM quantity field integrity already enforced by P2.1. |
| Part/material identifier reconciliation | `part_or_material_id` appears only in the BOM and has no exact authority rule. | Define the compared source, normalization, and conflict behavior. |
| BOM item-to-drawing agreement | The BOM has `drawing_number`, but no accepted rule controls that field. | Add an exact authority rule before using `item_to_drawing` declarations as assurance. |
| Equipment-to-specification association | `AUTH-SPEC-001` is explicitly keyed to `equipment.datasheet_id`; its prose mention of specification does not authorize `specification_id` by analogy. | Add a separate exact specification-association rule. |
| Datasheet revision-history agreement | `AUTH-SPEC-003` controls specification revision only. | Add a separate datasheet revision rule. |
| Pressure, material, power, voltage, frequency, or enclosure compliance | Current fields are example-specific nested values; units, tolerances, applicability, and exact authority behavior are not frozen. | Define a versioned controlled-value contract and deterministic unit/tolerance rules in a later gate. |

These are product gaps, not implementation defects. P2.3 cannot be declared
fully complete, and v0.3.0 cannot claim these reconciliations, until the gaps
are explicitly closed or the release claims are narrowed.

## Implementation Sequence

After definition acceptance:

1. implement check 6 on its own branch and obtain explicit acceptance;
2. append checks 7 through 11 one bounded branch at a time;
3. after each slice, run relationship-focused tests, result/report/CLI focused
   tests, the full frozen suite, repository validation, Ruff, and coverage;
4. inspect one clean and one isolated-fault four-output run;
5. preserve accepted development and held-out assets byte-for-byte; and
6. open the authority-gap decision before P2.3 completion or P4.

The first implementation branch should be
`codex/p2.3-bom-item-equipment-reciprocity`.

## Required Tests for Every Slice

Each implementation is complete only when:

1. the accepted clean development package passes the full ordered check set;
2. the exact temporary development fault produces only the defined new
   relationship finding;
3. all P2.1 gates and predecessor relationship checks have the expected status;
4. the exact authority rule and behavior-critical fields are required;
5. a blocked gate returns every check in stable skipped order;
6. repeated evaluation and source/declaration reordering preserve substantive
   output and finding IDs;
7. evidence contains no absolute machine or temporary path;
8. the canonical result, issue registers, readiness summary, terminal exit, and
   four published files agree;
9. focused tests, full regression, validation, Ruff, and the coverage floor
   pass; and
10. fixtures, goldens, held-out content, accepted schemas/authority maps, frozen
    v0.2 behavior, and historical evidence remain unchanged.

Temporary test copies are allowed. Versioned fault fixtures and semantic
held-out execution require later accepted gates.

## Explicit Exclusions

This definition does not authorize:

- any evaluator, schema, adapter, fixture, golden, or authority-map change;
- the six authority-gap claims above;
- semantic held-out execution, exposure, or tuning;
- generic rule-engine or agent orchestration work;
- PDF/CAD extraction or redlining;
- API, database, RAG, frontend, hosting, observability platform, reward model,
  or reinforcement-learning work; or
- engineering sign-off, release approval, or code-compliance conclusions.

## Ten Review Decisions

| Question | Resolution |
|---|---|
| 1. What is P2.3 trying to improve? | Extend the accepted runnable audit from drawing controls into evidence-backed BOM/equipment, datasheet, and specification relationships. |
| 2. How large is one implementation block? | One appended deterministic check, one isolated development fault, and its end-to-end result/report/CLI proof. |
| 3. Which checks are supportable now? | The six exact checks numbered 6 through 11 in this definition. |
| 4. Which check comes first? | `bom_item_equipment_manifest_reciprocity` under exact `AUTH-BOM-002`. |
| 5. How is authority enforced? | A check requires the exact accepted rule ID and every behavior-critical field; similar wording or a nearby field is not a substitute. |
| 6. How are missing authority and conflicts separated? | Directional presence and agreement are separate checks when their state or evidence differs; check 8 routes missing/ambiguous authority to state 3, while check 9 routes a value conflict to state 1. |
| 7. What evidence is mandatory? | Ordered field-level source locators plus a manifest or collection-search locator where absence or reciprocity is tested; all paths remain package-relative. |
| 8. What happens to quantity and other single-source fields? | They remain visible authority gaps; P2.1 may validate structure, but P2.3 does not call them reconciled. |
| 9. How is the accepted audit path affected? | Only the ordered relationship set and resulting counts/findings expand; the state router, result, reports, publication set, and exits retain accepted meaning. |
| 10. What remains blocked? | Checks 7-11 until their individual slices are authorized, all authority-gap claims until separate acceptance, semantic held-out execution until P4, and every deferred multimodal/platform capability. |

## Definition of Done

This definition block is complete when:

- this document is reviewed against the workflow contract, acceptance plan,
  accepted authority map, source layouts, manifest declarations, current gate
  and relationship implementations, and result/report/CLI contracts;
- the controlling workbook records D-085 and EV-082;
- project handoff documents identify the definition as ready for review;
- the final diff contains no executable behavior or protected-asset change;
- repository validation and document consistency checks pass;
- the six temporary definition probes confirm all existing eight gates and
  five drawing checks pass before the proposed owner check;
- the branch is committed, pushed, and opened for review; and
- the user accepts, revises, or rejects this definition before implementation.

## Acceptance Record

The user accepted the complete P2.3 definition on 2026-07-20. PR #41 merged
the exact reviewed definition at `main` commit `a855d99`. Decision D-086 and
evidence EV-083 authorize only check 6,
`bom_item_equipment_manifest_reciprocity`, on its dedicated branch. Checks
7-11, all six authority/source gaps, semantic held-out execution, protected
asset changes, and deferred capabilities remain blocked.

## Check 6 Implementation Review Record

Implementation `c1dcc4a` appends
`bom_item_equipment_manifest_reciprocity` after the five accepted drawing
checks. It requires every behavior-critical field of exact `AUTH-BOM-002`,
evaluates release-required BOM rows and required manifest declarations in
stable item order, and emits one high-severity automatic-fail release hold per
affected item. Missing, extra, wrong, and multiple declarations are covered;
an unrelated missing drawing-authority rule does not block this check.

Verification passes 31 relationship tests, 75 focused relationship/result/
report/CLI tests, 278 full-suite tests with one expected Windows symlink skip,
repository validation 5/5, Ruff, and 87.02% coverage. The inspected clean run
has 8/8 gates, 6/6 checks, no findings, `automatic_pass`, and exit 0. The
isolated `REL-ITEM-EQ-001` target fault has 8/8 gates, 5/6 checks, one exact
`BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED` finding under `AUTH-BOM-002`,
`automatic_fail`, release hold true, and exit 1. Both runs publish exactly four
outputs without absolute local paths.

The user accepted check 6 on 2026-07-20. PR #42 merged the exact reviewed branch
at `main` commit `559bb81`. Decision D-087 and evidence EV-085 close the check.
The approved next action is a bounded behavior-preserving relationship
maintainability stabilization before check 7. Checks 7-11 remain unimplemented;
six authority/source gaps, held-out semantics, protected-asset changes, and
deferred capabilities remain blocked.

## Check 7 Implementation Review Record

The behavior-preserving relationship split is integrated through PR #44 at
exact `main` `56ac9d1`. Check 7 implements only
`bom_equipment_drawing_presence` under exact `AUTH-BOM-002`. Each
release-required BOM equipment tag must appear in at least one drawing metadata
`equipment_tags` collection. The check does not treat the BOM `drawing_number`
as authoritative and does not close the separate item-to-drawing authority gap.

Verification passes 35 relationship tests, 80 focused relationship/result/
report/CLI tests, 283 full-suite tests with one expected Windows symlink skip,
repository validation 5/5, Ruff, and 87.25% coverage. The inspected clean run
has 8/8 gates, 7/7 checks, no findings, `automatic_pass`, and exit 0. Removing
only `M-101A` from `DWMETA-001.equipment_tags` produces 8/8 passed gates, six
passed checks, one failed check, one exact
`BOM_EQUIPMENT_DRAWING_REFERENCE_MISSING` finding under `AUTH-BOM-002`,
`automatic_fail`, release hold true, and exit 1. Both runs publish exactly four
outputs without absolute local paths.

Decision D-090 is accepted. Evidence EV-087 and EV-088 record check 7 review
and integration through PR #45 at exact `main` `273c36a`. The next gate is
selection of one authorized sanitized structured package under
`authorized_structured_package_trial_v0.3.0.md`. Checks 8-11, six authority/
source gaps, semantic held-out execution, protected-asset changes, and deferred
capabilities remain blocked.
