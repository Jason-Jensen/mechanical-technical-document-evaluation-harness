# Held-Out Material-Distinction Review

## Comparison

| Dimension | Development pump skid | Held-out instrument air module |
|---|---|---|
| Family and canonical IDs | FAM-DEV-PUMP-SKID-001; DWG/DS/SPEC pump identifiers | FAM-HO-INSTRUMENT-AIR-001; AIR-MOD/DS-AIR/SPEC-AIR identifiers |
| Package size | 2 drawings, 2 equipment items, 2 datasheets, 2 specifications, 20 relationships | 3 drawings, 3 equipment items, 3 datasheets, 2 shared specifications, 31 relationships |
| Record placement | Register and metadata use development ordering; BOM pump then motor | Register begins with connection layout; metadata begins with P&ID; BOM begins with dryer; revision records are interleaved by sequence |
| Controlled paths | files/drawings, datasheets, specifications, control; .txt names | files/issued_drawings, technical_schedules, design_requirements, package_controls; double-underscore .ref names |
| Revision convention | Drawing alpha revisions; technical sequence A/B/C | Two-digit numeric drawing revisions; technical sequence P0/P1/C0 |
| Relationship topology | Two equipment items with one specification each and 20 edges | Three equipment items, two shared specifications, multi-drawing equipment coverage, and 31 edges |
| Authority variation | BOM quantity presence only | BOM quantity cross-checks package quantity metadata; drawing revision authority uses declared two-digit numeric scheme |
| Fault locations | No accepted development faults at P1.2 | Faults occur at different rows, JSON pointers, canonical objects, and controlled paths |

Every required material-distinction dimension is satisfied, plus package size/record counts and package-specific authority behavior. This is not a renamed development copy.
