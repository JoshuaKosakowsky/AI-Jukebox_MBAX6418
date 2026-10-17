# Agent handoff

## Session
2026-10-17 America/Denver; Codex. Task: A3-01 verified service contract slice.
## Constraints
User explicitly authorized one minimal live generation per required service.
Keys/raw responses/media stay ignored; no automatic calls or collaborator invites.
## Repository state
Branch codex/service-contract-probes; base main d0d566238b184413960076985b5681576111737c.
Check actual Git/PR state on entry; main protection remains in force.
## Work completed and decisions
Located dated class file; inspected all four deployed schemas/models, then made
one successful generation each. Music is async submit/poll/double-JSON/download;
speech returns complete WAV with default voice omitted. Frozen requests in
contracts/service-probes.json; shared usage/limits in docs/SERVICE_CONTRACTS.md.
## Validation
All four live HTTP 200; decoded PNG and complete non-silent PCM WAVs. See
docs/TEST_RESULTS.md and results/service-contract-probes.json for exact evidence.
Offline scaffold/coverage and 18 gate tests pass; frozen requests/evidence match
private originals. Remote CI/review status belongs to the linked issue/PR.
## Blockers and unchecked areas
A3-01 remains open: runtime/startup/shared objects/adapters pending. No app,
approved samples or ZIP acceptance; reference uploads, vocals and browser untested.
## Next steps
1. Review/merge this contract slice; reuse payloads rather than guessing/reprobing.
2. Complete A3-01 startup/shared objects, then demonstrate the instrumental flow.
3. Add collaborators/review buddy when the user supplies teammates.
## References
[A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1);
docs/SERVICE_CONTRACTS.md; PLAN.md; docs/TEST_RESULTS.md.

The inherited note below is preserved for provenance. Its models-only limitation
and unverified 9007/9008 status were superseded by the 2026-10-17 probes above.

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
