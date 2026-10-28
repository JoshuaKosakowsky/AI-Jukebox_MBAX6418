# Delivery plan - Assignment 3

**Current state:** startup foundation and v1 shared app contracts on the A3-01
task branch, pending review/merge. No generation/playback features, approved
samples or release acceptance yet. Local setup A3-00 is complete. [GitHub repo](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418) and task
issues exist; [#11](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11) records publication/CI/protection verification.
The [four live service contracts](docs/SERVICE_CONTRACTS.md) are verified in an
merged A3-01 contract slice. The runtime/shared-object implementation is in the
current A3-01 PR; feature acceptance is still pending.
Team workflow active: all changes use task branches and reviewed PRs.
Joshua/the team will arrange invitations and lead/contributor assignments
(up to 3 assignees per issue: one lead who owns acceptance and merge, plus
up to two contributors). Any teammate without commits on a PR may review
and approve; the approving reviewer or the issue lead merges.
Collaborators and remaining implementation ownership are for the team to choose.

## Coverage and ownership

[acceptance.json](docs/acceptance.json) maps every brief requirement R01-R36 to a
work item and acceptance case. [ISSUES.md](docs/ISSUES.md) preserves each issue's
scope/acceptance checks. The links below are live GitHub issues; their state and
labels are authoritative for task progress. No requirement becomes optional when
a task or PR closes. Team chooses owners; integration owner: **unassigned**.

| Work item | Lead / contributors | Depends on | State |
|---|---|---|---|
| [A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1) Startup and service contracts | JoshuaKosakowsky (lead); contributors pending | None | See issue |
| [A3-02](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/2) Playable instrumental UI flow | Unassigned | 01 | See issue |
| [A3-03](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/3) Vocal songs and AI lyrics | Unassigned | 02 | See issue |
| [A3-04](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/4) New matching covers | Unassigned | 01 | See issue |
| [A3-05](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5) Default DJ queue and controls | Unassigned | 02, 04 | See issue |
| [A3-06](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/6) MP3/WAV reference DJ | Unassigned | 05 | See issue |
| [A3-07](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/7) Three ready sample tracks | Unassigned | 02, 03, 04 | See issue |
| [A3-08](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/8) Failure recovery and safeguards | Unassigned | 01; continuous | See issue |
| [A3-09](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/9) Verified report and evidence | Unassigned | 01; continuous | See issue |
| [A3-10](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/10) Independent ZIP and submission | Unassigned | 03, 05-09, GH | See issue |
| [A3-GH](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11) Public GitHub/protection | Joshua (lead); contributors unassigned | Publication verification | See issue |

## Demonstrate progress early

1. **Startup:** Python/FastAPI, uv.lock and the normal scripts/dev.py launcher;
   shared Track/GenerationJob/Playback objects in docs/APP_CONTRACTS.md. Review
   and merge the current A3-01 foundation before dependent integration. Earlier
   live provider probes remain separate evidence; models-list is not generation.
2. **First useful flow:** normal launch -> instrumental generation -> library ->
   playback, then a newly generated matching cover. A3-02/04 coordinate on merged
   contracts. Never substitute test adapters in the normal launcher.
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
