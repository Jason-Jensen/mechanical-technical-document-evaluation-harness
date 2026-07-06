# Architecture

## Purpose

The Mechanical Technical Document Evaluation Harness is a local, schema-first evaluation kernel for structured mechanical-engineering workflow artifacts.

Its responsibility is narrow:

1. load a versioned evaluation case;
2. validate its linked specifications;
3. accept an external candidate artifact;
4. run mandatory gates and deterministic checks;
5. calculate a weighted score;
6. preserve failure evidence in an immutable result record.

The harness evaluates artifacts. It does not generate engineering work, operate an agent, or authorize release.

## Architecture principles

The architecture keeps six concerns separate:

1. task;
2. agent;
3. environment;
4. trace and artifacts;
5. evaluator;
6. results.

This separation allows the evaluator to remain independent of the system that produced the candidate artifact.

## Core components

### 1. Task

A task defines the work request and acceptance context.

It includes:

- task identity;
- workflow identity;
- instructions;
- input assets;
- expected deliverable;
- constraints;
- evaluation intent.

Task specifications are versioned under `specs/tasks/` and referenced by case definitions.

The task does not contain generated run evidence.

### 2. Agent

The agent is the producer of a candidate artifact.

Possible producers include:

- a human;
- a deterministic script;
- a direct language-model call;
- OpenClaw or another agent harness;
- a future tool-using technical workflow.

No agent runtime is implemented in the MVP.

The current CLI receives only the finished candidate artifact. This keeps candidate generation independent from artifact evaluation.

### 3. Environment

The environment defines the files and constraints available to the artifact producer.

The MVP environment is static and local. It can describe:

- input directories;
- permitted assets;
- expected output form;
- file restrictions;
- workflow assumptions.

Environment specifications are versioned under `specs/environments/`.

The MVP does not provision virtual machines, containers, GUI sessions, cloud services, or production credentials.

### 4. Trace and artifacts

The primary artifact in the MVP is the candidate JSON file.

The harness also uses:

- versioned input assets;
- versioned reference artifacts;
- gate evidence;
- check evidence;
- final result records.

The MVP does not yet capture full agent trajectories, tool calls, GUI state, token use, latency, or correction history.

Those may be added later without changing the evaluator contract, provided trace data remains separate from case definitions and final result records.

### 5. Evaluator

The evaluator defines how one candidate artifact is judged.

An evaluator contains:

- mandatory gates;
- deterministic checks;
- check weights;
- failure-mode mappings;
- a pass threshold;
- a reference file.

Evaluator specifications are versioned under `specs/evaluators/`.

The MVP deliberately prefers deterministic checks over model-based judgment.

No LLM-as-judge component is implemented.

### 6. Results

A result is generated evidence from one evaluation run.

It records:

- run identity and creation time;
- harness version;
- case and workflow identity;
- candidate identity when available;
- artifact and reference paths;
- gate outcomes;
- deterministic check outcomes;
- weighted score;
- pass threshold;
- final pass/fail state;
- classified failure evidence.

Results conform to `schemas/result.schema.json`.

They are persisted beneath `runs/` by default, or beneath the directory supplied with `--runs-dir`.

Result records are generated evidence and must not be mixed with versioned case inputs.

## Repository relationships

```text
benchmarks/
    split and reporting controls
          │
          ▼
cases/<case-id>/case.json
          │
          ├── task reference ─────────► specs/tasks/
          ├── environment reference ──► specs/environments/
          ├── evaluator reference ────► specs/evaluators/
          ├── input assets
          └── reference artifacts

external candidate artifact
          │
          ▼
src/mech_eval_harness/
          │
          ├── validator.py
          ├── evaluation.py
          ├── scoring.py
          ├── results.py
          ├── persistence.py
          └── cli.py
          │
          ▼
runs/<generated-result-record>
```

## Evaluation lifecycle

### Phase 1 — Load and validate the case

The CLI resolves the requested case ID and loads:

- `case.json`;
- its task specification;
- its environment specification;
- its evaluator specification;
- linked schemas;
- input assets;
- the evaluator reference file.

Repository validation occurs before the case is treated as runnable.

Configuration defects return exit code `2` during evaluation.

### Phase 2 — Run mandatory gates

Mandatory gates test whether the candidate can proceed to detailed evaluation.

Typical gate concerns include:

- file existence;
- expected file type;
- parseability;
- required structure;
- candidate-schema validity.

If a mandatory gate fails:

- detailed checks are not run;
- the score is calculated according to gate-failure rules;
- the failure evidence is preserved;
- a result record is still written when persistence succeeds.

This distinguishes an unusable deliverable from a usable artifact that contains technical errors.

### Phase 3 — Validate candidate identity and schema

After initial file gates pass, the candidate is loaded against:

```text
schemas/candidate.schema.json
```

The candidate must be associated with the requested case.

An invalid candidate becomes evaluation failure evidence rather than being silently discarded.

### Phase 4 — Run deterministic checks

The harness compares candidate fields against the case's reference payload using checks configured by the evaluator.

Implemented checks are artifact-based and deterministic.

The check layer produces structured outcomes containing:

- check ID;
- check type;
- pass/fail status;
- weight;
- failure mode;
- evidence.

Check execution is separate from score calculation.

### Phase 5 — Calculate weighted scoring

`scoring.py` combines gate and check outcomes using the evaluator's configured weights and pass threshold.

The scoring layer produces:

- normalized score;
- pass threshold;
- final pass/fail state;
- structured failures.

This separation allows scoring policy to change without embedding score arithmetic inside each deterministic check.

### Phase 6 — Build the result record

`results.py` converts the loaded case, candidate identity, artifact paths, gate outcomes, check outcomes, and scoring output into the result-schema contract.

The result builder does not write files.

This permits independent testing of result construction.

### Phase 7 — Persist immutable evidence

`persistence.py`:

1. generates a run ID;
2. validates the completed result against `result.schema.json`;
3. writes the result beneath the selected run directory;
4. refuses to replace an existing run record.

Persistence failure returns exit code `3`.

The CLI prints the final result-record path after a completed evaluation.

## End-to-end data flow

```text
case ID + candidate path
          │
          ▼
load versioned case and specifications
          │
          ▼
mandatory artifact gates
          │
          ├── failure ──► score gate failure
          │
          └── pass
                │
                ▼
        candidate-schema validation
                │
                ├── failure ──► add invalid-file gate evidence
                │
                └── pass
                      │
                      ▼
              deterministic checks
                      │
                      ▼
              weighted scoring
                      │
                      ▼
             structured failures
                      │
                      ▼
             result-schema validation
                      │
                      ▼
              immutable JSON record
```

## CLI boundary

`cli.py` is the user-facing orchestration layer.

It supports:

- `validate`;
- `list`;
- `inspect`;
- `evaluate`.

It does not implement engineering checks directly. It coordinates the validator, gate/check runner, scoring layer, result builder, and persistence layer.

Exit codes form part of the CLI contract:

| Code | Meaning |
|---:|---|
| `0` | Success or passing evaluation |
| `1` | Failed evaluation or failed repository validation |
| `2` | Configuration error |
| `3` | Unexpected internal or persistence error |

## Case definitions versus run data

This distinction is an architectural invariant.

### Versioned benchmark inputs

These include:

- case definitions;
- task specifications;
- environment specifications;
- evaluator specifications;
- schemas;
- input assets;
- reference artifacts;
- benchmark split manifests.

They describe what is being tested and how success is defined.

### Generated evidence

This includes:

- candidate artifacts;
- run records;
- temporary files;
- benchmark execution directories;
- future traces, logs, costs, and latency records.

They describe what happened during one execution.

Generated evidence must not silently modify the benchmark definition.

## Benchmark controls

The MVP benchmark is defined by:

```text
benchmarks/mvp_v1/split.json
```

Development cases:

- `MECH-001`;
- `MECH-002`;
- `MECH-004`;
- `MECH-005`.

Held-out validation case:

- `MECH-003`.

`MECH-003` is frozen from the split date forward and must be reported separately.

It is not a pristine blind case because it was historically seen during initial authoring and review.

Changes to the split require a documented decision.

Candidate examples for the held-out case are prohibited.

## Baseline interpretation

The baseline under `evidence/mvp_v1_baseline/` verifies the harness itself.

It demonstrates:

- reference-equivalent artifacts can pass the complete evaluation path;
- curated unit, completeness, revision, and verification defects are detected;
- development and held-out cases can be reported separately;
- result records are produced through the production persistence path.

It does not establish:

- model accuracy;
- agent capability;
- human-level engineering competence;
- statistical coverage of all failure modes;
- suitability for autonomous engineering decisions.

## Continuous integration

GitHub Actions executes the repository quality gate on pushes and pull requests.

The workflow:

1. installs Python 3.12;
2. installs the package and development dependencies;
3. validates all five cases;
4. runs the complete pytest suite.

CI tests the harness and repository contract. It does not evaluate the quality of an external AI model unless model-produced candidates are deliberately added to a separate benchmark run.

## Failure model

The harness distinguishes several failure layers:

### Artifact or gate failure

Examples:

- missing file;
- invalid JSON;
- invalid candidate schema;
- unusable deliverable.

Detailed checks may not run.

### Deterministic technical-check failure

Examples:

- wrong unit;
- wrong revision;
- calculation mismatch;
- incomplete required content;
- failed verification.

The candidate remains parseable, but one or more technical expectations are not met.

### Configuration failure

Examples:

- malformed evaluator;
- missing reference;
- unsupported check configuration;
- invalid scoring weights.

This indicates a problem with the benchmark or harness configuration, not merely a weak candidate.

### Internal or persistence failure

Examples:

- inability to create the result record;
- attempted result overwrite;
- unexpected runtime exception.

This is a software-operability failure.

## Extension points

Later capabilities may be attached without collapsing the current boundaries.

### Additional artifact types

Potential additions:

- PDF;
- CSV and spreadsheet workbooks;
- drawings and page images;
- native CAD metadata;
- multi-file engineering packages.

Each format should expose deterministic or narrowly anchored evaluation evidence where practical.

### Agent evaluation

A future agent runtime may add:

- actions;
- tool calls;
- environment states;
- errors;
- corrections;
- cost;
- latency;
- process-quality scoring.

Outcome score and process-quality score should remain separate.

### Model-based judges

An LLM judge should only be introduced when no practical deterministic alternative exists.

Its criteria should be:

- narrow;
- evidence-anchored;
- versioned;
- calibrated;
- tested against human labels.

### API and storage

A later API or database may wrap the same evaluation services.

The CLI, evaluator, result builder, and schema contracts should remain usable independently of that deployment layer.

## Safety and professional boundary

The harness produces evaluation evidence, not professional authorization.

It may support:

- completeness review;
- revision review;
- calculation checking;
- technical-document evaluation;
- benchmark execution;
- workflow assistance.

It must not be represented as providing:

- engineering authentication;
- autonomous approval;
- code-compliance certification;
- safety-critical release authority;
- substitution for qualified human review.
