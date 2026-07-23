# AI Management System Internal Audit - 2026-07-22

**Audit ID:** AIMS-AUD-001

**Scope:** Initial AI management and quality-control system implementation

**Criteria:** Project policy, machine-readable governance schema, lifecycle
gates, evidence requirements, accepted project controls, and public ISO/NIST
management-system guidance

**Independence limitation:** This is an internal project audit performed during
system implementation. It is not independent certification or external
assurance.

## Evidence Sampled

- AI management policy and quality-control manual;
- AI system inventory, risk register, controls, objectives, and release state;
- current P4.2 D-113 failed-run record and D-114 hold;
- project authority hierarchy and engineering boundary;
- improvement register and prior management review;
- automated governance validator, tests, and CI integration; and
- official public ISO and NIST source records listed in the gap assessment.

## Results

### Conforming internal controls

- scope, intended use, roles, human authority, and prohibited uses are defined;
- current, adjacent, and future AI systems are inventoried;
- impacts and risks identify affected parties, treatments, evidence, and review
  triggers;
- mandatory lifecycle gates fail closed;
- control and evidence cross-references are machine validated;
- release status reflects open risk and nonconformity rather than passing on
  documentation alone;
- engineering sign-off, held-out custody, and protected evidence boundaries are
  retained; and
- continual improvement links failures to preventive controls and proof.

### Nonconformity

At the time of this audit, `NC-001` remained open: D-113 consumed the external benchmark family after all
eight evaluator invocations failed in atomic output publication. No semantic
benchmark result exists. The release hold and no-rerun boundary are correct.

### Opportunities for improvement

- obtain an organization-authorized standard only if formal conformity work is
  justified;
- formalize supplier, model-change, privacy, and security review before using
  confidential data or production AI;
- add external stakeholder, accessibility, and fairness evidence before a real
  service pilot; and
- add model monitoring only when a model-based product capability is approved.

## Audit Conclusion

The internal management system is implemented and suitable to control the
current repository workflow. It is not release-ready and does not establish
ISO/IEC 42001 conformity. The normal governance validator should pass; its
release-ready mode should fail until `NC-001` and every mandatory hold are
closed through accepted evidence.

## Corrective-Action Follow-Up

After this audit, the owner accepted D-114. Development-only reproduction
identified the internal staging path length as the root cause. The corrected
publication layer, exact diagnostics, fallback marker, and bounded four-output
sentinel verify corrective and preventive action, so `NC-001` is closed.

Release-ready mode must still fail on `AIR-003` and pending D-116 because no
comparable independent semantic benchmark result exists.
