# Agent handoff

## Session
2026-10-17 America/Denver; Codex. Task: activate team workflow; retire setup exception.
## Constraints
Task branches and reviewed PRs apply to every change, including setup. No direct
main updates or protection overrides. Joshua/the team manages invitations/assignments.
## Repository state
Branch codex/activate-team-workflow; base main ada2a6cc66eaab24e87439627fa5fc8c7e5685f3.
Confirm actual Git/PR state on entry; the transition requires normal review/merge.
## Work completed and decisions
Removed preparation bypass instructions from all current guides and both hooks.
Regression tests cover blocked main operations, ignored retired configuration
and permitted task-branch work. PR #12 is historical implementation/testing only;
docs/CONTRIBUTIONS.md explicitly records no independent review.
## Validation
Scaffold/coverage and all 28 offline tests pass; live protection matches the saved
policy via read-only API check. Original prompt/policy unchanged; no retired config.
No new service calls, collaborator invitations, owner or review-buddy assignments.
## Blockers and unchecked areas
Main still needs the transition PR merged before onboarding. A3-01 startup/runtime/
shared objects remain unfinished; app, samples and release acceptance remain absent.
## Next steps
1. Review/merge this transition with existing main protection; do not bypass it.
2. Joshua/the team invites collaborators and assigns owners/review buddies afterward.
3. Continue A3-01 startup/shared objects using the verified service contracts.
## References
CONTRIBUTING.md; docs/GITHUB_SETUP.md; docs/CONTRIBUTIONS.md;
[A3-01](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/1).

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
