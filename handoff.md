# Agent handoff

## Session
2026-10-17 00:36 MDT (America/Denver); Codex. Task: authorized initial public GitHub publication.

## Constraints
Publication/branch collaboration authorized; collaborator invitations deferred.
No app generation or class-service calls in this setup task. Preserve inherited notes.

## Repository state
Repo: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418. Origin configured; pre-publication commit: 6edac1e6bc349b85b06875254dde4b1c905140ad.
The reviewed scaffold on codex/project-setup is the initial main baseline.
Read actual branch/history on entry; local hooks still block direct main work.

## Work completed and decisions
Created public repo, required labels and issues #1-#11 from all mapped task briefs.
Updated canonical docs from local-only instructions to normal branch/PR workflow.
Live publication, CI and protection results are recorded in [issue #11](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11);
use that record for final remote state rather than inferring it from this commit.
Initial main seeding uses a one-command local hook override, then server protection.

## Validation
Local scaffold/coverage pass; 18 offline gate tests pass. Reviewed 64 historical
blobs for prohibited private files and credential patterns; no findings.
No app/live/browser acceptance. Publication verification is tracked in #11.

## Blockers and unchecked areas
App/samples/independent ZIP are still absent: submission NOT READY. Owners/runtime
and generation request schemas are pending; discovery below is not generation proof.

## Next steps
1. Check publication issue #11 for CI/protection readback and current Git state.
2. Claim issue #1; choose integration owner/runtime/contracts and review buddies.
3. Add collaborators later when named by the user; use PRs for subsequent changes.

## References
PLAN.md; docs/ISSUES.md; docs/GITHUB_SETUP.md; docs/acceptance.json.

### Hermes entry (2026-10-15)

Local `.env` created with all four required services, keyed and verified:
JUKEBOX_TEXT=http://dobolyi.com:9001/v1 (Qwen3.6-35B-A3B),
JUKEBOX_ART=http://dobolyi.com:9006/v1 (FLUX.2-klein-4B),
JUKEBOX_MUSIC=http://dobolyi.com:9007/v1 (acestep-v15-xl-turbo),
JUKEBOX_SPEECH=http://dobolyi.com:9008/v1 (chatterbox-v3).
Same class key as Assignment 2 (copied from A2 `.env`; hash-verified, never printed).
`.env` confirmed gitignored (`git check-ignore .env`); no commits, no push.
All four respond to `/v1/models` with the key. Unverified: request/response
payload schemas for 9007/9008 (music/TTS) — still need class-endpoints.txt
before building adapters.
