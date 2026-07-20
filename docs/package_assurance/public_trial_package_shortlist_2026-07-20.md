# Public Structured-Package Trial Shortlist

**Status:** Superseded operationally; NASA/JPL and OpenFlexure co-equal intakes complete
**Date:** 2026-07-20
**Baseline:** PR #46 integrated at exact `main` commit `361cc77`
**Research boundary:** Original shortlist research; the active intake decision is recorded below

## Superseding Operational Decision

The Precious Plastic trial stopped on 2026-07-20 without a download. Its
official package source requires an account, and the user cannot create or
access one. No workaround or authentication bypass will be attempted.

NASA/JPL Open Source Rover v4.0.0 and OpenFlexure Microscope v7.0.0-beta5 now
proceed as co-equal trials. The original ranking remains below as historical
research, but it no longer controls execution. Both active packages must use
the same official-source, license, preservation, hashing, inventory,
source-family, authority-gap, and evidence protocol. Complete both fit-gap
assessments before proposing any transformation or audit run.

Both controlled intakes are now complete. Their hashes, inventories, fit gaps,
and combined recommendation are recorded in
`dual_public_package_intake_fit_gap_2026-07-20.md`.

## Original Recommendation (Superseded)

Select **Precious Plastic Shredder Basic 3.3** for the first practical-use
trial.

**Original CEO decision, 2026-07-20:** Accepted, then superseded after official
Precious Plastic access proved unavailable.

It is the closest of the reviewed public options to the package this product is
intended to audit. The official machine package is described as containing 3D
CAD, laser-cut DXF files, blueprint PDFs, schematics, a BOM, and supporting
material for one bounded fabrication project. That gives us meaningful
relationships among parts, drawings, controlled files, and equipment without
starting with an enormous system.

Its imperfect document control is also useful. The first trial should expose
where a real public package lacks formal drawing registers, revisions, or
authority declarations. Those gaps are business learning, not data to invent.

The publisher states that its content is licensed under Creative Commons
Attribution-ShareAlike 4.0. Before download, the exact package link, license,
attribution, and access conditions will be captured in the intake record.

## Three Candidates

| Rank | Candidate | Why it is useful | Main limitation | Fit |
|---:|---|---|---|---|
| 1 | Precious Plastic Shredder Basic 3.3 | One manufacturing-oriented package with CAD, DXF, blueprints, schematics, BOM, and a machine manual | We should expect weak formal revision and source-authority records | Best match to the intended commercial workflow |
| 2 | NASA/JPL Open Source Rover v4.0.0 | Mature public project with a released version, mechanical subassemblies, Onshape CAD, structured parts-list CSV files, assembly documentation, and Apache 2.0 licensing | More COTS assembly guide than controlled drawing-release package | Best provenance and easiest structured intake |
| 3 | OpenFlexure Microscope v7.0.0-beta5 | Versioned source, generated STL release assets, downloadable CSV BOM, assembly instructions, file hashes between revisions, and CERN-OHL-S-2.0 licensing | Generated 3D-print project with few conventional engineering drawings or equipment tags | Best reproducibility and revision experiment |

## Source Evidence

### Precious Plastic Shredder Basic 3.3

- Package page: https://community.preciousplastic.com/library/shr---33-
- License statement: https://www.preciousplastic.com/about/open-source
- The official package page lists `.step`, `.f3d`, `.dxf`, blueprint `.pdf`,
  schematics, BOM, and related manufacturing files.
- The machine is identified as version 3.3 and is presented as a buildable
  metalworking project.
- Precious Plastic states that its content is shared under CC BY-SA 4.0.

### NASA/JPL Open Source Rover v4.0.0

- Repository: https://github.com/nasa-jpl/open-source-rover
- Release: https://github.com/nasa-jpl/open-source-rover/releases/tag/v4.0.0
- Mechanical tree:
  https://github.com/nasa-jpl/open-source-rover/tree/master/mechanical
- Parts list:
  https://github.com/nasa-jpl/open-source-rover/tree/master/parts_list
- The repository contains mechanical subassembly documentation,
  `parts_list.csv`, `digikey_bom.csv`, an Onshape model, and a stable v4.0.0
  release. The repository states Apache 2.0 licensing.

### OpenFlexure Microscope v7.0.0-beta5

- Source repository:
  https://gitlab.com/openflexure/openflexure-microscope/-/tree/master
- Releases:
  https://gitlab.com/openflexure/openflexure-microscope/-/releases
- Release documentation:
  https://build.openflexure.org/openflexure-microscope/v7.0.0-beta5/
- Example BOM:
  https://build.openflexure.org/openflexure-microscope/v7.0.0-beta5/high_res_microscope_BOM.html
- The project publishes assembly instructions, release-specific source and STL
  assets, CSV BOM downloads, and a hash file for identifying STL changes
  between revisions. The source declares CERN-OHL-S-2.0 for hardware and
  GPL-3.0 for documentation and software.

## Original Decision Logic

The first trial should optimize for learning about the intended customer
workflow, not for making the current evaluator look successful.

- Precious Plastic offers the strongest drawing/BOM/fabrication relationships.
- JPL offers the cleanest conventional repository and release provenance.
- OpenFlexure offers the strongest automated release and revision evidence.

For that reason, Precious Plastic ranks first even though it will require more
careful intake. The likely authority and revision gaps are exactly the kind of
friction the trial is meant to expose.

## Current Entry Decision

CEO approval authorizes these actions for both active packages under the same
protocol:

1. verify and record the official download, license, and attribution;
2. download the package to a local, Git-ignored intake area;
3. hash and inventory the untouched source files; and
4. produce a source-fit and authority-gap report before any transformation.

It does not authorize engineering approval, safety or compliance conclusions,
PDF/CAD engineering-content extraction, transformation, an audit run, schema
changes, new evaluator rules, benchmark changes, or publication of third-party
source files. The combined fit-gap assessment must be reviewed first.
