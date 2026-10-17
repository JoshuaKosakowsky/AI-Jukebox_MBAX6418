# Agent handoff

## Session
2026-10-16 19:50 MDT (America/Denver); Codex. Task: finalize local workflow documentation commit.

## Constraints
Local commits are authorized. No remote configuration, GitHub pushes/writes or
service calls. Preserve the inherited Hermes note.

## Repository state
Branch: codex/project-setup; pre-handoff commit: `d742a906975717d576c29b5d0c8c1676d15b3db0`.
The user authorized committing the eight documentation files locally, including
the preserved Hermes note. This handoff is written before that commit; use
`git log -1` for its final hash and verify the working tree on entry.

## Work completed and decisions
Simplified AGENTS, CONTRIBUTING, README, PLAN, TESTING, COMMITS and the PR template.
Routine related fixes stay in-task; separate work is for independent scope.
Added focused PRs, blocking/suggestion distinction, shared contracts, integration
ownership and early complete user flows. Assignment requirements are unchanged.

## Validation
`python scripts/verify_repo.py`: PASS (23 tracked files); `git diff --check`: PASS.
Original assignment unchanged; Hermes service note preserved verbatim.
No app, browser or generation checks; inherited endpoint discovery not reverified.

## Blockers and unchecked areas
No app yet; runtime, owners, shared contracts and generation schemas still need work.
Hermes reports local configuration/discovery below; do not treat it as generation proof.

## Next steps
1. Claim A3-01; choose an integration owner/review buddies, runtime and contracts.
2. Confirm documented requests, then deliver the first playable user flow in PLAN.
3. Continue local work/commits; keep GitHub publication pending authorization.

## References
PLAN.md; CONTRIBUTING.md; docs/ASSIGNMENT.md; docs/GITHUB_SETUP.md.

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
