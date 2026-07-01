# Mechanical Technical Document Evaluation Harness

This repository starts as a **case-definition and validation system** for synthetic mechanical-engineering workflows.

Month 1 does not run an AI model. It establishes valid tasks, controlled input assets, isolated references, deterministic evaluator specifications, and tests. Later, the same cases can be run with a direct-model baseline, OpenClaw, or another agent harness without rewriting the cases.

## Month 1 result

The repository separates:

- **Task specification** — instructions, input assets, required deliverable, and constraints.
- **Environment specification** — readable and writable locations plus reference isolation.
- **Evaluator specification** — gates, deterministic checks, scoring, and failure labels.
- **Case instance** — the concrete files and references for one runnable case.

Agents, traces, and results are intentionally absent from the case definition. They are runtime concerns added later.

## Repository map

```text
cases/          Concrete case instances and their input/reference assets
specs/tasks/    Reusable task definitions
specs/environments/
specs/evaluators/
schemas/        JSON Schemas for all specifications
src/            Python loader, validator, and CLI
tests/          Regression tests for the specification system
docs/           Scope, architecture, taxonomy, and review checklist
runs/           Ignored runtime outputs for later experiments
```

## Windows setup

Open PowerShell in this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

## Verify the starter

```powershell
python -m mech_eval_harness validate .
python -m mech_eval_harness list .
python -m mech_eval_harness inspect . MECH-001
pytest
```

Expected result:

- 3 cases validate.
- 3 cases are listed.
- The selected case and its linked specifications are summarized.
- All starter tests pass.

## Create the Git repository

```powershell
git init
git add .
git commit -m "Create schema-first mechanical evaluation harness"
git branch -M main
```

Create an empty GitHub repository named:

```text
mechanical-technical-document-evaluation-harness
```

Do not initialize it with another README, `.gitignore`, or license.

```powershell
git remote add origin https://github.com/YOUR-USERNAME/mechanical-technical-document-evaluation-harness.git
git push -u origin main
```

## Month 1 boundary

Read these before adding features:

- `docs/month_1_scope.md`
- `docs/out_of_scope.md`
- `docs/architecture.md`
- `docs/case_review_checklist.md`
