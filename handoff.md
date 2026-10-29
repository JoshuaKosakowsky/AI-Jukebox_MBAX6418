# Agent handoff

## Session
2026-10-28 America/Denver; Codex. Task: reconcile PR #17 with merged main.
## Constraints
Reviewed PR only; no bypass/protection/assignment changes or new service calls.
## Repository state
Branch codex/matching-covers, merging main 2775f0b (PR #16) into reviewed cover head bcdfcb5.
Matt approved bcdfcb5; the reconciliation needs current CI and independent approval.
## Work completed and decisions
Preserved main's route/media-ID hardening and JPEG renames; retained all cover code,
session integration, both evidence histories and inherited notes. Fixed screenshot
links and deferred grammar nit; consolidated completed PR #16/#17 review credit.
## Validation
Locked --check PASS: all 76 tests, verifier 60 files, coverage 36/11/19; whitespace/links clean.
Previous live cover/browser evidence is unchanged and identifies 264c391/5ccb371.
## Blockers and unchecked areas
New head needs review; #4 stays open for merged-main and live playable-song pairing with #2.
No new generation. FLUX lettering limitation persists; samples/ZIP acceptance NOT READY.
## Next steps
1. Publish the reconciliation, verify CI and obtain fresh eligible approval; merge normally.
2. A3-02 extends this store/POST /api/tracks for audio, preserving track IDs and covers.
3. Verify two playable generated songs with matching art on main before closing #4.
## References
[PR #17](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/17);
docs/APP_CONTRACTS.md; docs/TEST_RESULTS.md; PR #16 merge 2775f0b.

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
