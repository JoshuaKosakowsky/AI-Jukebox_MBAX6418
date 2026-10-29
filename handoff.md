# Agent handoff

## Session
2026-10-27 America/Denver; Codex. Task: review/merge PR #15 and small review follow-ups.
## Constraints
Protected task-branch PRs only; no bypass, protection/assignment changes or new service calls.
## Repository state
Branch codex/runtime-review-followups from main c635e86; PR #15 merged normally.
Matt approved exact head 91eca84. Main CI passed; #1 closed; #2/4/8/9 ready.
## Work completed and decisions
Normal browser/HTTP startup passed on merged main. Completion record credits implementation
and Matt's independent HTTP/test review accurately. PLAN mirrors current live leads.
Follow-up tightens download queries/media IDs and renames unchanged JPEG screenshots.
Retain reachable HTTPX InvalidURL handler (regression proves it); other speech formats deferred.
## Validation
Locked python scripts/dev.py --check: verifier/coverage PASS; 63 offline tests PASS.
Schema regenerated; staged whitespace PASS. PR/CI state must be read live before merging.
## Blockers and unchecked areas
Follow-up needs independent approval. No generation UI, writable sessions, playback,
reference voices, approved samples or independent ZIP acceptance. Submission NOT READY.
## Next steps
1. Review/merge this focused follow-up after green CI; preserve protected main.
2. A3-02 (jovi1214): first real instrumental UI/session/playback flow on merged contracts.
3. A3-04 (Joshua): new matching covers; coordinate shared objects with A3-02.
## References
[PR #15](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/15);
docs/APP_CONTRACTS.md; docs/TEST_RESULTS.md; GitHub issues own current status/assignees.

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
