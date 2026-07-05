# MECH-002 Candidate Examples

These synthetic candidate artifacts exercise the shaft-power evaluation
workflow without using proprietary engineering data.

| File | Expected exit | Expected score | Expected outcome |
|---|---:|---:|---|
| `valid.json` | 0 | 1.00 | All gates and checks pass |
| `unit-error.json` | 1 | 0.75 | `angular_velocity` fails with `UNIT_ERROR` |
| `incomplete.json` | 1 | 0.00 | `required_fields` gate fails with `INCOMPLETE_DELIVERABLE` |

Generated evaluation records are written beneath `runs/` and are excluded
from Git by default.
