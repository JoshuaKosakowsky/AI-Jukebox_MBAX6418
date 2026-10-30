# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Independent integration support: #20 ZIP evidence and #22 recovery audit.
## Constraints
Normal protected reviews/checks; no app changes or class calls. Matt leads #5/#6, Mike #3, prse #8/#9, jovi #7/#10.
## Repository state
Main e2b1e52 includes #21 vocals and #23 Moonlit candidate/preview fix. #20/#22 are being reconciled with that base.
Live issues/PRs are authoritative; Mike's #24 owns his implementation/review credit and may still need a main sync.
## Work completed and decisions
#20 retains the original 7b9dd2b ZIP rehearsal; no new release/independent-install acceptance claimed.
#22 retains the offline #8 audit/reproductions and Joshua's #21 review evidence; omit Mike's duplicate implementation row covered in #24.
Historical audit finding remains for prse: instrumental retry after capacity rejection; Mike's lyrics retry fix is a separate merged correction.
#23 media remain candidate-only; jovi owns final sample selection/library/ZIP. No task ownership is taken over here.
Desert Drive second candidate is ready in PR #25 for jovi; exact original media and cover-lettering limitation retained.
Confirmed cover-retry and Resume check capacity-rejection variants on isolated main e2b1e52; both stay disabled after release/refresh.
Reload plus explicit retry succeeds; resume uses its original ticket. Added safe record, screenshots and manual harness; no app fix.
## Validation
Variant audit: 71 isolated source files unchanged; MockTransport only; no .env or external calls; harnesses stopped.
Run locked checks and diff check after these artifacts; exact head/counts/CI posted on #22.
Prior 128-test baseline and offline/live evidence keep their stated scope; no new generation, listening or release acceptance here.
## Blockers and unchecked areas
#3 live vocal/browser/listening acceptance, #5/#6 DJ/references, #8 recovery fix, final samples and independent ZIP remain incomplete; NOT READY.
Any branch update requires fresh eligible approval and current green CI. Reviewers must have no commits on that PR.
## Next steps
1. Matt/prse review #22 with the new recovery evidence; prse owns a focused fix for instrumental/cover/resume controls, coordinating app.js with Matt.
2. Mike finishes #3 acceptance; Matt implements #5 then #6. They independently review each other's PRs.
3. Prse coordinates any unpublished #5 work with Matt and retains #8/#9; reconcile #22/#24 credit without duplication.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/24

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
