# Agent handoff

## Session
2026-10-29 22:15 America/Denver; Codex for Joshua. End-of-evening stopping point; refresh live GitHub before resuming.
## Constraints
Protected PR workflow unchanged. Claim exact pieces/branches/files; use explicit handoffs, avoid duplicate active work. No app changes or new class calls this session.
## Repository state
Checkout codex/a3-08-recovery-audit (#22); pre-handoff 8654a8a; clean/synced before this documentation update. Main e2b1e52 includes #21 vocals and #23 Moonlit.
#20 de256e2, #22 and #25 7ac548d await fresh review; #24 aa14c97 is approved but behind main. Sync/recheck remaining PRs after any merge.
## Work completed and decisions
#20 preserves historical ZIP rehearsal; #22 contains offline recovery probes/screenshots and Joshua's #21 review credit. Mike's credit is in #24; keep distinct rows on reconciliation.
#8 now has three confirmed disabled-control cases: instrumental retry, Retry cover and Resume check after capacity rejection. Reload + explicit retry works; resume reuses the original task.
#25 packages original Desert Drive (not earlier chat's Dawn), hashes/provenance and muted preview. Known DESSERT DRIVE cover lettering documented; no new generation/listening. Manifest unchanged.
Live #3/#5-10 issues now define lead/backup, next steps and eligible review pools. Matt leads #5; Mike #3/#6; prse #8/#9; jovi #7/#10.
Matt/prse back each other on #5/#8/#9; Mike/jovi on #3/#6/#7/#10. Reviewer must have no commits on that PR; use the other pair if both assignees implement.
## Validation
8654a8a: 128 tests, verifier 84 files, coverage structure 36/11/19 and all four CI checks passed. This final edit is handoff-only; recheck verifier/links/whitespace before push.
#25: 128 tests/all four CI green; WAV/PNG full decode and original/staged hashes match; muted browser play/pause/resume passed. Not sample-library/ZIP acceptance.
Offline recovery used synthetic media/MockTransport, no .env or external requests; all 71 isolated main files stayed identical. All temporary servers stopped; no merge/rebase in progress.
## Blockers and unchecked areas
#3 live vocal/browser/listening acceptance, #5/#6 DJ/references, #8 fixes, final sample library and independent ZIP remain incomplete; NOT READY. Published inactivity does not prove no local work.
## Next steps
1. Matt: #5; Mike: finish #3 acceptance, then #6 after #5 integration. Claim optional backup pieces only if unclaimed or explicitly handed off.
2. Tomorrow prse: #8 control correction/regressions coordinated with Matt's app.js, then #9. Jovi: select/integrate three samples (#23/#25 candidates), then arrange #10's independent final ZIP after prerequisites.
3. Any eligible teammate reviews #20/#22/#24/#25; prse/jovi may review each other tomorrow. Keep branches still during review; require current approval/checks, resolve conversations, merge normally.
## References
[Shared work/review coverage](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5#issuecomment-6514747773)
[Recovery PR #22](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22); [candidate PR #25](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/25)
[ZIP PR #20](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20); [credit PR #24](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/24)

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
