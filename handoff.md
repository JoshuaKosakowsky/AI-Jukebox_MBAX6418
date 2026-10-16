# Agent handoff

## Session

Updated: 2026-10-15 19:15 MDT (America/Denver). Agent: Codex; model identity not recorded.
Task: A3-00, prepare a local Assignment 3 collaboration scaffold from Assignment 2.

## Constraints

Do not push, create a remote, or modify GitHub. Future repository must be public
with main protected like Assignment 2. No service calls authorized by setup.
Read AGENTS.md first and update this file at every session/model transition.

## Repository state

Current branch: `codex/project-setup`.
Last known commit before this handoff update: `9d8ee0e2139cdbe623cfef8706b91e5bdcd75a65`
(the initial bootstrap on main). This handoff and validation record are the
only pending changes, to be committed on this working branch. Read
`git log -1 --oneline` for the final commit and verify
`git status --short --branch` before continuing. No origin is configured.
Local hooks block main commits and all pushes by default.

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

- `python scripts/verify_repo.py`: PASS for all 23 tracked files, links,
  tracked-file safeguards, handoff sections and exact saved protection policy.
- Compared original PDF starter prompt to docs/ASSIGNMENT.md using pypdf:
  PASS, identical words after whitespace normalization.
- `git hook run pre-commit` on main after bootstrap: blocked as intended.
- `git hook run pre-push` with default local config: blocked as intended.
- `git -c jukebox.allowPush=true hook run --to-stdin=<temporary probe> pre-push`:
  main update and deletion blocked; task-branch ref allowed. This is a local
  hook invocation, not a push. Temporary input removed. The first probe used
  a shell pipe, which Git hook run does not forward; corrected to --to-stdin
  and reran all ref cases successfully. No hook defect was observed.
- `git hook run pre-commit` on codex/project-setup: allowed as intended.
- `git config --local --get jukebox.allowPush`: false (unchanged by probes).
- `git remote -v`: empty; no GitHub writes or pushes occurred.
- `.env`/endpoint/upload/reference paths are ignored; sample audio is permitted
  under assets/samples/ so required approved samples can ship (verified below
  in the final check). No app, browser, endpoint or generated-media tests run.

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
