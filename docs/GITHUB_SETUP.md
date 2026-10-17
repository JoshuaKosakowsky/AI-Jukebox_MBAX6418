# GitHub setup - future authorized publication only

**Current state: local only. No remote exists. Nothing has been pushed.**
The user explicitly prohibited pushing. Do not execute remote write commands
until a later explicit instruction authorizes publication and configuration.

Recommended name: `AI-Jukebox_MBAX6418`.
Planned owner: JoshuaKosakowsky (confirm before publishing).
Visibility: **public**, per user instruction. No GitHub URL exists yet.

## Verified Assignment 2 baseline

Read-only GitHub API inspection on 2026-10-15 America/Denver:
`JoshuaKosakowsky/Course-Assistant_MBAX6418`, main commit
`1a19c33ab9929dd2796ac7a5ea53247602a0cd32`.
No repository rulesets were returned. Classic main protection was:

- Required status check `test`, GitHub Actions app ID 15368.
- Strict checks: branch must be up to date before merge.
- One approving review; dismiss stale approvals on new commits.
- Require approval of the most recent reviewable push.
- Require conversation resolution; enforce protection for admins.
- No code-owner review requirement; no signed-commit or linear-history rule.
- Force pushes and branch deletion disabled; branch not locked.

The API update payload in `.github/main-protection.json` preserves these
settings for later application. It is inert configuration; a JSON file cannot
protect a branch on GitHub.

## Local guards

Setup configures `core.hooksPath=.githooks`, `core.longpaths=true` (Windows path
length), and `jukebox.allowPush=false`. The pre-commit hook blocks main after
bootstrap; pre-push blocks all pushes unless locally enabled and always blocks
main updates/deletion. Git hooks are per checkout, bypassable, and not equivalent
to server enforcement. Teammates must install them per README after cloning.
Initial main bootstrapping on GitHub needs a deliberate hook override only after
publication authorization; never silently disable these controls.

## Checklist for the later publication task

1. Obtain explicit authorization for remote creation/push/protection. Verify
   account, final name, public-safe files, current branch and clean working tree.
2. Create the empty public remote, add origin, and publish the reviewed initial
   main baseline. Document any deliberate local bootstrap override. Never merge
   later work through this exception.
3. Enable Actions and wait for CI job `test` to run. Verify its exact context.
4. Apply `.github/main-protection.json` to the new repository's
   `/branches/main/protection` API endpoint. Verify the response/readback matches
   every setting above. Do not claim protection before successful readback.
5. Inspect effective repository rules too. Keep main protected; don't weaken
   rules to bypass failed checks, missing approvals, or administrator policy.
   Confirm who has review-dismissal permission. CONTRIBUTING.md permits recorded
   dismissal of an independently verified-as-resolved review when its original
   reviewer is unavailable; all remaining protections still apply.
6. Set `jukebox.allowPush=true` locally only once publishing is authorized.
   Main pushes stay locally blocked; future changes use reviewed PRs.
7. Confirm teammate identities/access. Create or reuse the required labels
   defined in CONTRIBUTING.md before creating work issues from docs/ISSUES.md;
   retain requirement/case IDs from docs/acceptance.json, choose owners/review
   buddies, add the actual issue links to PLAN.md, and apply
   their type/status labels and claim owners. Ensure every teammate contributes
   and reviews. Do not invent accounts.
8. Update README, PLAN and handoff with the actual URL, protection verification,
   commands/results and remaining work. Never commit credentials.

Do not store collaborator names, remote URLs or issue IDs as facts until they
exist. The shared repository must remain public and accessible through grading.
