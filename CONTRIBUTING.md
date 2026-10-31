# Contributing - AI Jukebox, MBAX 6418-801

Agents follow AGENTS.md. Requirements live in docs/ASSIGNMENT.md. Every teammate
must contribute meaningfully and review a teammate's work.

## Team workflow active

All changes, including setup, use task branches and reviewed PRs. Main protection
applies to everyone, including admins. Do not disable protection or push directly
to main. Joshua/the team handles invitations and lead/contributor assignments.

## Team workflow: work in small steps

1. Claim one substantial work item with acceptance checks, one lead and up
   to two contributors (max 3 assignees per issue). The lead owns the
   acceptance checks and the merge; contributors co-implement and are the
   natural first-review pool. Before publication, record it in PLAN.md;
   afterward use GitHub issues.
2. Branch each task from current main (`codex/<task>` or `type/slug`).
   Independent tasks may have concurrent PRs from the same contributor.
   Keep each PR focused; coordinate overlapping files or shared interfaces and
   record dependencies/merge order where needed. Waiting for one PR's review
   must not hold up unrelated work.
3. Implement the smallest useful behavior. Fix related small problems in that
   change. Open separate work for independent bugs or scope/interface changes,
   not every typo, missing import or straightforward local correction.
4. Run relevant checks (docs/TESTING.md), inspect the diff and update affected
   docs. Use docs/COMMITS.md for readable commits; wording nits are non-blocking.
5. Open a PR with its result, issue link and actual validation. Use `Refs #N`
   for partial work; `Closes #N` only when that issue's checks are satisfied.
6. Address blocking findings together, update the branch, rerun affected checks,
   then request approval on that head. Keep handoff.md current each session.

Publication and branch/issue/PR collaboration for assigned work are authorized.
Main protection requires teammate approval, passing `test`, up-to-date branches,
resolved conversations and latest-push approval for everyone.
See docs/GITHUB_SETUP.md. Do not bypass protection to accelerate merging.

## Acceptance before issue closure

Use the concrete local briefs in [docs/ISSUES.md](docs/ISSUES.md) and requirement
IDs/cases in [docs/acceptance.json](docs/acceptance.json). After publication put
those IDs, dependencies, lead/contributors and the user outcome in each issue.
PRs state which checks they actually satisfy; unmapped new scope needs review.
Before closing a parent, verify the normal-launch user flow on merged main and
record inputs, expected/actual results, tester, commit and evidence. Skipped,
stubbed or unrun live checks remain unverified. Update the issue checklist itself.
The integration owner runs a full-brief gap check at each milestone and arranges
the first independent install as soon as all core flows work. The final GitHub
ZIP and exact commit receive a separate freeze/check; see docs/TESTING.md.
Required completion, safety and reproducibility take priority over optional
refactors, style preferences or paperwork. Keep focused commits and required
reviews; fix small related problems directly instead of opening process issues.

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

- **Review eligibility:** the PR author cannot approve their own PR. Any
  teammate with zero commits on the PR may review, approve, or request
  changes, even if they did not code the change.
- **Merge:** the approving reviewer or the issue lead merges once the one
  required approval, green `test`, and resolved conversations are present.
  A PR author may merge after an eligible approval exists, but convention
  is that a non-author merges.
- **Branch freeze at review:** last-push approval and stale-review
  dismissal are enabled, so any collaborator push invalidates an approval.
  When the lead calls for review, collaborators stop pushing to that
  branch until the verdict; the reviewer who approves must not be the last
  committer.

### Resolved blocking review; original reviewer unavailable

The original reviewer is preferred for re-review, but is not the only person
who can verify a fix. If they are unavailable, a teammate other than the fix's
author must independently verify every blocking finding in that review against
the current PR head, including relevant regression checks, before dismissal. Record the findings, fix commit,
actual verification results and verifier in the PR conversation.

An administrator or maintainer with effective GitHub permission may then dismiss
that outdated review, explaining the original reviewer's unavailability and
linking the independent verification. Use GitHub's recorded dismissal action;
it does not represent approval by the original reviewer. No separate issue or
exception document is required. An eligible replacement reviewer can approve.

Unresolved findings remain blocking. A deadline alone is never grounds for
dismissal. All other approval, latest-push, CI and conversation-resolution
requirements still apply; do not weaken branch protection. See
[GitHub's dismissal guidance](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/dismissing-a-pull-request-review).

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

## Completion record

When substantial work merges or a review finishes, add/update one brief row in
[docs/CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md) with the responsible teammate,
outcome and evidence. Credit implementation, review, testing and integration;
combine follow-up revisions. Routine edits do not need entries or extra issues.

## Keep records useful

Issues own task status; PLAN owns milestone checks and integration ownership;
README owns setup/use; docs/TEST_RESULTS.md owns evidence; handoff owns resumption.
Update the affected source and its summary, not every file on every change.
Report bugs with steps, expected/actual behavior and environment. No secrets,
uploads, voice recordings or third-party assets in reports or committed files.
No license is selected yet; public visibility alone does not grant one.
