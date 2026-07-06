# v0.2.0 Final Acceptance Report

## Release decision

**FINAL ACCEPTANCE MATRIX: PASS**

The Mechanical Technical Document Evaluation Harness version `0.2.0` was accepted and released on July 5, 2026.

- Accepted commit: `45336a21c9c5f4dcd4b3bd009d05183621061b5d`
- Annotated tag: `v0.2.0`
- Tag object: `8d426d295b883433a68a86f16abe4c4a170a41ee`
- Tagged commit: `45336a21c9c5f4dcd4b3bd009d05183621061b5d`
- Tag pushed to the origin remote: yes

## Clean-clone acceptance environment

- Python: `3.12.6`
- Installed package: `mechanical-technical-document-evaluation-harness`
- Installed package version: `0.2.0`
- Source: clean clone of `origin/main`
- Clean-clone commit matched accepted commit: yes
- Final clean-clone Git state: clean

## Acceptance matrix

| Check | Result |
|---|---|
| Exact clean-clone commit | PASS |
| Package and release-document version consistency | PASS |
| Clean Python 3.12 installation | PASS |
| Five-case repository validation | PASS |
| Complete automated test suite: 121 tests | PASS |
| Nine-scenario MVP baseline reproduction | PASS |
| Two-scenario portfolio-demo reproduction | PASS |
| Eleven generated result records at `harness_version = 0.2.0` | PASS |
| Required release claim boundaries present | PASS |
| Clean-clone Git state | PASS |
| Annotated tag points to accepted commit | PASS |
| Remote tag verification | PASS |

## Baseline reproduction

The clean-clone baseline reproduced all expected scenarios:

- development oracle checks: `4/4`;
- held-out oracle checks: `1/1`;
- curated fault-injection detections: `4/4`.

The baseline remains harness-verification evidence. It is not evidence of AI-model or agent performance.

`MECH-003` remains separately reported as held-out and is not claimed to be a pristine blind case because it was authored and reviewed before the split was established.

## Portfolio-demo reproduction

The clean-clone portfolio demo verified both committed `MECH-002` scenarios:

- passing artifact: exit code `0`, score `1.00`;
- structurally valid angular-velocity unit error: exit code `1`, score `0.75`, failure mode `UNIT_ERROR`.

Both scenarios produced immutable local result records.

## Result-version verification

The acceptance run produced eleven result records:

- nine baseline records;
- two portfolio-demo records.

All eleven reported:

```text
harness_version = 0.2.0
```

## Release integrity

Before tag creation:

- the release branch matched `origin/main`;
- the branch pointed to the accepted commit;
- the working tree was clean;
- no prior `v0.2.0` tag existed.

After tag creation:

- the annotated tag was pushed successfully;
- the peeled remote tag resolved to `45336a21c9c5f4dcd4b3bd009d05183621061b5d`;
- the local release branch remained clean.

## Acceptance-wrapper incidents

Two earlier acceptance-wrapper attempts failed before the acceptance matrix completed:

1. a native-command quoting defect affected the installed-version lookup;
2. a PowerShell parsing defect affected the generated wrapper script.

These were wrapper defects, not harness failures. The corrected clean-clone run completed every acceptance step successfully and supersedes the incomplete attempts.

## Interpretation boundary

This release verifies a deterministic, JSON-first evaluation kernel with versioned cases, mandatory gates, deterministic checks, weighted scoring, structured evidence, immutable local result records, regression tests, CI, a reproducible harness-verification baseline, a terminal portfolio demo, and explicit release limitations.

It does not establish:

- AI-model or agent performance;
- pristine-blind benchmark generalization;
- professional engineering authorization;
- engineering sign-off or autonomous release;
- production deployment readiness;
- multimodal, API, database, observability, agent-runtime, governance-pack, or RL capability.

All engineering outputs require review by an appropriately qualified person.

## Evidence-recording note

This normalized report and its machine-readable summary are post-release project-control evidence. They are intended to be committed after the `v0.2.0` tag and therefore are not part of the tagged source tree.
