# Delivery plan - Assignment 3

**Current state:** runtime/contracts, instrumental generation/playback and matching
covers are accepted (A3-01/02/04). Mike's vocal implementation (#21) is merged;
A3-03 stays open for real-class normal-launch vocal/browser/listening acceptance.
Main `e2b1e52` includes #23's Moonlit candidate; the final sample library remains
unfinished. Matt leads the ready A3-05 default DJ queue; Mike leads A3-03
acceptance and A3-06 reference voices after A3-05 integration. Matt/prse provide
reciprocal backup coverage for A3-05/08/09; Mike/jovi for A3-03/06/07/10.
Mike/Matt can independently review each other tonight, and prse/jovi tomorrow,
provided the reviewer has no commits on the PR.
Prse retains A3-08 recovery/safeguards and A3-09 documentation; coordinate shared
frontend edits and any unpublished A3-05 work with Matt. Jovi retains A3-07
samples and A3-10 independent ZIP/submission. Our #20 ZIP rehearsal and #22
offline audit are supporting evidence, not final feature/release acceptance.
Evidence: [main acceptance](results/main-instrumental-acceptance.json) and
[test results](docs/TEST_RESULTS.md). Full submission remains **NOT READY**.
Team workflow active: all changes use task branches and reviewed PRs.
Joshua/the team will arrange invitations and lead/contributor assignments
(up to 3 assignees per issue: one lead who owns acceptance and merge, plus
up to two contributors). Any teammate without commits on a PR may review
and approve; the approving reviewer or the issue lead merges.
GitHub issues hold the current assignments; the table reflects the accepted team.
Before editing, claim the specific piece/branch/files on its issue; check existing
claims and PRs. Backups can claim unclaimed work or continue an explicit handoff,
without taking over an active claim. On stopping, push the branch and leave the
commit, completed/remaining checks, blockers and next step; update handoff.md.
Assignees are coverage, not reserved reviewers; anyone without PR commits may
review. Keep branches still during review and preserve all required checks.

## Coverage and ownership

[acceptance.json](docs/acceptance.json) maps every brief requirement R01-R36 to a
work item and acceptance case. [ISSUES.md](docs/ISSUES.md) preserves each issue's
scope/acceptance checks. The links below are live GitHub issues; their state and
labels are authoritative for task progress. No requirement becomes optional when
a task or PR closes. Team chooses owners; integration owner: **unassigned**.

| Work item | Lead / contributors | Depends on | State |
|---|---|---|---|
| [A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1) Startup and service contracts | JoshuaKosakowsky (lead); contributors pending | None | See issue |
| [A3-02](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/2) Playable instrumental UI flow | mase7919 (lead); contributors unassigned | 01 | See issue |
| [A3-03](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/3) Vocal songs and AI lyrics | MSpanny (lead); jovi1214 (contributor / backup) | 02 | See issue |
| [A3-04](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/4) New matching covers | JoshuaKosakowsky (lead); contributors unassigned | 01 | See issue |
| [A3-05](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5) Default DJ queue and controls | mase7919 (lead); prse4479 (contributor / backup) | 02, 04 | See issue |
| [A3-06](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/6) MP3/WAV reference DJ | MSpanny (lead); jovi1214 (contributor / backup) | 05 | See issue |
| [A3-07](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/7) Three ready sample tracks | jovi1214 (lead); MSpanny (contributor / backup) | 02, 03, 04 | See issue |
| [A3-08](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/8) Failure recovery and safeguards | prse4479 (lead); mase7919 (contributor / backup) | 01; continuous | See issue |
| [A3-09](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/9) Verified report and evidence | prse4479 (lead); mase7919 (contributor / backup) | 01; continuous | See issue |
| [A3-10](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/10) Independent ZIP and submission | jovi1214 (lead); MSpanny (contributor / backup) | 03, 05-09, GH | See issue |
| [A3-GH](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11) Public GitHub/protection | Joshua (lead); contributors unassigned | Publication verification | See issue |

## Demonstrate progress early

1. **Startup:** Python/FastAPI, uv.lock and the normal scripts/dev.py launcher;
   shared Track/GenerationJob/Playback objects in docs/APP_CONTRACTS.md. Complete
   on merged main c635e86, with normal-launch browser/HTTP verification and green
   CI. Earlier provider probes remain separate evidence; models-list is not generation.
2. **First useful flow:** normal launch -> instrumental generation -> library ->
   playback, with a newly generated matching cover. Verified on main 7cc9645
   using the normal launcher and real services; see the acceptance record above.
3. **All core flows:** add vocals and the default DJ queue; observe playback/control
   transitions in the actual browser. Start sample generation once its paths work.
4. **Rehearsal:** after all three core features first work, a teammate installs an
   extracted GitHub ZIP using README/class keys. Fix gaps before optional polish.
   If publication is not authorized, an isolated local rehearsal helps but does not
   satisfy the required GitHub ZIP check. Reference voice and samples stay required.
5. **Final freeze:** all requirements/evidence satisfied; choose a merged main SHA,
   download its GitHub ZIP, independently retest it and run the release check.
   A code/dependency/asset change creates a new candidate and requires relevant
   rechecks plus a fresh ZIP rehearsal. Never change submission identity silently.

At each milestone the integration owner checks R01-R36 for missing, blocked or
unverified items and prioritizes those over optional features, style or refactors.
Each feature PR brings its own tests/evidence. Screenshots and reports grow with
the working app; do not leave all evidence to A3-09 at the end.

## Keep completion honest and practical

Small related fixes stay in the current task. A component PR may merge with narrow
passing checks; its parent user outcome stays open until demonstrated on main.
Before closing a parent issue, reconcile its requirement IDs, evidence and leftover
work. Use Refs for partial work. Optional review suggestions never block required
completion. Security/correctness/required acceptance still block; the documented
unavailable-reviewer exception in CONTRIBUTING remains available.

Run `python scripts/check_readiness.py` for coverage structure. It never declares
the app complete. `python scripts/check_readiness.py --release` refuses readiness
without a completed independent evidence record and exact GitHub ZIP. Instructions
are in [TESTING.md](docs/TESTING.md). Current submission status: **NOT READY**.
