# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Task: isolated instrumental failure/recovery audit, Refs #8.
## Constraints
Support prse4479; keep Mike's application work untouched. No actual class requests/keys; no self-approval.
## Repository state
Branch codex/a3-08-recovery-audit from main 7b9dd2b; PR #20 remains the author's active PR awaiting review.
Mike has opened vocal PR #21; audit does not review or change it. PR #20 evidence remains on its own branch.
## Work completed and decisions
Seven backend fault groups passed; offline real-browser 503 cover retry and music timeout resume passed.
Confirmed P2: after a 429, a card's Generate instrumental stays disabled after slots free and Refresh status.
Reload then explicit retry recovers. Likely cached-card skip in app.js; documented steps/fix guidance for prse4479.
Added RECOVERY_AUDIT, safe JSON/screenshots and standalone offline reproductions; application files untouched.
All 65 isolated source files unchanged; harness stopped; no private .env was loaded.
## Validation
Backend probes passed through real routes/store/provider parsers with MockTransport; no real requests.
Locked checks passed: 115 tests, verifier 71 files, coverage 36/11/19; staged whitespace clean. AT-10/12 remain partial.
## Blockers and unchecked areas
Shared app.js fix must coordinate with Mike's #21; normal-launch/live failure recovery still required.
Keep one active PR: publish the audit as branch + #8 findings while #20 awaits review; do not merge unreviewed.
## Next steps
1. prse4479 coordinates the focused retry fix with Mike and adds actual browser regression coverage.
2. Open/review the audit PR after #20 merges; preserve honest fixture-vs-live evidence and add credit on merge.
3. Retest normal-launch recovery as remaining features integrate; leave issue ownership unchanged.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/8
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20

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
