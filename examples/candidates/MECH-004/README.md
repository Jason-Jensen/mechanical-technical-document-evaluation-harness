# MECH-004 Candidate Examples

These synthetic artifacts exercise cross-document reconciliation between a
controlled drawing parts list and a procurement bill of materials.

| File | Exit | Score | Expected result |
|---|---:|---:|---|
| `valid.json` | 0 | 1.00 | All gates and checks pass |
| `revision-error.json` | 1 | 0.80 | `revision_mismatches` fails with `WRONG_REVISION` |

Generated result records are written under `runs/` or a caller-supplied run
directory and are not versioned as benchmark inputs.
