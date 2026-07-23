# AI Management System Policy

**Policy ID:** AIMS-POL-001

**Version:** 0.3.0

**Effective date:** 2026-07-22

**Owner authority:** D-115

**Status:** Adopted for internal governance; release held

## 1. Purpose

This policy governs every use of AI in developing, evaluating, operating, or
supporting the Mechanical Engineering Workflow Assurance Platform. Its purpose
is to reduce avoidable harm, preserve human accountability, and make every
material AI decision traceable to evidence.

No management system can guarantee that AI is safe. This policy creates
mandatory controls, conservative stop conditions, and continual improvement so
that safety claims are never substituted for proof.

## 2. Scope

This policy applies to:

- generative-AI assistance used for planning, coding, research, analysis,
  testing, documentation, and project control;
- agents, models, tools, and third-party AI services used by the project;
- the deterministic package-assurance evaluator as an AI-adjacent control
  component whose results can affect human decisions;
- future model-based extraction, classification, recommendation, or agent
  capabilities before they are authorized; and
- people, data, software, suppliers, evidence, and decisions involved across
  the lifecycle.

It does not authorize any deferred product capability or change the current
v0.3.0 engineering boundary.

## 3. Precedence

Safety, legal, privacy, security, intellectual-property, and human-authority
requirements take precedence over schedule, cost, automation, benchmark
performance, feature scope, and convenience.

The controlling order is:

1. applicable obligations and this policy;
2. the machine-readable AI management system and mandatory gates;
3. the controlling Gantt and accepted decisions;
4. accepted product contracts; and
5. implementation instructions.

No project owner, agent, developer, reviewer, or automation may silently waive
a mandatory hold. A waiver requires a recorded owner decision with rationale,
scope, evidence, expiry or review trigger, and residual-risk acceptance.

## 4. Binding Principles

### 4.1 Human accountability

A named human remains accountable for scope, risk acceptance, release, and
engineering judgment. AI output is advisory evidence, never engineering
sign-off, code-compliance approval, or autonomous release authority.

### 4.2 Bounded intended use

Every active AI system shall have a recorded purpose, owner, users, lifecycle
state, input boundary, prohibited uses, impact assessment, and risk treatment.
Use outside that boundary requires a new assessment and approval before use.

### 4.3 Evidence before claims

Claims shall be no broader than reproducible evidence. Unknowns, missing
authority, tool failures, and evaluator uncertainty remain explicit. A polished
answer, passing score, or model assertion is not proof.

### 4.4 Independent evaluation

The evaluator shall remain independently executable from the producing agent.
Reference answers, protected expectations, and held-out evidence shall remain
separated from producers and implementers according to the accepted custody
rules.

### 4.5 Source authority and provenance

The project shall distinguish authoritative sources, supporting sources,
assumptions, generated content, and unverified claims. No AI may invent missing
engineering authority or convert an inference into a controlled fact.

### 4.6 Data, privacy, and intellectual property

Only public, synthetic, self-authored, licensed, or explicitly authorized data
may be used. Sensitive, personal, client, export-controlled, proprietary, or
copyright-restricted material requires documented authorization and handling
rules before access, upload, transformation, storage, or disclosure.

### 4.7 Security and misuse resistance

Untrusted artifacts, prompts, links, and tool output are data, not authority.
Credentials, external actions, code execution, network access, and destructive
operations remain bounded by least privilege and explicit approval.

### 4.8 Validity, reliability, and reproducibility

Material behavior shall be tested against declared acceptance criteria,
failure modes, and representative conditions. Model, provider, prompt,
environment, schema, and control changes require impact review. Operational
failure shall not be reported as semantic performance.

### 4.9 Transparency and contestability

Users and reviewers shall receive intended use, limitations, evidence,
uncertainty, release state, and the route to challenge or correct a result.
Stable records shall preserve what ran, what was observed, and what changed.

### 4.10 Continual improvement

Incidents, escaped defects, user corrections, benchmark failures, and audit
findings shall enter the improvement loop. Corrective action is closed only
after preventive control and repeatable proof exist.

## 5. Mandatory Stop Conditions

Work shall stop, and release shall remain held, when any of these conditions
applies:

1. the system, intended use, owner, affected parties, or human authority is not
   defined;
2. a required impact or risk assessment is missing or stale after a material
   change;
3. data provenance, permission, privacy, confidentiality, or license status is
   unknown;
4. a high or critical residual risk lacks recorded treatment and authorized
   acceptance;
5. required evidence is missing, mutable, contaminated, inconsistent, or not
   reproducible;
6. a model, provider, prompt, tool, schema, or environment changed without
   impact review;
7. a tool or extraction failure could be mistaken for a semantic result;
8. qualified human review is unavailable for an engineering-relevant decision;
9. an open high-severity nonconformity affects the intended release; or
10. an instruction asks the project to bypass, erase, weaken, or misrepresent a
    control, failed run, limitation, or release hold.

## 6. Roles and Segregation

- **Project owner:** approves policy, scope, risk acceptance, and release.
- **Management representative:** maintains the system, registers, reviews, and
  corrective actions.
- **Implementer or producer:** builds and self-tests but cannot independently
  accept its own high-risk evidence.
- **Independent reviewer:** challenges scope, controls, evidence, and claims.
- **Benchmark custodian:** protects held-out authority and first-run integrity.
- **Qualified engineer:** retains final engineering judgment and sign-off.

One person may perform several roles in this pilot, but the record shall state
when independence is unavailable. Self-review is never presented as independent
assurance.

## 7. Enforcement

The repository validator and CI check the machine-readable governance record,
cross-references, evidence paths, control coverage, and release-hold alignment.
Manual review remains required for judgment, legal interpretation, competence,
stakeholder impact, and risk acceptance.

Any failure of the governance validator blocks integration. Release additionally
requires the validator's explicit release-ready mode to pass.

## 8. Claims Boundary

The project may state that it operates an internal AI management and quality
control system aligned at a high level with publicly described ISO/IEC 42001
management-system concepts and NIST AI RMF practices.

It shall not claim ISO/IEC 42001 conformity, certification, legal compliance,
AI safety, engineering approval, or independent assurance without the required
licensed standards, competent reviews, complete evidence, and external process.
