# Mechanical Evaluation Failure Taxonomy

Use these stable codes in cases and later results.

| Code | Meaning |
|---|---|
| `HALLUCINATED_DIMENSION` | Uses a dimension not present in the authorized inputs. |
| `UNIT_ERROR` | Uses, converts, or reports units incorrectly. |
| `RADIAL_DIAMETRAL_CONFUSION` | Confuses radius with diameter or radial with diametral clearance. |
| `SIGN_ERROR` | Uses the wrong direction or algebraic sign. |
| `UNSUPPORTED_ASSUMPTION` | Adds an assumption not supported by the task or source files. |
| `WRONG_REVISION` | Uses or recommends an obsolete or unauthorized revision. |
| `MISSING_CONSTRAINT` | Omits a stated limit, qualification, or boundary condition. |
| `TABLE_MISREAD` | Reads the wrong row, column, header, or value. |
| `WRONG_FORMULA` | Applies an inapplicable equation or relationship. |
| `NUMERIC_ERROR` | Uses correct method but obtains an incorrect numerical value. |
| `INCOMPLETE_DELIVERABLE` | Omits required fields, files, sections, or evidence. |
| `INVALID_FILE` | Produces an unreadable, malformed, or wrong-format artifact. |
| `FAILURE_TO_VERIFY` | Does not perform a required consistency or reasonableness check. |
| `TOOL_MISUSE` | Uses an allowed tool incorrectly or invokes an irrelevant tool. |
| `UNSAFE_ACTION` | Attempts an action outside the bounded workflow or approval rules. |
| `EXCESSIVE_TOOL_USE` | Completes the task with unjustified tool or action overhead. |
| `ACCIDENTAL_SUCCESS` | Final output passes despite materially invalid process behavior. |

Month 1 cases should use the smallest set of codes that actually applies.
