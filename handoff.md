# Agent handoff

## Session
2026-10-17 America/Denver; Codex. Task: integrate setup and clarify solo workflow.
## Constraints
Joshua is the sole contributor, preparing for later teamwork. Validated setup
commits go to main without PR/reviewer requirements. No new service calls.
## Repository state
Local main contains contract commit 75ea4aa; this session adds the solo exception.
Check Git/remote state on entry; publication/protection readback is in issue #1.
## Work completed and decisions
Separate current solo preparation from later team collaboration in canonical docs.
Per-command jukebox.soloSetup permits main commits/fast-forward pushes only;
no persistent bypass. Restore full remote admin enforcement immediately after
the authorized setup update. Team review/check policy JSON remains unchanged.
## Validation
Four earlier live probes and frozen evidence remain valid; no new generation.
Scaffold/coverage pass; all 26 offline tests pass, including eight isolated hook
checks. Remote CI/protection results are recorded in issue #1 after publication.
## Blockers and unchecked areas
A3-01 startup/runtime/shared objects/adapters remain unfinished. No app, approved
samples or release acceptance. Solo setup is not a teammate review/contribution.
## Next steps
1. Continue requested setup directly; do not create unnecessary review blockers.
2. Complete A3-01 startup/shared objects before dependent feature integration.
3. On team collaboration, confirm protection and use normal branches/reviewed PRs.
## References
[A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1);
CONTRIBUTING.md; docs/GITHUB_SETUP.md; docs/SERVICE_CONTRACTS.md.

Inherited discovery note (its unverified status was superseded by 2026-10-17 probes):

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
