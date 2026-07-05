# MVP v1 Benchmark Review Checklist

## Purpose

This checklist records the review status and split assignment of the five
synthetic MVP benchmark cases.

Review indicates that the case is suitable for deterministic benchmark use.
It does not constitute engineering approval, release authorization, design
sign-off, or acceptance for safety-critical use.

## Case review record

| Case | Workflow | Synthetic or authorized | Reference independently verified | Deterministic evaluator | Human-review boundary present | Split | Evidence |
|---|---|---:|---:|---:|---:|---|---|
| MECH-001 | Fit and clearance disposition | Yes | Yes | Yes | Yes | development | `docs/seed-case-verification.md` |
| MECH-002 | Shaft-power calculation | Yes | Yes | Yes | Yes | development | `docs/seed-case-verification.md` |
| MECH-003 | Revision and instruction audit | Yes | Yes | Yes | Yes | held_out | `docs/seed-case-verification.md` |
| MECH-004 | Drawing parts list versus procurement BOM | Yes | Yes | Yes | Yes | development | `docs/additional-case-verification.md` |
| MECH-005 | Linear thermal expansion | Yes | Yes | Yes | Yes | development | `docs/additional-case-verification.md` |

## Review criteria

- [x] Inputs are synthetic, self-authored, public, or otherwise authorized.
- [x] Case instructions and required deliverables are explicit.
- [x] Reference artifacts are reproducible from the controlled inputs.
- [x] Evaluator checks are deterministic and evidence-producing.
- [x] Numeric tolerances have documented engineering rationale where used.
- [x] Failure modes are narrow enough to support diagnosis.
- [x] Passing and failing behavior has regression evidence where fixtures exist.
- [x] Qualified human review is required for engineering use.
- [x] No case authorizes autonomous design release or engineering sign-off.
- [x] Development and held-out membership are versioned.
- [x] Held-out limitations and prior exposure are disclosed.

## Held-out controls

MECH-003 is frozen as the MVP v1 held-out case.

The following controls apply:

1. Do not add versioned candidate examples under
   `examples/candidates/MECH-003`.
2. Do not modify MECH-003 inputs, reference data, task specification, or
   evaluator merely to improve a benchmark result.
3. Any justified change to MECH-003 must be documented as a benchmark revision.
4. Report development and held-out results separately.
5. Preserve failed held-out runs as evaluation evidence.
6. Do not describe MECH-003 as historically blind or uncontaminated.

## Split limitation

MECH-003 was created and independently reviewed before the held-out split was
established. It is therefore a frozen validation case, not a pristine external
test set. A future benchmark version should add newly authored cases that are
held back before candidate development begins.
