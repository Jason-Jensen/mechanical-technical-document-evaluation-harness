# ISO/IEC 42001 Alignment and Gap Assessment

**Assessment ID:** AIMS-GAP-001

**Date:** 2026-07-22

**Decision basis:** D-115

## 1. Assessment Boundary

This assessment compares the project's internal controls with the management
system topics publicly described by ISO for ISO/IEC 42001:2023. It supplements
those topics with the operational risk functions in NIST AI RMF 1.0 and the
NIST Generative AI Profile.

This is not a clause-by-clause conformity assessment. The supplied local PDF
was not used as a repository source because it is marked as a single-user copy
licensed to another purchaser and prohibits copying/networking. It is not
committed, quoted, or referenced as project evidence.

Formal conformity assessment requires a properly licensed standard and a
competent independent review. ISO does not certify organizations; certification
is performed by independent certification bodies.

## 2. Authoritative Public Sources

- ISO/IEC 42001:2023 official record and public overview:
  https://www.iso.org/standard/42001
- ISO public explanation of AI management systems:
  https://www.iso.org/artificial-intelligence/ai-management-systems
- ISO/IEC 23894:2023 official risk-management record:
  https://www.iso.org/standard/77304.html
- NIST AI Risk Management Framework:
  https://www.nist.gov/itl/ai-risk-management-framework
- NIST AI RMF Playbook:
  https://airc.nist.gov/airmf-resources/playbook/
- NIST Generative AI Profile:
  https://doi.org/10.6028/NIST.AI.600-1

At this assessment date, NIST states that AI RMF 1.0 is being updated. A
published revision is a mandatory source, impact, risk, and control-review
trigger; this record does not assume version 1.0 will remain current.

ISO publicly describes ISO/IEC 42001 as a management system for establishing,
implementing, maintaining, and continually improving responsible AI governance
through risk and opportunity management. NIST provides voluntary operational
practices organized around Govern, Map, Measure, and Manage. The project uses
the two as complementary references, not interchangeable certifications.

## 3. Management-System Alignment

| Management-system area | Project implementation | Status |
|---|---|---|
| Organizational context | Defined scope, interested parties, current and future systems, engineering boundary, and explicit exclusions | Implemented for pilot scope |
| Leadership | Owner-approved policy, named accountability, human final authority, and non-waivable holds | Implemented |
| Planning | Inventory, impact assessment, scored risk register, treatments, objectives, and change triggers | Implemented; open release risk retained |
| Support | Document control, competence roles, communication rules, evidence retention, CI tooling, and provider-independent controls | Implemented internally; formal competence records need expansion before external operation |
| Operation | Eight lifecycle gates, data/rights checks, source authority, verification, human review, incident response, and change control | Implemented for current repository workflow |
| Performance evaluation | Automated governance validation, tests, objectives, internal audit, management review, and improvement register | Implemented |
| Improvement | Nonconformity process, root-cause requirement, corrective-action proof, and reusable improvement register | Implemented; `NC-001` remains open |

## 4. Project Control Domains

| Project domain | Primary evidence | NIST function |
|---|---|---|
| Policy, scope, and accountability | Policy, roles, Gantt decisions | Govern |
| System inventory and intended use | Machine-readable system records and impact assessment | Govern / Map |
| AI risk and opportunity management | Risk method, register, treatments, release holds | Map / Measure / Manage |
| Data, privacy, rights, and provenance | Data classifications, source authority, authorization stop conditions | Govern / Map / Manage |
| Lifecycle and change control | Lifecycle gates, acceptance contracts, Git review, CI | Govern / Manage |
| Testing, evaluation, validation, and verification | Focused tests, regression, benchmarks, independent review, evidence inspection | Measure / Manage |
| Human oversight and transparency | Engineering boundary, limitations, evidence-linked reports, challenge route | Govern / Map / Manage |
| Supplier and model dependency | Provider-independent core contracts and material-change review | Govern / Map / Manage |
| Monitoring, incidents, and improvement | Objectives, nonconformities, audit, management review, improvement register | Measure / Manage |

## 5. Material Gaps and Actions

### Gap 1: Formal ISO/IEC 42001 conformity is unverified

The project does not possess a project-authorized licensed standard in this
record and has not undergone an independent conformity or certification audit.

**Action:** obtain a properly licensed organizational copy and commission a
qualified gap/conformity review only if certification or a customer requirement
creates sufficient value.

### Gap 2: The external benchmark is not evaluable

The D-113 run preserved valid operational evidence but produced no semantic
outputs because atomic publication failed. This is an open high-severity
nonconformity and release hold.

**Action:** D-114 remains a separate owner decision. No rerun or new held-out
family is authorized by this governance block.

### Gap 3: Supplier and model-provider assurance is lightweight

The project uses provider-independent behavioral controls but does not yet
maintain a formal supplier assurance package, contractual privacy assessment,
or model-change notification process.

**Action:** require those records before client-confidential data or a
production model-dependent service is authorized.

### Gap 4: Production security and privacy systems are not in scope

There is no hosted service, production identity system, client database, or
operational monitoring platform. Current controls prohibit introducing them
without a later gate.

**Action:** perform dedicated security, privacy, threat-model, and incident
response reviews before hosted or sensitive-data use.

### Gap 5: External stakeholder evidence is limited

The current impact assessment is internal and engineering-workflow focused.
It does not include customer, worker, regulator, or affected-community
consultation.

**Action:** collect stakeholder feedback and accessibility/fairness evidence
before a real external pilot or product claim.

### Gap 6: Model monitoring is not yet applicable to the product

The v0.3.0 evaluator is deterministic and calls no AI model. Future extraction
or agent capabilities are blocked, so drift, model-performance, and production
misuse monitoring are not yet executable controls.

**Action:** treat any model-based capability as a new system requiring its own
inventory record, impact assessment, benchmark, monitoring plan, and owner
authorization before implementation.

## 6. Assessment Conclusion

The repository now has an operational internal AI management and quality
control system for its current pilot scope. It is materially stronger than a
policy-only adoption because its inventory, risks, controls, evidence, holds,
audits, and release state are machine checked in CI.

The project remains release-held. It may claim internal high-level alignment
with publicly described ISO/IEC 42001 management-system concepts and NIST AI
RMF practices. It may not claim ISO conformity, certification, independent
assurance, legal compliance, or guaranteed AI safety.
