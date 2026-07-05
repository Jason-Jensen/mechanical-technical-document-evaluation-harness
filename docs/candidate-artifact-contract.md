# Candidate Artifact Contract

## Purpose

A candidate artifact is the output submitted to the evaluation harness for
checking against a versioned engineering case.

Candidate artifacts are separate from case definitions:

- `cases/` contains versioned benchmark inputs and reference material.
- `examples/candidates/` contains example outputs submitted for evaluation.
- `runs/` will contain generated evaluation evidence and result records.

The candidate contract is independent of how the output was produced. A
candidate may come from a human, direct model call, scripted workflow, or
agent runtime.

## Envelope

Every candidate is a JSON object with the following structure:

```json
{
  "schema_version": "1.0",
  "case_id": "MECH-002",
  "candidate_id": "mech-002-valid-001",
  "artifact_type": "structured_engineering_response",
  "artifacts": [],
  "payload": {},
  "provenance": {}
}