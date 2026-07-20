# Authorized Structured-Package Trial - Decision Gate

**Status:** Two co-equal public-package intakes complete; combined fit-gap ready for review
**WBS:** P2.3 practical-use trial gate
**Product baseline:** PR #45 integrated at exact `main` commit `273c36a`
**Scope:** Two independent, development-only public mechanical packages

## Executive Purpose

Use realistic packages to learn whether the current audit is useful in an
actual review workflow. The trial should expose preparation burden, confusing
evidence, incorrect findings, missed conditions, and missing source authority
before more checks are built.

This is a product-learning exercise. It is not a benchmark, an engineering
approval, a production-readiness claim, or proof of real-world accuracy.

## Source Authorization Rule

For each practical-use package, select one of these source types:

1. **An authorized, sanitized package from a real past project (recommended).**
   This gives the strongest practical learning.
2. **A public mechanical package.** This is suitable when project data cannot
   be shared, provided its use and retention are permitted.
3. **A newly authored realistic synthetic package.** This is the fallback and
   provides weaker real-world evidence.

Before work starts, the CEO must identify the files or directory and confirm
that the project may use the material. Confidential, personal, export-controlled,
client-owned, or otherwise restricted content must be removed or explicitly
authorized.

The default data rule is:

- original source material stays outside Git;
- analysis uses a working copy;
- missing values are recorded, never invented;
- only an explicitly approved sanitized package and approved evidence may be
  committed; and
- raw or derived material is deleted from the working area only with separate
  approval.

## What the Current Product Can Use

The v0.3.0 audit accepts structured JSON and CSV records for:

- package manifest;
- drawing register and drawing metadata;
- BOM or equipment list;
- datasheet and specification metadata;
- revision history; and
- package-specific authority rules.

Referenced PDFs, drawings, spreadsheets, and models may remain controlled
package files, but the current product checks only their declared paths,
identifiers, and metadata. It does not read their engineering content.

If the starting package is not already in this structure, the first trial stage
is a fit-and-gap assessment. Conversion is documented as a manual preparation
step and is not presented as automated extraction.

## Trial Protocol

Each authorized package follows the same steps independently. Complete both
intakes before comparing them or proposing transformation.

1. **Authorize and inventory.** Confirm permitted use and list available source
   files without changing them.
2. **Assess fit.** Identify which required records exist, which are absent, and
   which authority decisions are unknown.
3. **Prepare a sanitized working copy.** Record every mapping, omission, and
   transformation. Do not infer engineering facts.
4. **Run the accepted audit unchanged.** Preserve the immutable result, issue
   register, readiness summary, and command outcome.
5. **Review with a qualified person.** Mark each finding accepted, overturned,
   unclear, or outside scope, and record important conditions the audit missed.
6. **Improve deliberately.** Convert each useful lesson into a proposed
   contract, test, check, evidence, or operating change. Review those proposals
   before implementation.

## Success Measures

No time tracking is required. The trial records:

- required source families available and missing;
- number and type of manual transformations;
- assumptions refused because authority was unavailable;
- findings accepted, overturned, unclear, or outside scope;
- important conditions found by the human but missed by the audit;
- evidence links the reviewer could or could not verify;
- repeated manual steps that may justify later automation; and
- product or authority gaps exposed by the package.

The trial succeeds if it produces honest learning and a clear next decision,
even if the package cannot be fully audited.

## Stop Conditions

Stop and return for review if:

- authorization or confidentiality is uncertain;
- sanitization would remove the relationships needed for a meaningful trial;
- required facts would have to be invented;
- the package would require PDF/CAD content extraction to proceed;
- a current contract or authority rule must change;
- protected benchmark assets would need to change; or
- the reviewer cannot independently verify the generated evidence.

## Outputs

The trial will produce:

- an intake and authorization record;
- a structured fit-and-gap summary;
- a transformation and assumption log;
- one preserved audit run per package when its entry gate is satisfied;
- a reviewer disposition record;
- an improvement-loop summary; and
- a continue, revise, or stop recommendation.

Checks 8-11, held-out execution, benchmark changes, multimodal extraction, API,
database, RAG, agent, and frontend work remain blocked during this trial.

## CEO Approval Record

To authorize the trial, provide:

1. each selected package location or attached file set;
2. confirmation that each material set may be used for this local development trial;
3. confirmation that sensitive material has been removed, or instructions for
   what must remain outside Git and outside retained evidence; and
4. the person who can judge whether findings are useful and factually grounded.

The CEO first authorized Precious Plastic Shredder Basic 3.3 on 2026-07-20.
That intake stopped without a download because the official source requires an
account the user cannot create or access. The project will not bypass that
control. The CEO then authorized NASA/JPL Open Source Rover v4.0.0 and
OpenFlexure Microscope v7.0.0-beta5 as co-equal trials. The CEO will review
product usefulness. Factual claims must remain traceable to publisher source
material; these trials do not provide engineering approval.

## Public-Package Research

The CEO reported that no private package is available and authorized public
package research. The reviewed shortlist and the superseding access decision
are recorded in `public_trial_package_shortlist_2026-07-20.md`.

The active trials are:

1. NASA/JPL Open Source Rover v4.0.0; and
2. OpenFlexure Microscope v7.0.0-beta5.

Neither package is ranked above the other. Both use identical controls:
official release source and license verification, separate local Git-ignored
storage, preservation of the untouched archive, SHA-256 hashing, file-level
inventory, source-family and authority-gap assessment, and no engineering-
content extraction. The combined fit-gap assessment must be reviewed before
either package is transformed or audited.

The completed evidence and recommended controlled-mapping gate are recorded in
`dual_public_package_intake_fit_gap_2026-07-20.md`.
