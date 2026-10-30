# Agent handoff

## Session
2026-10-29 America/Denver (MDT); Hermes for MSpanny (Michael). Task: A3-03 vocal songs with AI lyrics (#3 lead; claimed, label status: in progress).

## Constraints
Task branch + reviewed PR only; no main/protection/assignment changes. One deliberate live lyrics/music acceptance run once class keys exist; reloads and offline tests never submit generation.

## Repository state
Branch codex/a3-03-vocal-songs from main 7b9dd2b (PR #19 merged). No other open PRs touch these files. Local machine has NO .env — live acceptance blocked until the class keys exist.

## Work completed and decisions
- providers.lyrics(prompt): same verified Qwen chat endpoint/model; max_completion_tokens 192->512 for this call only (documented deviation, live evidence pending).
- SessionStore: queue_lyrics/generate_lyrics (text kind, MAX_ACTIVE_TEXT=1, 404/409/422/429 validations, lyrics attach to Track.lyrics, replacement replaces, failure retryable); queue_music now 409s vocal tracks without lyrics and generate_music re-checks at submit so a job can never silently fall back to the "[Instrumental]" marker; vocal music submits track's current lyrics in the SAME frozen ACE-Step request with a vocal-aware prompt; instrumental path byte-identical.
- app.py: POST /api/tracks/{id}/lyrics (require_text) + lyrics_generation_available status flag.
- Frontend: mode radio (Instrumental | Vocal with AI lyrics) on the create form; one-click vocal chain = cover job at create, then lyrics job, then the poll loop starts vocal music EXACTLY once when a lyrics job observed alive succeeds (seeded from first snapshot so page reloads never auto-submit; a music job's existence blocks re-chaining; failed vocal stays a manual button). Cards show a collapsible lyrics block, lyrics status line and mode-aware buttons (Generate lyrics / Retry lyrics / Generate new lyrics; Generate vocal song / Generate new vocal song; Resume check unchanged). Instrumental flow and playback-preservation rules unchanged.
- Tests: tests/test_lyrics.py (5 HTTP + 7 store, incl. 409-no-lyrics zero-side-effects, submit-time guard, out-of-order safety, no-key-leak, config-missing never calls providers) + 3 new static frontend guards.
- Docs: README (intro, behavior steps, API list, next task), docs/APP_CONTRACTS.md (lyrics route, status flag, vocal orchestration section, bounds, adapter bullet), this handoff.

## Validation
python scripts/dev.py --check PASS on this branch: verifier 65 files, coverage 36 requirements/11 tasks/19 cases, all 127 tests (115 baseline + 12 new); schema untouched; Starlette TestClient deprecation warning pre-existing. NO live Qwen/ACE-Step acceptance performed (no .env on this machine).

## Blockers and unchecked areas
No class keys locally: live vocal acceptance (R10/AT-04 inputs+results), audible/visual browser verification and the token-budget deviation evidence are pending. Interactive-browser vocal chain not yet exercised in a real browser (static guards + offline HTTP only). PR not yet opened.

## Next steps
1. User supplies .env (class keys, never paste in chat) -> run deliberate live vocal acceptance through the normal launcher: one Qwen lyrics call + one ACE-Step vocal + automatic cover; decode/non-silent check; record results/vocal-live-record.json and add an A3-03 evidence section in docs/TEST_RESULTS.md.
2. Open the PR (Closes #3 refs per brief; honest status: offline-verified, live run pending) and request a teammate review (Matt or Joshua; zero commits on this PR).
3. On merge: verify the vocal flow on integrated main, then docs/CONTRIBUTIONS.md row + close #3. #5 (DJ queue) is the next feature and consumes the same Track/MediaRef contracts.

## References
Issue #3; docs/ISSUES.md A3-03 brief (R10/AT-04); docs/SERVICE_CONTRACTS.md; docs/APP_CONTRACTS.md; tests/test_lyrics.py; tests/test_frontend.py.

### Session (Codex for Joshua, #19 publication follow-up)
2026-10-29 America/Denver; Codex for Joshua. Task: publish #19 corrections and sync OneDrive.
### Constraints
Joshua authorized repo commits/messages/pushes and local sync. Protected PR workflow; no self-approval.
### Repository state
Branch codex/a3-02-browser-acceptance; pre-handoff 99536f2 pushed; main 7cc9645.
Original OneDrive checkout fast-forwarded cleanly to 99536f2; ignored .env preserved.
Review clone /private/tmp/ai-jukebox-review-20261029 has the same tracked branch.
### Work completed and decisions
Corrected TEST_RESULTS count to 40 PASS / 0 FAIL, attributed to Matt's review recount;
external qa-browser-final.txt unavailable for our own recount. Updated results/README evidence,
CONTRIBUTIONS listening credit and README's contradictory acceptance statement. No app/dependency changes.
Posted correction summary to #19 and formally requested mase7919 re-review; approval still required.
Pinned OneDrive repo via Finder; cloud-only Git metadata downloaded, allowing safe fetch/fast-forward.
### Validation
Earlier locked checks: 115 tests, verifier 65 files, coverage 36/11/19 with Python 3.12.14/Git 2.53.
05f4382 CI caught missing required headings in handoff, edited after those checks; restored them here.
Initial Apple Git 2.39 run failed 7 hook tests (--to-stdin unsupported); current Git resolved those.
All four GitHub CI checks passed on 99536f2. Final handoff verifier/coverage/whitespace checks pass.
No new class-service generation or browser acceptance run.
### Blockers and unchecked areas
#19 awaits Matt's re-review on the final documentation head; no merge or review dismissal.
Submission NOT READY; remaining feature work unchanged. OneDrive filesystem sync is managed by its client.
### Next steps
1. Matt verifies #19 corrections on the final head; merge normally after approval and green CI.
2. Keep the OneDrive task branch aligned with GitHub; local main already matches origin/main.
3. #3 vocals (jovi1214) and #5 DJ queue (prse4479) ready; references/samples/independent ZIP follow.
### References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/19#issuecomment-6500246029

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
