# Agent handoff

## Session

Updated: 2026-10-15 19:39 MDT (America/Denver). Agent: Codex; model identity not recorded.
Task: follow-up to A3-00, document useful GitHub labels as a requirement.

## Constraints

Do not push, create a remote, or modify GitHub. Future repo must be public
and main protected like Assignment 2. Maintain this file every agent/model
transition. No class service calls are part of this documentation change.

## Repository state

Branch: `codex/project-setup`. Last known commit before this update:
`ef7032bb42ab71eeafc544f9f904f4ea2934843f`. Working tree was clean at entry.
This session changes CONTRIBUTING.md, docs/GITHUB_SETUP.md and handoff.md;
these changes are to be committed locally. Inspect git log and git status for
final commit/state. No remote is configured; pushes remain disabled locally
(`jukebox.allowPush=false`).

## Work completed and decisions

Prior setup created all 23 scaffold files and verified the original starter
prompt, local guards, ignored private paths and exact saved protection policy.
See docs/TEST_RESULTS.md for that earlier evidence.

Added a required, small label scheme in CONTRIBUTING.md: one primary type
(bug, enhancement, documentation, testing or infrastructure) and one current
status (ready, in progress, blocked or review) on each open work issue and PR.
Owners maintain labels and reviewers check them. Assignees track ownership;
GitHub closed/merged states track completion. Labels become required when
GitHub collaboration is authorized; no remote labels have been created.
Updated the publication checklist to create/reuse labels before work issues.

## Validation

`python scripts/verify_repo.py`: PASS, all 23 tracked files and local links.
`git diff --check`: PASS. Reviewed the three-file diff for scope and accuracy.
Documentation-only change; no app/service/browser tests apply.

## Blockers and unchecked areas

class-endpoints.txt unavailable; request the connection documentation before
building adapters. Hosts/routes/auth/payloads and response formats unverified.
Teammates, ownership, runtime/UI, storage/playback design and license undecided.
No samples, no app, no real-service/browser tests, no GitHub Actions run, no
server-side protection. These are planned work, not setup failures.

## Next steps

1. Read AGENTS.md and this file; verify branch, current commit and working tree.
2. Claim A3-01, coordinate teammates, choose stack and obtain private endpoint
   documentation before writing service adapters.
3. Follow PLAN.md for implementation, samples, test evidence and ZIP deployment.
4. Only after explicit publication authorization, follow docs/GITHUB_SETUP.md,
   including the required label setup and main protection verification.

## References

CONTRIBUTING.md (required labels); PLAN.md; README.md; docs/ASSIGNMENT.md;
docs/GITHUB_SETUP.md; docs/TESTING.md; docs/TEST_RESULTS.md.
No remote issues, PRs or labels exist for this project.
