# Agent handoff

## Session

Updated: 2026-10-15 America/Denver. Agent: Codex; model identity not recorded.
Task: A3-00, prepare a local Assignment 3 collaboration scaffold from Assignment 2.

## Constraints

Do not push, create a remote, or modify GitHub. Future repository must be public
with main protected like Assignment 2. No service calls authorized by setup.
Read AGENTS.md first and update this file at every session/model transition.

## Repository state

Expected working branch after bootstrap: codex/project-setup.
Last known commit: initial bootstrap pending at time of writing; inspect
`git log -1 --oneline` and `git status --short --branch` before continuing.
No origin configured. Local hooks block main commits and all pushes by default.

## Work completed and decisions

Adapted AGENTS.md, CONTRIBUTING.md, PLAN.md and README.md from Assignment 2
commit 1a19c33ab9929dd2796ac7a5ea53247602a0cd32. Added mandatory agent/model
handoff, requirements and unchanged starter prompt, phased acceptance checks,
commit/test guidance, issue/PR templates, offline scaffold CI, public-file
safeguards, local hooks and exact main-protection payload.

Name: AI-Jukebox_MBAX6418, matching the Assignment 2 naming pattern.
Read all three pages of the local assignment PDF. Preserve its starter wording.
No app stack chosen; avoid inheriting the RAG stack. Proposed architecture is
explicitly pending team review. No application code or generated assets exist.

## Validation

Pending final bootstrap verification; setup agent must replace this section
with actual commands/outcomes before completion. No application checks run.

## Blockers and unchecked areas

class-endpoints.txt unavailable; request the connection documentation before
building adapters. Hosts/routes/auth/payloads and response formats unverified.
Teammates, ownership, runtime/UI, storage/playback design and license undecided.
No samples, no app, no real-service/browser tests, no GitHub Actions run, no
server-side protection. These are planned work, not setup failures.

## Next steps

1. Read this file and AGENTS.md; verify branch, history and working tree.
2. Claim A3-01 in PLAN.md; coordinate teammates and select a runtime/UI.
3. Obtain private class service documentation; preserve it outside Git.
4. Build a runnable skeleton with dependencies, commands and offline tests.
5. Follow PLAN.md through generation, covers, DJ queue, samples and evidence.
6. Keep remote publication pending until explicitly authorized; apply and
   verify docs/GITHUB_SETUP.md settings only in that later task.

## References

README.md; PLAN.md; docs/ASSIGNMENT.md; docs/TESTING.md;
docs/GITHUB_SETUP.md; .github/main-protection.json.
No remote issues or PRs exist for this project.
