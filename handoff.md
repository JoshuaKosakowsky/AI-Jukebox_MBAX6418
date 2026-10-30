# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Desert Drive second sample candidate for jovi, then isolated recovery variants.
## Constraints
No app/manifest changes or class calls. Matt #5/#6, Mike #3, prse #8/#9, jovi #7/#10; normal reviews/protection.
## Repository state
codex/desert-drive-sample-candidate from main e2b1e52. #20 de256e2 and #22 156739b are separate reviewed-work candidates.
## Work completed and decisions
Packaged the retained Desert Drive WAV/PNG and safe candidate record; original title is Drive, not earlier chat's Dawn.
Original cover says DESSERT DRIVE; limitation explicitly retained for jovi selection. No new generation/listening claimed.
Updated sample guide and preview index; final manifest remains empty. Normal-app library and ZIP acceptance stay with jovi.
## Validation
Hashes match the original acceptance; 20 s/48 kHz/stereo PCM16 full decode and PNG inspection; muted static browser play/pause/resume passed.
Run locked repo checks and staged-blob comparisons before commit; record exact head/results on the PR. No live-provider acceptance here.
## Blockers and unchecked areas
#3 live vocal acceptance, DJ/references, #8 correction, final samples/ZIP remain incomplete; NOT READY.
## Next steps
1. Jovi reviews/selects this pair alongside Moonlit; integrate final three samples and verify normal-launch/ZIP playback.
2. Perform isolated offline cover-retry/resume rejection variants against main e2b1e52; report findings for prse without app edits.
3. Review/merge independent #20/#22/#24 normally, retaining distinct contribution rows and refreshing stale branches as needed.
## References
results/main-instrumental-acceptance.json; assets/samples/desert-drive.candidate.json; results/desert-candidate-preview.png.
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/7
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22

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
