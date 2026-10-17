# GitHub repository and protection

Public repository: [AI-Jukebox_MBAX6418](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418). Owner verified as JoshuaKosakowsky.
Publication authorized by the user on 2026-10-17 America/Denver. Collaborator
invitations are deferred; no usernames or review assignments have been invented.

[Publication issue #11](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11) is the authoritative record of the initial
push, CI run and branch-protection readback. Check its actual evidence before
claiming remote protection; the checked-in JSON alone never proves enforcement.
The local task briefs are published as issues #1-#11 and linked from PLAN.md.

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

## Local guards and bootstrap

Configured: core.hooksPath=.githooks, core.longpaths=true and jukebox.allowPush=true.
Task-branch pushes for assigned work are permitted. Local hooks block main changes
by default; the explicit solo option below permits only fast-forward main updates.
GitHub provides server enforcement.
New checkouts install these local settings from README; hooks are bypassable.

The initial publication uses a documented one-command hooksPath override solely
to seed main from the reviewed local scaffold. Later solo setup uses the explicit
exception below; hooks are never permanently disabled. Main protection was
applied after initial CI succeeded, then verified through the GitHub API. The exact
commands, resulting SHA, CI URL and policy readback are recorded in issue #11.

## Solo setup exception (current phase)

The owner is preparing the repository alone. Validated setup can be committed
and pushed directly to main, without creating a PR or requiring teammate review.
Use `git -c jukebox.soloSetup=true commit ...` and the same per-command option
for a normal fast-forward push. Keep the option out of persistent Git config.

The saved Assignment 2 team policy stays unchanged and enforced at rest. If it
blocks a user-authorized solo setup update, an owner with actual admin permission
may briefly disable admin enforcement, push the validated commit, then immediately
restore admin enforcement in a finally/cleanup step and read back the full policy.
Do not remove review/check rules, enable force pushes/deletion, or leave the
exception active. Record the resulting commit, CI and protection readback with
the setup evidence. This permission is limited to solo preparation; it cannot be
used to bypass a teammate's blocking findings or failed checks.

Before teammates begin contributing, confirm the full policy matches the saved
JSON and start the team branch/review workflow. No teammate is needed to approve
the preliminary setup itself.

## Team collaboration

Use the requirement-mapped issues in [PLAN](../PLAN.md), claim an owner/review
buddy, and work through branches and reviewed PRs. Main requires the policy above;
do not weaken it to merge failed checks or bypass missing approvals. An unavailable
reviewer's independently verified-as-resolved review can be dismissed under the
documented CONTRIBUTING exception by someone with actual dismissal permission.

Required type/status labels are configured. Keep real task state on the issues.
Add collaborators only when the user chooses them. The app and class-service
features are still unimplemented. The four minimal generation contracts are
verified in docs/SERVICE_CONTRACTS.md; CI validates scaffold and gates only.
Keep this public repo accessible through grading. Final release readiness is
separate from publication; follow [TESTING](TESTING.md) for the exact GitHub ZIP.
