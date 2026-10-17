# GitHub repository and protection

Public repository: [AI-Jukebox_MBAX6418](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418).
Owner: JoshuaKosakowsky. Team workflow is active, including for setup changes.
Joshua/the team handles collaborator invitations and issue lead/contributor
assignments. Agents must not add people or change assignments in this task.

[Publication issue #11](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11)
records the initial publication, CI and protection readback. Local briefs are
published as issues #1-#11 and linked from PLAN.md. Check live GitHub evidence;
the checked-in JSON alone never proves enforcement.

## Required main protection

The Assignment 2 baseline was inspected on 2026-10-15 at commit
1a19c33ab9929dd2796ac7a5ea53247602a0cd32. The required policy is saved in
[main-protection.json](../.github/main-protection.json):

- Strict required status check `test`, GitHub Actions app ID 15368.
- One approving review; dismiss stale approvals on new commits.
- Require approval of the most recent reviewable push.
- Require conversation resolution; enforce protection for admins.
- No code-owner review, signed-commit or linear-history requirement.
- Force pushes and branch deletion disabled; branch not locked.

All changes use task branches and reviewed PRs. Do not disable admin enforcement,
weaken these rules or update main directly. Historical preparation integrations
are audit records, not permission for future exceptions. An unavailable reviewer's
independently verified-as-resolved review may be dismissed under CONTRIBUTING's
documented procedure by someone with actual permission; other protections remain.

## Local guards

Configure core.hooksPath=.githooks, core.longpaths=true and jukebox.allowPush=true
as shown in README. Hooks block main commits after bootstrap and all direct main
updates/deletion; authorized task-branch pushes are permitted. They complement
GitHub's server enforcement and do not grant a local exception to the PR rules.

## Work and delivery

Use the requirement-mapped issues in [PLAN](../PLAN.md), task branches and reviewed
PRs. Keep type/status labels and actual task progress current. Invitations and
assignments remain with Joshua/the team; missing reviewers do not permit bypasses.
The four minimal generation contracts are verified in docs/SERVICE_CONTRACTS.md;
app features are still unimplemented. CI validates scaffold and gates only.
Keep the repo public through grading. Follow [TESTING](TESTING.md) for the final
independent GitHub ZIP and acceptance checks.
