# Integration Instructions

> Historical transfer instructions. The modernization package was merged in PR #24 and these commands are no longer current project control.

This package modernizes project control and documentation. It does **not** claim that the local repository was modified.

## Recommended Integration

From PowerShell:

```powershell
cd C:\Projects\mechanical-technical-document-evaluation-harness

git status
git switch -c planning/gpt-5-6-modernization
```

Copy these files into the repository root while preserving paths:

- `AGENTS.md`
- `PROJECT_CONTEXT.md`
- `PROJECT_INSTRUCTIONS_5_6.md`
- `MEMORY_UPDATE.md`
- `docs/...`

Replace the project-source `gantt.xlsx` with the supplied workbook only after retaining a backup or confirming the previous version is committed.

Do not overwrite the existing README automatically. Merge relevant sections from `README_MODERNIZATION_PATCH.md` into it while preserving verified setup, CLI, demo, and release instructions.

Then inspect:

```powershell
git status --short
git diff --stat
git diff
```

Run the existing verification suite before committing:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
python scripts\run_mvp_baseline.py
```

Use the repository's existing demo/acceptance commands as documented in the current README and release files.

Suggested commit:

```powershell
git add AGENTS.md PROJECT_CONTEXT.md PROJECT_INSTRUCTIONS_5_6.md MEMORY_UPDATE.md README_MODERNIZATION_PATCH.md gantt.xlsx docs
git commit -m "Modernize project control for v0.3 package assurance pilot"
git push -u origin planning/gpt-5-6-modernization
```

## Acceptance Before Merge

- Existing v0.2.0 tests and baseline remain unchanged and passing.
- The annotated v0.2.0 tag still resolves to the accepted release commit.
- `gantt.xlsx` opens without repair warnings.
- `Start Here`, `AI Context`, `Pilot Dashboard`, and `Pilot Gantt` agree on active WBS P0.1.
- No implementation work is represented as complete.
- README changes preserve verified run instructions.
