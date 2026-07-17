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
| `IMP-005` | `package_assurance/gates.py` concentrates many responsibilities, making future rule additions harder to review. Horizontal implementation encouraged continued growth. | Do not add P2.2 relationship behavior to the existing gate functions. Define a narrow relationship module boundary before the next implementation slice. | `docs/package_assurance/p2_2_relationship_slice_definition_v0.3.0.md`; focused module tests remain required during implementation. | Validating |
| `IMP-006` | Accepted feature work accumulated ahead of remote `main`, increasing integration risk. Acceptance and integration were treated as separate, informal steps. | End accepted capability chains with one reviewed integration pull request and verify its checks before merge. | Draft integration PR #27 is open, merge-clean, and has green GitHub checks. | Validating; review and merge pending |
| `IMP-007` | CI proved behavior but did not automatically catch basic source defects or coverage loss. | Run Ruff checks and enforce an initial 80% test-coverage floor in CI. | Local lint passes; full suite establishes 84% baseline before the floor is enabled. | Retained |
| `IMP-008` | Excel lock files appeared as recurring working-tree noise while the controlling workbook was open. | Ignore `~$*.xlsx` temporary files without ignoring the workbook itself. | Clean status while `gantt.xlsx` is open. | Retained |

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
