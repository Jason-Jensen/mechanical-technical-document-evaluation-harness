# P4.2 External Benchmark Execution Gate

**Version:** 0.3.0

**Date:** 2026-07-23

**Status:** Proposed D-117 owner review

**Predecessor:** D-116 recovery freeze passed

## Proposed Decision D-117

Authorize exactly one invocation of
`RUNNER-D116-CIM-20260723-04` against frozen family
`FAM-D116-CIM-20260723-01`.

That one runner invocation may execute the accepted evaluator exactly once for
each of the eight opaque scenarios in the frozen order. It must then freeze the
complete raw evidence without interpretation or repair, permit a separate
oracle-blind raw-evidence verification, and permit a later protected comparison
by the benchmark custodian.

## Freeze Binding

Any D-117 authorization must bind exactly to:

- decision `D-117`;
- family `FAM-D116-CIM-20260723-01`;
- evaluator commit
  `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`;
- runner manifest SHA-256
  `a0949d94b48a5935912fcafd549dcce138ce2a592627fbdf0ebe4b3faba00590`;
- runner inventory-file SHA-256
  `d0aba02653bfb5ef551e7d803fbcf76f3d0ac5c2468805ef558d3674e1a7e741`;
- static aggregate SHA-256
  `9d7ce69ed630654eaf1a81b19f16cb02b3bbf7f179a174b78380cff17703c1eb`;
- the frozen scenario-order hash inside the runner manifest; and
- eight authorized audit attempts inside one runner invocation.

## Exact Command

This command is prepared but not authorized:

```text
C:\Users\User\.codex\visualizations\2026\07\16\019f694e-e2b3-7863-8d6d-5f7c9300d695\d116r4\python_env\Scripts\python.exe -B C:\Users\User\.codex\visualizations\2026\07\16\019f694e-e2b3-7863-8d6d-5f7c9300d695\d116r4\controls\run_semantic_once.py --authorization C:\Users\User\.codex\visualizations\2026\07\16\019f694e-e2b3-7863-8d6d-5f7c9300d695\d116r4\runtime\authorization\d117_authorization.json
```

The authorization file is intentionally absent. It may be created only after
explicit owner acceptance of D-117.

## Required Sequence

1. Create one authorization file bound to the exact identities above.
2. Reverify static hashes, read-only flags, runtime emptiness, and absent
   consumption marker.
3. Invoke the exact command once.
4. Permit one evaluator attempt per opaque scenario, in frozen order.
5. Preserve raw command, stdout, stderr, exit, publication, attempt order, and
   static pre/post evidence.
6. Freeze the complete raw evidence immediately.
7. Verify the raw evidence in an oracle-blind context.
8. Compare against the protected oracle only in a separate custodian context.
9. Return the result, limitations, and any next decision to the owner.

## Explicit Prohibitions

D-117 would not authorize:

- retry, resume, overwrite, repair, or a second runner invocation;
- reuse of the authorization for another family, runner, or evaluator;
- tuning, evaluator changes, scenario changes, or oracle-guided adjustment;
- protected comparison inside the runner;
- deletion or replacement of failed or partial raw evidence;
- public-package or prior held-out reruns;
- P4.3 release work; or
- release, accuracy, false-positive, false-negative, certification,
  conformity, or engineering-correctness claims before comparison and review.

## Owner Review Question

Does the project owner accept D-117 exactly as bounded above?

Until the answer is explicit, semantic execution remains prohibited and
release remains held by `AIR-003`.
