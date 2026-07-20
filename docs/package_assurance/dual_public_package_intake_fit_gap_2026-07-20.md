# Dual Public-Package Intake and Fit-Gap Assessment

**Status:** Ready for CEO review
**Date:** 2026-07-20
**WBS:** P2.3 dual public-package intake
**Branch:** `codex/p2.3-dual-public-package-intake`
**Packages:** NASA/JPL Open Source Rover v4.0.0 and OpenFlexure Microscope v7.0.0-beta5

## Decision Requested

Accept both controlled intakes and authorize one next block to define a manual,
source-to-audit mapping for each package. Keep the packages co-equal and keep
all source material outside Git. Do not transform either package or run either
audit until both mapping definitions are reviewed.

## Executive Result

Both packages are usable for product learning, but neither is directly usable
by the current structured audit.

- NASA/JPL is the stronger test of a conventional COTS assembly and parts-list
  workflow. It has several tabular BOMs, many native model files, and extensive
  build documentation, but it mixes current and historical subsystem material
  and has no formal drawing register or authority map.
- OpenFlexure is the stronger test of a generated, configuration-dependent
  hardware release. It has source models, generated STL files, declarative part
  specifications, an Open Know-How manifest, and a release changelog, but it
  does not use conventional drawing or equipment-register structures.

The useful conclusion is not that one package wins. Together they expose two
important customer patterns that the product must eventually handle: curated
assembly repositories and generated parametric releases.

## Equal Intake Protocol

The same controls were applied to both packages:

1. use one official, version-specific source archive;
2. record the publisher release and license sources;
3. store the archive in a separate local Git-ignored directory;
4. preserve the downloaded archive unchanged and calculate SHA-256;
5. validate the ZIP and inventory its central-directory metadata;
6. inspect only filenames, file types, plain-text documentation, and structured
   data needed to determine source fit;
7. do not open or interpret PDF or CAD engineering content;
8. do not transform source records, create an audit package, change schemas or
   rules, or run the audit; and
9. compare the completed evidence without ranking either package.

Raw archives and inventories remain under `scratch/public-package-intake/` and
are ignored by Git. Third-party source files are not included in this change.

## Preserved Intake Evidence

| Evidence | NASA/JPL Open Source Rover | OpenFlexure Microscope |
|---|---|---|
| Official release | https://github.com/nasa-jpl/open-source-rover/releases/tag/v4.0.0 | https://gitlab.com/openflexure/openflexure-microscope/-/releases/v7.0.0-beta5 |
| Official archive | https://github.com/nasa-jpl/open-source-rover/archive/refs/tags/v4.0.0.zip | https://build.openflexure.org/openflexure-microscope/v7.0.0-beta5/source.zip |
| Archive size | 403,500,249 bytes | 62,624,351 bytes |
| SHA-256 | `8bcf4985904cdbabcd0b48c77e68aac66ea069947aad60fa7bc50ac283e77a7b` | `aecf6640c4c99538a281abaedbf75c5464543159d8a5ed4b729830b234939a78` |
| ZIP entries | 998 | 463 |
| Files inventoried | 897 | 423 |
| Uncompressed file bytes | 480,016,607 | 73,563,477 |
| License evidence | `LICENSE.txt`: Apache License 2.0 | `License`: CERN-OHL-S-2.0; `okh.yml` declares GPL-3.0 for documentation and software |
| Inventory method | ZIP metadata; no PDF/CAD content opened | ZIP metadata; no PDF/CAD content opened |

The first NASA/JPL working-copy extraction attempt was stopped by Windows path
length handling. The incomplete attempt is preserved locally and was excluded
from the inventory evidence. The complete archive remained valid and unchanged.
Both final inventories were therefore generated directly from ZIP metadata.

## Source-Family Findings

### NASA/JPL

- 12 structured or tabular files were identified: eight CSV files, one XLSX,
  one XML, one YAML, and one YML.
- Filename evidence identified 17 BOM or parts-list-related paths, including
  `parts_list/parts_list.csv`, `parts_list/digikey_bom.csv`, and several PCB
  BOM versions.
- The main mechanical parts-list CSV declares assembly, part number, name,
  link, cost, quantity, and assembly-multiplier fields.
- A PCB-generated CSV includes a `Datasheet` column, but there is no package
  datasheet register.
- 103 CAD or model files were identified, including STEP, STL, DXF, SolidWorks
  part, and SolidWorks assembly formats. No CAD geometry was opened.
- 95 paths matched build or assembly documentation signals, and the mechanical
  documentation links to an external Onshape model.
- No explicit drawing register, drawing-metadata dataset, package authority
  map, package manifest, specification register, or package-level revision
  history was identified by filename.
- Historical and current-looking folders coexist, including `PCB_old` and
  versioned PCB BOM directories. The publisher does not provide the authority
  hierarchy required to decide which of these are release-controlling inputs.

### OpenFlexure

- Five YAML/YML files provide structured release metadata, build
  configuration, mechanical part definitions, electronic part definitions,
  and CI configuration.
- `okh.yml` is a useful package-level Open Know-How manifest, but it is not the
  accepted audit manifest and identifies version `7.0` rather than the full
  release label `v7.0.0-beta5`.
- `docs/parts/mechanical.yml` and `docs/parts/electronics.yml` define named
  parts with descriptions, specifications, suppliers, and supplier part
  numbers. They are source catalogs, not a released per-configuration BOM.
- The source archive contains 146 OpenSCAD files, 25 STL files, and six DXF
  files. No model geometry was opened.
- `CHANGELOG.md` contains a specific `v7.0.0-beta5` section, giving this package
  stronger package-level revision evidence than NASA/JPL.
- The official release documentation offers generated build instructions,
  configuration-specific BOMs, and a dependency-hash file, but the source
  archive itself contains no CSV BOM.
- No explicit drawing register, drawing-metadata dataset, equipment register,
  datasheet register, accepted authority map, or accepted audit manifest was
  identified.
- Hardware, documentation, and software have different declared license
  scopes. Any retained or transformed working package must preserve those
  distinctions; this assessment is not a legal opinion.

## Current Audit Fit

| Current required source | NASA/JPL fit | OpenFlexure fit | Gap before audit |
|---|---|---|---|
| Package manifest | Missing | Open Know-How metadata exists, but not the accepted contract | Create a documented trial manifest mapping; do not change the accepted schema yet |
| Drawing register | Missing | Missing and not natural to the project | Record absence; do not invent drawing authority |
| Drawing metadata | Native models exist, but no accepted metadata dataset | Source and generated models exist, but no accepted metadata dataset | Define which filenames may be declared without interpreting geometry |
| BOM/equipment list | Several CSV BOM and parts-list candidates | Declarative part catalogs and generated BOM capability | Select a bounded release configuration and record the source choice |
| Datasheet metadata | Some PCB BOM rows can reference datasheets | No package datasheet register identified | Missing authority must remain explicit |
| Specification metadata | No package specification register identified | Structured per-part `Specs` fields exist | Map only publisher-declared fields and preserve source locators |
| Revision history | Release tag and subsystem versions; no package changelog identified | Release tag, changelog, and external dependency hashes | Define package versus subsystem revision rules |
| Authority map | Missing | Missing | Human decision required before deterministic comparisons |

## Main Risks

1. **False authority:** A convenient CSV, YAML file, or folder name is not proof
   that the publisher considers it authoritative.
2. **Configuration ambiguity:** OpenFlexure can generate multiple legitimate
   microscope configurations; one exact configuration must be selected before
   quantities or required files can be tested.
3. **Mixed revisions:** NASA/JPL includes old and versioned subsystem material
   inside one tagged source archive; the current audit cannot choose among it
   without a reviewed authority decision.
4. **Concept mismatch:** Neither package is a conventional controlled drawing
   release. Changing the evaluator to make them pass would weaken the product
   and distort the trial.
5. **Preparation burden:** Both require manual mapping before the existing
   audit can run. That work must remain traceable and reversible.

## Recommended Next Gate

Proceed with both packages to a **controlled manual mapping definition**.

The next block should:

1. select one bounded release configuration for each package;
2. define exact source-to-manifest mappings without changing source files;
3. identify every required audit field as direct, derived, missing, or not
   applicable;
4. define package-specific authority choices for CEO review;
5. create one shared transformation-and-assumption log format;
6. stop wherever a value or authority would have to be invented; and
7. return both mapping definitions for review before creating working audit
   packages or running `audit-package`.

Do not add a generic loader, YAML support, PDF/CAD extraction, or new evaluator
rules during that block. Repeated preparation pain should be recorded as
future product evidence, not solved prematurely inside this trial.

## Verification

- both downloaded archives reopened as valid ZIP files and their SHA-256
  values were recomputed before reporting;
- both ZIP-native inventories completed from the same script and method;
- 27 repository-focused tests passed;
- the full regression suite passed 283 tests with one expected Windows symlink
  skip;
- all five repository cases passed validation;
- Ruff passed;
- the Gantt formula-error scan found zero matches; and
- all six controlling workbook sheets were visually inspected after the final
  update.

The first targeted Pytest attempts encountered permissions and a missing parent
directory in the default/isolated temporary locations. No product assertion
failed. The final focused and full runs used fresh Git-ignored temp directories
with the Pytest cache disabled and passed.

## Review Boundary

Acceptance of this assessment would confirm only that both source intakes are
complete and that controlled mapping design may begin. It would not approve
engineering content, license compliance, a source-authority conclusion, an
audit result, or product accuracy.
