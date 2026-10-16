# Contributing - AI Jukebox (MBAX 6418-801)

Use issues, branches, commits, pull requests, teammate reviews, and repeatable
tests as in Assignment 2. Every teammate must contribute meaningfully and review
someone else's work. AI agents must follow AGENTS.md and maintain handoff.md.

## Current local-only stage

No GitHub publishing is authorized. Record proposed work and ownership in
PLAN.md until remote issues are authorized. No remote exists. Keep `main` as
the baseline and work on `codex/<task>` or `type/slug` branches. The setup
commit on main is the sole bootstrap exception. Do not push or change remote
settings. See docs/GITHUB_SETUP.md for the future publication checklist.

## Team workflow after publication

1. Create or claim an issue with acceptance checks; check existing issues first.
   Coordinate overlapping files and record the owner in PLAN.md.
2. Branch from up-to-date main. One issue = one branch = one PR.
3. Follow docs/COMMITS.md: type prefix, imperative subject of at most 50
   characters, no trailing period; blank line then body wrapped at 72.
4. Add meaningful tests for changed logic and wiring. Run the offline checks
   and describe any deliberate real-service tests (docs/TESTING.md).
5. Check the diff for secrets, uploads, voice references, and third-party media.
6. Open a PR with the template and `Closes #N`. State tested and unchecked
   behavior and include reviewed screenshots for UI changes.
7. Obtain at least one teammate approval; address feedback on the same branch.
   Passing `test`, up-to-date branches, resolved conversations, and latest-push
   approval are required. Admins follow the same protection rules.
8. Update PLAN.md and handoff.md before finishing. A model switch is a handoff.

## Bugs and review

One bug per issue. Report the problem with a unique summary, reproducibility,
precise steps, expected versus actual results, environment, and safe evidence.
Separate facts from speculation. Never paste keys or upload private recordings.

Review scope against the issue, functionality and failure cases, test evidence,
credential handling, media provenance, sample inclusion, docs, and handoff.
Be specific and constructive. Do not approve your own work in place of a
teammate review or weaken branch protection to merge.

## Security and public assets

See AGENTS.md and docs/ASSIGNMENT.md. Use class services only; no paid services
or requests to port 9000. Credentials stay server-side. User uploads and voice
references never enter Git or archives. Only approved class-generated samples
may be bundled, with provenance. No license is chosen for this scaffold;
public visibility alone does not grant a license. Agree licensing as a team.
