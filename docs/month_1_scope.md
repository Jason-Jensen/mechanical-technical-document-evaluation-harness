# Exact Month 1 Scope

## Objective

Produce a reliable local specification layer for mechanical technical evaluation cases.

The Month 1 artifact is not an AI application. It is the test-case foundation that future baselines and agents will execute against.

## Required deliverables

1. One GitHub repository with a clean `main` branch.
2. One Python 3.12+ virtual environment and installable local package.
3. JSON Schemas for:
   - case instances;
   - task specifications;
   - environment specifications;
   - evaluator specifications.
4. At least 8 synthetic, self-authored mechanical cases.
5. At least 3 workflow families with more than one instance in at least one family.
6. Input and reference assets stored separately for every case.
7. Deterministic evaluator specifications for every case.
8. A CLI that can:
   - validate the whole repository;
   - list cases;
   - inspect one case and its linked specifications.
9. At least 20 meaningful pytest tests.
10. A documented mechanical failure taxonomy.
11. A completed human review checklist for each case.
12. A tagged release named `v0.1.0`.

## Required case quality

Every Month 1 case must be:

- synthetic, self-authored, public, or explicitly authorized;
- mechanically correct;
- unambiguous enough to produce one checkable deliverable;
- economically or professionally plausible;
- bounded and safe;
- outside engineering sign-off or autonomous release;
- checkable primarily through deterministic evidence;
- associated with named failure modes;
- assigned to `development` or `held_out`.

At least two cases must be marked `held_out` before Month 1 ends. Do not tune evaluator logic against held-out results.

## Required failure coverage

The Month 1 set must collectively cover at least:

- wrong units or failed unit conversion;
- radial/diametral confusion;
- wrong revision;
- unsupported assumption;
- missing constraint;
- sign error;
- table misread;
- wrong formula;
- incomplete deliverable;
- failure to verify.

## Month 1 proficiency gate

These commands must exit successfully:

```text
python -m mech_eval_harness validate .
pytest
```

You must also be able to explain:

- the difference between a workflow and a case instance;
- why task, environment, evaluator, agent, trace, and result are separate;
- why reference assets are isolated from the agent workspace;
- why gates run before weighted checks;
- how to add a new case without editing Python;
- how to create a branch, commit a change, merge it, and restore a mistaken edit.

## Four-week sequence

### Week 1
Create the repository, specifications, schemas, CLI, tests, and three seed cases.

### Week 2
Add two additional cases and one second instance of an existing workflow. Expand validation tests.

### Week 3
Reach eight cases, add two held-out cases, and reach 20 tests.

### Week 4
Review every case, clean documentation, practise Git recovery, and tag `v0.1.0`.
