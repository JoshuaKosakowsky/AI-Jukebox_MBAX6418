# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Shared integration handoff for PR #20 ZIP evidence and #23 Moonlit candidate.
## Constraints
Protected reviews/checks unchanged; concurrent independent PRs authorized. Preserve prse's #5/#8/#9 and jovi's #7/#10 ownership.
## Repository state
Branches codex/windows-zip-startup (#20) and codex/moonlit-sample-candidate (#23), each reconciled against main 7d003c6.
Main includes Mike's #21; live vocal/listening acceptance still remains on #3. Audit/review records stay in PR #22.
Both branches use this same consolidated handoff to avoid conflicting status rewrites on the next merge.
## Work completed and decisions
#20 preserves the original 7b9dd2b ZIP identity/65-file startup rehearsal alongside Mike's vocal evidence; no new ZIP acceptance claimed.
#23 retains the original Moonlit WAV/PNG, hashes/provenance and candidate status; final manifest/library/ZIP acceptance still belongs to jovi.
The Moonlit preview index entry belongs to #23's results README; #20 keeps only its ZIP evidence additions.
Reconciliation changes docs/handoff only; inherited application code matches main. No prse task or assignment is taken over.
## Validation
Merged-main baseline: 128 tests and four CI checks passed; prior media decoding/preview and ZIP observations retain their original scope.
Run python scripts/dev.py --check and git diff --check for each reconciled head; exact results/head IDs are posted on #20/#23.
No class-service generation, new media, credentials or user uploads were introduced during reconciliation.
## Blockers and unchecked areas
Fresh review is required after these updates; request MSpanny on both heads and keep normal protection in force.
No published prse branch/PR was affected; unpublished local work is not visible. Her task ownership remains unchanged.
#3 live vocal acceptance, #8 instrumental fix, DJ/reference features, final samples and independent ZIP remain incomplete; NOT READY.
## Next steps
1. Mike re-reviews the updated #20/#23 heads; merge normally only after eligible approval and green CI.
2. Recheck the remaining PR against main after the first merge; retain all distinct evidence and task notes.
3. Continue normal-launch vocal acceptance on main; prse's feature/recovery work and jovi's sample/ZIP work can proceed separately.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/23
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22

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
