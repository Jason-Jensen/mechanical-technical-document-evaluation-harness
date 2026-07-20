# Project Context

**Updated:** 2026-07-20
**Repository:** `C:\Projects\mechanical-technical-document-evaluation-harness`
**Current branch:** `codex/p2.3-bom-item-equipment-reciprocity`

## Executive Summary

The repository contains two deliberately different assets:

- **v0.2.0 Mechanical Technical Document Evaluation Harness:** a frozen, verified evaluation kernel;
- **v0.3.0 Package Assurance Pilot:** the active effort to prove one complete structured Mechanical Package Consistency Audit.

The project is not building a generic AI platform or SaaS product. Its near-term goal is to prove that a bounded, deterministic-first workflow can identify package inconsistencies, preserve evidence, route uncertainty correctly, and support qualified human release review.

## Frozen Baseline

v0.2.0 is frozen at accepted commit `45336a2` and the annotated `v0.2.0` tag.

Accepted evidence:

- five reviewed mechanical cases;
- 121 passing tests;
- 9/9 harness-verification baseline;
- 2/2 deterministic portfolio demo;
- immutable result records, CI, release documentation, and clean-clone acceptance.

Do not rewrite this kernel or alter its protected evidence without an approved interface-conflict decision.

## Active Work

- **Release:** v0.3.0 Package Assurance Pilot
- **Active WBS:** P2.3 relationship maintainability stabilization
- **Status:** Check 6 is accepted and integrated through PR #42 at exact `main` `559bb81`; a bounded behavior-preserving cleanup is authorized before check 7
- **Implementation state:** Eight ordered gates and six ordered relationship checks feed the canonical result and report views through one bounded `audit-package` command. Four outputs are staged outside the package and published together by one final directory rename; existing runs are not overwritten, controlled package failures are retained, and package-state exits remain `0`-`5`. Check 6 reconciles release-required BOM item/equipment mappings with manifest declarations under exact `AUTH-BOM-002`; checks 7-11 and all six authority-gap claims remain unimplemented

P0.1 is accepted. Its reviewed workflow contract and authority-map example freeze the package boundary, identifiers, authority rules, result states, evidence contract, human-review boundary, and exclusions.

P0.2 is accepted. It freezes the development/held-out split, minimum scenario matrix, exact oracle matching, state and CLI routing, reproducibility, contamination handling, false-positive/false-negative review, bounded claims, and release stop conditions.

P1.1 is accepted and locally integrated at commit `42ad037`. It validates package metadata, mandatory source declarations, canonical manifest identifiers, document revisions, relationship declarations, authority-map references, and controlled paths. It resolves source and file declarations without parsing source records or assigning package result states; those behaviors remain in later gated work.

P1.2 is accepted at commit `f26ed27`. It provides `SCN-DEV-PUMP-SKID-CLEAN-001`, a clean, fully synthetic pump-skid package with all seven mandatory sources, nine controlled file references, 20 reviewed semantic relationships, exact hidden evidence locators, expected clean results, and a package-tree content hash. Its source layouts are fixture examples rather than accepted general schemas.

P1.3 is accepted at commit `4b7516e`. It provides a materially distinct synthetic held-out family with exact protected findings, evidence locators, check IDs, package states, per-scenario hashes, material-distinction evidence, contamination controls, and freeze-set hash `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884`. Its recorded `frozen_pre_tuning` status is active. It is self-authored pre-tuning, not independently blind. During P2.1, tracked held-out path names were inadvertently enumerated and the full suite exercised opaque integrity checks; protected source and oracle content was not opened or used to tune evaluator behavior. The first semantic held-out evaluation remains gated.

P2.1 implementation is committed at `e1ada72`. It adds fail-closed structured-source adapters, deterministic evidence models, eight ordered package gates, stable findings, and explicit prerequisite skips without selecting a package-level result state. Focused verification passed 60 tests with one expected Windows symlink skip; the full suite passed 187 tests with the same skip. An approved EOL-only repair adds byte-preserving Git attributes so raw benchmark inventories remain reproducible on Windows; no fixture JSON value, oracle, expected state, or accepted hash changed.

The accepted stabilization block closes cross-platform evidence-path and JSON fixture-profile version gaps, adds ten regression cases, installs Ruff and an 80% coverage floor in CI, ignores temporary Excel lock files, and records reusable lessons in `docs/quality/improvement_register.md`. Verification passes 26 focused tests, 197 full-suite tests with one expected Windows symlink skip, five-case repository validation, Ruff, and 84.33% coverage. No P2.2 relationship, package-state routing, report, CLI, semantic held-out execution, or deferred capability was added.

The accepted P2.2 definition freezes one drawing-register-to-metadata revision comparison under `AUTH-DWG-001`. It defines exact joining, pass/fail behavior, a high-severity release-hold finding, both field-level evidence locators, deterministic identity, a separate `relationships.py` boundary, downstream P2.4/P3 handoff, acceptance tests, and explicit exclusions. It does not authorize any other relationship rule, package-state routing, report, CLI, or protected-asset change.

The implemented slice keeps P2.1 gates unchanged, consumes their completed evaluation, and emits no package-level state. The clean development package passes; a temporary metadata mutation from revision `C` to `A` produces exactly one stable `DRAWING_REVISION_MISMATCH` finding with both frozen locators. Repeated runs and reordered records preserve semantic finding identity and order. Verification passes 30 focused tests, 201 full-suite tests with one expected skip, repository validation 5/5, Ruff, and 84.64% coverage.

The user accepted the implementation by merging PR #29 into the accepted definition branch on 2026-07-17. PR #28 then integrated the complete definition-and-implementation chain to `main` at `5866212`. Verification on that exact merged tree passes 30 focused tests, 201 full-suite tests with one expected skip, repository validation 5/5, Ruff, and 84.64% coverage.

The accepted second slice checks only whether every authoritative drawing-register entry has a drawing-metadata counterpart. It deliberately excludes the reverse orphan-record direction because a metadata record with no register authority routes to `missing_authoritative_information`, not the same `automatic_fail`, and needs separate absence evidence. The user accepted the definition and implementation on 2026-07-17. PR #31 integrated the complete slice to `main` at `36338c0`. Verification on that exact merged tree passes 35 focused tests, 206 full-suite tests with one expected skip, repository validation 5/5, Ruff, and 84.93% coverage.

The accepted third direction is `drawing_metadata_register_authority` v0.3.0. PR #32 integrated its definition to `main` at `6d1f2f2`; implementation commit `8eb431d` appends the third check without changing the first two. PR #33 integrated the accepted implementation and acceptance evidence to `main` at `8d7f314`. Exact merged-tree verification passes 40 focused tests, 211 full-suite tests with one expected skip, repository validation 5/5, Ruff, and 85.37% coverage. No accepted fixture, golden, held-out asset, schema, authority map, or historical evidence changed.

The accepted fourth slice is `drawing_register_metadata_file_reference` v0.3.0 under `AUTH-DWG-002`. A temporary development-package copy proves the gap: metadata drawing `DWG-PSK-1001` can point to the valid `FILE-DWG-002` reference while all eight P2.1 gates and the first three P2.2 checks pass. PR #34 integrated the definition and acceptance record at exact `main` commit `12c45dd`. Implementation commit `74970c3` appends the fourth check, requires the exact accepted authority rule, and produces the frozen high-severity `automatic_fail` release hold with both compared field locators and both resolved manifest file-reference locators. PR #35 integrated the accepted implementation and evidence at exact `main` commit `e5db29e`. Exact merged-tree verification passes 19 relationship tests, 45 focused tests, 216 full-suite tests with one expected skip, repository validation 5/5, Ruff, and 85.47% coverage. Accepted fixtures, schemas, authority maps, goldens, held-out assets, and historical evidence remain unchanged. Full document-to-file reciprocity and shared undeclared source references remain explicit gaps.

The accepted first-usable-audit definition closes the planning gap identified
by `IMP-012`. It freezes five implementation blocks: P2.2 manifest reciprocity,
P2.4 result core, P3.1/P3.2 report views, P3.3 CLI integration, then broad P2.3
expansion before P4. The current authorization is limited to the first block.
The fifth check reuses `AUTH-DWG-002`, evaluates one authoritative drawing at a
time, and produces one evidence-rich automatic-fail release hold per drawing
whose manifest inventory, controlled file, or required document-to-file mapping
is not reciprocal.

Implementation commit `4f06352` appends that fifth check without changing the
eight P2.1 gates or the first four relationship checks. Temporary development
copies prove the clean case, missing required mapping, wrong-but-valid target,
conflicting required mapping, shared undeclared reference, two-finding order,
repeatability, exact authority prerequisite, and portable evidence. Verification
passes 25 relationship tests, 51 focused package tests, 222 full-suite tests
with one expected Windows symlink skip, repository validation 5/5, Ruff, and
85.64% coverage. No accepted fixture, schema, authority map, golden, held-out
asset, historical evidence, or v0.2 behavior changed. The user accepted and
authorized integration on 2026-07-19. PR #36 merged the definition at
`5b32b6d`; PR #37 merged the implementation at exact `main` `5571d2a`.
Verification on that merged tree passes 25 relationship tests, 51 focused
package tests, 222 full-suite tests with one expected Windows symlink skip,
repository validation 5/5, Ruff, and 85.64% coverage. P2.2 is closed for the
accepted vertical slice.

P2.4 implementation commit `cbcfc2b` adds the bounded package-result core on
`codex/p2.4-result-core` from accepted predecessor `1e7da37`. It requires the
exact ordered eight-gate/five-check result set and fails closed on missing,
duplicate, out-of-order, or unexplained skipped results. It converts gate and
relationship findings into one canonical report-ready finding set, applies the
accepted six-state precedence without scoring, fingerprints only declared
package inputs, validates `package_result.json` against a separate v0.3.0
schema, and writes new run directories without overwrite. The frozen v0.2
result schema and persistence path are unchanged. Verification passes 15
focused result tests, 237 full-suite tests with one expected Windows symlink
skip, repository validation 5/5, Ruff, and 86.10% coverage. P2.4 acceptance
and integration evidence is recorded below. Reports, CLI, P2.3 expansion, and
deferred capabilities were not part of the implementation.

The user accepted P2.4 on 2026-07-19. PR #39 merged the implementation and
review evidence at exact `main` commit `cd9b52e`. Verification on that merged
tree passes 15 focused result tests, 237 full-suite tests with one expected
Windows symlink skip, repository validation 5/5, Ruff, and 86.10% coverage.
P2.4 is closed. P3.1 is authorized next only for deterministic CSV and Markdown
issue-register views of the immutable canonical result; P3.2 release summary,
P3.3 CLI, P2.3 expansion, semantic held-out execution, and deferred
capabilities remain blocked.

P3.1 implementation commit `2f93335` adds a package-assurance-specific issue
register renderer on `codex/p3.1-issue-register` from accepted predecessor
`b9de4e6`. It reads strict JSON, rejects duplicate keys and non-JSON numeric
constants, validates the immutable result against `package_result.schema.json`,
and emits deterministic CSV and Markdown strings from the stored canonical
finding order. Structured identifiers, expected/actual values, and evidence
remain JSON in the CSV; the Markdown preserves the same facts and the accepted
human-review limitation. It does not rerun gates, checks, authority selection,
state routing, or holds, and it does not write reports or add CLI behavior.
Verification passes 11 renderer tests, 26 focused result/report tests, 248
full-suite tests with one expected Windows symlink skip, repository validation
5/5, Ruff, and 86.49% coverage. A real drawing-revision conflict report was
inspected and contains package-relative evidence without approval language.
That review evidence was the basis for the acceptance and integration recorded
below.

The user accepted P3.1 and authorized its merge on 2026-07-19. The exact
reviewed branch was fast-forwarded to `main` at `8f66b12`. Verification on that
exact merged tree passes 26 focused package-result/report tests, 248 full-suite
tests with one expected Windows symlink skip, repository validation 5/5, Ruff,
and 86.49% coverage. P3.1 is closed. P3.2 is authorized next only for one
concise, non-approving Markdown release-readiness view of the immutable result;
report publishing, P3.3 CLI, broad P2.3, semantic held-out execution, and
deferred capabilities remain blocked.

P3.2 implementation commit `7536bea` adds one in-memory Markdown
release-readiness renderer on `codex/p3.2-release-readiness-summary` from
accepted predecessor `3466398`. It shares P3.1's strict JSON and schema-valid
result loading, then reports only stored package/run identity, state, release
hold, blocking states, gate/check status counts, finding counts by state,
output names, the exact engineering-review limitation, and the required
qualified-human decision. It does not rerun evaluator logic, publish reports,
or add CLI behavior. Verification passes 36 focused package-result/report
tests, 258 full-suite tests with one expected Windows symlink skip, repository
validation 5/5, Ruff, and 86.75% coverage. An inspected drawing-revision fault
summary matches the immutable result and contains no absolute machine path or
approval claim. That review evidence was the basis for the acceptance and
integration recorded below.

The user accepted P3.2 and authorized continuation on 2026-07-19. The exact
reviewed branch was fast-forwarded to `main` at `4b848b9`. Verification on that
exact merged tree passes 36 focused package-result/report tests, 258 full-suite
tests with one expected Windows symlink skip, repository validation 5/5, Ruff,
and 86.75% coverage. P3.2 is closed. P3.3 is authorized next only for atomic
publication of the accepted result/report artifacts and the bounded
`audit-package` CLI with accepted exits. Broad P2.3, semantic held-out
execution, protected changes, and deferred capabilities remain blocked.

P3.3 implementation commit `b5f0fcd` adds a package-assurance workflow and
atomic multi-file publication boundary on `codex/p3.3-audit-package-cli` from
accepted predecessor `main` `441e521`. The command validates usage, runs the
accepted eight gates and five checks, builds the canonical result, and
publishes `package_result.json`, `issue_register.csv`, `issue_register.md`,
and `release_readiness.md` together. The v0.3 package-result schema keeps the
accepted one-file variant and adds one exact four-output variant; the frozen
v0.2 result schema and CLI behavior are unchanged. Verification passes 49
focused result/report/CLI tests, 271 full-suite tests with one expected Windows
symlink skip, repository validation 5/5, Ruff, and 86.76% coverage. Inspected
clean evidence has 8 passed gates, 5 passed checks, zero findings, and exit 0.
The inspected removed-mapping fault has 8 passed gates, 4 passed and 1 failed
check, exactly one `DRAWING_DOCUMENT_FILE_RECIPROCITY_FAILED` issue, release
hold true, and exit 1. Both runs contain exactly four outputs and no absolute
local paths. This was the evidence presented for the acceptance recorded below.

The user explicitly accepted P3.3 on 2026-07-20. PR #40 merged the reviewed
implementation and evidence at exact `main` commit `e4080fd`. Verification on
that exact merged tree passes 49 focused package-result/report/CLI tests, 271
full-suite tests with one expected Windows symlink skip, repository validation
5/5, Ruff, and 86.76% coverage. P3.3 is closed. P2.3 definition is authorized
next; evaluator implementation and semantic held-out execution remain blocked
until the definition is reviewed and accepted.

The P2.3 definition separates six checks supported by the accepted sources and
authority rules from six claims that are not currently supportable. The
supported sequence covers BOM item/equipment manifest reciprocity, BOM
equipment presence in drawing metadata, datasheet authority presence,
equipment/datasheet agreement, equipment/datasheet manifest reciprocity, and
specification revision history. Quantity reconciliation, part/material
agreement, BOM item/drawing agreement, equipment/specification association,
datasheet revision history, and controlled technical-value compliance remain
authority/source gaps. The user accepted this definition on 2026-07-20, and
PR #41 merged it at exact `main` commit `a855d99`. This distinction prevents a
parsed single-source value from being misreported as a reconciled
cross-document value.

Six temporary development-package definition probes confirmed the ownership
boundary: each proposed isolated fault passed all eight P2.1 gates and all five
accepted drawing checks with zero findings. The new checks therefore close
real gaps rather than duplicating current behavior. Only ignored scratch copies
were mutated.

Check 6 implementation `c1dcc4a` appends
`bom_item_equipment_manifest_reciprocity` without changing the eight gates or
five accepted drawing checks. It evaluates release-required BOM rows and
required manifest declarations in stable item order, requires every
behavior-critical field of exact `AUTH-BOM-002`, emits one high-severity
automatic-fail release hold per affected item, and remains independent of an
unrelated drawing-authority rule. Missing, extra, wrong, and multiple
declarations are covered without changing accepted fixtures or schemas.

Verification passes 31 relationship tests, 75 focused relationship/result/
report/CLI tests, 278 full-suite tests with one expected Windows symlink skip,
repository validation 5/5, Ruff, and 87.02% coverage. Inspected clean evidence
has 8/8 gates, 6/6 checks, no findings, state `automatic_pass`, hold false, and
exit 0. The isolated valid-but-wrong target has 8/8 gates, 5/6 checks, exactly
one `BOM_ITEM_EQUIPMENT_RECIPROCITY_FAILED` under `AUTH-BOM-002`, state
`automatic_fail`, hold true, and exit 1. Both runs contain exactly four outputs
and no absolute local path. The implementation is not integrated pending
explicit user acceptance.

## Intended Outcome

The pilot audits structured relationships among:

`drawing register <-> drawing metadata <-> BOM/equipment list <-> datasheet/specification metadata <-> revision history <-> controlled file references`

Primary deliverables:

- immutable machine-readable package result;
- evidence-linked issue register;
- release-readiness summary;
- explicit package states and stable CLI exits;
- benchmark and clean-clone evidence;
- bounded service demonstration.

## Operating Decisions

- Use gate and evidence completion, not hours, to control progress. Prospective time tracking is waived; historical values remain archival context.
- Keep the evaluator independent of any producer, model, or agent runtime.
- Prefer deterministic, source-linked checks and fail closed on unsafe normalization or missing authority.
- Preserve failed runs and keep package definitions, expected assets, candidate artifacts, traces, and results separate.
- Use only public, synthetic, self-authored, or explicitly authorized data.
- Treat the first commercial offer as a bounded audit service, not software access.

## Document Authority

Read current project information in this order:

1. `gantt.xlsx` for active status, gates, decisions, risks, evidence, and next action;
2. accepted workflow and acceptance contracts for product behavior;
3. `AGENTS.md` for durable repository controls;
4. this file for the compact current handoff;
5. architecture, strategy, commercial, and release documents for supporting context.

Files under `docs/archive/` and dated modernization records are historical provenance, not current control.

## Current Authorized Action

Complete a bounded behavior-preserving relationship-module and focused-test
cleanup before check 7. Preserve all accepted gates, checks, result/report/CLI
semantics, schemas, fixtures, authority maps, goldens, held-out content, and
frozen v0.2 behavior. After exact regression proof, implement only check 7.
The sanitized real-package development trial requires an explicitly authorized
package; held-out semantics and deferred multimodal/platform capabilities remain
blocked.

Reusable lessons, prevention actions, and proof are controlled in
`docs/quality/improvement_register.md`.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
