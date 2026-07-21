# P2.3 Completion and v0.3.0 Claim Boundary

**Date:** 2026-07-21

**Decision authority:** D-107 and D-108, accepted by the project owner

**Integrated implementation baseline:** `main` commit
`69c0d1b4cfe49323c8dc629584abb3f8fdc1ccd7`

## Decision

P2.3 is complete for the v0.3.0 Package Assurance Pilot.

The pilot release claim is limited to the eight accepted mandatory gates, the
eleven implemented relationship checks, the accepted result-state router, and
the four immutable audit outputs. P2.3 completion does not mean that every
potential mechanical package comparison is implemented.

The six authority/source gaps below are explicitly deferred. They are excluded
from v0.3.0 acceptance, benchmark scoring, release claims, demonstrations, and
service language unless a later reviewed release adds the missing source and
authority contracts.

## Proven Relationship Scope

The accepted eleven-check sequence is:

1. drawing register/metadata revision agreement;
2. required drawing-metadata presence;
3. drawing-metadata register authority;
4. drawing metadata/file-reference agreement;
5. drawing register/manifest file reciprocity;
6. BOM item/equipment manifest reciprocity;
7. BOM equipment presence in drawing metadata;
8. equipment datasheet authority presence;
9. BOM/equipment datasheet association;
10. equipment/datasheet manifest reciprocity; and
11. specification revision-history agreement.

These checks retain their accepted IDs, authority prerequisites, result states,
hold behavior, evidence contracts, and deterministic ordering. No new check or
engineering interpretation is created by this closeout.

## Deferred Claims

| Deferred claim | v0.3.0 disposition | Re-entry requirement |
| --- | --- | --- |
| Cross-document quantity reconciliation | Deferred; P2.1 may validate BOM quantity structure only. | Name a controlled comparison source and exact authority rule. |
| Part/material identifier reconciliation | Deferred; no cross-document agreement claim. | Define the compared source, normalization, and conflict behavior. |
| BOM item-to-drawing agreement | Deferred; existing checks do not make the BOM `drawing_number` authoritative. | Add and review an exact authority rule for that field. |
| Equipment-to-specification association | Deferred; `AUTH-SPEC-001` controls datasheet association only. | Add a separate exact specification-association rule. |
| Datasheet revision-history agreement | Deferred; `AUTH-SPEC-003` controls specification revision only. | Add a separate exact datasheet-revision rule. |
| Controlled technical-value compliance | Deferred for pressure, material, power, voltage, frequency, enclosure, units, tolerances, and applicability. | Freeze a versioned value, unit, tolerance, applicability, and authority contract. |

Deferral is a scope decision, not evidence that the underlying package values
are correct. Missing support must remain visible in limitations and may not be
reported as a pass.

## Allowed v0.3.0 Claim

The bounded claim is:

> On the named benchmark revision and evaluator commit, the structured package
> audit executed eight mandatory gates and eleven deterministic relationship
> checks, produced the accepted result and report set, and matched the frozen
> scenario expectations reported for each benchmark split.

Every use of that claim must name the evaluator commit, benchmark revision,
development and held-out counts separately, observed false positives and false
negatives, contamination status, and known limitations.

The project must not claim complete package correctness, engineering approval,
code or standards compliance, autonomous release authority, real-world error
rates, production readiness across arbitrary packages, or coverage of any
deferred comparison.

## P2.3 Completion Criteria

P2.3 is complete because:

- checks 6 through 11 were each defined, implemented, reviewed, and integrated;
- the clean development package passes all eight gates and eleven checks;
- each new relationship check has an isolated controlled-fault proof;
- canonical result, issue registers, readiness summary, terminal behavior, and
  CLI exits agree;
- full regression, coverage, repository validation, Ruff, frozen baseline, and
  portfolio demo verification passed at the check-11 review baseline;
- protected fixtures, schemas, authority maps, goldens, public packages,
  historical results, and v0.2.0 behavior were unchanged; and
- unsupported claims are explicitly excluded rather than inferred.

## P4 Authorization Boundary

P4.1 is authorized next to add benchmark regression and fault-injection
coverage using the accepted development family and temporary/generated package
copies. It may define and test the benchmark runner, exact oracle comparison,
scenario inventory, repeated-run normalization, failure preservation, and
reporting contract.

P4.1 must not execute protected held-out package semantics or expose protected
held-out expected results to evaluator logic. The evaluator commit, development
benchmark revision, runner behavior, limitations, and stop conditions must be
frozen before P4.2.

P4.2 is a separate one-way evaluation gate. It will execute the frozen
development and held-out scenario sets, preserve first raw runs, compare results
only after evaluation, report the splits separately, and stop before any rule
tuning or protected-asset change.

## Acceptance Record

The project owner accepted check 11, directed the six unsupported claims to be
deferred, approved the eleven-check v0.3.0 claim boundary, and authorized P4
startup on 2026-07-21. This record closes D-107, records D-108 as accepted, and
opens P4.1 only.
