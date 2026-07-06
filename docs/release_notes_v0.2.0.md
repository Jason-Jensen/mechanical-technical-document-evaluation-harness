# Release Notes — v0.2.0

## Status

Release candidate documentation for the first tagged MVP release.

The `v0.2.0` tag is not created by this document. Tagging occurs only after the final acceptance run in WBS 5.3.

## Release scope

Version `0.2.0` is the first release candidate of the Mechanical Technical Document Evaluation Harness.

It provides a schema-first Python CLI for evaluating structured candidate artifacts against versioned mechanical-engineering workflow cases.

Implemented commands:

- `mech-eval validate`
- `mech-eval list`
- `mech-eval inspect`
- `mech-eval evaluate`

Implemented evaluation behaviour:

- versioned case, task, environment, evaluator, and reference definitions;
- candidate-artifact loading and schema validation;
- ordered mandatory gates;
- deterministic technical checks;
- numeric tolerances and Boolean comparisons;
- weighted scoring and pass thresholds;
- structured failure evidence;
- classified failure modes;
- immutable local `result.json` records;
- explicit exit codes for success, evaluation failure, configuration failure, and internal or persistence failure.

## Benchmark content

The MVP benchmark contains five synthetic, self-authored mechanical workflow cases:

- `MECH-001` — shaft and hole fit-clearance disposition;
- `MECH-002` — shaft-power calculation and verification;
- `MECH-003` — controlled drawing and shop-instruction revision audit;
- `MECH-004` — drawing parts-list and procurement-BOM reconciliation;
- `MECH-005` — unconstrained thermal-expansion calculation.

Benchmark split:

- development: `MECH-001`, `MECH-002`, `MECH-004`, `MECH-005`;
- held-out: `MECH-003`.

`MECH-003` is frozen from the current benchmark version forward and has no committed candidate-example directory. It is not claimed to be a pristine blind case because it was authored and reviewed before the split was established.

Held-out results must remain reported separately.

## Verification evidence

The reproducible MVP v1 harness-verification baseline produced:

- development oracle checks: `4/4` passed;
- held-out oracle checks: `1/1` passed;
- curated fault-injection scenarios: `4/4` produced the expected outcomes.

This baseline verifies evaluator and harness behaviour. It is not evidence of AI-model or agent performance.

The deterministic portfolio demo verifies:

- a passing `MECH-002` candidate with exit code `0` and score `1.00`;
- a structurally valid `MECH-002` candidate containing an angular-velocity unit error with exit code `1`, score `0.75`, and failure mode `UNIT_ERROR`;
- immutable result-record creation for both scenarios.

The accepted repository state contains:

- five validating cases;
- 121 passing automated tests;
- GitHub Actions validation on pushes and pull requests;
- a demonstrated controlled red CI run followed by corrected green push and pull-request runs.

## Installation and compatibility

Minimum supported Python version:

```text
Python 3.12
```

Install from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The MVP has been exercised locally on Windows and in GitHub Actions on Ubuntu with Python 3.12. This is not a guarantee of compatibility across every operating system or Python configuration.

## Verification commands

```powershell
mech-eval validate .
python -m pytest
```

Run the deterministic portfolio demo:

```powershell
python scripts\run_portfolio_demo.py `
    --runs-dir runs\portfolio-demo `
    --report-path evidence\portfolio_demo\report.md
```

A successful demo ends with:

```text
DEMO VERIFIED: 2/2 scenarios
```

## Evidence locations

- `evidence/mvp_v1_baseline/report.md`
- `evidence/mvp_v1_baseline/summary.json`
- `evidence/portfolio_demo/report.md`
- `docs/portfolio_demo.md`
- `.github/workflows/ci.yml`

Generated raw run records are runtime evidence. They are separate from versioned case definitions and benchmark manifests.

## Professional boundary

The harness produces evaluation evidence, not professional engineering authorization.

It does not provide:

- engineering sign-off;
- stamped or sealed deliverables;
- code-compliance opinions;
- autonomous design release;
- safety-critical final decisions;
- unreviewed operational control.

Outputs require review by an appropriately qualified person.

## Deferred capability

The following are not implemented in version `0.2.0`:

- PDF, drawing, image, table, or native CAD parsing;
- redline generation or verification;
- standards or GD&T compliance engines;
- LLM judges;
- model or agent execution;
- OpenClaw integration;
- process-trace or trajectory capture;
- API or database services;
- web or desktop frontend;
- observability platform;
- deployment automation;
- governance packs;
- reward models, LoRA, or reinforcement learning.

See [limitations.md](limitations.md) for the complete limitation and claim-control statement.
