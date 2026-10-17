# Agent handoff

## Session
2026-10-17 America/Denver; Codex. Task: fix Matt's non-blocking PR #14 finding.
## Constraints
User authorized the correction and merge if possible, without another review
request. Keep branch protection intact; no admin override, service calls or assignments.
## Repository state
Branch codex/team-assignee-workflow; Matt (mase7919) approved reviewed head 3aaaba4.
Read actual GitHub eligibility after the correction is pushed; approval may be dismissed.
## Work completed and decisions
Changed the feature issue-template header to lead/contributors/dependencies.
The earlier scan omitted hidden files; scan hidden .github content as well.
Recorded Matt's completed review against its actual head, not any later correction.
## Validation
Scaffold/coverage and all 28 tests pass; whitespace clean; hidden-file scan has
zero obsolete terms. CI and current approval/merge status are authoritative on PR #14.
## Blockers and unchecked areas
Merge only if GitHub permits it under existing protection. Do not request another
review or weaken protection. App/startup/samples and release checks remain absent.
## Next steps
1. Push the verified correction, wait for CI and merge normally if permitted.
2. Record the docs implementation completion when it actually merges.
3. Joshua/the team assigns leads/contributors and continues A3-01 startup work.
## References
[PR #14](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/14);
CONTRIBUTING.md; docs/CONTRIBUTIONS.md.

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
