# Improvement Loop and Register

## Purpose

This file is the project's durable memory for lessons that should change how
future work is performed. An AI work session does not train itself or become
permanently smarter on its own. Improvement becomes real when a correction,
failure, or useful discovery is converted into a reviewed contract, test,
check, fixture, or operating rule in the repository.

The loop applies to three areas:

- **Work quality:** reduce user corrections, scope mistakes, and repeated
  engineering errors.
- **Product quality:** improve correct fault detection, clean-package handling,
  result-state routing, and evidence accuracy.
- **Review value:** increase useful findings and reduce findings that qualified
  reviewers reject or cannot verify.

## Standard Loop

1. **Observe:** record a correction, escaped defect, false result, confusing
   control, or repeated manual step.
2. **Explain:** identify the root cause, not only the immediate symptom.
3. **Prevent:** choose the smallest durable change that can stop recurrence.
4. **Prove:** add or identify repeatable evidence that the change works.
5. **Review:** keep, revise, or retire the change based on later evidence.

A lesson is not closed because a document says it is closed. It is closed only
when its prevention and proof exist. New controls should remain small; controls
that create more burden than value should be revised or retired.

## Core Measures

These are counts or rates, not time tracking:

- user corrections and reopened work items;
- escaped defects found after a work block was declared complete;
- unauthorized scope changes;
- clean-package false holds;
- seeded-fault detection rate;
- correct result-state routing rate;
- findings with complete, reproducible evidence locators;
- reviewer-accepted versus reviewer-overturned findings;
- CI failures that identify a real defect before review.

Do not set performance targets until the first complete vertical slice produces
a trustworthy baseline. Never improve a metric by weakening a golden result,
held-out case, acceptance rule, or mandatory hold.

## Register

| ID | Observation and root cause | Permanent prevention | Proof | Status |
|---|---|---|---|---|
| `IMP-001` | Windows absolute paths could pass the POSIX-only evidence-path check. Cross-platform path forms were not tested. | Validate both POSIX and Windows path forms and require POSIX package-relative locators. | `tests/test_package_models.py` covers absolute, drive, UNC, traversal, and backslash forms. | Retained |
| `IMP-002` | Structured JSON sources accepted any non-empty schema version. The adapter had no explicit compatibility policy. | Accept only the versioned fixture profile supported by the pilot and fail closed on other versions. | `test_unsupported_json_source_version_fails_closed` verifies a controlled gate failure and dependent skips. | Retained |
| `IMP-003` | The dashboard reported P2 as complete while P2.2-P2.4 had not started. A phase percentage was manually hard-coded. | Derive the P2 phase value from completed sub-WBS rows and show acceptance state in the note. | Corrected `gantt.xlsx` dashboard plus accepted decision/evidence entries. | Retained |
| `IMP-004` | The current held-out package set is protected from tuning but was created inside this project. It is not independently blind evidence. | Keep the protected set for regression and claim-boundary testing; require a separately controlled unseen package before any independent-performance claim. | Acceptance and limitations language; future external validation evidence. | Open |
| `IMP-005` | `package_assurance/gates.py` concentrates many responsibilities, making future rule additions harder to review. Horizontal implementation encouraged continued growth. | Do not add P2.2 relationship behavior to the existing gate functions. Define a narrow relationship module boundary before the next implementation slice. | Accepted definition plus isolated `relationships.py` and `tests/test_package_relationships.py`; `gates.py` remained unchanged. | Retained |
| `IMP-006` | Accepted feature work accumulated ahead of remote `main`, increasing integration risk. Acceptance and integration were treated as separate, informal steps. | End accepted capability chains with one reviewed integration pull request and verify its checks before merge. | PR #27 merged to `main` at `94d9117` after green GitHub checks. | Retained |
| `IMP-007` | CI proved behavior but did not automatically catch basic source defects or coverage loss. | Run Ruff checks and enforce an initial 80% test-coverage floor in CI. | Local lint passes; full suite establishes 84% baseline before the floor is enabled. | Retained |
| `IMP-008` | Excel lock files appeared as recurring working-tree noise while the controlling workbook was open. | Ignore `~$*.xlsx` temporary files without ignoring the workbook itself. | Clean status while `gantt.xlsx` is open. | Retained |
| `IMP-009` | Bidirectional counterpart gaps initially looked like one rule, but the two directions have different authority states and negative-evidence needs. | Define relationship directions separately whenever authority, result-state routing, or absence evidence differs; do not hide distinct failures in one check. | The accepted definition and implementation commit `b24ca65` isolate register-to-metadata absence, prove collection-level negative evidence, and explicitly defer metadata-without-register authority. | Retained |
| `IMP-010` | Presence and boundary checks can all pass when a source points to the wrong but still valid controlled identifier. Testing only missing or malformed references would not expose this relationship gap. | For identifier reconciliation, include a wrong-but-valid target fault that preserves structural validity and all prerequisite gates. | Definition probe and implementation test change only `DWMETA-001.file_ref_id` to existing `FILE-DWG-002`; all eight P2.1 gates and the first three P2.2 checks pass before commit `74970c3` emits the exact fourth-check finding. | Retained |
| `IMP-011` | P2.1 can structurally accept a renamed authority rule that still controls the required field. Structure alone does not prove that an executable relationship consumed the reviewed rule identity and semantics. | Each relationship check must fail closed unless its exact accepted authority rule and behavior-critical fields are present; never substitute another rule by field similarity. | `test_file_reference_check_requires_exact_accepted_authority_rule` renames `AUTH-DWG-002` in a temporary copy while P2.1 remains green; the first three checks pass and only the dependent fourth check is skipped against the authority gate. | Retained |
| `IMP-012` | Horizontal delivery made state routing and user-facing outputs wait for every planned relationship family. Individual checks accumulated without one command a reviewer could use end to end. | Deliver a thin accepted vertical slice from one bounded relationship fault through package state, immutable result, reports, and CLI before broad rule-family expansion. | The accepted `first_usable_audit_vertical_slice_definition_v0.3.0.md`, D-073, and EV-070 freeze the sequence. Fifth-check commit `4f06352` is integrated through PR #37. Accepted P2.4 commit `cbcfc2b` is integrated through PR #39 at exact main `cd9b52e`. Accepted P3.1 implementation `2f93335` is integrated at exact main `8f66b12`. Accepted P3.2 implementation `7536bea` is integrated at exact main `4b848b9`. Accepted P3.3 implementation `b5f0fcd` and review evidence `411928e` are integrated through PR #40 at exact main `e4080fd`; exact-main proof is 49 focused tests, 271 full-suite passes, 5/5 validation, Ruff, 86.76% coverage, and inspected clean/fifth-check-fault runs. | Retained |
| `IMP-013` | A project plan can demand quantity, material, or association reconciliation even when the accepted package has only one source for the field or no exact authority rule. A structural presence check can then be mistaken for agreement proof. | Before implementing each relationship family, classify every planned claim as cross-source supported, single-source structural only, or blocked by an authority/source gap. Never use broad authority prose to substitute for an exact controlled field. | The accepted `p2_3_relationship_expansion_definition_v0.3.0.md`, PR #41, D-086, and EV-083 freeze six implementable checks and six explicit gaps. Six temporary definition faults each passed all existing eight gates and five checks with zero findings, proving uncovered ownership. Quantity, part/material, item/drawing, specification association, datasheet revision, and technical-value claims stay blocked pending reviewed source/authority decisions. | Retained |
| `IMP-014` | A global authority shortcut can skip a new independent check merely because an unrelated earlier authority rule is unavailable. That hides usable evidence and makes the ordered pipeline more coupled than its contracts state. | Evaluate each new relationship check against its own exact authority dependency after the common package-gate boundary; preserve earlier accepted skip behavior but do not propagate unrelated authority failures into the new check. | Check 6 uses its dedicated `AUTH-BOM-002` path. Check 8 uses exact `AUTH-SPEC-001`; `test_datasheet_presence_is_independent_of_drawing_and_bom_authority` proves it still passes when the drawing checks and checks 6-7 correctly skip under their own unavailable authority rules. | Retained |
| `IMP-015` | The relationship implementation and focused tests each exceeded 1,700 lines before five more checks were added. Domain ownership was becoming harder to see and each addition increased review risk. | Keep one small public coordinator, shared deterministic primitives, and separate drawing and BOM/equipment domain modules and focused tests. Split a domain before adding a new rule family; do not create a generic rule engine. | Check 8 adds a separate datasheet-domain module and focused test file while the public coordinator remains small. The broader focused set passes 111 tests; the full 295-test suite passes with one expected Windows skip at 87.71% coverage; validation 5/5, Ruff, baseline 9/9, and demo 2/2 pass. | Retained |
| `IMP-016` | A real public package can lack a conventional mandatory source while a generated header-only CSV still passes structural presence checks. Empty records do not prove that the publisher authoritatively requires no records, so a vacuous clean result could hide a product-model mismatch. | Before a real-package audit, require a reviewed source-to-audit disposition and predeclared expected state. Add an explicit source-applicability/authority control before accepting a result; a generated empty source must retain missing authority unless an accepted source proves the empty condition. | The NASA/JPL and OpenFlexure mapping definitions and shared transformation log freeze this refusal boundary. One authorized run of each package preserved the intended `missing_authoritative_information` hold and exposed eight absent authority rules. Neither run supplied the missing authority or justified treating an empty source as not applicable. | Open |
| `IMP-017` | The first public-package audit returned internal exit `70`: intentionally blank optional BOM references were treated as malformed required identifiers, and the invalid blank value was copied into canonical `affected_identifiers`, causing the strict result schema to reject the evaluator's own finding. Synthetic fixtures had populated every optional reference, so this interface mismatch was not exercised end to end. | Separate identifier presence from identifier syntax. Skip syntax checks only for explicitly optional blank BOM references; keep mandatory and nonblank values strict. Invalid source values stay in evidence and never enter canonical affected-identifier fields. Require a synthetic missing-authority CLI regression before rerunning public packages. | D-099 implementation permits only the three approved exact blank BOM references, preserves strict malformed-value holds and raw evidence, and uses valid parent identifiers or an empty list in results. Six new tests include full CLI exit `3`/four-output and exit `1`/four-output proofs. Focused 47; full 289/1; coverage 87.57%; validation 5/5; Ruff; baseline 9/9; demo 2/2. The single D-100 NASA/JPL and D-101 OpenFlexure runs both passed identifier syntax, published four schema-valid outputs, and returned the exact missing-authority exit `3` contract with no malformed-identifier finding. | Retained |
| `IMP-018` | NASA/JPL and OpenFlexure produced the same semantic authority finding and therefore the same stable `finding_id`, despite having different package IDs. That is unambiguous inside separate package results but can collide if a future portfolio view assumes `finding_id` is globally unique. | Treat `(package_id, finding_id)` as the identity in every future multi-package report, API, or database. Do not change the accepted per-package hashing algorithm during this pilot without a separate contract and migration decision. | The two inspected results both contain `FND-1704FCB7F45DFE73` and `AUTHORITY_REQUIRED_RULE_MISSING`, while their `package_id` values remain distinct. The D-101 comparison evidence and review record the required composite scope before any aggregation layer exists. | Open - control before aggregation |
| `IMP-019` | A manual check-9 fault run generated all four correct staged outputs, but Windows denied the final staging-directory rename with `PermissionError`. The workflow correctly preserved the failed publication and returned exit `70`; an immediate unchanged invocation succeeded. A transient sharing lock can therefore prevent a valid audit from publishing. | Retry only the final same-parent rename after `PermissionError`, using a fixed subsecond budget. Never retry or overwrite a final-directory collision or retry another operating-system failure; preserve failed evidence and exit `70` after exhaustion. | D-104 authorized five total attempts with fixed 50/100/200/400 ms waits. Injected tests prove transient recovery, exact exhaustion, no collision retry, no other-error retry, and CLI exit `70` with four staged outputs plus the failure marker. Twenty consecutive Windows audits passed with four outputs and no hidden failures. D-105 accepted the control, PR #57 integrated it at exact `main` `dbcd242`, and `I-005` closed as controlled. Full 304/1; coverage 88.08%; validation 5/5; Ruff; baseline 9/9; demo 2/2. See `publication_resilience_stabilization_review_2026-07-21.md`. | Retained |
| `IMP-020` | P0.2 required six end-to-end package states, but the accepted eight gates and eleven checks can genuinely emit only four. Unit coverage of a router capability was mistaken for proof that an accepted package condition could reach that state. | Maintain a capability-to-claim matrix that separates full-audit semantic coverage from router-only contract coverage. A benchmark may never synthesize a state by editing output or mocking the evaluator. Any variance must stop the next gate and receive an explicit decision. | `P4.1-DEV-1` executes 22 scenarios twice, covers all 8 gate failures and all 11 check failures, and records `engineering_review_required` and `evaluator_uncertainty` as contract-only. D-109 accepted this bounded claim on 2026-07-21 and retains the control for P4.2 and release language. | Retained - D-109 accepted |
| `IMP-021` | The frozen v0.2 baseline replay script defaults its summary and report to tracked historical evidence. An ordinary verification run therefore changed protected timestamps and run paths even though behavior passed. | Every non-release replay must pass a generated `--evidence-dir` under `runs/`; the repository agent instructions now state this explicitly. Inspect protected evidence paths immediately after every baseline replay. | The accidental timestamp-only changes were fully restored with no remaining diff. The 9/9 replay result is preserved under ignored runtime output, and `AGENTS.md` records the safe invocation rule. | Retained |
| `IMP-022` | The first P4.1 hosted run failed one exact oracle because a sanitized manifest-error path used backslashes on Windows and forward slashes on Linux. Local repeatability on one operating system did not prove portable evidence. | Canonicalize path separators in stable findings before IDs and reports are built. Require the complete exact-oracle revision to pass both local Windows verification and hosted Linux CI before acceptance. | Commit `4cf9fe8` uses POSIX separators in portable manifest errors, adds direct missing/malformed-manifest assertions, and changes only the affected oracle. Both Python 3.12 and 3.14 focused matrices pass locally; both hosted Linux CI jobs changed from red to green. | Retained |

## Work-Block Closeout Rule

At each substantial work-block closeout:

1. run focused tests, the full frozen regression suite, repository validation,
   lint, and the coverage floor;
2. inspect generated evidence and the final Git diff;
3. add a register entry only for a new, reusable lesson;
4. update an existing entry when its proof or status changes;
5. use a fresh review pass to challenge scope, claims, and failure behavior;
6. record unresolved limits rather than smoothing them over.

The next product increment should be a thin vertical slice: one approved
relationship fault should flow from source records to evidence, issue, package
state, and CLI output. That slice requires a separate accepted scope and must
not begin during this stabilization block.
