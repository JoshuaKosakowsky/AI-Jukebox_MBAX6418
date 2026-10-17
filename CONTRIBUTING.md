# Contributing - AI Jukebox, MBAX 6418-801

Agents follow AGENTS.md. Requirements live in docs/ASSIGNMENT.md. Every teammate
must contribute meaningfully and review a teammate's work.

## Work in small steps

1. Claim one substantial work item with acceptance checks, an owner and a review
   buddy. Before publication, record it in PLAN.md; afterward use GitHub issues.
2. Branch from current main (`codex/<task>` or `type/slug`). Keep one substantial
   PR active per contributor. A broad milestone can have several focused child
   issues/PRs; avoid long-lived dependent branches unless merge order is explicit.
3. Implement the smallest useful behavior. Fix related small problems in that
   change. Open separate work for independent bugs or scope/interface changes,
   not every typo, missing import or straightforward local correction.
4. Run relevant checks (docs/TESTING.md), inspect the diff and update affected
   docs. Use docs/COMMITS.md for readable commits; wording nits are non-blocking.
5. Open a PR with its result, issue link and actual validation. Use `Refs #N`
   for partial work; `Closes #N` only when that issue's checks are satisfied.
6. Address blocking findings together, update the branch, rerun affected checks,
   then request approval on that head. Keep handoff.md current each session.

Local setup remains **no push/no remote writes** until explicitly authorized.
Main protection, including teammate approval, passing `test`, up-to-date branches,
resolved conversations and latest-push approval, is mandatory for everyone.
See docs/GITHUB_SETUP.md. Do not bypass protection to accelerate merging.

## Integration and review

- Name an integration owner to coordinate dependencies and verify the combined
  app. Merge shared data/service contracts before their implementations diverge.
  Coordinate shared-file and interface changes with affected contributors.
- Each PR should demonstrate one behavior. If a reviewer cannot explain its
  result and checks briefly, split it by behavior; do not use a rigid line quota.
- **Blocking:** broken required behavior, unsafe handling, incompatible contracts,
  failed relevant checks or unmet acceptance criteria. Include reproduction and
  expected behavior. Batch findings from the review; new evidence may justify more.
- **Non-blocking:** preferences, wording, optional refactors and out-of-scope
  improvements. Mark them as suggestions; do not turn them into merge conditions.
- Review correctness and the user flow, not test counts alone. No self-approval.
  Parent features close only after their flow passes on merged main; child PRs
  may deliver tested components without claiming the whole feature is complete.

## Required labels (after publication is authorized)

Create/reuse the labels below before opening work issues. Every open work issue
and PR gets one primary type and one current status; the owner keeps them current.

| Type | Use |
|---|---|
| `bug` | Broken behavior |
| `enhancement` | New/improved feature |
| `documentation` | Instructions/report/handoff |
| `testing` | Tests and evidence |
| `infrastructure` | Setup, CI, dependencies, deployment |

Statuses: `status: ready` (claimable issue), `status: in progress` (active work
or draft PR), `status: blocked` (explain blocker and next action), `status: review`
(ready PR or linked issue awaiting review). Replace the old status on transition.
Use assignees for ownership and closed/merged state for completion. Prefer the
linked issue's type for its PR. Do not create an issue merely to apply a label.

## Keep records useful

Issues own task status; PLAN owns milestone checks and integration ownership;
README owns setup/use; docs/TEST_RESULTS.md owns evidence; handoff owns resumption.
Update the affected source and its summary, not every file on every change.
Report bugs with steps, expected/actual behavior and environment. No secrets,
uploads, voice recordings or third-party assets in reports or committed files.
No license is selected yet; public visibility alone does not grant one.
