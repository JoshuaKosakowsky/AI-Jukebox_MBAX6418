# Delivery plan - Assignment 3

**Current state (2026-11-02):** protected main `e17997d` includes six layouts,
Light/Dark, editable Surprise me ideas and merged #59's default-DJ ZIP procedure.
[Main CI passed](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/actions/runs/41564908360).
Runtime/contracts, instrumental generation and matching covers are accepted
(A3-01/02/04). Current integration and remaining acceptance:

- **Vocals (#3):** implementation #21/#29/#44/#37 is merged. Mike's
  [#61](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/61) records
  historical HTTP/provider observations and his listening judgment on `a1a41d1`.
  Those do not establish real-provider browser form/playback/reload acceptance;
  #3 stays open. Bundled vocal playback is a separate accepted observation.
- **Default DJ (#5):** Matt [closed the scoped feature](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5)
  after reconciling merged implementation, historical real/synthetic evidence
  and listening. The [three-intro default-voice record](results/a3-05-default-dj-live.json)
  remains pinned to `2be9625`; Joshua's later clarity/voice feedback is attributed.
  Live comparison of the newer presentation styles remains pending under #10.
- **Reference voices (#6):** upload/chooser wiring #26/#46 is merged. The prior
  run stopped with speech failures; MP3/WAV upload acceptance is not a listening
  comparison. The failed run/accounting is preserved in #61. No personal voice
  recording is requested by the default-DJ ZIP procedure and no previous spent
  service allowance is renewed here. Full AT-08 remains unverified.
- **Samples (#7):** Afterglow Avenue (45s vocal), Moonlit Reflection (30s
  instrumental) and Antlercover (60s vocal) ship with covers/lyrics/provenance.
  [Integrated-main playback/reload](results/a3-07-integrated-main-library.json)
  retains its original `2be9625` source. Final independent ZIP verification remains.
- **Recovery/report (#8/#9):** #8 is closed within its documented recovery/privacy
  scope. Preethi's #34 findings/design trade-off and original evidence remain.
  #9 refreshes the current guide/screenshots without rerunning historical service
  tests; actual teammate verification of the documentation/findings is still needed.
- **Release (#10):** [the merged agent-executable procedure](docs/DEFAULT_DJ_ZIP_TEST.md)
  pins candidate `0a34502`, including current layouts and ideas. One actual teammate
  claims/coordinates the clean-ZIP/default-DJ run; one successful run suffices.
  The prepared packet/verified archive is not independent acceptance. Keep its
  original SHA/ZIP identity unless a new candidate is explicitly selected.

Genre controls #37 and wordless-cover prompt #40 are integrated. Quality limits
#35/#36 and draft scorecard #43 remain distinct from required release acceptance.

**Next:** finish #61 review, run one coordinated independent ZIP test and have a
teammate verify the finished-app report in their own words. No status update,
merge or model switch creates a new service-call allowance. Full submission
remains **NOT READY**; [test results](docs/TEST_RESULTS.md) preserve actual sources
and distinguish live, synthetic, author UI and unchecked work.

Team workflow active: all changes use task branches and reviewed PRs.
Joshua/the team will arrange invitations and lead/contributor assignments
(up to 3 assignees per issue: one lead who owns acceptance and merge, plus
up to two contributors). Any teammate without commits on a PR may review
and approve; the approving reviewer or the issue lead merges.
The named disclosed Hermes/JoshKozy reviewer may also approve under
[CONTRIBUTING](CONTRIBUTING.md#disclosed-hermes-reviewer-joshkozy) once adopted on
main; it never merges and is not another teammate or issue owner.
GitHub issues hold current assignments and claims; the table mirrors that coverage.
Assigned coverage is not completed work; see docs/CONTRIBUTIONS.md for actual results.
Before editing, claim the specific piece/branch/files on its issue; check existing
claims and PRs. Backups can claim unclaimed work or continue an explicit handoff,
without taking over an active claim. On stopping, push the branch and leave the
commit, completed/remaining checks, blockers and next step; update handoff.md.
Assignees are coverage, not reserved reviewers; anyone without PR commits may
review. Keep branches still during review and preserve all required checks.

## Coverage and ownership

**Names:** `MSpanny` is **Mike**; `mase7919` (Mase) is **Matt**.
Mike leads A3-03/A3-06; Matt leads A3-05. Live issues remain authoritative.

[acceptance.json](docs/acceptance.json) maps every brief requirement R01-R36 to a
work item and acceptance case. [ISSUES.md](docs/ISSUES.md) preserves each issue's
scope/acceptance checks. The links below are live GitHub issues; their state and
labels are authoritative for task progress. No requirement becomes optional when
a task or PR closes. Joshua coordinates remaining delivery under issues #7-#10;
individual task ownership remains with the live issues.

| Work item | Lead / contributors | Depends on | State |
|---|---|---|---|
| [A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1) Startup and service contracts | JoshuaKosakowsky (lead); contributors pending | None | See issue |
| [A3-02](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/2) Playable instrumental UI flow | mase7919 (lead); contributors unassigned | 01 | See issue |
| [A3-03](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/3) Vocal songs and AI lyrics | MSpanny (lead); jovi1214 (contributor / backup) | 02 | See issue |
| [A3-04](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/4) New matching covers | JoshuaKosakowsky (lead); contributors unassigned | 01 | See issue |
| [A3-05](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5) Default DJ queue and controls | mase7919 (lead); prse4479 (contributor / backup) | 02, 04 | See issue |
| [A3-06](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/6) MP3/WAV reference DJ | MSpanny (lead); jovi1214 (contributor / backup) | 05 | See issue |
| [A3-07](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/7) Three ready sample tracks | JoshuaKosakowsky (lead); MSpanny; prse4479 (retained-source handoff) | 02, 03, 04 | See issue |
| [A3-08](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/8) Failure recovery and safeguards | JoshuaKosakowsky (lead); mase7919 (contributor / backup) | 01; continuous | See issue |
| [A3-09](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/9) Verified report and evidence | JoshuaKosakowsky (lead); mase7919 (contributor / backup) | 01; continuous | See issue |
| [A3-10](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/10) Independent ZIP and submission | JoshuaKosakowsky (lead); MSpanny (contributor / backup) | 03, 05-09, GH | See issue |
| [A3-GH](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11) Public GitHub/protection | Joshua (lead); contributors unassigned | Publication verification | See issue |

## Demonstrate progress early

1. **Startup:** Python/FastAPI, uv.lock and the normal scripts/dev.py launcher;
   shared Track/GenerationJob/Playback objects in docs/APP_CONTRACTS.md. Complete
   on merged main c635e86, with normal-launch browser/HTTP verification and green
   CI. Earlier provider probes remain separate evidence; models-list is not generation.
2. **First useful flow:** normal launch -> instrumental generation -> library ->
   playback, with a newly generated matching cover. Verified on main 7cc9645
   using the normal launcher and real services; see
   [instrumental acceptance](results/main-instrumental-acceptance.json).
3. **All core flows:** reconcile published vocal-creation acceptance and finish
   real MP3/WAV reference comparisons. Default-DJ and three-song main evidence are
   recorded above; use the existing samples and preserve original test attribution.
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
