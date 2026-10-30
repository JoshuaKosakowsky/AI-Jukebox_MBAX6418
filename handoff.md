# Agent handoff

## Session
2026-10-30 America/Denver (MDT); Hermes for MSpanny. Task: A3-03 lyrics parser diagnostics (#3 lead; follow-up to Joshua's failed live run, PR #28). Branch codex/a3-03-lyrics-diagnostics from main 770ce62.

## Constraints
Task branch + reviewed PR; no main/protection/assignment changes. Fix is offline-only: NO speculative token-budget/schema changes; bounded live rerun stays pending class .env.

## Repository state
Main 770ce62 = #23 Moonlit + #20 ZIP evidence merged. Open: #22 audit, #24 contributions, #25 Desert Drive candidate, #26 A3-06 references (MSpanny; CI green), #28 failure record. no other PR touches providers.py/tests/test_providers.py.

## Work completed and decisions
text()/lyrics() refactored onto a shared `_chat` guard whose SafeError names the exact failing condition: unexpected model id, missing/empty content (finish included), or non-stop finish (e.g. length). Safe metadata only (model ids + finish_reason; never raw content/reasoning). Behavior unchanged: content accepted only when present, non-empty, stop. Reasoning fields never leak. 3 new MockTransport guard tests; probe-fidelity test still byte-identical. Docs: TEST_RESULTS diagnostics section; this handoff.

## Validation
python scripts/dev.py --check PASS: 131 tests (128 prior + 3 new), verifier 74 files, coverage 36/11/19. No live calls.

## Blockers and unchecked areas
Live cause still unknown until the bounded rerun with class keys (.env absent here). AT-04/#3 remain open/failed (Joshua's run on 770ce62 failed at the lyrics guard). Human listening pending. #6 lead discrepancy (issue says MSpanny; Josh handoff text says Matt) flagged on #20 review; issue remains authoritative.

## Next steps
1. Open PR (Refs #3, honest: diagnostics only, live rerun pending), request Matt's review.
2. When .env exists: bounded normal-launch vocal rerun — the parser now reports which guard fired (or succeeds); then decoded-media + browser + listening acceptance for AT-04.
3. If the cause is finish=length: decide with team whether to raise the lyrics budget further (documented live-evidence change), not blind.

## References
Issue #3; PR #28 (Joshua's failure record); docs/TEST_RESULTS.md diagnostics section; tests/test_providers.py.

### Session (Codex for Joshua, #20/#22 integration)
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
## Validation
Run python scripts/dev.py --check and git diff --check per reconciled head; record exact results/CI on #20/#22.
Prior 128-test baseline and offline/live evidence keep their stated scope; no new generation, listening or release acceptance here.
## Blockers and unchecked areas
#3 live vocal/browser/listening acceptance, #5/#6 DJ/references, #8 recovery fix, final samples and independent ZIP remain incomplete; NOT READY.
Any branch update requires fresh eligible approval and current green CI. Reviewers must have no commits on that PR.
## Next steps
1. Mike reviews reconciled #20; Matt/prse review #22. Merge normally only with current approval/checks; sync remaining PRs afterward.
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
