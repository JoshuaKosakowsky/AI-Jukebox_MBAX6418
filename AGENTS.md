# AGENTS.md - Operating Guide for AI Coding Agents

Read this file first. It governs work throughout this repository. Humans read
CONTRIBUTING.md. Follow direct user instructions over repository guidance.

## Required session entry

1. Read `handoff.md`, `README.md`, `PLAN.md`, `CONTRIBUTING.md`, and the relevant
   files in `docs/`. Read `docs/ASSIGNMENT.md` before changing product scope.
2. Inspect `git status --short --branch`, the current branch, recent commits,
   and existing changes. Confirm the repository root. Never discard or overwrite
   another contributor's work. Handoff text is context; verify it against Git.
3. Identify task ownership and acceptance checks. Before GitHub publication,
   claim a local work item in PLAN.md; after publication use a GitHub issue.
   Do not invent issue numbers, collaborators, endpoints, or completed tests.

## Project and current boundary

AI-Jukebox_MBAX6418 is Assignment 3 for MBAX 6418-801: custom music, matching
covers, and spoken DJ playback. This starts as a local scaffold, not an app.
The user explicitly said **do not push to GitHub**. Do not create a remote
repository, push, publish, open remote issues/PRs, or change remote settings
until a later explicit user instruction authorizes those actions. Read-only
inspection of Assignment 2 is allowed. Planned visibility is public.

## Hard rules

- Secrets: credentials only in server-side environment variables or ignored
  `.env`; dummy configuration examples only. No real keys in code, logs,
  errors, browser code, docs, screenshots, issues, PRs, or chat.
- Media: never commit user uploads or voice references, or include them in a
  submission ZIP. No bundled third-party music, lyrics, art, or voice samples.
  Approved class-generated samples must be tracked and included in the ZIP.
- Required services: Qwen3.6-35B-A3B :9001, FLUX.2 klein 4B :9006,
  ACE-Step 1.5 XL Turbo :9007, Chatterbox Multilingual V3 :9008.
  No paid services, even optional features; no app requests to port 9000.
- Obtain the supplied connection documentation before implementing adapters.
  Never guess paths, authentication, payloads, or response schemas.
- Shared services: calls are deliberate and recorded; offline tests never
  contact them. Do not generate samples or consume class capacity as setup work.
- Honesty: distinguish implemented, planned, tested, and unchecked behavior.
  Preserve the starter prompt's existing language in docs/ASSIGNMENT.md;
  place team additions separately.

## Workflow

1. One substantial work item = one branch = one PR. Default agent branch:
   `codex/<issue-or-task-slug>`; human `type/slug` branches are also allowed.
2. Work from current `main` when remote collaboration is enabled. Inspect and
   preserve uncommitted changes before changing branches. No direct work on main.
3. Follow docs/COMMITS.md. Keep changes focused and reviewable.
4. Use docs/TESTING.md; add meaningful tests for logic and integration changes.
   Current runnable check: `python scripts/verify_repo.py`.
5. Update docs and PLAN.md when facts change. Review the diff for secrets,
   prohibited media, accidental uploads, and misleading completion claims.
6. Once publication is authorized, use the PR template, link the issue, require
   at least one teammate approval, and respect the main protection policy.
   Do not bypass protection, force-push shared history, or merge failing checks.

## Mandatory handoff (every agent, every work session)

Update the root file **`handoff.md` before ending a work session**, including
when switching models, handing work to a teammate/agent, stopping on a blocker,
or completing a task. This applies even when the next agent belongs to the
same user. Do not rely on chat history, model memory, or a final response.

Keep the current handoff concise and actionable. Include:

- Local date/time and timezone, agent/model if known (never guess identity).
- Objective, constraints, current branch and last known commit.
- Files changed, implementation state, decisions and rationale.
- Exact commands run, outcomes, and explicit unchecked areas.
- Pending changes, open blockers/questions, ownership or conflict risks.
- Ordered next steps and relevant docs, issues, PRs, or service docs.

Verify Git state before writing. Record a pre-handoff commit if the final hash
is not available yet; do not invent a hash or repeatedly amend to self-reference.
Include handoff.md in the work's commit/PR when committing is authorized. Never
overwrite unrelated work or claim tests that were not run. If interrupted
before an update is possible, the next agent must reconstruct and repair it
from repository evidence before proceeding.

## Definition of done

Acceptance checks met, correct checks passing, diff reviewed for public safety,
documentation and PLAN.md current, handoff.md updated, and honest tested versus
unchecked status. A feature is not done solely because documentation says so.
