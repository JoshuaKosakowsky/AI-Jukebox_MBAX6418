# Agent handoff

## Session
2026-10-30 America/Denver; Codex for Joshua. Task: name/ownership correction and approved PR sequence.
## Constraints
MSpanny = Mike; mase7919 (Mase) = Matt. Mike leads #3/#6; Matt #5; prse #8/#9; jovi #7/#10.
Normal protected PR workflow; user authorized commits/messages/pushes. No assignment changes or class calls.
## Repository state
#20 merged normally at main 770ce62 after Mike approved de256e2 and CI 4/4 passed.
#22 synchronized with main; pre-handoff b2d5a68. No application changes in this reconciliation.
## Work completed and decisions
PLAN now states the name mapping; resolved handoff ownership mismatch without changing issue leads.
Preserved #20 ZIP evidence alongside #22 audit/variants, and added Joshua's separate #26 review credit.
#26 cdb00cd: independent review requests changes for multipart disk spooling/late cap and malformed audio acceptance.
#24 Mike owns his three credit rows; asked him to sync current main and request fresh review (old approval dismissed).
Prior pending work preserved: #8 instrumental/cover/resume retry controls remain disabled after rejection; reload works.
#25 Desert Drive candidate remains for Jovi's review; DESSERT DRIVE cover lettering disclosed; manifest unchanged.
## Validation
#26 locked check PASS: 137 tests, verifier 72 files, coverage 36/11/19; Python 3.12.14/Git 2.53.0.
Offline HTTP probes: valid 1.92 MB WAV spools to disk; oversized upload spools before 422; 44-byte WAV/3-byte ID3 return 201.
Temporary files closed after requests; no claim of persistent files. Synthetic bytes, no .env/providers/user recordings.
#22 final locked check and whitespace results are recorded in its follow-up comment after reconciliation.
## Blockers and unchecked areas
#26 needs Mike's fixes and re-review; #27 Matt's draft DJ queue awaits readiness/review and live acceptance.
#3 live vocal/browser/listening, #5/#6 integration, #8 fixes, three-sample library and independent ZIP remain; NOT READY.
## Next steps
1. Eligible teammate reviews final #22; Mike synchronizes #24 and addresses #26, then request current-head reviews.
2. Matt finalizes #27; coordinate reference consumption/UI with Mike before #6 acceptance; prse/Matt handle #8 shared frontend.
3. Mike/Jovi finish #3 acceptance and #7 sample selection/library; #23/#25 candidates are not final sample acceptance.
## References
[#26 review](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/26#pullrequestreview-5713181117)
[#24 sync request](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/24#issuecomment-6524316120)

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
