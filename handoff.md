# Agent handoff

## Session
2026-10-27 America/Denver; Codex. Task: A3-01 runtime/startup/shared contracts.
## Constraints
Protected task-branch PR only; no main/protection/assignment changes. Four deliberate
adapter smokes completed; no generation on startup/CI. Raw media/ticket stay ignored.
## Repository state
Branch codex/app-runtime-contracts; base main 301585b; pre-handoff code 60853ac51a5386412723470209e7971bdd172871.
The current PR is linked from issue #1; read actual CI/review state before proceeding.
## Work completed and decisions
FastAPI + plain same-origin frontend, exact uv.lock, Windows-safe short environment
launcher. Typed v1 Track/MediaRef/GenerationJob/Playback/session schema and real
class clients with safe errors, bounds, decoded media and async music ticket handling.
README startup and docs/APP_CONTRACTS.md are the integration baseline after merge.
## Validation
All 60 offline tests and scaffold/coverage checks pass. Normal browser startup and
refresh work with private config and without .git/.env in a clean source copy.
All four new adapters passed one real request each; safe measurements/screenshots
are in results/ and docs/TEST_RESULTS.md. CI matrix results belong to the task PR.
## Blockers and unchecked areas
Foundation awaits teammate review/merged-main startup verification. No generation
UI, writable sessions, playback, references, approved samples or release acceptance.
The source-copy rehearsal is not independent GitHub ZIP evidence. Submission NOT READY.
## Next steps
1. Review/merge; verify normal startup on main before closing #1/unblocking dependents.
2. A3-02 implements the first real instrumental UI/session flow using these contracts.
3. Record this substantial implementation on merge; preserve the shared objects.
## References
README.md; docs/APP_CONTRACTS.md; docs/TEST_RESULTS.md;
[A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1).

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
