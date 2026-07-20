# First Usable Package Audit Vertical Slice Definition v0.3.0

## Control Status

- **WBS:** Cross-WBS definition for the remaining P2.2, P2.4, and P3 pilot work
- **Status:** Accepted 2026-07-19; P2.2, P2.4, P3.1, and P3.2 are integrated;
  P3.3 audit-package CLI is the next authorized block
- **Baseline:** `main` at `a18fc5f`
- **Branch:** `codex/first-usable-audit-definition`
- **P2.2 implementation:** accepted commit `4f06352`; integrated through PR
  #37 at exact `main` commit `5571d2a`
- **P2.4 implementation:** accepted commit `cbcfc2b`; integrated through PR
  #39 at exact `main` commit `cd9b52e`
- **P3.1 implementation:** accepted commit `2f93335`; integrated with review
  evidence at exact `main` commit `8f66b12`
- **P3.2 implementation:** accepted commit `7536bea`; integrated with review
  evidence at exact `main` commit `4b848b9`
- **Time tracking:** Waived; progress is controlled by acceptance evidence
- **Protected assets changed:** None

The user accepted all ten review decisions and instructed the project to begin
the next step on 2026-07-19. Acceptance authorizes only the bounded sequence in
this document. It does not collapse the separate implementation, review, and
integration gates for P2.2, P2.4, P3, or P2.3.

This definition converts the next several horizontal work items into one thin,
usable path through the existing platform. It does not reduce the accepted
v0.3.0 release scope. It changes the order in which that scope is delivered so
a complete package audit can be exercised before more rule families are added.

## Plain-Language Goal

Produce the first command a reviewer can actually run against a structured
package and receive:

1. an explicit package state;
2. an immutable machine-readable result;
3. an evidence-linked issue register;
4. a short release-readiness summary; and
5. a stable command-line exit code.

The slice uses the eight accepted P2.1 gates, the four accepted drawing checks,
and one final drawing-to-manifest reciprocity check. It does not inspect PDF or
CAD content and it does not make an engineering release decision.

## Management Decision

The current schedule makes P2.4 state routing wait for all of P2.3, then makes
the issue register, release summary, and CLI wait for routing. That sequence
creates a long period in which individual checks work but a user cannot run a
complete audit.

The recommended order is:

1. close the bounded drawing declaration/manifest reciprocity gap in P2.2;
2. implement the minimum P2.4 state router and canonical package result;
3. persist the result and render the P3.1 issue register and P3.2 summary;
4. expose that path through the P3.3 `audit-package` command;
5. prove the complete slice on clean and temporary development faults; and
6. resume broad P2.3 BOM, equipment, datasheet, specification, and revision
   relationship expansion through the proven result pipeline.

P2.3 remains required for v0.3.0 release. It is moved behind the first usable
audit, not removed. Semantic held-out execution remains blocked until the
development slice and evaluator commit are accepted and frozen.

## Frozen Slice Boundary

### Inputs

The command accepts one package directory that follows the accepted structured
v0.3.0 package contract. The package contains the seven mandatory JSON/CSV
sources and controlled file references already defined by P0.1 and P1.

The slice reads controlled-file paths and existence only. It does not extract
or interpret file contents.

### Evaluation Stages

The required stage order is:

```text
package directory
  -> eight ordered P2.1 gates
  -> five ordered P2.2 relationship checks
  -> required-result completeness check
  -> P2.4 package-state router
  -> canonical package_result.json
  -> issue_register.csv and issue_register.md
  -> release_readiness.md
  -> audit-package exit code
```

The four implemented drawing checks retain their accepted identities, order,
findings, and evidence. The fifth check is appended and does not reinterpret
the earlier checks.

### Outputs

One controlled audit attempt writes a new run directory outside the package:

```text
runs/<run_id>/
  package_result.json
  issue_register.csv
  issue_register.md
  release_readiness.md
  logs/
```

No run directory is overwritten. Generated output is never written into a
package, expected-results directory, golden asset, or held-out asset.

## Fifth Check: Drawing Manifest Reciprocity

### User Question

> Does every authoritative drawing-register document and file reference have
> one matching, declared, resolvable, required document-to-file mapping in the
> package manifest?

The accepted fourth check proves that drawing register and drawing metadata
agree with each other. It does not catch both sources repeating the same bad
reference, or a manifest that omits or contradicts the required
`document_to_file` declaration.

### Frozen Identity

| Item | Decision |
|---|---|
| Check ID | `drawing_register_manifest_file_reciprocity` |
| Check version | `0.3.0` |
| Finding code | `DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED` |
| Authority rule | Existing `AUTH-DWG-002` |
| Authoritative source | `drawing_register` |
| Package declaration source | `package_manifest` |
| Result state | `automatic_fail` |
| Severity | `high` |
| Release hold | `true` |
| Review owner | `document_control` |

No new authority rule is required. `AUTH-DWG-002` already controls
`drawing.file_ref_id`, makes the drawing register authoritative, requires a
declared reference to resolve to the same canonical drawing, and routes a
conflict to an automatic release hold. The manifest is the controlled package
declaration being tested; it does not replace drawing-register authority.

### Exact Reciprocity Test

For each authoritative drawing-register record, sorted by normalized
`drawing_number`, the following must all be true:

1. exactly one manifest `document_inventory` item matches its `document_id` and
   `drawing_number`;
2. that inventory item declares the same normalized `file_ref_id`;
3. that `file_ref_id` exists in manifest `file_references` and passed the P2.1
   boundary/resolution gate;
4. exactly one required `document_to_file` relationship maps the same
   `document_id` to that same `file_ref_id`; and
5. no additional required `document_to_file` relationship maps that drawing
   document to another file reference.

The check passes only when all five clauses pass for every authoritative
drawing. One failed drawing produces one finding that reports every failed
clause in a structured actual-value object. This avoids turning one mapping
problem into several repetitive issue-register rows.

### Required Evidence

A pass preserves deterministic evidence for each drawing. A failure includes:

- the drawing-register `document_id`, `drawing_number`, and `file_ref_id` field
  locators;
- the matching manifest inventory item, or the searched
  `/document_inventory` collection when absent;
- the file-reference resolution locator, or the searched `/file_references`
  collection when absent; and
- the exact relationship declaration, or the searched
  `/relationship_declarations` collection when missing or conflicting.

Negative evidence identifies the complete collection searched and the exact
tuple expected. It must not rely only on a free-text statement. Absolute local
paths are prohibited.

### Primary Development Fault

The first end-to-end failing demonstration removes only the required
`REL-DOC-FILE-001` declaration from a temporary copy of the clean development
package. The manifest remains schema-valid, all P2.1 gates pass, and the first
four P2.2 checks pass. The fifth check emits exactly one stable finding for
`DOC-DWG-001` / `DWG-PSK-1001` / `FILE-DWG-001`.

Additional focused tests must cover a wrong-but-valid manifest target, two
conflicting required mappings, and both drawing sources repeating the same
undeclared file-reference ID. These cases use temporary development copies
only; no accepted or held-out fixture is edited.

## Package Result and Router Contract

### Required Completeness

An `automatic_pass` is allowed only when all eight accepted gate IDs and all
five accepted relationship-check IDs are present exactly once, in the accepted
order, and have `passed` status.

A prerequisite skip caused by an actually failed gate is retained and the
gate finding controls package state. A missing, duplicate, out-of-order, or
unexpectedly skipped required result is a release-holding
`evaluator_uncertainty` finding named `REQUIRED_EVALUATION_INCOMPLETE`.
Silently dropping a check can therefore never produce a pass.

### State Selection

The router collects every non-pass finding state and applies the accepted
precedence exactly:

1. `automatic_fail`
2. `extraction_or_tool_failure`
3. `missing_authoritative_information`
4. `evaluator_uncertainty`
5. `engineering_review_required`
6. `automatic_pass`

The selected package state is the highest-precedence observed state. The
result also retains all observed non-pass states in precedence order. A
release hold is true when any retained finding requires one. No numeric score
is used in this slice, and a score can never override a hold.

### Canonical Result Contents

`package_result.json` is the sole source for reports and CLI rendering. It
contains at minimum:

- schema, evaluator, router, workflow-contract, and authority-map versions;
- run ID and declared volatile run metadata;
- package ID, nullable only when a readable package directory exists but the
  manifest cannot establish identity;
- a deterministic input fingerprint and package-relative input inventory;
- selected package state, release hold, and every observed blocking state;
- all ordered gate and relationship results, including skips and references to
  their canonical finding IDs;
- one canonical list that stores each non-pass finding body, stable ID, and
  evidence exactly once;
- required-result completeness evidence;
- output-generation status and package-relative output names; and
- the explicit engineering and human-review limitation.

Only run ID, timestamps, duration, host metadata, and output location may vary
between unchanged runs. Package state, hold, finding identity and order,
evidence, and report meaning must remain stable.

The input fingerprint is SHA-256 over the sorted package-relative paths and raw
bytes of the declared seven sources and controlled file references. It excludes
`expected/`, generated outputs, and undeclared files. The result records every
included path and file digest so the audited input can be reproduced without
storing an absolute machine path.

### Final-Finding Interface Clarification

The accepted relationship findings already carry the fields needed by the
final issue register. Current P2.1 gate findings are intentionally smaller
intermediate records and do not carry every final-report field, such as package
ID, severity, review owner, and an authority reference.

Implementation must add one canonical final-finding boundary rather than make
reports infer missing fields from messages. It may extend the package-assurance
intermediate model where necessary, but it must not change frozen v0.2 result
records or their schema.

For authority-based findings, `authority_rule_id` is mandatory. For parser,
schema, path-boundary, evidence-completeness, and evaluator-integrity findings
that logically precede field authority, a `governing_control_id` is mandatory
and `authority_rule_id` is not fabricated. This is a clarification of the P0.1
finding contract and requires acceptance with this definition before code is
written.

## Context and Failure Boundary

### Pre-Package Errors

The following do not establish an audit result and return CLI exit `64`:

- invalid `audit-package` arguments;
- missing repository root;
- missing package path; or
- package path that is not a directory.

An unexpected unhandled failure before a controlled package result can be
constructed or safely persisted returns `70`.

### Controlled Package Failures

Once a real package directory and run context exist:

- unreadable or malformed manifest/source data is retained as the accepted
  gate finding state;
- `package_id` remains `null` when identity cannot be established rather than
  being invented;
- controlled parse, tool, or environment failure affecting required evidence
  routes to `extraction_or_tool_failure` and exit `4`; and
- the failed result is preserved whenever the output location remains usable.

Report rendering is a pure transformation of the already constructed result.
Output bytes are prepared and validated before final names are published. A
partial output directory is never reported as a complete audit and is
preserved with failure evidence when possible.

## Report Views

### Issue Register

The CSV and Markdown issue registers flatten only non-pass findings from
`package_result.json`. They do not rerun gates, checks, authority selection, or
state routing.

The CSV includes stable fields for finding ID, state, hold, severity, review
owner, governing check/gate, finding code, authority or governing control,
affected identifiers, expected/actual condition, and evidence. Evidence is
machine-readable JSON inside the CSV field rather than an ambiguous prose-only
summary.

Ordering is package-state precedence, then accepted gate/check order, then
stable finding ID. A clean result writes the header and zero issue rows.

### Release Readiness

The Markdown summary shows package and run identity, package state, release
hold, observed blocking states, passed/failed/skipped counts, issue counts by
state, output links, limitations, and the required qualified-human decision.

It may state whether the package is ready to proceed to qualified human review.
It may not approve release, certify compliance, or state that engineering work
is correct.

## CLI Contract

The first pilot command is:

```powershell
mech-eval audit-package <repository-root> <package-directory> `
  [--runs-dir <directory>]
```

The repository-root argument preserves the current pilot's schema and contract
lookup boundary. Product packaging can simplify that later without changing
audit semantics.

Package-state exits remain exactly `0` through `5`. Pre-package usage errors
use `64`; unexpected pre-result internal failures use `70`. Existing v0.2
commands and their exit behavior remain unchanged.

Terminal output is a compact view of the immutable result: run ID, package ID
when known, state, hold, issue count, and result path. It does not recompute or
silently downgrade the result.

## Reuse and Module Boundaries

Implementation should reuse proven patterns without coupling the two releases:

- keep P2.1 gates and P2.2 relationships independently executable;
- add package-assurance-specific routing, final-result, persistence, and report
  modules under `src/mech_eval_harness/package_assurance/`;
- reuse the v0.2 run-ID and immutable-write concepts where appropriate, but do
  not coerce package results into the v0.2 score/case result schema;
- extend the existing CLI only at command registration and dispatch boundaries;
  and
- keep report code as pure result-to-text/CSV transformations.

No generic rule engine, agent abstraction, provider integration, API, database,
or frontend is justified by this slice.

## Acceptance Matrix

The implementation chain is complete only when it proves:

1. the clean development package produces `automatic_pass`, exit `0`, an
   immutable result, empty issue register, and non-approving readiness summary;
2. the removed declaration fault produces exactly the fifth-check finding,
   package `automatic_fail`, release hold true, one issue row, and exit `1`;
3. a wrong-but-valid target, duplicate/conflicting mappings, and a shared
   undeclared source reference produce their frozen reciprocity evidence;
4. one development scenario for every package state routes to exits `0`-`5`;
5. every ordered state pair and order permutation selects the same accepted
   precedence while retaining all observed states;
6. actual prerequisite skips preserve their blocker and state, while an
   unexpected missing/skipped required result routes to evaluator uncertainty;
7. an unreadable manifest in an existing package directory persists a result
   with nullable package ID, extraction/tool state, and exit `4`;
8. usage errors return `64` without a package result and pre-result internal
   failure returns `70`;
9. repeated unchanged runs differ only in declared volatile metadata and
   preserve stable findings, ordering, evidence, and report semantics;
10. output is outside the package, existing runs are never overwritten, and a
    failed run is not rewritten as a pass;
11. reports exactly reflect the immutable result and contain no absolute local
    evidence paths;
12. focused tests, the full frozen regression suite, repository validation,
    Ruff, and the coverage floor pass; and
13. protected fixtures, goldens, held-out content, historical results, the
    v0.2.0 tag, and accepted v0.2 behavior remain unchanged.

The first semantic held-out run is a later P4 gate. It is not part of this
implementation acceptance matrix.

## Implementation Blocks After Acceptance

Each block receives its own branch, focused review, full regression, and
integration evidence:

1. **P2.2 reciprocity:** fifth check and temporary-development tests only.
2. **P2.4 result core:** completeness control, canonical findings, state router,
   package result, schema, and immutable persistence.
3. **P3.1/P3.2 views:** CSV/Markdown issue register and release summary as pure
   result views.
4. **P3.3 integration:** `audit-package`, exact exits, end-to-end tests, and
   development demonstration.
5. **P2.3 expansion:** add the remaining relationship families through the
   accepted result path before the P4 benchmark gate.

No implementation block begins until this definition and its sequencing and
contract clarifications are accepted.

## Explicit Exclusions

This vertical slice does not add:

- PDF text/table extraction or drawing-image interpretation;
- native CAD/model metadata extraction;
- engineering calculations, code/standards compliance, or design review;
- redline editing, engineering sign-off, or autonomous release;
- generic agent orchestration or model-provider assumptions;
- semantic held-out execution or tuning;
- APIs, databases, dashboards, frontends, hosting, observability platforms,
  RAG, reward models, or RL; or
- broad P2.3 BOM/equipment/datasheet/specification/revision checks before the
  first usable audit is accepted.

## Accepted Review Decisions

| Question | Accepted resolution |
|---|---|
| 1. What is the next user-visible milestone? | One structured package directory produces an immutable result, issue register, release summary, and exact CLI exit. |
| 2. Why change the sequence? | The current horizontal sequence delays user testing until many rules are built; a thin vertical slice proves the product boundary earlier. |
| 3. What relationship gap must close first? | Drawing-register `document_id` and `file_ref_id` must be reciprocal with manifest inventory, declared files, and one required `document_to_file` mapping. |
| 4. Does the fifth check need a new authority rule? | No. Existing `AUTH-DWG-002` controls drawing file-reference authority and declared canonical resolution. |
| 5. When may the package pass? | Only when all eight required gates and all five required checks are present exactly once and pass. |
| 6. How is package state chosen? | Retain all non-pass states and select the highest accepted precedence; any hold remains a hold and no score overrides it. |
| 7. How are current gate findings made report-ready? | Add one canonical final-finding boundary; authority findings require an authority rule, while pre-authority structural/tool findings use an honest governing control ID. |
| 8. What establishes a package context? | A valid command naming an existing repository root and package directory; manifest identity may remain null on controlled manifest failure. |
| 9. What are the reports and CLI allowed to do? | Render only the immutable result, return exact exits, preserve failures, and avoid engineering approval claims. |
| 10. What remains blocked? | All implementation until definition acceptance; semantic held-out execution until its later gate; broad P2.3 expansion until this vertical slice is accepted; and every deferred multimodal/platform capability. |

## P2.2 Reciprocity Implementation Review

Commit `4f06352` implements only the fifth ordered relationship check defined
above. It leaves the eight P2.1 gates and first four P2.2 checks unchanged. The
check fails closed when exact `AUTH-DWG-002` semantics are unavailable and
emits one deterministic `DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED` automatic
failure and release hold for each affected authoritative drawing.

Temporary development-package copies prove clean behavior, a missing required
mapping, a wrong-but-valid target, an additional conflicting required mapping,
a shared undeclared register/metadata reference, two sorted findings,
repeatability, exact evidence, and prerequisite skips. Verification passes 25
relationship tests, 51 focused package tests, 222 full-suite tests with one
expected Windows symlink skip, repository validation 5/5, Ruff, and 85.64%
coverage.

No accepted fixture, schema, authority map, expected result, golden, held-out
asset, historical evidence, or v0.2 behavior changed. The implementation is
accepted by the user and integrated through PR #37 at exact `main` commit
`5571d2a`. P2.4 subsequently completed and is integrated as recorded below.

## P2.4 Result-Core Implementation Review

Commit `cbcfc2b` implements only the accepted minimum result core. It checks
that all eight gate and five relationship results are present once in the
accepted order, permits only skips caused by an actually failed prerequisite
gate, and emits release-holding `REQUIRED_EVALUATION_INCOMPLETE` uncertainty
when evaluator output is missing, duplicated, reordered, or unexpectedly
skipped.

The result boundary converts intermediate gate and relationship findings into
one canonical finding list, applies the accepted six-state precedence, retains
all blocking states, fingerprints only declared package inputs, validates the
separate `package_result.schema.json`, and writes `package_result.json` to a
new run directory without overwrite. It does not change the frozen v0.2 result
model, schema, or persistence path.

Verification passes 15 focused result tests, 237 full-suite tests with one
expected Windows symlink skip, repository validation 5/5, Ruff, and 86.10%
coverage. A clean result artifact and controlled incomplete result were
inspected from the ignored test output. Reports, CLI, broad P2.3 relationships,
semantic held-out execution, and deferred capabilities remain blocked pending
separate gates.

The user accepted P2.4 on 2026-07-19. PR #39 integrated implementation
`cbcfc2b` and its review evidence at exact `main` commit `cd9b52e`. Exact-main
verification preserves the same 15 focused result passes, 237 full-suite
passes with one expected Windows symlink skip, repository validation 5/5,
Ruff, and 86.10% coverage. P3.1 issue-register views are authorized next;
P3.2, P3.3, broad P2.3, semantic held-out execution, and deferred capabilities
retain separate gates.

## P3.1 Issue-Register Implementation Review

Implementation commit `2f93335` adds only the bounded issue-register view on
`codex/p3.1-issue-register` from accepted predecessor `main` commit `b9de4e6`.
The renderer loads strict JSON, rejects duplicate object keys and non-JSON
numeric constants, validates the document against the accepted package-result
schema, and then renders CSV and Markdown from the stored canonical findings.
It preserves finding order and does not import or call the gate, relationship,
authority, state-routing, or hold logic.

The CSV has one stable header and stores affected identifiers,
expected/actual values, and evidence as deterministic JSON fields. A clean
result has zero data rows. The Markdown carries package/run identity, the exact
engineering-review limitation, and the same finding facts without release,
compliance, or correctness approval. Report publishing, release readiness,
CLI integration, P2.3 expansion, held-out semantics, and deferred capabilities
are not included.

Verification passes 11 focused renderer tests, 26 focused package-result and
report tests, 248 full-suite tests with one expected Windows symlink skip,
repository validation 5/5, Ruff, and 86.49% coverage. A generated
drawing-revision conflict was inspected: its CSV evidence parses back to the
accepted package-relative locators, its Markdown shows the same authority and
values, and neither view contains an absolute machine path. P3.1 acceptance
and integration were required before P3.2 could begin and are recorded below.

The user accepted P3.1 and authorized merge on 2026-07-19. The reviewed branch
was fast-forwarded to exact `main` commit `8f66b12`. Exact-main verification
preserves the same 26 focused package-result/report passes, 248 full-suite
passes with one expected Windows symlink skip, repository validation 5/5,
Ruff, and 86.49% coverage. P3.2 is authorized next only for the non-approving
Markdown release-readiness view defined above. Report publishing, P3.3 CLI,
broad P2.3, semantic held-out execution, and deferred capabilities remain
separately gated.

P3.2 implementation commit `7536bea` adds a pure in-memory Markdown view of a
strict, schema-valid `package_result.json`. A shared report-input loader retains
P3.1 duplicate-key, non-JSON-constant, root-object, and schema validation while
preserving each view's explicit render error. The summary displays stored
package/run identity, package state, release hold, observed blocking states,
gate and relationship passed/failed/skipped counts, finding counts by state,
known output names, the exact engineering-review limitation, and the required
qualified-human decision. It does not derive a new readiness state, rerun
gates, checks, authority, state routing, or holds, publish files, or add CLI
behavior.

Verification passes 10 focused readiness tests, 36 focused package-result and
report tests, 258 full-suite tests with one expected Windows symlink skip,
repository validation 5/5, Ruff, and 86.75% coverage. An inspected seeded
drawing-revision conflict preserves the immutable result's 8 passed gates,
4 passed and 1 failed relationship checks, `automatic_fail` state, release
hold, one `automatic_fail` finding, and package-result link. The Markdown has
no absolute machine path or release, compliance, or engineering-correctness
approval. P3.2 acceptance and integration were required before P3.3 could
begin and are recorded below.

The user accepted P3.2 and authorized continuation on 2026-07-19. The reviewed
branch was fast-forwarded to exact `main` commit `4b848b9`. Exact-main
verification preserves 36 focused package-result/report passes, 258 full-suite
passes with one expected Windows symlink skip, repository validation 5/5,
Ruff, and 86.75% coverage. P3.3 is authorized next only for atomic publication
of the already accepted result and report views plus the bounded
`audit-package` CLI and accepted exit behavior. Broad P2.3, semantic held-out
execution, protected changes, and deferred capabilities remain separately
gated.

## Definition of Done

This definition block is done when:

- the ten decisions are reviewed against P0.1, P0.2, current code, and the clean
  development package;
- the sequencing change and final-finding clarification are accepted, revised,
  or rejected explicitly;
- the controlling workbook records the decision, evidence, active gate, and
  next authorized block;
- short project handoffs point to this definition rather than the closed PR #35
  gate;
- the final diff contains no executable behavior, schema, fixture, authority
  map, expected result, or held-out change; and
- documentation checks and workbook inspection pass before publication.

All definition criteria were satisfied on 2026-07-19. Decision `D-073` and
evidence `EV-070` record acceptance; the first authorized implementation block
is the fifth P2.2 reciprocity check only.
