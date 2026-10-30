# Agent handoff

## Session — Joshua integration check (2026-10-30 America/Denver)
Local recheck of 2f872b4 found one missing djReady stub in the merged #30
retry probe; corrected only that test fixture, not the DJ implementation.
PASS after correction: 153 locked tests, verifier 82, coverage 36-11-19; whitespace clean.
Actual-function timer probes still reproduce stale retry after Pause and
persistent-rejection segment completion; posted both to #27, no class calls.
Joshua now contributes to this PR and cannot approve it; Mike/Jovi remain
eligible if they have no commits. Prior Matt implementation/handoff follows.

## Session
<<<<<<< HEAD
2026-10-30 America/Denver; Codex for mase7919. A3-05 default AI DJ queue
implementation on `codex/a3-05-dj-queue` (draft PR #27) — now synchronized
with main `770ce62` (includes PR #20's Windows ZIP evidence, merged after
E2B1E52). This file consolidates the A3-05 entry with PR #20's ZIP-evidence
entry and preserves #23's Moonlit candidate notes below.

## Constraints
Protected reviews/checks unchanged. User-controlled workflow: the A3-05 draft
PR must stay DRAFT until mase7919 authorizes readiness/review; no
self-approval, no branch-protection bypass, no merge. Keep prse's #8/#9 and
jovi's #7/#10 ownership; A3-06 (#6, MSpanny, PR #26) is excluded from A3-05 —
its branch is untouched and its speech(reference=None) seam is backward
compatible. #20 remains as the recorded ZIP startup evidence; no new ZIP
acceptance is claimed.

## Repository state
Main `770ce62` (includes #18 instrumentals, #19 acceptance evidence, #21
vocals, #23 Moonlit candidate, and #20 Windows ZIP evidence). Open PRs: #22
recovery audit (dirty on handoff only), #24 vocal credits, #25/#26 teammate
PRs, and #27 (A3-05, DRAFT, MERGEABLE). A3-05 branch `codex/a3-05-dj-queue`
= main + playback controller (queue + AI DJ commentary) + concurrency
hardening; the branch was merged with main `770ce62` after #20 landed; the
only merge conflicts were the shared docs (TEST_RESULTS.md, handoff.md),
resolved by keeping both entries.

## Work completed and decisions
A3-05 implemented end-to-end: queue endpoints, DJ speech jobs (Qwen text ->
Chatterbox default-voice speech, voice omitted per contract), playback state
machine on the existing Playback contract (no schema change; track.speech
reused as the per-track introduction), one persistent browser audio element +
engine loop for sequencing, play/pause/resume/skip in both phases, automatic
advancement, end-of-queue, reload without regeneration. Every transition
including the first is DJ-introduced (documented design choice; same code
path for all transitions). Commentary speech attaches to the TRACK so stale
jobs from skipped tracks can never play out of turn.
Concurrency audit (delayed/reordered requests) found and fixed three real
races: stale phase-after-skip rejected via track-scoped preconditions (409),
stale pause records the current track's true phase, advance-from-paused no
longer 500s. Browser: single-flight advances (a Skip coalesces into an
in-flight automatic advance for the same track; rapid skips serialize), a
FIFO for user intents, pause-failure un-halting, crash-proof engine loop.
Final edge cases: a skip while paused during music keeps the queue paused
and resumes with the NEXT song's introduction (paused_from is always
"speaking" after a paused advance — carrying the old track's "playing"
phase bypassed the introduction), and a failed advance request no longer
creates an unobserved orphan promise (in-flight slot cleared inside the
advance promise; controller recovers).
#20 notes (historical): original 7b9dd2b ZIP identity/65-file startup
rehearsal recordings remain intact on main and in this branch after the
merge; #23: original Moonlit WAV/PNG candidate material. Neither is touched
by A3-05.

## Validation
A3-05 head: 151/151 tests (14 tests/test_dj.py incl. concurrency races and
edge cases, 21 frontend guards incl. DJ guards) plus real-Chrome offline
harness runs with fixture providers: 18/18 functional, 12/12 deterministic
concurrency, plus edge-case browser checks (paused-music -> Skip -> Resume
-> next-song intro -> music; forced advance failure with no unhandled
rejection) — evidence retained outside the repo (dj-browser-evidence.json,
dj-concurrency-evidence.json). Baseline gates on merged main 770ce62:
`python scripts/dev.py --check` PASS; CI 4/4 on the PR head. #20's ZIP
evidence and #23's Moonlit files are byte-preserved through the merge. No
class service, no .env, no credentials were used in A3-05 development; no
new live generation was requested.

## Blockers and unchecked areas
Live Qwen/Chatterbox acceptance (AT-07, AT-09 live portion) is NOT done —
authorized separately, planned on the normal launcher. Not claimed: audible
listening, headed-browser listening, class-service connectivity. #22 remains
dirty (handoff-only conflict; sync + current-head CI before its formal
review). #8's instrumental retry P2 is unfixed on main and out of A3-05
scope. Not ready for submission: vocals live acceptance, reference voices
(A3-06 integration wiring is a coordinated follow-up after #27/#26 merge),
samples, ZIP acceptance.

## Next steps
1. mase7919 authorizes readiness/review of the A3-05 draft; MSpanny is the
   preferred independent reviewer if eligible.
2. Propose the bounded live acceptance procedure (normal launcher, one
   2-track queue, real commentary + speech + sequencing in a browser) for
   authorization — no live calls before then.
3. After #27 merges, wire A3-06's take_reference into generate_dj_speech
   (coordinate with MSpanny; the reference=None default keeps the seam
   compatible), reconcile #22's handoff, and re-verify current-head CI.

## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/27
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/26
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5

## A3-08 retry controls (PR #30, merged into main 2026-10-30)
2026-10-30 America/Denver; Codex for Joshua. Task: recheck Matt, then fix #8 retry controls.
### Constraints
MSpanny = Mike; mase7919/Mase = Matt. No ownership/protection changes or class calls.
Claim posted on #8; app.js edits confined to cover/music/resume rejection catches; no DJ code edits.
### Repository state
Branch codex/a3-08-retry-controls from main 770ce62. Existing #22/#24/#26/#28/#29 remain separate.
### Work completed and decisions
Matt #27 895a616 rejected-advance cleanup verified fixed; 151 locked tests PASS. Manual/DJ overlap remains open.
Restore the three rejected controls explicitly; retain cached cards, audio nodes, active/config guards and deliberate retry semantics.
Added dependency-free optional Node handler regression in default Python discovery; Node is not an app dependency.
### Validation
Node regression fails baseline and passes patch, including pending, configuration, same-node and no-auto-submit checks.
Real browser offline: cover/music/resume reject -> release -> refresh -> explicit retry all PASS without reload.
Fixture counters cover 4/6/7; resume submissions 1/3/3; music 0/2/3. Safe record/screenshot committed.
Sequential tabs avoid cross-port localhost cookie collisions; initial mixed setup discarded and cover rerun cleanly.
Final locked checks/CI reported in PR. No real providers, .env, user recordings or listening involved.
### Blockers and unchecked areas
#8 broader normal-launch/live acceptance stays open. Matt's overlap fix and Mike's #26/#29 findings remain separate.
Submission NOT READY; no issue closed and no self-approval.
### Next steps
1. Eligible teammate reviews this focused #8 patch; coordinate merge order with Matt's #27 shared app.js.
2. Rerun integrated browser regression after normal protected merge; preserve full acceptance gaps on #8.
3. Mike/Matt continue their existing follow-ups; do not repeat generation on session switches.
### References
Issue #8; results/retry-control-fix.json; docs/TEST_RESULTS.md; tests/frontend_retry_probe.cjs.

Inherited discovery note (its unverified status was superseded by the October 17
probes and October 27 production-adapter smoke; preserve as history only):

### Hermes entry (2026-10-15)

Local `.env` created with all four required services, keyed and verified:
JUKEBOX_TEXT=http://dobolyi.com:9001/v1 (Qwen3.6-35B-A3B),
JUKEBOX_ART=http://dobolyi.com:9006/v1 (FLUX.2-klein-4B),
JUKEBOX_MUSIC=http://dobolyi.com:9007/v1 (acestep-v15-xl-turbo),
JUKEBOX_SPEECH=http://dobolyi.com:9008/v1 (chatterbox-v3).
Same class key as Assignment 2 (copied from A2 `.env`; hash-verified, never printed).
`.env` confirmed gitignored (`git check-ignore .env`); no commits, no push.
All four respond to `/v1/models` with the key. Unverified: request/response
payload schemas for 9007/9008 (music/TTS) — still need class-endpoints.txt
before building adapters.
