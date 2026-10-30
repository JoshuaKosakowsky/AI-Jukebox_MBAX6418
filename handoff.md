# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Task: publish failure audit and allow independent concurrent PRs.
## Constraints
Joshua explicitly authorized parallel independent PRs now; keep protected reviews/checks and issue ownership.
## Repository state
Branch codex/a3-08-recovery-audit from main 7b9dd2b; audit/review evidence through 2d19839 is pushed.
PR #20 and codex/moonlit-sample-candidate are separate tasks; no application files changed in this audit.
## Work completed and decisions
#8: seven offline backend probe groups and browser failure/recovery observations; one P2 music retry lock after 429.
RECOVERY_AUDIT includes safe JSON/screenshots, runnable offline probes, reload workaround and focused fix guidance.
#21: independent review/recheck at 3245fcd still reproduced the new lyrics retry lock; formal review remains recorded.
Updated AGENTS/CONTRIBUTING: concurrent independent PRs allowed; coordinate overlap/dependencies as needed.
The candidate PR carries the identical guide update, so either merge order works; reconcile handoff text on integration.
## Validation
Audit: seven probe groups and 115 tests passed; verifier 73 files after review records; coverage 36/11/19.
#21 recheck: 127 tests, verifier 67 files and four exact-head CI checks passed on 3245fcd; retry still failed in browser.
All fault probes used MockTransport/synthetic media; no real class keys/requests. Harnesses stopped.
Final guide/handoff checks passed: verifier 73 files, coverage 36/11/19, whitespace clean; runtime/protection untouched.
## Blockers and unchecked areas
prse4479 owns #8's fix; coordinate shared app.js edits with Mike's #21. No code fix or normal-launch acceptance here.
Full submission NOT READY; review/candidate records preserve their separate scopes. No dependency on #20's approval.
## Next steps
1. Teammate reviews the evidence PR; merge normally after approval and green CI.
2. prse implements the focused retry fix and browser regression, coordinating with Mike.
3. Record normal-launch recovery as remaining features integrate; preserve task notes when merging handoff updates.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/8#issuecomment-6512838146
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/21#pullrequestreview-5707271820
Audit: docs/RECOVERY_AUDIT.md; results/a3-08-recovery-audit.json; results/pr21-independent-review.json.

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
