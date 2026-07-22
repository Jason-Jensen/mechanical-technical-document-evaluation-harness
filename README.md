# Mechanical Engineering Workflow Assurance Platform

This repository combines a frozen evaluation kernel with an active, structured package-assurance pilot.

The released **Mechanical Technical Document Evaluation Harness v0.2.0** is a schema-first Python CLI that converts engineering review requirements into reproducible gates, deterministic checks, weighted scores, failure evidence, and immutable result records.

The project's highest-level internal quality controls are the
[AI Management System Policy](docs/governance/ai_management_system_policy_v0.3.0.md)
and its machine-validated
[AI management-system record](governance/ai_management_system.json). They make
human accountability, authorized data, evidence, risk treatment, explicit
holds, and continual improvement mandatory above feature work and schedule.

## Project status

- **Released and frozen:** v0.2.0 at accepted commit `45336a2`, with 121 tests, baseline 9/9, demo 2/2, and an annotated release tag.
- **Active release:** v0.3.0 Package Assurance Pilot, a structured Mechanical Package Consistency Audit.
- **Current gate:** D-113 is consumed. PR #65 integrated it at exact `main` `6a74c74`; preflight passed, but all eight one-shot attempts returned exit `70` in the atomic publication layer and produced no complete output set. Independent verification passed and the protected comparison classified the benchmark as not evaluable. D-114 stabilization authority is proposed for owner review; release remains held.
- **AI governance:** D-115 adopts an internal ISO/IEC 42001-aligned and NIST-informed AI management system. It inventories three systems, thirteen risks, twenty controls, eight lifecycle gates, six objectives, one open nonconformity, and an explicit held release state. This is not an ISO conformity or certification claim.
- **Implementation boundary:** Eight ordered gates and eleven ordered relationship checks feed the canonical package result with fail-closed completeness, exact state precedence, declared-input fingerprints, schema validation, and immutable persistence. P2.3 is complete for this exact scope. Six unsupported authority/source claims are explicitly deferred and excluded from v0.3.0 release claims.

The accepted P2.3 completion boundary limits v0.3.0 to the eleven proven checks and defers six claims that lack a comparison source or exact authority rule. This prevents single-source field validation from being presented as cross-document reconciliation.

Check 6 verifies that each release-required BOM item has exactly one reciprocal manifest item-to-equipment declaration under `AUTH-BOM-002`. The clean development package passes; an isolated valid-but-wrong target produces one evidence-linked automatic-fail release hold through the result, reports, and CLI. Verification passes 31 relationship tests, 75 focused tests, and 278 full-suite tests with one expected skip.

Check 7 verifies that each release-required BOM equipment tag appears in drawing metadata under exact `AUTH-BOM-002`, without claiming that the BOM `drawing_number` is authoritative. The clean package passes 7/7 checks; removing only `M-101A` from drawing metadata produces one release hold through all four outputs and exit `1`. Verification passes 35 relationship tests, 80 focused tests, and 283 full-suite tests with one expected skip.

Check 8 requires exactly one release-required datasheet metadata record for each release-required BOM equipment tag under exact `AUTH-SPEC-001`. The clean package passes 8/8 checks; removing one record produces one missing-authority release hold through all four outputs and exit `3`, while competing records remain deterministic. Verification passes 111 focused tests and 295 full-suite tests with one expected skip at 87.71% coverage.

Check 9 compares each eligible BOM `datasheet_id` with the single authoritative metadata ID. The clean package passes 9/9 checks; changing the pump to an existing but wrong datasheet produces one exact automatic-fail hold through all four outputs and exit `1`. D-104 accepted and PR #56 integrated this check at exact `main` `7146b23`.

The publication-resilience block retries only a transient final-rename `PermissionError` using four fixed waits totaling 0.75 seconds. Collision and non-permission failures never retry; exhausted retries preserve the failed publication and CLI exit `70`. D-105 accepted and PR #57 integrated the block at exact `main` `dbcd242`. Verification passes 24 focused tests and 304 full-suite tests with one expected skip at 88.08% coverage; 20/20 consecutive Windows audits published exactly four outputs with no hidden failures.

Check 10 requires release-required authoritative equipment/datasheet mappings and manifest `equipment_to_datasheet` declarations to agree in both directions. The clean package passes 10/10 checks; changing only `REL-EQ-DS-001` to the existing wrong target `DS-M-101` produces one exact automatic-fail hold through all four outputs and exit `1`. Verification passes 93 focused tests and 308 full-suite tests with one expected skip at 88.27% coverage.

Check 11 requires every release-required specification-metadata revision to match exactly one current revision-history record by normalized `specification_id`. The clean package passes 11/11 checks; changing only `SPMETA-001.revision_id` from `A` to valid value `B` produces one exact automatic-fail hold through all four outputs and exit `1`. Verification passes 99 focused tests and 314 full-suite tests with one expected skip at 88.48% coverage.

The v0.3.0 pilot will reconcile drawing registers, drawing metadata, BOM/equipment lists, datasheet/specification metadata, revision history, and controlled file references. Its intended outputs are an immutable package result, an evidence-linked issue register, and a release-readiness summary for qualified human review.

Current execution status is controlled in `gantt.xlsx`. Product behavior is defined in the [workflow contract](docs/package_assurance/workflow_contract_v0.3.0.md), [acceptance plan](docs/package_assurance/acceptance_plan_v0.3.0.md), and accepted [P2.3 relationship expansion definition](docs/package_assurance/p2_3_relationship_expansion_definition_v0.3.0.md). The two public-package observations and their mapping records remain historical evidence; they are not authority for new engineering claims. Reusable lessons and permanent controls are tracked in the [improvement register](docs/quality/improvement_register.md).

The controlling P2.3 closeout is the [completion and claim boundary](docs/package_assurance/p2_3_completion_and_claim_boundary_v0.3.0.md). P4.1 may build and verify the development benchmark machinery; protected held-out semantic execution remains a separate P4.2 gate.

P4.1 revision `P4.1-DEV-1` generates 22 development scenarios from the accepted clean pump-skid baseline and runs each twice through the real four-output audit. The exact-commit acceptance run at implementation `4cf9fe8` passed 22/22 scenarios and covered all eight gate failures and all eleven relationship-check failures with exact normalized output hashes. Full regression passes 319 tests with one expected Windows skip at 88.57% coverage; validation 5/5, Ruff, frozen baseline 9/9, demo 2/2, and both hosted Linux CI jobs also pass. D-109 accepts the bounded claim that four states have genuine full-package scenarios while two states have router/exit coverage only. The [P4.1 definition and review](docs/package_assurance/p4_1_development_benchmark_definition_and_review_v0.3.0.md), [external-custody freeze review](docs/package_assurance/p4_2_external_custody_freeze_review_v0.3.0.md), and [external first-run result review](docs/package_assurance/p4_2_external_first_run_result_review_v0.3.0.md) control the next decision.

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
- a machine-validated AI management, risk, control, audit, and release-hold system;
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
The AI management system reduces and exposes risk; it does not guarantee AI
safety, legal compliance, or engineering correctness.

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

### Run the development package benchmark

```powershell
python scripts/run_package_assurance_development_benchmark.py
```

The command creates a new timestamped directory under
`runs/package_assurance-development-benchmark/`, verifies the accepted clean
fixture hash, generates all 22 reviewed development scenarios without hidden
expected assets, runs each scenario twice, and writes JSON and Markdown
reports. Existing evidence is never overwritten. A selected `--scenario`
spot check is useful for diagnosis but is reported as unscored and cannot
claim full benchmark acceptance.

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
