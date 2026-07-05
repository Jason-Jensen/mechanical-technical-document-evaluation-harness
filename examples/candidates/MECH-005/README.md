# MECH-005 Candidate Examples

These synthetic artifacts exercise unconstrained linear thermal-expansion
calculation, unit conversion, independent verification, and disposition logic.

| File | Exit | Score | Expected result |
|---|---:|---:|---|
| `valid.json` | 0 | 1.00 | All gates and checks pass |
| `unit-error.json` | 1 | 0.65 | Primary expansion and relative-difference checks fail |

The unit-error candidate reports a result calculated in metres as though it
were already in millimetres. The independent millimetre-based verification
retains the correct result and exposes the unit conversion error.

Generated run records are not versioned as benchmark inputs.
