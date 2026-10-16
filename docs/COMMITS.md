# Commit message conventions

Adapted from Assignment 2. Follow for commits and PR titles.

| Type | Purpose |
|---|---|
| feat | New feature |
| fix | Bug fix |
| refactor | Restructure without behavior change |
| chore | Repository maintenance |
| perf | Performance improvement |
| ci | Continuous integration |
| ops | Deployment/operations |
| build | Build system or dependencies |
| docs | Documentation |
| style | Formatting only |
| revert | Revert a change |
| test | Tests |

Use `type: Capitalized imperative subject`, at most 50 characters, no final
period. Blank line before body; wrap body at 72 characters and explain what
and why. One logical change per commit.

```text
feat: Add instrumental song generation

Let listeners create tracks without vocals using the class music
service. Preserve generation settings with each library entry.
```

One issue = one branch = one PR. Agent branches default to `codex/<task>`;
human branches may use `feat/<slug>`, `fix/<slug>`, `docs/<slug>`, etc.
Use `Closes #N` only for an existing issue. During local-only setup, use the
PLAN.md work item ID instead. Update handoff.md with each session's work.
