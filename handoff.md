# Agent handoff

## Session
2026-10-30 America/Denver; Codex for mase7919. A3-05 default AI DJ queue
implementation on `codex/a3-05-dj-queue` (draft PR), built on main
`e2b1e52`. This file also retains the #20 ZIP-evidence and #23 Moonlit
candidate coordination notes below.

## Constraints
Protected reviews/checks unchanged. User-controlled workflow: this draft PR
must stay DRAFT until mase7919 authorizes readiness/review; no self-approval,
no branch-protection bypass, no merge. Keep prse's #8/#9 and jovi's #7/#10
ownership; #6 (reference voices) is explicitly out of scope of A3-05.

## Repository state
Main `e2b1e52` (includes #18 instrumentals, #19 acceptance evidence, #21
vocals, #23 Moonlit candidate). Open: #20 ZIP evidence (behind main, sync
requested), #22 recovery audit (dirty on handoff only), #24 vocal credits.
A3-05 branch `codex/a3-05-dj-queue` = main + playback controller (queue +
AI DJ commentary), one draft PR.

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
#20 notes (historical): original 7b9dd2b ZIP identity/65-file startup
rehearsal; #23: original Moonlit WAV/PNG candidate material. Neither is
touched by A3-05.

## Validation
Baseline `e2b1e52`: 128 tests / 4 CI. A3-05 head: 142/142 tests (9 new
tests/test_dj.py, 5 new frontend guards) and a REAL-Chrome offline harness
run with fixture providers: 18/18 checks (ordered speech->music sequencing
for 3 tracks, skip during speech and music, pause/resume in both phases,
reload resumes without regeneration, exactly 3 Qwen + 3 speech requests
total — zero duplicates, no console errors, no 4xx). Evidence retained
outside the repo (dj-browser-evidence.json, dj-browser-final.txt). No class
service, no .env, no credentials were used; no new live generation was
requested.

## Blockers and unchecked areas
Live Qwen/Chatterbox acceptance (AT-07, AT-09 live portion) is NOT done —
authorized separately, planned on the normal launcher. Not claimed: audible
listening, headed-browser listening, class-service connectivity. #22 remains
dirty (handoff-only conflict; sync + current-head CI before its formal
review). #8's instrumental retry P2 is unfixed on main and out of A3-05
scope. Not ready for submission: vocals live acceptance, reference voices,
samples, ZIP acceptance.

## Next steps
1. mase7919 authorizes readiness/review of the A3-05 draft; MSpanny is the
   preferred independent reviewer if eligible.
2. Propose the bounded live acceptance procedure (normal launcher, one
   2-track queue, real commentary + speech + sequencing in a browser) for
   authorization — no live calls before then.
3. After #25 merges, reconcile #20/#22 handoff (integration owner) and
   re-verify current-head CI. Keep #6 extension clean on top of the A3-05
   controller.

## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/25
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5

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
