# P4.2 External Benchmark Recovery Freeze Review

**Version:** 0.3.0

**Date:** 2026-07-23

**Status:** D-116 complete; D-117 owner review required

**Authority:** D-116

**Accepted predecessor main:** `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`

## Executive Result

D-116 is complete. A materially distinct, entirely synthetic carton-indexing
conveyor family and an oracle-blind one-shot runner were prepared outside the
ordinary repository. The final freeze passed all 8 mandatory controls and all
51 detailed controls.

The development-only publication sentinel ran exactly once in the final
physical runner pattern. It returned exit `0`, published all four schema-valid
outputs, reached `automatic_pass`, preserved exact static identities, and
exercised the former publication-path defect at a 264-character legacy staged
path.

No opaque scenario has been evaluated. Opaque semantic executions, held-out
publications, and protected comparisons remain zero. The D-117 authorization
file does not exist.

## Custody and Access

- Family: `FAM-D116-CIM-20260723-01`
- Runner: `RUNNER-D116-CIM-20260723-04`
- Opaque scenarios: 8
- Data rights: self-authored synthetic content
- Producer capsule: 129 files, aggregate SHA-256
  `ccaf7ed4a06e75549246f7443cc2e6fd16644f99be23297dc5a792b8158d2173`
- Protected capsule: 3 files, aggregate SHA-256
  `27911e904e37aaf4fda68f08162380bc67619305742dbbb94ade3845eb007002`
- Author inventory: 140 entries, SHA-256
  `6b2af81deeb298cac366fc215bbaf53244046b70fac50078d52cb42cd776e529`

The family, oracle, runner, and raw verification evidence remain outside Git.
The implementation context read only public-safe handoffs. The independent
review context accessed the protected oracle only to verify contract
completeness and scan for leakage; it published no protected semantic values.

This was an internal AI-assisted separation of duties under the same project
owner. It is not external independent assurance.

## Material Distinction

The family models a carton-indexing conveyor rather than a pump skid,
public-source research package, or overhead-crane hoist. Its equipment,
document identities, drawing set, BOM structure, datasheet/specification
records, controlled files, and scenario family were newly authored before
execution.

Independent checks confirmed:

- 8/8 manifests are schema-valid;
- all declared structured sources and controlled files are present;
- the accepted authority contract is complete;
- the protected oracle contract covers each opaque scenario exactly once;
- 258 producer-visible and runner-visible files contain zero protected-value
  leaks; and
- no expected state, finding, severity, comparison value, or scenario
  condition entered the producer or runner capsule.

## Runner Freeze

Revision 4 uses the short external root required to keep every staged path
inside the tested Windows boundary. Its frozen identity is:

- evaluator commit:
  `3a6766f6f1cc563b27c24fa07a9a4a2a7d1206f6`;
- exact evaluator Git blobs: 48/48;
- static files: 340/340 read-only;
- inventory entries: 339;
- static aggregate SHA-256:
  `9d7ce69ed630654eaf1a81b19f16cb02b3bbf7f179a174b78380cff17703c1eb`;
- inventory-file SHA-256:
  `d0aba02653bfb5ef551e7d803fbcf76f3d0ac5c2468805ef558d3674e1a7e741`;
- runner-manifest SHA-256:
  `a0949d94b48a5935912fcafd549dcce138ce2a592627fbdf0ebe4b3faba00590`;
- capsule interpreter SHA-256:
  `e725f520cfbb2e4844fe0a9fc8949236f20b0d67e470d1232618b99504a0691a`;
- capsule Python environment: 148 files;
- frozen runtime dependencies: 5 distributions and 139 files; and
- `__pycache__` directories and `.pyc` files: 0.

The runner requires a future authorization bound to D-117, the family, the
evaluator commit, the runner manifest, the static inventory, and the frozen
scenario order. It consumes itself at semantic start and has no retry, resume,
overwrite, tuning, or protected-comparison path.

## Publication Sentinel

The final independent sentinel verification passed:

- mandatory controls: 8/8;
- detailed controls: 51/51;
- pre-sentinel controls: 34/34;
- post-sentinel controls: 17/17;
- designated sentinel invocations: 1;
- retries: 0;
- outer and child exits: 0;
- output count: 4;
- result schema: valid;
- development state: `automatic_pass`;
- release hold: false;
- static pre/post identity: exact;
- inherited `PATH`, credentials, tokens, and proxies: not forwarded;
- target and actual runs path length: 193;
- calculated and actual longest staged path: 256;
- tested usable boundary: 259;
- former-defect legacy staged output path: 264; and
- post-sentinel bytecode artifacts: 0.

This is publication and runner evidence, not external benchmark-performance
evidence.

## Repository Verification

The public closeout records and governance transition passed:

- focused AI-governance tests: 22/22;
- protected-safe full regression: 340 passed, 1 expected Windows skip,
  88.33% coverage;
- repository validation: 5/5;
- Ruff: passed;
- repository publication sentinel: four outputs, `automatic_pass`;
- P4.1 development benchmark: 22/22;
- frozen v0.2 baseline: 9/9 using an explicit generated evidence directory;
- portfolio demo: 2/2; and
- AI governance: normal mode passed; strict release-ready mode returned `2`
  for `AIR-003` and pending D-117.

The first full-suite invocation used an unnecessarily long sandbox test root
and failed only when the development benchmark could not read its deeply nested
generated result path. The unchanged suite passed from the short generated root
`runs/t116`. This is recorded under the whole-tree path-budget control in
`IMP-035`; it is not presented as an evaluator semantic defect.

## Preserved Failed Revisions

Three runner revisions were rejected before any opaque execution:

1. Revision 1 exposed that a top-level vendored dependency path was not
   available inside the accepted sentinel's nested child.
2. Revision 2 exposed import-time Python bytecode mutation before static
   preflight.
3. Revision 3 passed every static control but its long physical root caused
   Windows error 206 while staging the development evaluator.

Each failed runner and verification record is preserved byte-for-byte. None was
retried, repaired in place, or used for an opaque audit. Their lessons are
retained as `IMP-033` through `IMP-035`.

## Claims Boundary

The freeze proves that the family and runner are ready for an owner execution
decision. It does not prove benchmark accuracy, false-positive or
false-negative performance, external assurance, product release readiness, or
engineering correctness.

Release remains held by `AIR-003`. D-117 remains pending.

## Next Decision

The separate
[D-117 execution gate](p4_2_external_benchmark_execution_gate_v0.3.0.md)
requests one runner invocation, containing one audit attempt for each frozen
opaque scenario, followed by immutable raw-evidence freeze, oracle-blind raw
verification, and separate protected comparison.

No semantic command may be executed before the project owner explicitly
accepts D-117.
