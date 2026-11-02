# Delivery plan - Assignment 3

**Current state (2026-11-02):** protected main `eb29bab` includes merged #39;
[main CI passed](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/actions/runs/41484629978).
Runtime/contracts, instrumental generation/playback and matching covers are
accepted (A3-01/02/04). Component integration and remaining acceptance are:

- **Vocals (#3):** implementation #21, diagnostics #29, non-thinking lyrics #44
  and genre controls #37 are merged. Mike reports 14/14 AT-04 checks on `a1a41d1`
  for Moonlit Rehearsal, with human listening pending. His cited acceptance JSON
  is not on main. [Result/stop record](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/3#issuecomment-6567842638).
  Reconcile the issue's checked boxes with published evidence and listening;
  the two packaged vocals do not replace normal-launch vocal-creation acceptance.
- **Default DJ (#5):** #27 and integrated evidence #51 are merged. The
  [real default-DJ record](results/a3-05-default-dj-live.json), tested on `2be9625`,
  records three successful intros, sequential playback/controls and cached
  replay/reload using text3/speech3. Joshua described the first clip as relaxed/NPR-like.
  #52 adds Relaxed/Public Radio, Upbeat Radio and Playful presentation choices;
  those choices have offline/browser checks, not a live style-quality comparison.
- **Reference voices (#6):** upload/provider #26 and chooser/DJ wiring #46 are
  merged. Mike's last AT-08 run stopped at failed speech jobs; upload validation
  alone did not establish a default/MP3/WAV listening comparison.
  [Result/stop record](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/6#issuecomment-6567842868).
  A new bounded, strictly sequential run needs one coordinated tester and fresh
  authorization; the previous 13-request allowance is spent, not reusable.
- **Samples (#7):** #48/#49/#50 ship three owner-approved pairs: Afterglow Avenue
  (45 s vocal), Moonlit Reflection (30 s instrumental), Antlercover (60 s vocal).
  The two-vocal project target is met. [Integrated-main evidence](results/a3-07-integrated-main-library.json)
  pins full playback, covers, lyrics, controls and reload to `2be9625` with zero
  new provider calls. Final GitHub-ZIP installation/sample verification is pending.
- **Recovery/report (#8/#9):** Preethi's #32 live recovery evidence and #34 README
  findings, the rejected-control correction #30, and #39's historical 27-case
  synthetic browser regression are merged. [Browser report](docs/MAIN_BROWSER_REGRESSION.md)
  remains attributed to `25f8617`; no later browser rerun is implied. Reconcile the
  remaining requirement checks and finished-app screenshots/report before closure.
- **Release (#10):** #42's runbook/mechanics and #20's earlier ZIP startup are
  preparation only. A different teammate must install/test the final exact GitHub
  ZIP and complete the release evidence/gate. No final candidate is certified.

Genre controls #37 and wordless-cover prompt #40 are integrated; documented
quality limits (#35/#36) remain. The historical 20-style scorecard is still draft
PR #43; its case-specific ratings are not a guarantee of every genre or vocal.

**Next:** coordinate Mike's #3 evidence/listening and #6 comparison; reconcile
#5/#7 checklists using existing records; finish #8/#9 and arrange #10's independent
installer. Confirm actual teammate contribution/review evidence before submission.
No status update, merge or model switch creates a new service-call allowance.
Full submission remains **NOT READY**. [Test results](docs/TEST_RESULTS.md) retain
source commits and the distinction between live, synthetic and unchecked work.

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
