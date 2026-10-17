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

Keep each PR focused on one behavior; milestone issues may have several child
issues/PRs. Related small fixes stay with the current task. Agent branches use
`codex/<task>`; human branches may use `feat/<slug>`, `fix/<slug>`, etc.
Use `Refs #N` for partial work and `Closes #N` only when that issue's checks
are met. Before publication use a PLAN ID. Commit wording preferences should
not block an otherwise correct change. Update handoff.md each session.
