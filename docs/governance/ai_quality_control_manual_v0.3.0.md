# AI Quality Control Manual

**Manual ID:** AIMS-MAN-001

**Version:** 0.3.0

**Effective date:** 2026-07-22

## 1. Operating Model

The project uses a Plan-Do-Check-Act management cycle:

- **Plan:** define context, interested parties, intended use, systems, impacts,
  risks, objectives, controls, and acceptance evidence.
- **Do:** perform only authorized work under bounded data, tool, change, and
  human-review controls.
- **Check:** validate records, test behavior, inspect evidence, audit controls,
  measure objectives, and conduct management review.
- **Act:** contain failures, preserve evidence, correct root causes, strengthen
  controls, and reassess residual risk before resuming.

The machine-readable record at `governance/ai_management_system.json` is the
current source for inventory, risks, controls, gates, objectives,
nonconformities, audits, and release status.

## 2. Document Hierarchy

1. AI management system policy;
2. machine-readable management-system record and schema;
3. this manual, impact assessment, audit, and management-review records;
4. controlling Gantt decisions, risks, evidence, and work blocks;
5. accepted product contracts and acceptance plans;
6. code, tests, generated evidence, and reports.

Documents use repository-relative POSIX paths. Accepted history, failed-run
evidence, protected benchmarks, and release records are immutable unless a
reviewed decision expressly authorizes a versioned replacement.

## 3. Lifecycle Gates

Every active or proposed AI use passes these gates in order.

| Gate | Required evidence | Failure action |
|---|---|---|
| `AIG-01` Intended use and ownership | System inventory entry, purpose, owner, users, prohibited uses, lifecycle state | Stop work |
| `AIG-02` Data and rights | Data classes, provenance, authorization, privacy/security/IP handling | Stop access and use |
| `AIG-03` Impact and risk | Impact assessment, affected parties, inherent risk, treatment, residual risk | Hold implementation or use |
| `AIG-04` Design and change control | Accepted requirements, architecture boundaries, versioned change record, rollback or containment plan | Reject change |
| `AIG-05` Verification and evidence | Representative tests, negative tests, reproducibility, failure-state proof, independent review where required | Hold integration |
| `AIG-06` Human review and transparency | Qualified reviewer, limitations, evidence, uncertainty, challenge route | Hold decision or release |
| `AIG-07` Operational readiness | Monitoring, incident response, supplier/change review, output publication, retention | Hold deployment or benchmark |
| `AIG-08` Release and improvement | No unresolved mandatory holds, management decision, audit status, corrective actions | Keep release held |

Passing a later gate cannot cure a failed earlier gate.

## 4. Risk Method

Likelihood and impact are each scored from 1 to 5. The score is their product:

- 1-4: low;
- 5-9: medium;
- 10-16: high; and
- 17-25: critical.

Critical risk is avoided until reduced. High residual risk holds release unless
the project owner records exceptional acceptance with evidence, scope, expiry,
and monitoring. Medium risk requires treatment and review. Low risk is
monitored.

Risk statements identify cause, event, consequence, affected parties, owner,
controls, evidence, residual score, and review trigger. A risk is not controlled
merely because a control is documented; its evidence must exist and be tested.

## 5. AI System Inventory

The inventory includes active generative-AI assistance, the deterministic
assurance component that constrains its outputs, and blocked future model-based
capabilities. New models, providers, autonomous actions, data categories,
deployment contexts, or affected parties require inventory and impact updates
before use.

The deterministic evaluator is explicitly identified as non-AI. This prevents
the project name or workflow from creating a false claim that deterministic
rules are machine intelligence.

## 6. Operational Controls

### 6.1 Work authorization

The Gantt records the active work block and owner decisions. Agents and
implementers may act only within that scope. Scope changes are recorded before
implementation.

### 6.2 Data and source handling

Inputs are classified before use. Unknown or restricted material is not copied
into Git, model prompts, reports, or external services. Source authority and
transformation records distinguish facts, assumptions, and generated content.

### 6.3 Human oversight

AI may draft, analyze, test, or recommend. A qualified human retains approval
for engineering decisions and the project owner retains governance and release
authority. High-risk self-review requires an independent challenge before
acceptance.

### 6.4 Verification

Verification scales with risk and includes focused tests, full regression,
negative and fault-injection cases, schema checks, immutable evidence,
cross-platform CI where stable outputs are claimed, and inspection of actual
artifacts. Held-out evidence remains isolated from producers.

### 6.5 Change and supplier control

Model, provider, prompt, dependency, tool, environment, schema, and policy
changes are treated as configuration changes. Material changes trigger impact
and risk reassessment. Provider-specific behavior is isolated from core
contracts where practical.

### 6.6 Communication

Reports disclose intended use, limitations, evidence, uncertainty, hold state,
and human-review requirements. Complaints, corrections, and contested findings
enter the issue or improvement process and receive a recorded disposition.

## 7. Incidents and Nonconformities

When an incident or nonconformity occurs:

1. stop unsafe or misleading use;
2. preserve logs, inputs, outputs, environment identity, and failure evidence;
3. classify impact and notify the accountable owner;
4. prevent retry, deletion, or tuning when doing so would compromise evidence;
5. identify root cause using non-protected evidence where necessary;
6. implement the smallest effective correction;
7. verify corrective and preventive action; and
8. reassess risk and obtain authorization before resuming.

The D-113 output-publication failure is `NC-001`. It remains open and release
holding until a separately accepted corrective-action decision is completed.

## 8. Monitoring and Objectives

The system measures evidence completeness, human-review coverage, unauthorized
release events, governance validation, false holds, missed conditions,
correction frequency, benchmark comparability, and corrective-action closure.

Metrics never override mandatory holds and are never improved by changing
goldens, hiding failures, weakening criteria, or excluding inconvenient cases.

## 9. Internal Audit and Management Review

An internal audit occurs before each release candidate, after a material
incident or scope change, and at least annually while the project is active.
It checks both documented design and sampled operating evidence.

Management review considers audits, incidents, objective results, stakeholder
feedback, changes in context or obligations, supplier changes, resource needs,
open risks, and improvement opportunities. Decisions and follow-up owners are
recorded in the Gantt and management-system record.

## 10. Release Decision

Normal governance validation confirms that the control system is internally
consistent. It can pass while accurately reporting a release hold. Open risk
holds, nonconformity holds, and pending release decisions all block strict
release readiness.

Release requires this stricter command to pass:

```powershell
.\.venv\Scripts\python.exe -m mech_eval_harness.ai_governance . --require-release-ready
```

The project owner makes the final release decision only after every mandatory
gate and qualified engineering-review requirement is satisfied.
