# Project Context

**Updated:** 2026-07-21
**Repository:** `C:\Projects\mechanical-technical-document-evaluation-harness`
**Current branch:** `codex/p4.2-held-out-replacement-freeze`

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
- **Active WBS:** P4.2 second contamination and external-custody gate
- **Status:** D-111 integrated through PR #63 at exact `main` `4d2c0f5`, but Git's integration summary exposed scenario-level path and comparative file-statistics metadata before first execution. Semantic execution count remains zero. Both exposed families are preserved unchanged and release-ineligible; proposed D-112 moves a materially distinct replacement outside the ordinary repository until raw first-run evidence is frozen
- **Implementation state:** Eight ordered gates and eleven ordered relationship checks feed the canonical result and report views through one bounded `audit-package` command. P2.3 is complete for that exact scope; quantity, part/material, BOM-item/drawing, equipment/specification, datasheet-revision, and controlled technical-value reconciliation are excluded from v0.3.0 claims

P0.1 is accepted. Its reviewed workflow contract and authority-map example freeze the package boundary, identifiers, authority rules, result states, evidence contract, human-review boundary, and exclusions.

P0.2 is accepted. It freezes the development/held-out split, minimum scenario matrix, exact oracle matching, state and CLI routing, reproducibility, contamination handling, false-positive/false-negative review, bounded claims, and release stop conditions.

P1.1 is accepted and locally integrated at commit `42ad037`. It validates package metadata, mandatory source declarations, canonical manifest identifiers, document revisions, relationship declarations, authority-map references, and controlled paths. It resolves source and file declarations without parsing source records or assigning package result states; those behaviors remain in later gated work.

P1.2 is accepted at commit `f26ed27`. It provides `SCN-DEV-PUMP-SKID-CLEAN-001`, a clean, fully synthetic pump-skid package with all seven mandatory sources, nine controlled file references, 20 reviewed semantic relationships, exact hidden evidence locators, expected clean results, and a package-tree content hash. Its source layouts are fixture examples rather than accepted general schemas.

P1.3 is accepted at commit `4b7516e`. It provides a materially distinct synthetic held-out family with exact protected findings, evidence locators, check IDs, package states, per-scenario hashes, material-distinction evidence, contamination controls, and freeze-set hash `428f8c31f35e5c4f20a345621b937628c686576617bb5348db60db4d90e25884`. Its recorded `frozen_pre_tuning` status is active. It is self-authored pre-tuning, not independently blind. During P2.1, tracked held-out path names were inadvertently enumerated and the full suite exercised opaque integrity checks; protected source and oracle values were not surfaced to or inspected by the implementation agent or used to tune evaluator behavior. The first semantic held-out evaluation remains gated.

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
and no absolute local path. The user accepted check 6. PR #42 merged it, and
PR #43 integrated its closeout at exact `main` `b36441f`.

Check 7, `bom_equipment_drawing_presence`, was accepted and integrated through
PR #45 at exact `main` `273c36a`. It verifies that every release-required BOM
equipment scope appears in drawing metadata under exact `AUTH-BOM-002` without
claiming that the BOM drawing number is authoritative. The clean development
package passes 7/7 checks; the isolated missing-tag fault produces one release
hold. Full verification remains 283 passed with one expected Windows skip.

The authorized structured-package trial, public-source selection, dual intake,
and fit-gap assessment were integrated through PRs #46-#48. D-097 accepted the
bounded NASA/JPL and OpenFlexure mappings plus the shared transformation log,
and PR #49 merged them at exact `main` `53e19ad`.

Both approved public packages are now prepared in separate Git-ignored roots.
Independent verification passed all pinned-source hashes, byte-preserved source
copies, manifest boundaries, structured-source loading, all fields across 91
BOM rows, 91 required manifest relationships, complete log coverage, explicit missing
authority, package-tree hashes, and audit-output absence. NASA/JPL contains 58
BOM rows and 126 copied source artifacts; OpenFlexure contains 33 BOM rows and
51 copied artifacts. Both are expected to route to
`missing_authoritative_information`. The tracked review is
`docs/package_assurance/dual_public_package_preparation_review_2026-07-20.md`.

D-098 was accepted and PR #50 merged the preparation review at exact `main`
`7009fe2`. The first controlled NASA/JPL audit reverified the accepted package
tree, then returned internal exit `70` before atomic publication. The identifier
gate treated each intentionally blank BOM drawing, datasheet, and specification
reference as a malformed required identifier and copied the blank value into
canonical `affected_identifiers`; the strict package-result schema rejected the
malformed findings. No output was published and no package changed. The
OpenFlexure audit was not executed; a read-only diagnostic confirmed the same
defect would produce 99 blank-identifier findings. `IMP-017` and
`docs/package_assurance/dual_public_package_audit_failure_review_2026-07-20.md`
record the root cause and proposed narrow stabilization.

D-099 was accepted and PR #51 merged the failure review at exact `main`
`624acce`. The stabilization changes only identifier-gate presence semantics and
invalid-finding representation. Six new tests prove exact optional blanks,
strict malformed nonblank handling, valid parent-row affected identifiers, and
full CLI publication for both missing-authority and automatic-fail outcomes.
The focused set passes 47 tests; the full suite passes 289 with one expected
Windows skip at 87.57% coverage; validation is 5/5; Ruff, baseline 9/9, and demo
2/2 pass. Both public package trees and all 1,764 accepted mapping-log rows
remain exact. The tracked review is
`docs/package_assurance/identifier_result_contract_stabilization_review_2026-07-20.md`.

D-100 was accepted and PR #52 merged the stabilization at exact `main`
`0611d916`. One and only one unchanged NASA/JPL audit was then executed. Run
`RUN-20260721T001431760486Z-4f1b9817` returned the predeclared
`missing_authoritative_information` state, release hold `true`, CLI exit `3`,
and exactly four outputs. The canonical result passed its strict schema; the
CSV and Markdown issue registers and release-readiness summary reproduced
exactly from it. Four gates passed, the authority gate failed with the one
expected `AUTHORITY_REQUIRED_RULE_MISSING` finding, three dependent gates were
skipped, and all seven relationship checks were skipped against that authority
prerequisite. No malformed-identifier finding or absolute local output path was
present. Pre- and post-run hashes confirm both accepted package trees and logs
remain unchanged, and OpenFlexure was not executed. The tracked review is
`docs/package_assurance/nasa_jpl_public_audit_confirmation_review_2026-07-20.md`.

D-101 was accepted and PR #53 merged that confirmation at exact `main`
`65c9699b`. One and only one unchanged OpenFlexure audit was then executed. Run
`RUN-20260721T004222043918Z-254a2eca` returned the same predeclared
`missing_authoritative_information` state, release hold `true`, CLI exit `3`,
and exactly four outputs. The canonical result passed its strict schema; both
issue-register views and the readiness summary reproduced exactly from it.
Four gates passed, the authority gate failed with one expected
`AUTHORITY_REQUIRED_RULE_MISSING` finding, three gates skipped, and all seven
relationship checks skipped against the authority prerequisite. Both public
package trees and all 1,764 accepted log rows remain exact after one authorized
audit each. `I-004` is closed, `IMP-017` is retained, `IMP-016` remains open,
and `IMP-018` records the package-scoped finding-ID requirement for future
multi-package reporting. The tracked review is
`docs/package_assurance/openflexure_public_audit_confirmation_review_2026-07-20.md`.

D-102 was accepted and PR #54 merged the OpenFlexure confirmation at exact
`main` `b0b32bb`. Check 8, `equipment_datasheet_authority_presence`, is now the
eighth ordered relationship check. It requires exactly one release-required
datasheet metadata record for each release-required BOM equipment tag under the
exact `AUTH-SPEC-001` rule. Zero or competing records produce a high-severity
`missing_authoritative_information` hold with deterministic BOM and datasheet
collection evidence. The clean development package passes 8/8 checks. An
isolated removed datasheet produces one exact finding, exit `3`, and four
schema-valid outputs. Focused verification passes 111 tests; the full suite
passes 295 with one expected Windows skip at 87.71% coverage; validation 5/5,
Ruff, baseline 9/9, and demo 2/2 pass. The tracked review is
`docs/package_assurance/equipment_datasheet_authority_presence_implementation_review_2026-07-20.md`.

D-103 was accepted and PR #55 merged check 8 at exact `main` `fb0113d`.
Check 9, `equipment_datasheet_association`, is now the ninth ordered
relationship check. It compares each release-required BOM `datasheet_id` with
the single authoritative metadata ID for the same normalized equipment tag.
The clean development package passes 9/9 checks. Changing only the pump BOM
reference to existing valid `DS-M-101` produces one
`EQUIPMENT_DATASHEET_MISMATCH`, `automatic_fail`, release hold true, exit `1`,
and four schema-valid outputs. Focused verification passes 88 tests; the full
suite passes 299 with one expected Windows skip at 87.86% coverage; validation
5/5, Ruff, baseline 9/9, and demo 2/2 pass. The first manual fault invocation
preserved a transient Windows final-rename `PermissionError` at exit `70`; an
unchanged retry succeeded. `IMP-019` records the required stabilization. The
tracked review is
`docs/package_assurance/equipment_datasheet_association_implementation_review_2026-07-20.md`.

D-104 was accepted and PR #56 merged check 9 at exact `main` `7146b23`.
The publication-resilience stabilization makes at most five final-rename
attempts with fixed waits of 50, 100, 200, and 400 milliseconds. Only
`PermissionError` qualifies. A collision or other operating-system error does
not retry, and exhaustion preserves the failed publication with CLI exit `70`.
Four injected publication tests and one CLI exhaustion test prove these
boundaries. Twenty consecutive Windows audits passed with nine relationship
checks and four outputs each, with no hidden failed-publication directory. The
full suite passes 304 tests with one expected Windows skip at 88.08% coverage;
validation 5/5, Ruff, baseline 9/9, and demo 2/2 pass. The tracked review is
`docs/package_assurance/publication_resilience_stabilization_review_2026-07-21.md`.

D-105 was accepted and PR #57 merged the publication stabilization at exact
`main` `dbcd242`. Check 10, `equipment_datasheet_manifest_reciprocity`, is now
the tenth ordered relationship check. It compares release-required
authoritative datasheet metadata with release-required manifest declarations
in both directions under exact `AUTH-SPEC-001`, while check 8 retains ownership
of missing or ambiguous authority for required BOM equipment. The clean
development package passes 10/10 checks. Changing only `REL-EQ-DS-001` to the
existing wrong target `DS-M-101` produces one
`EQUIPMENT_DATASHEET_RECIPROCITY_FAILED` finding, `automatic_fail`, release
hold true, exit `1`, and four consistent outputs. Focused verification passes
93 tests; the full suite passes 308 with one expected Windows skip at 88.27%
coverage; validation 5/5, Ruff, baseline 9/9, and demo 2/2 pass. The tracked
review is
`docs/package_assurance/equipment_datasheet_manifest_reciprocity_implementation_review_2026-07-21.md`.

D-106 was accepted and PR #58 merged check 10 at exact `main` `761ac76`.
Check 11, `specification_revision_history`, is now the eleventh ordered
relationship check. It compares every release-required specification-metadata
revision with exactly one current revision-history record joined by normalized
`specification_id` under exact `AUTH-SPEC-003`. The clean development package
passes 11/11 checks. Changing only `SPMETA-001.revision_id` from `A` to valid
value `B` produces one `SPECIFICATION_REVISION_MISMATCH` finding,
`automatic_fail`, release hold true, exit `1`, and four consistent outputs.
Focused verification passes 99 tests; the full suite passes 314 with one
expected Windows skip at 88.48% coverage; validation 5/5, Ruff, baseline 9/9,
and demo 2/2 pass. The tracked review is
`docs/package_assurance/specification_revision_history_implementation_review_2026-07-21.md`.

PR #59 merged accepted check 11 at exact `main` `69c0d1b`. D-108 then froze
P2.3 at eight gates and eleven checks, explicitly deferred six unsupported
cross-source claims, and integrated through PR #60 at exact `main` `b439974`.

P4.1 revision `P4.1-DEV-1` is implemented on
`codex/p4.1-development-benchmark` at implementation commit `4cf9fe8`. It
derives 22 controlled development scenarios from the accepted pump-skid
baseline without staging `expected/` assets. Every scenario runs the real
evaluator and four-output publication twice. The exact-commit acceptance
execution passed 22/22 scenarios, 44/44 complete
publications, all eight mandatory-gate failure cases, all eleven relationship
failure cases, repeated-run equality, and exact normalized publication hashes.
Generated evidence is preserved under
`runs/p4.1-development-acceptance-4cf9fe8-final/` and remains separate from
versioned benchmark definitions. No protected held-out semantics were
executed. Focused benchmark tests pass 5; the full suite passes 319 with one
expected Windows skip at 88.57% coverage; repository validation 5/5, Ruff,
frozen baseline 9/9, portfolio demo 2/2, and both hosted Linux CI jobs pass.
The first hosted run exposed one Windows/Linux separator difference in a
portable manifest-error message. Commit `4cf9fe8` canonicalizes the path,
updates only the affected reviewed oracle, and closes the red-to-green loop.

D-109 was accepted by the project owner on 2026-07-21. The evaluator has
accepted genuine full-package paths to four states;
`engineering_review_required` and `evaluator_uncertainty` remain tested at the
router and exit-contract layer but have no accepted end-to-end semantic
trigger. The bounded release decision discloses and defers those semantic
triggers rather than manufacturing evidence or reopening P2.3 in this release.
P4.1 is accepted and integrated through PR #61. The controlling review is
`docs/package_assurance/p4_1_development_benchmark_definition_and_review_v0.3.0.md`.

PR #61 integrated P4.1 at exact `main`
`5a4d57e534bd5e900abac3c455cd484ef083e972`. During the subsequent P4.2
definition review, the current implementation context enumerated held-out path
names and opened top-level freeze and family-review records before the first
run. No protected or scenario-expected value was surfaced to or inspected by
the implementation context, no semantic audit was run, and no evaluator
behavior changed. Existing hosted CI later ran opaque fixture-integrity tests
that load protected JSON internally without printing its values. The exposed
top-level records nevertheless contained expected conditions and states, so
Section 15 of the accepted plan makes the existing family contaminated for
release held-out claims. D-110 was accepted on 2026-07-21. It preserves the
family unchanged and unexecuted and requires a materially distinct replacement
authored in an isolated custodian context. The
controlling record is
`docs/package_assurance/p4_2_held_out_contamination_and_replacement_gate_v0.3.0.md`.

The replacement was authored from isolated public bundle
`P4.2-CUSTODIAN-EA45DCF-V1`. Recovery custodians completed 326 structural and
hash checks after the initial context stopped before its freeze records. A
separate verifier passed 14/14 controls, and an isolated import check proved
210/210 files byte-identical. The complete-family hash is
`e619c81854d9676b5d821a752e3b00e68d0072572cef64509d5cc9132a3e6ff6`.
No semantic run occurred and protected values were not exposed to the
implementation context. The controlling owner package is
`docs/package_assurance/p4_2_replacement_freeze_review_v0.3.0.md`.

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

Present D-112 for owner review. Preserve both release-ineligible families
unchanged and unexecuted. Do not author or import a replacement, execute a
scenario, compare an oracle, restore protected-fixture CI, change evaluator
behavior or benchmark inputs, rerun either public package, begin P4.3, or add
deferred capabilities before D-112 is accepted.

Reusable lessons, prevention actions, and proof are controlled in
`docs/quality/improvement_register.md`.

## Engineering Boundary

Outputs are flags, evidence, draft reports, and review packages. They are not engineering sign-off, code-compliance opinions, autonomous release decisions, or safety-critical final decisions.
