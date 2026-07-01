# Architecture

## Core separation

The project uses six concepts that must remain separate.

### 1. Task

Defines what work must be done:

- instructions;
- required input assets;
- required output artifact;
- constraints;
- acceptance intent.

Stored under `specs/tasks/`.

### 2. Agent

The system attempting the task, such as a direct model, OpenClaw, or another harness.

No agent implementation is included in Month 1.

### 3. Environment

Defines the controlled workspace:

- readable input area;
- writable output area;
- evaluator-only reference area;
- allowed action categories;
- external-access policy.

Stored under `specs/environments/`.

### 4. Trace and artifacts

A future run record containing:

- actions;
- tool calls;
- tool results;
- environment state changes;
- errors;
- corrections;
- final outputs;
- timestamps and resource use.

Traces do not belong in case definitions.

### 5. Evaluator

Defines how success is measured:

- mandatory gates;
- deterministic checks;
- tolerances;
- weighted scoring;
- failure classifications.

Stored under `specs/evaluators/`.

### 6. Results

A future immutable record containing:

- case, agent, environment, and evaluator versions;
- outcome score;
- process score;
- pass/fail;
- failure evidence;
- cost and latency;
- artifact and trace locations.

Results do not belong in task or case files.

## Month 1 data flow

```text
case.json
   ├── links to task specification
   ├── links to environment specification
   ├── links to evaluator specification
   ├── points to input assets
   └── points to evaluator-only reference assets

validator
   ├── validates every JSON file
   ├── resolves every link
   ├── confirms every declared asset exists
   ├── checks path safety
   ├── confirms gate/check identifiers are unique
   └── confirms weighted checks sum to 1.0
```

## Why this structure is retained later

A single case can be run by multiple agents. A single agent can run many cases. Evaluators can be revised without altering the task instructions, and environments can change without redefining engineering correctness.

The structure also supports future workflow variants. Multiple cases may share one `workflow_id`, task specification, and evaluator while supplying different input and reference assets.
