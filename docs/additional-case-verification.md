# Additional Case Engineering Verification

## Scope

This record documents the engineering review of the two synthetic benchmark
cases added under WBS 3.2:

- MECH-004: drawing parts list versus procurement BOM reconciliation
- MECH-005: unconstrained linear thermal-expansion calculation

The cases test deterministic workflow assurance. They do not provide
engineering approval, release authorization, stress analysis, flexibility
analysis, or design sign-off.

## MECH-004 - BOM reconciliation

### Controlled inputs

The drawing parts list and procurement BOM are matched by exact part number.

| Part | Drawing | Procurement | Expected finding |
|---|---|---|---|
| P-101 | Qty 1, Rev C | Qty 1, Rev B | Revision mismatch |
| P-102 | Qty 2, Rev B | Qty 3, Rev B | Quantity mismatch |
| P-103 | Qty 4, Rev A | Absent | Missing from procurement BOM |
| P-104 | Absent | Qty 2, Rev A | Extra in procurement BOM |
| P-105 | Qty 1, Rev D | Qty 1, Rev D | No discrepancy |

The independently derived reference result is therefore:

- missing part numbers: `P-103`
- extra part numbers: `P-104`
- quantity mismatch part numbers: `P-102`
- revision mismatch part numbers: `P-101`
- disposition: `reject_for_correction`
- verification: `true`

### Evaluator rationale

Set comparisons are used because discrepancy order is not meaningful. A pass
threshold of 1.0 is appropriate because omitting any discrepancy or disposition
requirement makes the reconciliation incomplete.

The representative failing candidate intentionally omits the P-101 revision
mismatch. It must fail only `revision_mismatches`, produce
`WRONG_REVISION`, and score 0.80.

## MECH-005 - Thermal expansion

### Controlled inputs

- installed length: 12.0 m
- installation temperature: 20.0 C
- operating temperature: 180.0 C
- linear expansion coefficient: 0.000012 per C

### Independent calculation

Temperature change:

```text
delta_T = 180.0 - 20.0
        = 160.0 C
```

Primary route:

```text
delta_L = alpha * L * delta_T
        = 0.000012 * 12.0 * 160.0
        = 0.02304 m
        = 23.04 mm
```

Verification route:

```text
L = 12.0 m = 12000 mm

delta_L = 0.000012 * 12000 * 160.0
        = 23.04 mm
```

The relative difference between the two routes is 0.0 percent. The component
increases in length, and the required disposition is
`requires_expansion_accommodation_review`.

### Tolerance rationale

The four numeric checks use an absolute tolerance of 0.01 in their reported
units. For the expansion values, this permits normal two-decimal-place
reporting while remaining far smaller than the 1000:1 metre-to-millimetre
conversion error represented by the failing candidate.

The representative failing candidate reports 0.02304 m as 0.02304 mm while
retaining the correct independent verification value of 23.04 mm. It must fail:

- `free_expansion` with `UNIT_ERROR`
- `relative_difference` with `FAILURE_TO_VERIFY`

The expected score is 0.65.

## Regression evidence

Automated tests independently reconstruct both reference results from source
CSV inputs and execute the passing and failing candidate fixtures through the
CLI. Repository validation confirms that all five benchmark cases resolve
their task, environment, evaluator, input, and reference specifications.
