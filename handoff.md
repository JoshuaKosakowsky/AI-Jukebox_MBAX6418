# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Task: verify Mike's correction and record current integration handoff.
## Constraints
Independent concurrent PRs authorized; protected reviews/checks and issue ownership remain. No class generation here.
## Repository state
Branch codex/a3-08-recovery-audit, PR #22; pre-handoff 108d0f5. #23 is the separate Moonlit candidate PR.
Mike's #21 at 04650a5 is independently approved and its blocking thread resolved; no merge performed.
#20 is approved; #22/#23 await teammate review. Live GitHub remains authoritative if those states change.
## Work completed and decisions
#8's instrumental retry finding, offline reproductions and workaround remain valid on main 7b9dd2b; prse owns its fix.
Mike fixed the new lyrics-control instance: rejected 429 now restores the control; retry after capacity frees succeeds.
Pending-lyrics reload no longer starts music: mock submissions stayed at two until the deliberate third request.
Recorded exact-head approval/browser evidence, enabled-control screenshot, combined review credit and audit status note.
## Validation
#21: 128 tests, verifier 67 files, coverage 36/11/19, diff clean; all four exact-head CI checks green on 04650a5.
Independent browser used only MockTransport/synthetic media; no real keys/requests/listening. Harness stopped; clone clean.
Audit artifact checks passed: verifier 74 files, coverage 36/11/19, staged whitespace clean; app source unchanged.
## Blockers and unchecked areas
#3 live Qwen/ACE-Step vocal run, human listening and integrated-main acceptance remain open; approval is partial scope.
#8's instrumental fix and normal-launch recovery, DJ/references/samples/final ZIP remain incomplete; NOT READY.
## Next steps
1. Mike/eligible teammate merges #21 normally; perform bounded normal-launch vocal acceptance on integrated main afterward.
2. Teammates review #22/#23 independently; prse coordinates the outstanding instrumental-control correction.
3. Preserve all task notes on handoff reconciliation; update contributions as work merges, without duplicate review rows.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/21#pullrequestreview-5707544155
Audit: docs/RECOVERY_AUDIT.md; results/pr21-independent-review.json; results/pr21-lyrics-retry-enabled.jpg.

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
