# Case Review Checklist

Complete this checklist before a case is accepted.

## Provenance and safety

- [ ] All content is synthetic, self-authored, public, or authorized.
- [ ] No confidential employer, client, or platform material is present.
- [ ] The task does not request engineering sign-off or autonomous release.
- [ ] The task is bounded and non-destructive.

## Authenticity

- [ ] The workflow resembles real mechanical, QA/QC, maintenance, or technical-document work.
- [ ] The deliverable is useful and not a contrived trivia answer.
- [ ] The inputs contain all information required to complete the task.

## Correctness

- [ ] The reference output was independently recalculated or checked.
- [ ] Units, signs, limits, and tolerances are explicit.
- [ ] No unstated convention changes the answer.
- [ ] The evaluator rejects the named critical failures.

## Evaluability

- [ ] The required deliverable has a defined filename and format.
- [ ] Missing or malformed output fails a gate.
- [ ] Deterministic checks are used wherever possible.
- [ ] Check weights sum to 1.0.
- [ ] Failure labels map to the documented taxonomy.
- [ ] Passing cannot be achieved through an obvious shortcut.

## Dataset discipline

- [ ] `workflow_id` is correct.
- [ ] `development` or `held_out` split is assigned.
- [ ] Any variant identifies its parent case.
- [ ] A new case adds meaningful coverage rather than duplicating an existing case.
