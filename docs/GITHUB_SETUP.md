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
Task-branch pushes for assigned work are permitted. Local hooks continue blocking
main commits and direct main updates/deletion. GitHub provides server enforcement.
New checkouts install these local settings from README; hooks are bypassable.

The initial publication uses a documented one-command hooksPath override solely
to seed main from the reviewed local scaffold. It does not permanently disable
hooks or permit later direct main pushes. Main protection is applied immediately
after the initial CI succeeds, then verified through the GitHub API. The exact
commands, resulting SHA, CI URL and policy readback are recorded in issue #11.

## Working from this repo

Use the requirement-mapped issues in [PLAN](../PLAN.md), claim an owner/review
buddy, and work through branches and reviewed PRs. Main requires the policy above;
do not weaken it to merge failed checks or bypass missing approvals. An unavailable
reviewer's independently verified-as-resolved review can be dismissed under the
documented CONTRIBUTING exception by someone with actual dismissal permission.

Required type/status labels are configured. Keep real task state on the issues.
Add collaborators only when the user chooses them. The app and class-service
features are still unimplemented/unverified; CI validates scaffold and gates only.
Keep this public repo accessible through grading. Final release readiness is
separate from publication; follow [TESTING](TESTING.md) for the exact GitHub ZIP.
