# Delivery plan - Assignment 3

**Current state:** local scaffold only; no app, samples or release acceptance yet.
Local setup A3-00 is complete. GitHub publication is still prohibited.

## Coverage and ownership

[acceptance.json](docs/acceptance.json) maps every brief requirement R01-R36 to a
work item and acceptance case. [ISSUES.md](docs/ISSUES.md) contains concrete local
issue briefs. These A3 IDs are not GitHub issue numbers. No requirement is optional
because its task or PR is closed. Add real issue links and chosen owners here at
publication; team chooses ownership. Integration owner: **unassigned**.

| Work item | Owner / review buddy | Depends on | State |
|---|---|---|---|
| A3-01 Startup and service contracts | Unassigned | None | Pending |
| A3-02 Playable instrumental UI flow | Unassigned | 01 | Pending |
| A3-03 Vocal songs and AI lyrics | Unassigned | 02 | Pending |
| A3-04 New matching covers | Unassigned | 01 | Pending |
| A3-05 Default DJ queue and controls | Unassigned | 02, 04 | Pending |
| A3-06 MP3/WAV reference DJ | Unassigned | 05 | Pending |
| A3-07 Three ready sample tracks | Unassigned | 02, 03, 04 | Pending |
| A3-08 Failure recovery and safeguards | Unassigned | 01; continuous | Pending |
| A3-09 Verified report and evidence | Unassigned | 01; continuous | Pending |
| A3-10 Independent ZIP and submission | Unassigned | 03, 05-09, GH | Pending |
| A3-GH Public GitHub/protection | Joshua/team; buddy unassigned | Explicit authorization | Waiting |

## Demonstrate progress early

1. **Startup:** supported runtime, locked dependencies, real service contracts and
   minimal shared track/job/playback schema. Models-list discovery is not generation.
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
