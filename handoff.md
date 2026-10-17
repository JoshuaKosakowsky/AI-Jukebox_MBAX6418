# Agent handoff

## Session
2026-10-17 America/Denver; Codex. Task: docs-only lead/contributor team workflow.
## Constraints
No code/hooks/tests/config/service changes. No invitations, live issue-body edits
or assignments. Review requests deferred until Joshua names teammates. Protected
PR workflow applies; the explicitly authorized final exception is complete.
## Repository state
Branch codex/team-assignee-workflow; fresh origin/main base 8e41e6cdabf05bd629bd8e8869365ae3a05c4643.
PR #13 merged exact head d714d04; main CI passed; protection was restored byte-identically.
## Work completed and decisions
Issues allow one lead plus up to two contributors. Assignment does not determine
review eligibility: zero commits on the PR required. Approving reviewer or lead
merges; branch freezes for review. Updated guides and all 11 local task briefs.
Unavailable-reviewer procedure is unchanged; live issue bodies remain for Joshua.
## Validation
Scaffold/coverage and all 28 tests pass; whitespace checks clean; zero obsolete
terminology hits. Only Markdown changed. Unavailable-reviewer section unchanged;
live protection still byte-identical to the saved baseline after the docs change.
## Blockers and unchecked areas
This docs change awaits normal PR review/merge; app/startup/samples remain absent.
No independent review is claimed for PR #12 or the final authorized PR #13 integration.
## Next steps
1. Review/merge this docs PR without weakening protection.
2. On merge, add one completion row in docs/CONTRIBUTIONS.md for this docs change.
3. Joshua invites teammates and assigns leads/contributors and the integration owner.
## References
PLAN.md; CONTRIBUTING.md; docs/ISSUES.md;
[final exception audit](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/13#issuecomment-6240577780).

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
