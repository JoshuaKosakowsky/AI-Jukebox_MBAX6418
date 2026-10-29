# Agent handoff

## Session
2026-10-28 America/Denver; Codex for Joshua. Task: merge #18 and complete #2 acceptance.
## Constraints
Protected PR workflow; no protection/assignment changes. Two deliberate music + two art requests only.
## Repository state
PR #18 marked ready and merged normally at main 7cc9645 after current-head approval.
Branch codex/a3-02-browser-acceptance contains docs/evidence only; tested app code is exact main.
## Work completed and decisions
Clean-main normal launcher -> two real songs/covers -> native play/pause/resume -> reload/replay PASS.
Joshua confirmed both clips audible/instrumental and broadly matching styles. AT-03/05/06 satisfied.
Preserved pending PLAN #2 Matt/#7 jovi swap and review/merge credit; no ownership change in this task.
## Validation
Main --check: 115 tests, verifier 63 files before evidence addition, coverage 36/11/19; main CI green.
Both PCM WAVs fully decoded/non-silent at exact 30/20 s; both PNGs fully decoded at 512x512.
Same snapshot before/after reload: two tracks/four succeeded jobs; no console/media errors.
## Blockers and unchecked areas
Evidence PR needs review. Vocals/DJ/reference voices/samples/independent ZIP remain; submission NOT READY.
FLUX lettering is imperfect. Raw acceptance clips remain ignored, available for later sample consideration.
## Next steps
1. Review/merge this documentation evidence; #2 may close with the recorded main acceptance.
2. #3 (jovi) vocals and #5 (prse) DJ queue can proceed; #8/9 stay continuous.
3. Verify each remaining flow before closure; #6 waits for DJ, #7 for vocals; no needless regeneration.
## References
results/main-instrumental-acceptance.json; docs/TEST_RESULTS.md; PR #18; issue #2.

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
