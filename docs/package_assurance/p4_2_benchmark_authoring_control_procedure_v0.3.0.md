# P4.2 Benchmark-Authoring Control Procedure

**Version:** 0.3.0

**Date:** 2026-07-23

**Status:** Implemented under D-118; no new family authorized

## Purpose

This procedure prevents a schema-valid benchmark package from being described
as contract-complete when a public authoring defect would block its intended
test.

It adds two separate controls:

1. a producer-visible validator for non-secret package facts; and
2. a custodian-only reachability verifier that uses protected target mappings
   without publishing them.

Neither control changes evaluator gates, relationship semantics, result-state
routing, or protected expected outcomes.

## Public Package-Contract Validation

Run:

```powershell
mech-eval validate-package-contract `
    <repository-root> `
    <package-directory>
```

The command executes the accepted eight mandatory gates without executing any
relationship check. It writes deterministic JSON to standard output and
returns:

- `0` when all public package-contract gates pass;
- `1` when one or more public contract gates fail; or
- `64` for an invalid repository or package path.

The report includes:

- validator identity and version;
- package ID, when established;
- exact ordered gate statuses;
- finding codes and root blocking gates;
- `relationships_executed: false`; and
- an explicit claim boundary.

It contains no absolute machine path and does not approve release.

The validator covers the accepted public invariants, including:

- manifest structure and package-relative references;
- all seven required source declarations and files;
- exact `package_manifest.package_id` to `authority_map.applies_to` equality;
- accepted authority source IDs, rule fields, routes, profiles, revision
  schemes, duplicate policies, state precedence, and CLI exits;
- controlled-file boundaries and declared file existence;
- canonical identifier shape and scope;
- duplicate policy enforcement;
- revision format, progression, and current-state evaluability; and
- required evidence-locator structure.

For an ordinary producer package, any failed gate means the package is not
contract-complete. For a protected fault scenario, the scenario-level report
stays with the custodian. A failed gate is permitted only when the protected
plan identifies that exact gate as the intended target and every predecessor
gate passed.

## Custodian Target-Reachability Verification

The custodian runs:

```powershell
mech-eval verify-target-reachability `
    <repository-root> `
    <custody-root> `
    <public-index.json> `
    <protected-target-plan.json> `
    <new-output-directory>
```

All inputs and outputs must remain inside the isolated custody root. The output
directory must not already exist.

The public index contains only:

```json
{
  "schema_version": "0.3.0",
  "family_id": "FAM-OPAQUE",
  "scenario_results": [
    {
      "scenario_token": "S01",
      "package_result_path": "results/S01/package_result.json"
    }
  ]
}
```

The protected target plan contains exactly one clean scenario and one or more
fault scenarios:

```json
{
  "schema_version": "0.3.0",
  "family_id": "FAM-OPAQUE",
  "commitment_nonce": "<protected random 64-character lowercase hex>",
  "scenarios": [
    {
      "scenario_token": "S01",
      "scenario_role": "clean",
      "targets": []
    },
    {
      "scenario_token": "S02",
      "scenario_role": "fault",
      "targets": [
        {
          "kind": "relationship_check",
          "control_id": "<protected accepted check ID>"
        }
      ]
    }
  ]
}
```

The example is structural only. Actual scenario roles and target identities
are protected and must not enter Git or the implementation context. The
custodian generates the 256-bit commitment nonce inside custody and never
publishes it. It prevents the public protected-plan hash from becoming a
guessable dictionary of the small accepted control set.

The verifier requires:

- exact family and scenario-set agreement between the two inputs;
- a protected, custody-generated 256-bit commitment nonce;
- confined POSIX-relative, unique result paths;
- schema-valid package results;
- exact accepted gate and relationship-check order;
- every mandatory gate passed for the clean scenario;
- every predecessor gate passed before an intended gate target;
- every mandatory gate passed before an intended relationship target; and
- the intended target itself not skipped.

The verifier publishes two immutable files:

- `target_reachability.protected.json` contains scenario-level targets,
  statuses, blockers, and result hashes; and
- `target_reachability.public.json` contains only counts, pass/fail status,
  input hashes, aggregate result hash, protected-detail hash, and the statement
  `protected_values_published: false`.

Protected detail is written first. The redacted public attestation is the
completion marker and is written last. Existing output directories are never
overwritten.

## Corrected Freeze Checklist

A future family cannot be called contract-complete until all of these are
true:

1. rights, provenance, isolation, and no-network controls pass;
2. every scenario package and its authority map have distinct, matching
   package IDs;
3. the public validator result is preserved for every scenario;
4. the clean scenario passes every mandatory gate;
5. each fault scenario reaches every protected target with no earlier
   unplanned blocker;
6. scenario-level validator and reachability details remain protected;
7. only the redacted aggregate attestation enters a public handoff;
8. every failed authoring or verification revision is preserved;
9. public and protected files are frozen and hashed after validation;
10. a fresh reviewer reproduces the public hashes and attestation;
11. evaluator implementers do not access the family, target plan, or protected
    detail; and
12. a later owner gate separately authorizes any official benchmark execution.

JSON Schema validity alone is never contract-complete evidence.

## Development-Only Proof

The safe operating proof is:

```powershell
python scripts/run_benchmark_authoring_control_proof.py `
    . `
    runs/d118-proof
```

It uses only a generated copy of the accepted development package, excludes
the development expected directory, and proves:

- the clean package passes public validation;
- a valid relationship fault preserves all public gates;
- the exact D-117 authority-scope defect is rejected;
- a relationship target is reachable when all prerequisites pass;
- the same target is rejected when authority is an earlier blocker; and
- public attestations contain no scenario or target mapping.

It performs zero held-out semantic executions and cannot support benchmark
performance or release claims.

## Separation and Claims Boundary

The verifier code and public contract may be versioned. Any actual protected
target plan, scenario-level report, family package, or authoring-preflight
result must remain outside Git and outside evaluator-implementer access.

This procedure proves public-contract completeness and target reachability. It
does not prove exact finding correctness, false-positive or false-negative
performance, generalization, engineering correctness, release readiness,
independent assurance, conformity, or certification.
