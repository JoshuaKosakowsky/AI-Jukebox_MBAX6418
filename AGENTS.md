# Agent guide - AI Jukebox, MBAX 6418-801

Follow direct user instructions first. This guide applies throughout the repo.

## Start and finish

1. Read `handoff.md`; check branch, recent commits and working-tree changes.
   Preserve others' edits. Handoff claims must be checked against the repo.
2. Read the assigned task and relevant acceptance checks in `PLAN.md`. On your
   first visit, also read README, CONTRIBUTING and docs/ASSIGNMENT.md; afterward
   read only guidance relevant to changed work. Do not invent owners or issue IDs.
3. Complete the smallest useful change, run relevant checks, and update
   **handoff.md before ending every session or switching agents/models**.

## Current boundary and safeguards

- Local commits on working branches are authorized; do not ask again for them.
- Team workflow is active: use task branches and reviewed PRs for all changes,
  including setup. No direct main commits/pushes or protection bypasses.
  Main protection follows docs/GITHUB_SETUP.md and applies to admins too.
- Collaborator invitations and issue lead/contributor assignments are for
  Joshua/the team to arrange; do not add people or change assignments in this task.
  The PR author cannot approve their own PR; any teammate without commits on the
  PR may review/approve/request changes, and the approving reviewer or the lead merges.
- Credentials stay server-side in environment variables or ignored `.env`.
  No keys in browser code, logs, errors, screenshots, docs, chat, GitHub or archives.
- No user uploads or voice references in Git/archives; no bundled third-party
  music, lyrics, art or voice samples. Required class-generated samples must ship.
- Use the four required class services in docs/ASSIGNMENT.md. No paid features
  and no app requests to port 9000. Keep the original starter prompt unchanged.
- Use docs/SERVICE_CONTRACTS.md for the verified request baseline; check supplied
  documentation before changing it. Do not guess payloads. Generation calls must
  be deliberate, bounded and within the user-assigned task, never triggered by
  startup, CI or offline tests. A model/session switch does not justify new calls.
- Report implemented, tested and unchecked behavior accurately.

## Keep work moving

- Fix small, reversible problems within the authorized task directly: a typo,
  local validation error, missing import or straightforward test adjustment
  does not need a separate issue, planning document or permission request.
- Keep the fix in the same change if it supports the same acceptance checks.
  Separate work when it changes scope, a shared interface, data handling, or
  another contributor's ownership. Document deferred work briefly and proceed
  with unaffected work. Do not ignore security or correctness failures.
- Use the simplest existing implementation that meets the requirement. Avoid
  speculative abstractions, optional features and unrelated refactors.
- Share stable contracts before parallel work. Coordinate interface changes
  with consumers; do not code against an assumed unmerged implementation.
- Default to `codex/<task>` branches from main; no
  direct main commits. Keep one substantial PR active per contributor. PR scope
  and review rules live in CONTRIBUTING.md; commit style in docs/COMMITS.md.
  If a blocking reviewer is unavailable, follow its documented independent
  verification/dismissal exception; never waive an unresolved finding.
- Current check: `python scripts/verify_repo.py`. Use docs/TESTING.md for
  application changes. After checks pass, rerun only for changes, failures or
  unresolved risk. Do not create tests that merely restate documentation edits.

## Short, mandatory handoff

Keep the current entry to roughly 15-25 lines, plus necessary inherited notes:
date/timezone and agent; task/branch/base commit; changed files and decisions;
commands/results and unchecked areas; blockers; next 1-3 actions and links.
Do not copy chat transcripts or repeat the project plan. Never include secrets.

Preserve another agent's pending notes. Parallel contributors use task-labelled
entries; the integration owner consolidates them on merge. Record a pre-handoff
hash rather than repeatedly amending to reference the handoff's own commit.
If interrupted, the next agent reconstructs state from Git before proceeding.

## Deliver the brief, not just components

Map the task to R01-R36 in docs/acceptance.json and its brief in docs/ISSUES.md.
Check the full docs/ASSIGNMENT.md source when changing scope. Required behavior,
safe operation and reproducible delivery take priority over optional polish.
After each integrated milestone reconcile uncovered/unchecked requirements; do
not wait until submission. Use the normal launcher for live/browser evidence;
fixtures, backend tests, merged PRs and honest limitations do not satisfy missing
features. Run the coverage gate with relevant checks; only the explicit release
check with independent ZIP evidence can establish recorded submission readiness.

## Done

A PR meets its stated checks, has relevant passing
validation, inspected safe files, current affected docs and a handoff. A feature
milestone is done only after its user flow is verified on integrated main. Partial PRs must not close it.
