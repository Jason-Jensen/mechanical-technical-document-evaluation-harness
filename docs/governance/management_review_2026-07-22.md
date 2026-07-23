# AI Management System Management Review - 2026-07-22

**Review ID:** AIMS-MR-001

**Authority:** Project owner directive D-115

**Scope:** Initial adoption of a highest-level AI quality and safety governance
system

## Inputs Reviewed

- project purpose, engineering boundary, and current v0.3.0 scope;
- D-113 execution, independent verification, protected comparison, and release
  hold;
- existing improvement loop and twenty-eight retained lessons;
- official public descriptions of ISO/IEC 42001:2023 and ISO/IEC 23894:2023;
- NIST AI RMF 1.0 and the NIST Generative AI Profile;
- current use of generative AI in project work; and
- deferred future model, extraction, agent, API, database, and frontend work.

## Decisions

1. Adopt `AIMS-POL-001` as the highest-level repository quality and safety
   policy below applicable obligations.
2. Manage the current project through a documented Plan-Do-Check-Act cycle.
3. Require machine-valid inventory, risks, controls, evidence, objectives,
   nonconformities, audits, and release state in CI.
4. Preserve qualified human engineering judgment and project-owner release
   authority.
5. At this review, keep D-114 pending as a separate corrective-action decision; this review
   does not authorize a held-out rerun, new family, publication fix, or P4.3.
6. Reject certification, conformity, legal-compliance, or guaranteed-safety
   claims without licensed standards and competent independent assessment.
7. Do not commit or reproduce the supplied ISO PDF because its visible license
   belongs to another purchaser.

## Resources and Actions

- Maintain the governance validator and focused tests as required CI controls.
- Review the risk and control record before each release candidate and after
  material change or incident.
- Review the source baseline when NIST publishes its announced AI RMF update.
- Expand supplier, privacy, security, competence, and stakeholder records before
  external or sensitive-data operation.
- Treat every future model-based capability as a new assessed system.
- Continue the existing improvement register rather than creating a competing
  lessons process.

## Outcome

The AI management system is approved for internal operation. At this review,
the current product remained release-held and the next owner decision was
D-114.

## Follow-Up

The owner subsequently accepted D-114. The publication-layer corrective action
is verified and `NC-001` is closed. The product remains release-held by
`AIR-003`; proposed D-116 is the next owner decision and does not authorize a
semantic run by itself.
