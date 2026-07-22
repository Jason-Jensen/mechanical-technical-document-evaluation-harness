# AI Management and Quality Governance

This directory contains the project's highest-level internal controls for the
responsible development and use of AI-enabled work. These controls apply above
the project schedule, feature definitions, and implementation preferences.

## Authority Order

1. applicable law, safety obligations, privacy, security, and intellectual
   property restrictions;
2. `ai_management_system_policy_v0.3.0.md`;
3. the machine-readable `governance/ai_management_system.json` record and its
   mandatory release gates;
4. `gantt.xlsx` for active work, decisions, risks, evidence, and next action;
5. accepted product contracts and technical specifications; and
6. implementation plans and convenience.

A lower-level instruction cannot waive a higher-level hold. When requirements
conflict or evidence is incomplete, work stops in the conservative state and a
qualified human decides what may continue.

## Controlled Documents

- `ai_management_system_policy_v0.3.0.md`: binding policy and stop conditions.
- `ai_quality_control_manual_v0.3.0.md`: operating processes and lifecycle
  gates.
- `ai_impact_assessment_v0.3.0.md`: current-system impact assessment.
- `iso_iec_42001_alignment_and_gap_assessment_v0.3.0.md`: alignment and honest
  limitations.
- `internal_audit_2026-07-22.md`: initial internal audit.
- `management_review_2026-07-22.md`: initial management review and decisions.

The machine-readable source of current systems, risks, controls, objectives,
nonconformities, and release status is
`governance/ai_management_system.json`. Validate it with:

```powershell
.\.venv\Scripts\python.exe -m mech_eval_harness.ai_governance .
```

Add `--require-release-ready` only at a release gate. It intentionally fails
while any mandatory hold remains open.

## Standards Boundary

This is an original internal management system informed by official public
descriptions of ISO/IEC 42001:2023, ISO/IEC 23894:2023, NIST AI RMF 1.0, and the
NIST Generative AI Profile. It is not a reproduction of those publications and
does not establish certification or formal conformity.

Formal clause-by-clause assessment requires a properly licensed copy of the
standard, competent legal and security review where applicable, and an
independent certification or assurance process.
