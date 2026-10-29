# Agent handoff

## Session
2026-10-28 America/Denver; Hermes for mase7919. Task: A3-02 instrumentals (#2 lead).
## Constraints
Task branch + reviewed PR only; no main/protection/assignment changes, no bypass.
Two authorized live ACE-Step generations plus automatic covers; no other service calls.
## Repository state
Branch codex/a3-02-instrumental-generation from main 3e298fe (PR #17 merged).
No other open PRs touch these files. The task PR is linked from issue #2.
## Work completed and decisions
Extended SessionStore (per-kind active set, server-private music tickets,
queue/generate_music with bounded submit->poll->download), POST
/api/tracks/{id}/music + music_generation_available, two-step browser create
(draft+cover, then instrumental), per-track music status UI, GenerationJob
with_progress. Instrumentals 10-60 s (20 MB provider cap rationale). Music
failure leaves status/cover/audio untouched; replacement cleans old media on
success; art and music jobs coexist on one track; no auto-resubmission.
Hardening: POST .../music/resume?from={job} continues the SAME retained task
without a new submission; polling progress capped at 0.79 with the 0.9
downloading stage only after success; library cards render per-track so a
playing song survives unrelated updates; config-missing UX is explicit.
## Validation
Locked python scripts/dev.py --check PASS: all 109 tests (96 prior + 13
hardening/regression incl. static frontend guards), verifier 62 files, coverage
36/11/19; schema byte-identical; diff whitespace clean; key-scan clean.
Live: two real ACE-Step instrumentals (10 s and 20 s) with automatic FLUX covers
through the normal launcher (unchanged record results/instrumental-live-record.json);
no new live generation on the hardening pass.
## Blockers and unchecked areas
PR awaits teammate review and merged-main run before #2 closes. Audible browser
playback not independently performed (automation unavailable); verified via HTTP
surface, media decoding and the in-page audio element. No samples/ZIP acceptance.
## Next steps
1. Review/merge the A3-02 PR; verify two playable songs with covers on main.
2. Add the A3-02 implementation row in docs/CONTRIBUTIONS.md on merge.
3. A3-03 (vocals/AI lyrics) extends the same store/route pattern; A3-05 queues playback.
## References
Issue #2; README.md; docs/APP_CONTRACTS.md; docs/TEST_RESULTS.md;
results/instrumental-live-record.json.

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
payload schemas for 9007/9008 (music/TTS) â€” still need class-endpoints.txt
before building adapters.
