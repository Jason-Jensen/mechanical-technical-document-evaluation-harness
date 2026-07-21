# OpenFlexure Public-Package Audit Confirmation Review

**Date:** 2026-07-20

**Decision authority:** D-101, accepted by the project owner

**Integrated predecessor:** `main` commit `65c9699b87b5f1b6b0d968eb42c8f1521574b8bb`

**Confirmation branch:** `codex/p2.3-openflexure-public-audit-confirmation`

## Executive Result

The single authorized OpenFlexure Microscope audit completed exactly as
predeclared:

- package state `missing_authoritative_information`;
- release hold `true`;
- CLI exit `3`;
- exactly four schema-valid outputs; and
- one expected `AUTHORITY_REQUIRED_RULE_MISSING` finding.

No second OpenFlexure execution occurred. The result is a successful evaluator
observation, not an approval of the package.

## Controlled Scope

D-101 accepted the NASA/JPL confirmation, closed the original execution defect,
retained its prevention, and authorized one unchanged OpenFlexure audit. Any
unexpected state, exit, output count, schema result, source hash, or mapping-log
change was a mandatory stop.

This block did not authorize package or authority-map edits, expected-state
changes, evaluator changes, check 8, held-out semantic execution, or deferred
PDF/CAD, agent, API, database, RAG, or frontend capabilities.

## Input Integrity

The OpenFlexure inputs matched the accepted D-098 record before execution and
again after complete output review.

| Input | Accepted and post-run value | Result |
| --- | --- | --- |
| Package files | 58 | exact |
| Package tree SHA-256 | `71656da77b469ec3f688b0d936201fbd7be5218edda5a99fc59edcce4a87b29b` | exact |
| Mapping-log records | 620 | exact |
| Mapping-log SHA-256 | `a8ba53e53e2d77ce742264c29aed6938c9ba89150f050e5c66da456aef1b4566` | exact |

The NASA/JPL package also remained at 133 files and tree SHA-256
`52aedc3eaf6753305dbf29d01366f324dd959fe57e14ace6295e62f3801fd8ce`.
Its 1,144-row accepted log remained at SHA-256
`d1d910f02a89830f551e9daf949e48931471320e3764551fe3718a441125a9ec`.

## Single Execution

- Run ID: `RUN-20260721T004222043918Z-254a2eca`
- Package ID: `public-openflexure-microscope-v7.0.0-beta5-high-resolution`
- Stored duration: 34 ms
- Actual CLI exit: `3`
- Audit invocation count under D-101: 1
- Published run directories under the OpenFlexure target: 1
- Unexpected additional public-package audits: 0

The ignored local execution record, stdout, stderr, verification summary,
cross-package comparison, and post-run integrity evidence are preserved under
`scratch/public-package-audit-runs/ofm-beta5-high-res-control-20260720/`. The
four immutable outputs are preserved under the run-ID directory in
`scratch/public-package-audit-runs/ofm-beta5-high-res/`.

## Gate and Check Results

| Control | Result |
| --- | --- |
| Manifest gate | passed |
| Source-inventory gate | passed; 33 structured records |
| Authority gate | failed as expected |
| Package-boundary gate | passed; 51 controlled references |
| Identifier gate | passed; 66 present or required identifiers |
| Duplicate gate | skipped because authority was incomplete |
| Revision gate | skipped because authority was incomplete |
| Evidence gate | skipped because authority was incomplete |
| Seven implemented relationship checks | all skipped against the authority prerequisite |

The identifier gate produced no finding. This confirms the D-099 correction on
a second materially different real package.

## Finding Review

The result contains exactly one finding:

- finding ID `FND-1704FCB7F45DFE73`;
- code `AUTHORITY_REQUIRED_RULE_MISSING`;
- state `missing_authoritative_information`;
- severity `high`;
- release hold `true`;
- review owner `qualified_package_reviewer`; and
- governing control `GATE-PKG-AUTHORITY-001`.

The same eight release-relevant authority rules are absent as in the NASA/JPL
mapping. This is an accepted source limitation, not an evaluator defect. No
`CANONICAL_IDENTIFIER_INVALID` finding is present.

## Output Review

| Output | SHA-256 | Review |
| --- | --- | --- |
| `package_result.json` | `d484c716bbd3b44e97e7de2ca4706b34a3ac3d28b1cf03e32669fe657ef4f50b` | strict JSON and package-result schema passed |
| `issue_register.csv` | `b24db5d4819fa59abd14a2b89c7019beff84520e37161a4d254694ccd39c6c92` | exactly one row matching the canonical finding |
| `issue_register.md` | `6f7e4ee8359256c7842dc7c7d3fb395515c530c19fd9b390f8fac20dbccdd751` | exact deterministic reproduction from the result |
| `release_readiness.md` | `6b0bad123cee35049eae9b34d7f0e60b92fa21531c8021513c15a8a77efae1bf` | exact deterministic reproduction from the result |

The directory contains no extra file or subdirectory. Reports contain no
absolute local path, match the immutable result, require qualified-human review,
and explicitly do not approve release or certify compliance.

## Repository Verification

- focused gate/result/publication/CLI tests: 53 passed;
- full regression suite: 289 passed, 1 expected Windows skip;
- full-suite coverage: 87.57%, above the 80% CI floor;
- repository case validation: 5/5;
- Ruff: passed;
- frozen v0.2.0 baseline replay: 9/9; and
- frozen portfolio demo replay: 2/2.

PR #53 passed both GitHub `Validate and test` checks before merge.

## Dual Public-Package Learning

The two real packages differ materially in source structure and size, yet both
produced the exact predeclared safety outcome:

| Observation | NASA/JPL | OpenFlexure |
| --- | ---: | ---: |
| Package artifacts | 133 | 58 |
| Parsed structured records | 58 | 33 |
| Controlled file references | 126 | 51 |
| Present or required identifiers | 116 | 66 |
| Gates passed / failed / skipped | 4 / 1 / 3 | 4 / 1 / 3 |
| Relationship checks skipped | 7 | 7 |
| Findings | 1 | 1 |
| State / exit | missing authority / 3 | missing authority / 3 |

This proves useful real-world intake, source-boundary enforcement, identifier
handling, state routing, atomic output publication, and honest refusal when
engineering authority is absent.

It does not yet prove real-world relationship-fault detection. Both authority
gates correctly stopped all seven relationship checks. The public trials are
therefore safety and integration evidence, not an end-user effectiveness
benchmark.

## Improvement-Loop Outcome

- `I-004` is closed. The original exit-70 publication defect was corrected,
  synthetically proven, and then confirmed on both public packages.
- `IMP-017` is retained as the permanent optional-blank and canonical-finding
  prevention.
- `IMP-016` remains open. Neither public source supplies the missing engineering
  authority or proves that empty mandatory sources are not applicable.
- New `IMP-018` records that the same semantic gate finding has the same
  `finding_id` in both package results. Current per-package outputs are
  unambiguous because they also carry `package_id`; future multi-package views
  must use `(package_id, finding_id)` as their identity unless a separately
  reviewed contract changes the ID semantics.

## Practical Usefulness Assessment

The project now has a functioning structured audit pipeline and two honest
real-world observations. That is a meaningful reliability milestone, but a
customer would still see only a missing-authority hold on these packages. The
fastest route to a stronger demonstration is:

1. finish accepted structured checks 8-11 on the controlled development
   package, one reviewed slice at a time;
2. run the protected P4 benchmark only after the full structured check set is
   accepted;
3. package a terminal-first demonstration that shows a clean result and several
   evidence-rich seeded faults; and
4. then open a separate gate for PDF/CAD extraction and owner-controlled real
   engineering packages.

Inventing authority for these public repositories would make the demonstration
look better while making the product less trustworthy. That path is rejected.

## Recommended Decision D-102

Accept the OpenFlexure observation as matching D-101. Merge this confirmation,
close the dual public-package observation sequence, close `I-004`, retain
`IMP-017`, keep `IMP-016` open, and adopt `IMP-018` as a multi-package identity
control.

Authorize only P2.3 check 8, `equipment_datasheet_authority_presence`, next.
Require its accepted exact `AUTH-SPEC-001` dependency, missing-authority state,
release hold, evidence contract, full CLI publication proof, and regression
checks. Continue to keep checks 9-11, held-out semantics, public-package reruns,
and deferred multimodal/platform capabilities blocked until their respective
review gates.
