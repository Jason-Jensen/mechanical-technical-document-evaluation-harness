# Portfolio Demo Evidence

## Purpose

This report verifies the implemented MVP harness using one passing and one technically defective MECH-002 candidate.

- Executed at: `2026-07-06T00:19:56.334813+00:00`
- Case: `MECH-002`
- Workflow: `WF-SHAFT-POWER`
- Scenarios verified: `2/2`

## Results

| Scenario | Expected exit | Score | Result | Failure modes |
|---|---:|---:|---|---|
| `mech-002-pass` | 0 | 1.00 | PASS | None |
| `mech-002-unit-error` | 1 | 0.75 | FAIL | UNIT_ERROR |

## Immutable result records

- `mech-002-pass`: `runs\portfolio-demo\mech-002-pass\RUN-20260706T001956012820Z-0b1dc7c3\result.json`
- `mech-002-unit-error`: `runs\portfolio-demo\mech-002-unit-error\RUN-20260706T001956281133Z-f95c0acf\result.json`

## Captured CLI output

### Passing shaft-power artifact

```text
RESULT: PASS
CASE: MECH-002
CANDIDATE: C:\Projects\mechanical-technical-document-evaluation-harness\examples\candidates\MECH-002\valid.json
SCORE: 1.000 (threshold 0.950)
GATES:
  PASS output_exists [output_exists] | Candidate file exists: C:\Projects\mechanical-technical-document-evaluation-harness\examples\candidates\MECH-002\valid.json
  PASS valid_json [valid_json] | Candidate file contains valid JSON with an object root.
  PASS required_fields [required_fields_present] | All required payload fields are present.
  PASS field_types [field_types_match] | All declared payload field types match.
CHECKS:
  PASS angular_velocity [numeric_close] weight=0.250 | Actual 183.2596 at '$.angular_velocity_rad_s'; expected 183.2596 from '$.angular_velocity_rad_s'; absolute difference 0; tolerance 0.01.
  PASS shaft_power [numeric_close] weight=0.350 | Actual 21.9911 at '$.shaft_power_kw'; expected 21.9911 from '$.shaft_power_kw'; absolute difference 0; tolerance 0.02.
  PASS verification_power [numeric_close] weight=0.200 | Actual 21.9911 at '$.verification_power_kw'; expected 21.9911 from '$.verification_power_kw'; absolute difference 0; tolerance 0.02.
  PASS relative_difference [numeric_close] weight=0.100 | Actual 0.0 at '$.relative_difference_percent'; expected 0.0 from '$.relative_difference_percent'; absolute difference 0; tolerance 0.01.
  PASS verification [boolean_equals] weight=0.100 | Actual Boolean matches expected Boolean.
FAILURES:
  NONE
RESULT RECORD: C:\Projects\mechanical-technical-document-evaluation-harness\runs\portfolio-demo\mech-002-pass\RUN-20260706T001956012820Z-0b1dc7c3\result.json
```

### Shaft-power artifact with an angular-velocity unit error

```text
RESULT: FAIL
CASE: MECH-002
CANDIDATE: C:\Projects\mechanical-technical-document-evaluation-harness\examples\candidates\MECH-002\unit-error.json
SCORE: 0.750 (threshold 0.950)
GATES:
  PASS output_exists [output_exists] | Candidate file exists: C:\Projects\mechanical-technical-document-evaluation-harness\examples\candidates\MECH-002\unit-error.json
  PASS valid_json [valid_json] | Candidate file contains valid JSON with an object root.
  PASS required_fields [required_fields_present] | All required payload fields are present.
  PASS field_types [field_types_match] | All declared payload field types match.
CHECKS:
  FAIL angular_velocity [numeric_close] weight=0.250 | Actual 1750.0 at '$.angular_velocity_rad_s'; expected 183.2596 from '$.angular_velocity_rad_s'; absolute difference 1566.7404; tolerance 0.01.
  PASS shaft_power [numeric_close] weight=0.350 | Actual 21.9911 at '$.shaft_power_kw'; expected 21.9911 from '$.shaft_power_kw'; absolute difference 0; tolerance 0.02.
  PASS verification_power [numeric_close] weight=0.200 | Actual 21.9911 at '$.verification_power_kw'; expected 21.9911 from '$.verification_power_kw'; absolute difference 0; tolerance 0.02.
  PASS relative_difference [numeric_close] weight=0.100 | Actual 0.0 at '$.relative_difference_percent'; expected 0.0 from '$.relative_difference_percent'; absolute difference 0; tolerance 0.01.
  PASS verification [boolean_equals] weight=0.100 | Actual Boolean matches expected Boolean.
FAILURES:
  CHECK angular_velocity | UNIT_ERROR weight=0.250 | Actual 1750.0 at '$.angular_velocity_rad_s'; expected 183.2596 from '$.angular_velocity_rad_s'; absolute difference 1566.7404; tolerance 0.01.
RESULT RECORD: C:\Projects\mechanical-technical-document-evaluation-harness\runs\portfolio-demo\mech-002-unit-error\RUN-20260706T001956281133Z-f95c0acf\result.json
```

## Interpretation

The passing artifact traversed mandatory gates, deterministic checks, weighted scoring, and immutable result persistence with exit code 0 and score 1.00.

The defective artifact remained structurally valid, passed the mandatory gates, failed the angular-velocity check with `UNIT_ERROR`, returned exit code 1, scored 0.75, and still produced an immutable result record.

This is evidence of harness behaviour. It is not evidence of AI-model or agent performance, and it does not provide engineering sign-off.
