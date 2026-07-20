# Dual Public-Package Preparation Review

**Date:** 2026-07-20  
**WBS:** P2.3 - Public-package practical-use trial  
**Branch:** `codex/p2.3-dual-public-package-preparation`  
**Preparation authority:** accepted D-097  
**Integrated mapping baseline:** PR #49, exact `main` `53e19ad`  
**Review status:** ready for CEO decision; audit execution remains blocked

## Executive Conclusion

Both approved public packages have been prepared as separate, Git-ignored
working packages under the accepted mappings. The preparation is reproducible,
source-linked, and independently verified. No audit was run.

The preparation is fit for its intended next use: testing whether the current
evaluator reports known authority gaps honestly on imperfect public source
material. It is not evidence that either public design is complete, correct,
release-ready, or suitable as a benchmark.

## Prepared Packages

| Package | Structured BOM rows | Preserved source artifacts | Required item relationships | Mapping-log records | Package tree SHA-256 |
| --- | ---: | ---: | ---: | ---: | --- |
| NASA/JPL Open Source Rover v4.0.0, base mechanical rover | 58 | 126 | 58 | 1,144 | `52aedc3eaf6753305dbf29d01366f324dd959fe57e14ace6295e62f3801fd8ce` |
| OpenFlexure Microscope v7.0.0-beta5, high-resolution motorised configuration | 33 | 51 | 33 | 620 | `71656da77b469ec3f688b0d936201fbd7be5218edda5a99fc59edcce4a87b29b` |

Local review roots:

- `scratch/prep/osr-v4`
- `scratch/prep/ofm-beta5-high-res`
- `scratch/prep/independent_preparation_verification.json`

These paths are deliberately excluded from Git. The tracked review records the
controlling hashes and counts without publishing third-party source packages.

## What Was Mapped

### NASA/JPL

- The official v4.0.0 archive remains unchanged at SHA-256
  `8bcf4985904cdbabcd0b48c77e68aac66ea069947aad60fa7bc50ac283e77a7b`.
- All 58 official parts-list rows were preserved in source order.
- Quantity is the exact decimal product of `# req in assy` and
  `assembly multiplier`; the output unit is `each`.
- Publisher part numbers remain exact, including two part numbers intentionally
  shared by different assemblies.
- Every item is linked to accepted package scope `OSR-MECH-001` through one
  required `item_to_equipment` declaration.

### OpenFlexure

- The official beta5 source archive remains unchanged at SHA-256
  `aecf6640c4c99538a281abaedbf75c5464543159d8a5ed4b729830b234939a78`.
- The pinned official high-resolution BOM remains unchanged at SHA-256
  `fd841a6afa91feb5946ce9bc6171ec9bf6b24cbd8a94b3b7e1f22f2ca25bea92`.
- The file named `.csv` is actually tab-delimited and contains repeated
  supplier headings. It has 33 valid data rows, including eight tool rows.
- Quantity text is split into an exact numeric value and its stated unit, such
  as `each`, `cm^2`, `g`, or `drops`.
- A part ID is used only when an exact publisher part number exists. Search
  instructions are not converted into identifiers.
- Every item is linked to accepted package scope `OFM-HR-001` through one
  required `item_to_equipment` declaration.

## What Was Deliberately Not Invented

Both package manifests keep `document_inventory` empty. Their drawing register,
drawing metadata, datasheet/specification metadata, and revision-history
sources are present only in valid empty form because no accepted publisher
authority was identified for those controlled records.

The package-specific authority maps contain only `AUTH-PKG-001`,
`AUTH-PKG-002`, `AUTH-BOM-001`, and `AUTH-BOM-002`. They intentionally omit
eight required authority fields covering drawing identity and revision,
document release requirements, datasheets, operating pressure, specification
revision, and revision status.

OpenFlexure CAD/model files were not selected by guess. The source archive has
many models, but no accepted high-resolution configuration-to-model dependency
set. That gap remains explicit.

## Independent Verification

The preparation was checked by a separate program from the generator. All
checks passed:

- all three pinned source hashes;
- byte-for-byte source-copy hashes and sizes;
- package-manifest schema and path boundaries;
- structured-source loading with zero parse errors;
- all fields across 91 BOM rows;
- all 91 required manifest relationships;
- complete per-field and per-relationship transformation-log coverage;
- exact included and intentionally missing authority sets;
- empty controlled-source representations;
- package tree hashes and file counts; and
- absence of audit run directories and audit result/report files.

Every generated transformation-log row remains `proposed` until this review is
accepted. This is intentional: D-097 accepted the mapping method, not unseen
generated output.

## Expected First-Audit Result

Both packages are expected to route to
`missing_authoritative_information`. This is a useful expected hold, not a
failure of preparation. A different result must be investigated and preserved;
the package or evaluator must not be quietly changed to force the prediction.

## Remaining Limitations

- These are public project artifacts, not controlled industrial release
  packages.
- There is no independent engineering oracle for product correctness.
- Source preservation proves traceability, not publisher document control.
- The working packages do not make PDF, CAD, or free-text content machine
  authoritative.
- Checks 8-11 and all accepted authority/source-gap claims remain unimplemented.
- An audit result is decision support for qualified review, never engineering
  approval.

## Recommended Decision D-098

Accept the two exact prepared package trees and their populated logs. Authorize
one controlled `audit-package` run for each package, executed sequentially but
treated as co-equal trials, with these controls:

1. Verify each package tree hash immediately before execution.
2. Write each run outside its package and preserve all four outputs unchanged.
3. Do not edit sources, mappings, schemas, authority rules, checks, or expected
   states during the run block.
4. Compare actual state, holds, gates, checks, and findings with this review.
5. Stop and triage any unexpected evaluator behavior before implementing a fix
   or expanding scope.

PDF/CAD extraction, held-out semantic execution, check 8 implementation, and
all deferred platform capabilities remain blocked.
