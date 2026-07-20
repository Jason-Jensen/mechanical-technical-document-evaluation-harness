# Mechanical Engineering Workflow Assurance Platform

This repository combines a frozen evaluation kernel with an active, structured package-assurance pilot.

The released **Mechanical Technical Document Evaluation Harness v0.2.0** is a schema-first Python CLI that converts engineering review requirements into reproducible gates, deterministic checks, weighted scores, failure evidence, and immutable result records.

## Project status

- **Released and frozen:** v0.2.0 at accepted commit `45336a2`, with 121 tests, baseline 9/9, demo 2/2, and an annotated release tag.
- **Active release:** v0.3.0 Package Assurance Pilot, a structured Mechanical Package Consistency Audit.
- **Current gate:** Review P3.3 implementation `b5f0fcd`, which adds atomic report publication and the bounded `audit-package` command from accepted predecessor `main` commit `441e521`.
- **Implementation boundary:** Eight ordered gates and five ordered drawing checks feed an accepted canonical package result with fail-closed completeness, exact state precedence, declared-input fingerprints, schema validation, and immutable persistence. P3.3 now publishes that result and the accepted P3.1/P3.2 views together through one hidden staging directory and final atomic rename. It does not change evaluator meaning. Broad P2.3 relationships, held-out semantic execution, and deferred capabilities remain separately gated.

The v0.3.0 pilot will reconcile drawing registers, drawing metadata, BOM/equipment lists, datasheet/specification metadata, revision history, and controlled file references. Its intended outputs are an immutable package result, an evidence-linked issue register, and a release-readiness summary for qualified human review.

Current execution status is controlled in `gantt.xlsx`. Product behavior is defined in [the workflow contract](docs/package_assurance/workflow_contract_v0.3.0.md) and [acceptance plan](docs/package_assurance/acceptance_plan_v0.3.0.md). The accepted delivery sequence and fifth-check contract are in [the first usable audit vertical-slice definition](docs/package_assurance/first_usable_audit_vertical_slice_definition_v0.3.0.md). The implemented P2.2 behaviors remain bounded in [the revision relationship definition](docs/package_assurance/p2_2_relationship_slice_definition_v0.3.0.md), [the drawing metadata presence definition](docs/package_assurance/p2_2_drawing_metadata_presence_definition_v0.3.0.md), [the drawing metadata register authority definition](docs/package_assurance/p2_2_drawing_metadata_register_authority_definition_v0.3.0.md), and [the drawing file-reference definition](docs/package_assurance/p2_2_drawing_file_reference_definition_v0.3.0.md). Reusable lessons and their permanent checks are tracked in [the improvement register](docs/quality/improvement_register.md).

## Current MVP

The repository currently provides:

- five synthetic mechanical workflow cases;
- JSON Schema validation for cases, tasks, environments, evaluators, candidates, and results;
- mandatory artifact gates;
- deterministic artifact checks;
- weighted scoring with explicit failure evidence;
- immutable JSON result persistence;
- a development and held-out benchmark split;
- a reproducible harness-verification baseline;
- a command-line interface;
- 121 automated tests;
- GitHub Actions CI on pushes and pull requests.

The harness does not call an AI model. Candidate artifacts may be produced by a human, script, model, or agent outside the harness and then submitted for evaluation.

## Engineering boundary

This software supports testing, benchmarking, drafting workflows, completeness checks, revision checks, calculation checks, and technical workflow assurance.

It does not provide:

- engineering sign-off;
- stamped or sealed deliverables;
- autonomous design release;
- code-compliance opinions;
- safety-critical final decisions;
- unreviewed operational control.

All engineering outputs require review by an appropriately qualified person.

## Requirements

- Python 3.12 or newer
- Git
- PowerShell, Bash, or another terminal

## Installation

Clone the repository and enter it:

```powershell
git clone https://github.com/Jason-Jensen/mechanical-technical-document-evaluation-harness.git
cd mechanical-technical-document-evaluation-harness
```

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On Linux or macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the package and development dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Confirm the CLI is available:

```powershell
mech-eval --help
```

## Quick verification

Validate all cases and their linked specifications:

```powershell
mech-eval validate .
```

Expected summary:

```text
5 case(s) passed repository validation.
```

Run the complete regression suite:

```powershell
python -m pytest
```

The current accepted baseline is 121 passing tests.

## Portfolio demo

Run the deterministic portfolio demonstration:

```powershell
python scripts/run_portfolio_demo.py `
    --runs-dir runs\portfolio-demo `
    --report-path evidence\portfolio_demo\report.md
```

## CLI usage

### Validate the repository

```powershell
mech-eval validate .
```

This validates all case definitions and their linked task, environment, evaluator, schema, input, and reference assets.

### List cases

```powershell
mech-eval list .
```

The output includes the case ID, workflow ID, difficulty, dataset split, and title.

### Inspect one case

```powershell
mech-eval inspect . MECH-003
```

This reports the linked task, environment, evaluator, expected deliverable, input count, gate count, check count, and targeted failure modes.

### Evaluate a candidate artifact

```powershell
mech-eval evaluate . MECH-001 path\to\candidate.json
```

The candidate must conform to `schemas/candidate.schema.json` and identify the case it is intended to answer.

A completed evaluation prints:

- overall pass or fail;
- case and candidate paths;
- weighted score and threshold;
- gate evidence;
- check evidence;
- classified failures;
- the persisted result-record path.

By default, generated records are written beneath `runs/`.

Use another result directory when needed:

```powershell
mech-eval evaluate `
    . `
    MECH-001 `
    path\to\candidate.json `
    --runs-dir scratch\demo-runs
```

Generated run records are evidence. They are not versioned benchmark definitions.

### Audit a structured package

```powershell
mech-eval audit-package `
    . `
    benchmarks\package_assurance\development\pump_skid_clean_v1\package `
    --runs-dir scratch\package-audit-runs
```

The command runs the accepted package gates, relationship checks, and result
router. It publishes one new immutable run directory containing:

- `package_result.json`;
- `issue_register.csv`;
- `issue_register.md`; and
- `release_readiness.md`.

The output directory must be outside the audited package. Existing run
directories are never overwritten. A malformed manifest inside an existing
package directory is retained as a controlled package result when the output
location remains usable.

## Exit codes

| Code | Meaning |
|---:|---|
| `0` | Evaluation passed, or a non-evaluation CLI command completed successfully |
| `1` | Candidate evaluation failed, or repository validation failed |
| `2` | Case, evaluator, schema, scoring, or other configuration error |
| `3` | Unexpected internal or result-persistence error |

In PowerShell, inspect the last command result with:

```powershell
$LASTEXITCODE
```

A candidate that is valid but fails engineering checks normally returns `1`. That is an evaluation result, not necessarily a software defect.

The `audit-package` command uses the accepted package-state exits:

| Code | Package audit meaning |
|---:|---|
| `0` | `automatic_pass` |
| `1` | `automatic_fail` |
| `2` | `engineering_review_required` |
| `3` | `missing_authoritative_information` |
| `4` | `extraction_or_tool_failure` |
| `5` | `evaluator_uncertainty` |
| `64` | Invalid command arguments or package/repository path |
| `70` | Unexpected failure before a complete result can be published |

## Evaluation path

The implemented evaluation path is:

```text
versioned case
    ↓
linked task, environment, evaluator, and reference
    ↓
candidate file and mandatory gates
    ↓
candidate-schema validation
    ↓
deterministic checks
    ↓
weighted scoring and pass threshold
    ↓
failure evidence
    ↓
schema-valid immutable result record
```

Mandatory-gate failure prevents detailed checks from running. The result record still captures the failure evidence and final score.

See [docs/architecture.md](docs/architecture.md) for the implemented v0.2.0 component boundaries and [the package-assurance target architecture](docs/architecture/package_assurance_target_architecture.md) for the planned v0.3.0 extension.

## Benchmark cases

| Case | Workflow |
|---|---|
| `MECH-001` | Inspection disposition for a shaft and hole pair |
| `MECH-002` | Mechanical shaft-power calculation and verification |
| `MECH-003` | Controlled drawing and shop-instruction audit |
| `MECH-004` | Drawing parts list and procurement BOM reconciliation |
| `MECH-005` | Unconstrained thermal expansion calculation |

The frozen MVP benchmark manifest is located at:

```text
benchmarks/mvp_v1/split.json
```

Its split is:

- development: `MECH-001`, `MECH-002`, `MECH-004`, `MECH-005`;
- held-out validation: `MECH-003`.

`MECH-003` is held out from future development changes and has no versioned candidate-example directory. It is not claimed to be a pristine blind case because it was seen during initial case authoring and review before the split was established.

Held-out results must be reported separately.

## Baseline evidence

The reproducible baseline materials are in:

```text
evidence/mvp_v1_baseline/
```

The baseline verifies that:

- four development oracle artifacts traverse the harness successfully;
- one held-out oracle artifact traverses the harness successfully;
- four curated fault injections are detected as expected.

This is a harness-integrity baseline. It is not evidence of model or agent performance.

The fault set is small and curated, so no statistical generalization is claimed.

## Repository map

```text
.github/workflows/    GitHub Actions CI workflow
benchmarks/           Versioned benchmark manifests and split controls
cases/                Runnable case instances and case-specific assets
docs/                 Architecture and supporting documentation
evidence/             Versioned reports and accepted benchmark evidence
examples/             Optional non-benchmark candidate/demo workspace
runs/                 Generated immutable evaluation result records
schemas/              JSON Schemas for repository and result contracts
scratch/              Disposable local working files
scripts/              Reproducible benchmark and maintenance scripts
specs/                Reusable task, environment, and evaluator definitions
src/                   Python package and CLI implementation
tests/                 Unit, integration, scoring, persistence, and baseline tests
gantt.xlsx             Controlling project-management workbook
pyproject.toml         Package metadata, dependencies, and CLI entry point
```

Case definitions, specifications, schemas, references, and benchmark manifests are version-controlled inputs.

Generated run data belongs in `runs/` or another explicit run directory and must not be mixed into case definitions.

## Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request using Python 3.12.

CI performs:

1. repository checkout;
2. package and development-dependency installation;
3. five-case repository validation;
4. Python source linting;
5. the complete pytest suite with an 80% coverage floor.

A controlled seeded failure was used during CI acceptance to confirm that the workflow reports a red run when a required step fails.

## Design principles

- Define success before evaluating a candidate.
- Prefer deterministic and artifact-based checks.
- Preserve failure evidence rather than only a final score.
- Keep benchmark inputs separate from generated results.
- Report development and held-out results separately.
- Do not claim improvement without repeatable evidence.
- Use LLM judges only when no practical deterministic alternative exists.
- Keep the evaluator independent of any one model or agent runtime.

## Release documentation

- [Release notes — v0.2.0](docs/release_notes_v0.2.0.md)
- [Limitations and claim boundaries](docs/limitations.md)


## Current limitations

The MVP is intentionally narrow:

- structured JSON candidate artifacts only;
- local CLI execution;
- deterministic evaluation only;
- five synthetic workflow cases;
- no API or database;
- no PDF, image, drawing, or native CAD parsing;
- no agent runtime or trajectory collection;
- no LLM judge;
- no deployment or observability platform.

These are later expansion paths, not requirements for the current evaluation kernel.

## One-click portfolio demo

On Windows, double-click `RUN_DEMO.bat` in the repository root.

The demonstration evaluates two synthetic MECH-002 shaft-power artifacts:

- a valid artifact that should pass with a score of 1.000;
- an artifact containing an angular-velocity unit error that should fail with `UNIT_ERROR` evidence.

Generated reports and structured result records are written to `demo_output/`.
The launcher requires the local `.venv` environment created during project setup.
