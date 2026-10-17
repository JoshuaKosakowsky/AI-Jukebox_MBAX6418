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
- Local setup only: **do not push, create a remote, open remote issues/PRs or
  change GitHub settings** until explicitly authorized. Future repo is public;
  main protection is specified in docs/GITHUB_SETUP.md.
- Credentials stay server-side in environment variables or ignored `.env`.
  No keys in browser code, logs, errors, screenshots, docs, chat, GitHub or archives.
- No user uploads or voice references in Git/archives; no bundled third-party
  music, lyrics, art or voice samples. Required class-generated samples must ship.
- Use the four required class services in docs/ASSIGNMENT.md. No paid features
  and no app requests to port 9000. Keep the original starter prompt unchanged.
- Confirm service contracts from supplied documentation; do not guess payloads.
  Service calls are deliberate, bounded and recorded, never part of offline
  tests. This setup task does not authorize generation or other service calls.
- Report implemented, tested and unchecked behavior accurately.

## Keep work moving

- Fix small, reversible problems within the authorized task directly: a typo,
  local validation error, missing import or straightforward test adjustment
  does not need a separate issue, planning document or permission request.
- Keep the fix in the current PR if it supports the same acceptance checks.
  Separate work when it changes scope, a shared interface, data handling, or
  another contributor's ownership. Document deferred work briefly and proceed
  with unaffected work. Do not ignore security or correctness failures.
- Use the simplest existing implementation that meets the requirement. Avoid
  speculative abstractions, optional features and unrelated refactors.
- Share stable contracts before parallel work. Coordinate interface changes
  with consumers; do not code against an assumed unmerged implementation.
- Default to `codex/<task>` branches from main; no direct main commits after
  bootstrap. Keep one substantial PR active per contributor. PR scope and
  review rules live in CONTRIBUTING.md; commit style in docs/COMMITS.md.
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

## Done

A PR meets its stated checks, has relevant passing validation, reviewed safe
files, current affected docs and a handoff. A feature milestone is done only
after its user flow is verified on merged main. Partial PRs must not close it.
