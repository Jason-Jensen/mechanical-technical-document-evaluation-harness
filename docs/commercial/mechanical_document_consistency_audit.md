# Bounded Service Concept — Mechanical Document Consistency Audit

## Positioning

A fixed-scope audit that checks a controlled mechanical document package for missing items, wrong revisions, inconsistent identifiers, broken document relationships, and unsupported source mappings before human release review.

The service is not engineering sign-off and does not certify technical adequacy.

## Best Initial Customer Profile

- engineered-product manufacturer;
- fabricator;
- industrial service contractor;
- small or mid-sized engineering/project team;
- quality or document-control group with recurring package-review effort;
- Microsoft/shared-drive/EDMS workflow with exportable structured registers.

## Initial Scope

A first engagement should be intentionally bounded:

- one project/package;
- one drawing register;
- one BOM or equipment list;
- selected drawing metadata;
- selected datasheet/specification metadata;
- one revision-history source;
- a defined maximum number of records and files;
- client-confirmed authority hierarchy;
- no live production integration.

## Deliverables

1. Controlled package inventory.
2. Evidence-linked discrepancy register.
3. Severity and release-hold classification.
4. Missing-authority and engineering-review list.
5. Concise release-readiness summary.
6. Machine-readable result record.
7. Review meeting or walkthrough.
8. Optional recommendations for repeatable workflow controls.

## Client Responsibilities

The client must:

- provide authorized data;
- identify current controlled sources;
- approve the authority map;
- identify qualified reviewers;
- decide disposition of findings;
- approve and issue final engineering documents.

## Consultant Responsibilities

The consultant must:

- define scope and acceptance criteria;
- protect client data;
- preserve evidence and version information;
- distinguish deterministic failures from uncertainty;
- avoid unsupported technical conclusions;
- document limitations;
- return/delete data as agreed.

## Exclusions

- engineering design or validation;
- code or standards compliance opinion;
- document authentication or stamping;
- autonomous release approval;
- safety-critical decisions;
- native CAD alteration;
- production-system integration in the first pilot;
- guarantees that all errors are detected.

## Delivery Stages

### Stage 1 — Paid Diagnostic

- inspect workflow and source exports;
- define authority and acceptance criteria;
- estimate automatable checks;
- identify data/security constraints;
- produce a pilot plan.

### Stage 2 — Fixed-Scope Audit Pilot

- configure the package schema and rules;
- run the audit;
- review findings with the client;
- document false positives, missed conditions, and workflow value.

### Stage 3 — Repeatable Assurance Workflow

Only after a successful pilot:

- standardize exports and manifests;
- add recurring regression packages;
- automate repeat runs;
- add controlled extraction adapters or integrations where justified.

## Pricing Status

Do not publish firm pricing before v0.3.0 produces a credible demo and acceptance evidence.

The Alberta market report supports a future hypothesis of a paid diagnostic followed by a fixed-scope pilot, but actual pricing must reflect package size, source quality, confidentiality, review burden, and liability boundaries.

## Evidence-to-Product Loop

Every authorized engagement should create reusable, non-confidential improvements:

- sanitized regression cases;
- new check families;
- failure-taxonomy entries;
- better authority templates;
- improved evidence schemas;
- clearer acceptance criteria;
- measured review-time or rework outcomes.

Client data and proprietary details must not be converted into public benchmark assets without explicit permission.

## Commercial Proof Required Before Launch

- v0.3.0 frozen release;
- clean and failing demo packages;
- held-out benchmark results;
- documented limitations;
- data/security process;
- service scope and client-responsibility clauses;
- sample issue register and release summary;
- repeatable run instructions;
- no engineering-sign-off claim.
