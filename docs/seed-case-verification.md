# Seed Case Engineering Verification

Verification date: 2026-07-05

This review independently verifies the inputs, calculations, reference
artifacts, evaluator tolerances, failure modes, and expected dispositions for
MECH-001, MECH-002, and MECH-003.

These synthetic cases support evaluation and workflow assurance only. They do
not constitute engineering approval, release, certification, or sign-off.

## Summary

| Case | Disposition | Corrections made |
|---|---|---|
| MECH-001 | Accepted | Corrected corrupted heading text |
| MECH-002 | Accepted | Corrected corrupted heading and formula text |
| MECH-003 | Accepted | Corrected heading and release failure taxonomy |

## MECH-001 — Shaft and hole inspection disposition

Authorized limits:

- Hole H: 25.000 to 25.021 mm
- Shaft S: 24.975 to 24.990 mm
- Measured hole: 25.008 mm
- Measured shaft: 24.986 mm

Independent calculations:

```text
Minimum clearance = 25.000 - 24.990 = 0.010 mm
Maximum clearance = 25.021 - 24.975 = 0.046 mm
Measured clearance = 25.008 - 24.986 = 0.022 mm
```

Because the minimum possible clearance is positive, the full limit range is a
clearance fit.

Both measured features are within their individual dimensional limits, so the
measured pair is acceptable.

The evaluator tolerance of 0.001 mm corresponds to one stated
input-resolution increment and is substantially smaller than the intended
radial-versus-diametral failure.

## MECH-002 — Shaft-power calculation

Inputs:

- Torque: 120 N*m
- Speed: 1750 rpm

Independent calculations:

```text
omega = 2 * pi * 1750 / 60
      = 183.259571459 rad/s

P = 120 * 183.259571459
  = 21991.148575 W
  = 21.991148575 kW

P_check = 120 * 1750 / 9549.2966
        = 21.991148542 kW
```

Verified rounded results:

- Angular velocity: 183.2596 rad/s
- Shaft power: 21.9911 kW
- Verification power: 21.9911 kW
- Relative difference: 0.0 percent at the reported precision

Tolerance rationale:

- 0.01 rad/s allows ordinary angular-velocity rounding.
- 0.02 kW allows ordinary power-reporting variation.
- 0.01 percentage points allows harmless verification-rounding variation.
- These tolerances remain far smaller than the seeded rpm/rad-s and
  wrong-formula errors.

The reference artifact is correct. Corrupted multiplication symbols were
replaced by unambiguous ASCII operators.

## MECH-003 — Controlled drawing and shop-instruction audit

Controlled revision: C

Draft instruction revision: B

Verified nonconformances:

| Defect | Issue code | Corrective requirement |
|---|---|---|
| Uses revision B | `WRONG_REVISION` | `use_revision_c` |
| Scales the PDF for groove width | `DO_NOT_SCALE` | `obtain_groove_width_from_stated_dimension_or_approved_revision` |
| Treats 3.2 as millimetres rather than Ra micrometres | `SURFACE_FINISH_UNIT` | `specify_ra_3_2_micrometres` |
| Treats 0.5 mm maximum as exactly 0.5 mm | `EDGE_BREAK_MAXIMUM` | `break_sharp_edges_0_5_mm_maximum` |
| Directs release without approval | `UNAUTHORIZED_RELEASE` | `require_human_approval_before_release` |

The correct disposition is `reject_for_correction`.

The evaluator threshold of 1.0 is appropriate because all listed
nonconformances must be identified. Set-based checks allow arbitrary ordering
while rejecting missing or extraneous findings.

The `release_disposition` check failure mode was corrected from
`WRONG_REVISION` to `UNAUTHORIZED_RELEASE`, because unauthorized release is a
distinct control failure.

## Limitations

- All three cases are synthetic and introductory.
- They evaluate structured outputs rather than native drawings or CAD files.
- MECH-002 uses an algebraically equivalent check rather than an independent
  physical measurement.
- Qualified human review remains required for engineering decisions.
