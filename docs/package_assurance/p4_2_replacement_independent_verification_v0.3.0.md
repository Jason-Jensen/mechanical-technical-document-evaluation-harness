# Independent Replacement Freeze Verification

Status: **PASS**

Verifier role: independent P4.2 replacement-freeze verifier

Access boundary: **PASS**
Freeze integrity: **PASS**
Contamination status: `frozen_isolated_pre_execution`
Owner acceptance: `pending`
Semantic execution count: `0`
Replacement-family modifications by verifier: `0`

## Aggregate Checks

| Check ID | Status |
| --- | --- |
| `IV-001` | PASS |
| `IV-002` | PASS |
| `IV-003` | PASS |
| `IV-004` | PASS |
| `IV-005` | PASS |
| `IV-006` | PASS |
| `IV-007` | PASS |
| `IV-008` | PASS |
| `IV-009` | PASS |
| `IV-010` | PASS |
| `IV-011` | PASS |
| `IV-012` | PASS |
| `IV-013` | PASS |
| `IV-014` | PASS |

Checks: `14`
Passed: `14`
Failed: `0`

## Counts

| Count | Value |
| --- | ---: |
| Authorized input manifest files | 9 |
| Authorized input access files | 10 |
| Scenarios | 8 |
| Family files | 210 |
| Non-freeze inventory files | 208 |
| Scenario package files | 200 |
| Files per scenario package | 25 |
| Producer bundle files | 205 |
| Protected bundle files | 3 |
| Valid package manifests | 8 |
| Accepted relationship contracts | 11 |
| Controlled fault scenarios | 7 |
| Release-blocking faults | 7 |
| Compound scenarios | 1 |
| Required state categories | 4 |
| Exact finding records | 8 |
| Wildcards | 0 |
| Public leakage findings | 0 |
| Hash mismatches | 0 |
| Freeze-order violations | 0 |
| Blockers | 0 |
| Public reports | 2 |

## Bundle Hashes

| Bundle | SHA-256 |
| --- | --- |
| Producer | `da154aed47e2f1b26625c40fa0987cf9f4bd872285e5fec13907d1b85f408867` |
| Protected | `2b383800ad66625117febe883282392909ec9830286adb644006fc562e282c6e` |
| Complete family | `e619c81854d9676b5d821a752e3b00e68d0072572cef64509d5cc9132a3e6ff6` |

## Commands

| Command ID | Status |
| --- | --- |
| `IV-CMD-READ-PARSE` | completed |
| `IV-CMD-STATIC-VALIDATE` | completed |
| `IV-CMD-SHA256` | completed |
| `IV-CMD-REPORT-WRITE` | completed |
| `IV-CMD-SEMANTIC` | not run |

Blocker status: **NONE**
