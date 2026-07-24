# P4.2 Benchmark-Authoring Corrective-Action Gate

**Version:** 0.3.0

**Date:** 2026-07-23

**Status:** D-118 accepted; corrective action implemented

**Predecessor:** D-117 one-shot execution and comparison complete

## Decision D-118

Accept the D-117 execution, raw verification, and protected comparison as
valid consumed operating evidence. Classify
`FAM-D116-CIM-20260723-01` as invalid for intended downstream relationship
performance claims because a shared authority-scope authoring defect blocked
every target check.

Open `NC-002`, preserve all D-116 and D-117 evidence, prohibit rerun or reuse of
the consumed family, and authorize one bounded benchmark-authoring
corrective-action block.

## Authorized Corrective Action

D-118 authorizes only:

1. add a public-contract validator for producer-visible package facts that
   cannot reveal protected expectations;
2. enforce, at minimum, exact equality between every scenario
   `package_manifest.package_id` and `authority_map.applies_to`;
3. validate authority source IDs, package references, required files,
   identifier scope, revision declarations, and other public authoring
   invariants already stated in the accepted contract;
4. add a custodian-only protected target-reachability check proving that each
   intended gate or relationship check can execute without an unintended
   earlier blocker;
5. require the clean scenario to pass every mandatory gate in the custodian
   context;
6. require each fault scenario to have no unplanned blocker before its
   protected target;
7. preserve failed validator revisions and convert each material failure into
   a repeatable control;
8. update the D-116 freeze checklist so a schema-valid package cannot be
   described as contract-complete without these checks; and
9. return a reviewed corrective-action implementation and a separate decision
   request before any new external family is authored.

The producer-visible validator may use synthetic development examples and
public contract text. Protected target reachability must remain outside Git
and outside implementer access.

## Definition of Done

The block is complete only when:

- the public-contract validator rejects the exact D-117 authority-scope defect;
- focused tests cover each newly enforced public invariant;
- the accepted development package still passes;
- a separated custodian procedure proves clean-gate and target reachability
  without publishing oracle values;
- `NC-002` has verified containment and an explicit closure path;
- governance, protected-safe regression, validation, Ruff, frozen baseline,
  and demo checks pass;
- the controlling Gantt and improvement register are updated; and
- a later owner gate defines whether and how to prepare a genuinely new family.

## Explicit Exclusions

D-118 would not authorize:

- repair, rerun, reset, reuse, or reinterpretation of the consumed D-116
  family;
- editing its oracle, expected conditions, raw evidence, or comparison;
- changing evaluator gate or relationship semantics;
- tuning against protected outcomes;
- creating or executing another external family;
- importing protected custody assets into Git;
- P4.3 release work; or
- release, accuracy, generalization, conformity, certification, or engineering
  correctness claims.

## Owner Acceptance

The project owner accepted D-118 on 2026-07-23. The implementation is reviewed
in
`p4_2_benchmark_authoring_corrective_action_review_v0.3.0.md`.

The public validator, separated custodian procedure, development-only proof,
containment record, and proposed D-119 gate do not authorize a new external
family or semantic benchmark execution.

## Superseded Owner Review Question

Does the project owner accept D-118 exactly as bounded above?

Accepted. `NC-002`, `AIR-003`, `AIR-008`, and `AIR-011` remain open, and D-119 is the next
owner gate. No new family preparation or external semantic execution is
authorized.
