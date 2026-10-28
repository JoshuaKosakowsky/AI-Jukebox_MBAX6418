# Agent handoff

## Session
2026-10-27 America/Denver; Codex. Task: issue #4 matching cover generation.
## Constraints
Reviewed task-branch PR only; no bypass/assignment changes. Two deliberate FLUX calls;
no other live generation. No uploads, provider credentials or tickets in public files.
## Repository state
Branch codex/matching-covers from main c635e86; cover implementation 264c391; cookie fix 5ccb371.
PR #16 remains separately open with runtime hardening/completion records; preserve it on integration.
## Work completed and decisions
SessionStore, private media route, draft/create-cover APIs and actual form/library.
Title/style/mood drive fresh art; UUID pairing, bounded jobs/memory, manual retry,
old cover/audio/playback preserved on failure. v1 objects/schema/payloads unchanged.
## Validation
Locked --check PASS: 73 tests, 60 tracked files, coverage 36/11/19.
Normal browser: two real contextual FLUX covers, correct pairs after reload, no console errors.
Missing-art normal launcher: disabled control. Failure/retry/audio pairing proven offline only.
## Blockers and unchecked areas
PR requires review. #4 stays open for merged-main and live songs from #2; drafts have no audio.
FLUX added imperfect lettering despite prompt. No samples/ZIP acceptance. Submission NOT READY.
## Next steps
1. Review this cover PR normally; reconcile PR #16 docs if merge order conflicts.
2. A3-02 extends this session/store/POST /api/tracks for music; keep track IDs and automatic covers.
3. Verify two playable generated songs with correct art on main before closing #4.
## References
Issue #4; docs/APP_CONTRACTS.md (integration seam); docs/TEST_RESULTS.md; results/cover-generation.jpg.

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
