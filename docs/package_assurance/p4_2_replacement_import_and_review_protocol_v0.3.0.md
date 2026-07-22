# P4.2 Replacement Import And Review Protocol

**Version:** 0.3.0

**Date:** 2026-07-21

**Authority:** D-110

## Purpose

This protocol preserves the held-out boundary while an isolated custodian
family is verified, imported, reviewed, and frozen. It applies before the first
semantic execution.

## Roles

- **Authoring custodian:** creates package inputs, protected expected assets,
  and freeze records from the public input bundle only.
- **Independent freeze verifier:** uses a fresh context, reads only the same
  isolated bundle and completed outbound family, and publishes a public
  pass/fail attestation without scenario details.
- **Implementation context:** may inspect public records, verify public hashes,
  copy the exact family tree, and update project controls. It must not open,
  search, render, diff, or summarize protected values or scenario package
  contents.
- **Project owner:** accepts or rejects the freeze package before semantic
  execution.

## Authoring Completion Gate

The authoring custodian must report only:

- output root;
- scenario and file counts;
- structural-check count;
- producer, protected, and complete-family hashes;
- contamination status;
- semantic execution count; and
- blockers.

Scenario names, fault identities, mutations, state mappings, expected values,
and findings remain protected.

## Independent Verification Gate

The verifier checks without evaluator code or execution:

1. input hashes match the authorized input manifest;
2. only authorized paths were read and only `outbound/` was written;
3. every required public and protected artifact exists;
4. the public execution index contains eight opaque tokens and no oracle data;
5. every package manifest validates against the supplied schema;
6. JSON and CSV sources satisfy the public structural profiles;
7. declared source and controlled-file paths exist;
8. clean cross-file relationships satisfy the eleven public check contracts;
9. the protected matrix satisfies aggregate count, state, fault, compound,
   exact-finding, and no-wildcard requirements;
10. public files contain no protected scenario details;
11. per-file, package-tree, producer, protected, and family hashes reproduce;
12. contamination status is `frozen_isolated_pre_execution`;
13. semantic execution count is zero; and
14. owner acceptance remains pending.

The verifier writes a public attestation with check identifiers and pass/fail
only. It must not repeat protected values in its response or public report.

## Implementation-Context Import Rules

The implementation context may read only these outbound public files:

- `ACCESS_BOUNDARY.md`;
- `family_metadata.public.json`;
- `execution_index.public.json`;
- `material_distinction.public.md`;
- `custodian_attestation.public.md`;
- `freeze_record.public.json`; and
- the independent public verification report.

It must not:

- recurse or search the completed family;
- open `protected/` or scenario package files;
- run a semantic validator, evaluator, benchmark, or repository test that
  reads the new family;
- print a content diff for the new family;
- alter any imported family file; or
- expose protected file values in Git, CI, PR, or project-management output.

The exact family root may be copied and staged as an opaque tree. Git status,
commit, and PR summaries must use aggregate counts and public hashes only.

## Import Verification

After opaque copy, verify only:

- source and destination complete-family hashes match the accepted public
  freeze record;
- copied byte and file counts match;
- the independent public verification report hash matches; and
- the prior contaminated family has no diff.

Any mismatch stops the block. Do not repair the imported family in place.

## CI Boundary

Before first-run evidence is preserved, CI for the replacement-freeze PR may
run documentation, lint, frozen v0.2, development benchmark, and repository
checks only when they do not enumerate or load the new replacement root.
Protected replacement fixture tests and semantic package execution are
prohibited.

## Freeze Review Package

The owner review contains:

- public authoring contract and input manifest;
- public family metadata and execution index;
- public material-distinction and access attestations;
- public freeze record;
- independent public verification report;
- exact integration branch and commit;
- unchanged prior-family evidence; and
- a proposed first-run decision.

Owner acceptance authorizes only the separately defined first-run protocol. It
does not authorize tuning, reruns, fixture repair, or release claims.

## Failure Rule

If authoring, verification, import, or review exposes protected values to the
implementation context, changes evaluator behavior, runs a scenario, or
produces a hash mismatch, preserve the evidence, classify the replacement as
contaminated, and start again with a materially distinct family and fresh
isolated context.
