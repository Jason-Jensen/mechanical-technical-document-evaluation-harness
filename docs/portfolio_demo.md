# Portfolio Demo

## Purpose

This terminal-first demonstration shows the implemented MVP evaluation path using one passing and one technically defective candidate for `MECH-002`.

It is designed to prove observable harness behaviour rather than provide a polished user interface.

## What the demo proves

The script verifies that the harness can:

1. evaluate a structurally valid passing artifact;
2. evaluate a structurally valid artifact containing an angular-velocity unit error;
3. return exit code `0` for the passing evaluation;
4. return exit code `1` for the failed technical evaluation;
5. report deterministic gate and check evidence;
6. calculate the expected weighted scores;
7. classify the technical failure as `UNIT_ERROR`;
8. persist one immutable `result.json` record for each evaluation.

## Inputs

The demo reuses committed candidate fixtures:

- `examples/candidates/MECH-002/valid.json`
- `examples/candidates/MECH-002/unit-error.json`

No candidate is generated or modified during the demo.

## Run the demo

From the repository root with the development environment active:

```powershell
python scripts/run_portfolio_demo.py `
    --runs-dir runs\portfolio-demo `
    --report-path evidence\portfolio_demo\report.md
```

The script runs both scenarios, prints the captured CLI output, validates the returned result records, and writes an evidence report.

## Expected outcomes

| Scenario | Exit code | Score | Result | Failure mode |
|---|---:|---:|---|---|
| Passing candidate | `0` | `1.00` | PASS | None |
| Unit-error candidate | `1` | `0.75` | FAIL | `UNIT_ERROR` |

A successful demonstration ends with:

```text
DEMO VERIFIED: 2/2 scenarios
```

## Generated evidence

Raw result records are written below:

```text
runs/portfolio-demo/
```

Each scenario receives its own parent directory, and the harness generates a unique immutable run directory containing `result.json`.

The optional Markdown report is written to the path supplied with `--report-path`.

## Automated regression

Run the focused regression test:

```powershell
python -m pytest tests/test_portfolio_demo.py
```

Run the complete repository regression suite:

```powershell
python -m pytest
```

## Interpretation boundary

The demonstration verifies the harness contract:

- mandatory gates;
- deterministic checks;
- weighted scoring;
- failure evidence;
- exit codes;
- immutable result persistence.

It does not measure AI-model or agent performance. It does not provide engineering sign-off, autonomous approval, or substitution for qualified human review.
