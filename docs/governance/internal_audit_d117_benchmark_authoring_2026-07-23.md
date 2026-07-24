# Internal Audit: D-117 Benchmark Authoring

**Audit ID:** AIMS-AUD-002

**Date:** 2026-07-23

**Status:** Completed with finding

**Finding:** NC-002

## Scope

Review the D-116 family freeze, D-117 authorization, one-shot execution, raw
verification, protected comparison, claim boundary, and improvement response.

## Evidence Sampled

- D-116 recovery definition, freeze review, and machine-readable evidence;
- D-117 execution gate and owner instruction;
- immutable raw-execution handoff and aggregate;
- oracle-blind raw verification revisions 1 through 3;
- public protected-comparison aggregate;
- public replacement-custodian contract;
- evaluator authority gate; and
- controlling Gantt and improvement register.

Protected scenario-level expectations remained in the custodian context and
were not copied into this audit.

## Findings

### Effective Controls

- The runner consumed one authorization and executed once.
- Eight attempts produced eight complete four-output publications.
- Raw, static, producer, protected, and family identities remained unchanged.
- Oracle-blind verification and protected comparison remained separated.
- No retry, tuning, repair, or release claim occurred.
- The evaluator failed closed on an actual package-authority conflict.

### NC-002: Ineffective Family Contract Freeze

The accepted public contract requires each authority map to apply to its
scenario package ID. All eight frozen packages instead used the family ID.

The D-116 freeze passed because its checks covered schema, inventory, rights,
hashes, separation, leakage, and oracle coverage but omitted this public
semantic invariant and protected target reachability. The resulting readiness
claim was therefore overstated.

Every intended downstream check was blocked. The D-117 family cannot support
downstream performance claims and may not be repaired or rerun as fresh
held-out evidence.

## Containment

- Preserve D-116 and D-117 evidence unchanged.
- Mark the family consumed and invalid for intended downstream claims.
- Keep release held by AIR-003, AIR-011, and NC-002.
- Prohibit family rerun, reuse, evaluator tuning, and P4.3.
- Present D-118 as a separate bounded corrective-action decision.

## Independence Limitation

This was an internal AI-assisted review under the same project owner. Separate
contexts protected oracle access and raw verification, but this is not
external independent assurance or ISO/IEC 42001 certification.
