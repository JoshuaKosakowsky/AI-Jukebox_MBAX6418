# Agent handoff

## Session
2026-10-30 America/Denver (MDT); Hermes for MSpanny. Task: A3-06 temporary reference voices (R15/R16 provider layer; #6 lead, claimed, label status: in progress).

## Constraints
Task branch + reviewed PR only; no main/protection/assignment changes. No uploads/voice references committed; no live class call until #5 integration (Chatterbox reference path is schema-inspected only). Branch/PR: codex/a3-06-reference-voices.

## Repository state
Branch from main e2b1e52 (includes merged #21 vocals and #23 Moonlit candidate). No other open PR touches jukebox/app.py, sessions.py, providers.py, tests/test_references.py or pyproject/uv.lock. #20/#22/#24/#25 open; #3 live acceptance still pending (no .env).

## Work completed and decisions
- POST /api/references/speech (multipart file) + DELETE /api/references/speech/{id}; session-scoped memory-only store (Session.references), magic-byte sniffing (WAV/MP3), 5 MB cap, WAV 1-60 s duration validation; take_reference consumes exactly once; expiry deletes with session; references invisible to GET /api/session (no contract change); no read route (GET=405).
- ClassProviders.speech(text, reference=...) appends ref_audio as base64 data URI to the frozen probe request; no-reference path byte-identical; python-multipart 0.0.32 added to locked env (pyproject + uv.lock).
- Tests: tests/test_references.py (3 HTTP + 3 store + 2 provider = 8 test methods, 9 collected with sub-suite) — validation, isolation, capacity, consumption, expiry, snapshot invisibility, probe equality, data-URI payload.
- Docs: APP_CONTRACTS routes + "Temporary reference voices (interface for #5)" section + adapter bullet; README API note; TEST_RESULTS A3-06 offline section; this handoff.

## Validation
python scripts/dev.py --check PASS on this branch: verifier 71 files, coverage 36/11/19, all 137 tests (128 prior + 9 new). No live class-service calls; Chatterbox reference path still schema-inspected-only (needs .env for AT-08 acceptance; #5 supplies the normal-entrypoint flow).

## Blockers and unchecked areas
Final #6 acceptance blocked on #5 (DJ queue) — interface documented in APP_CONTRACTS for prse/Matt. Live MP3+WAV reference verification pending (.env + #5). MP3 duration not decoded at upload (documented). PR not yet opened.

## Next steps
1. Open the PR (Refs #6; honest: offline-only, live pending), request review from Matt/prse.
2. On merge: coordinate with #5 (prse4479/Matt) — the speech job consumes take_reference; UI upload control lands with the DJ flow.
3. Live acceptance when .env exists: upload a real MP3 AND WAV reference, generate Chatterbox speech with each, verify decoded WAV + default-voice fallback; record in TEST_RESULTS; then close #6 checks.

## References
Issue #6; docs/ISSUES.md A3-06 brief (R15/R16, AT-08); docs/SERVICE_CONTRACTS.md (schema-inspected reference paths); docs/APP_CONTRACTS.md; tests/test_references.py.

### Session (Codex for Joshua, consolidated #20/#23)
2026-10-29 America/Denver; Codex for Joshua. Shared integration handoff for PR #20 ZIP evidence and #23 Moonlit candidate.
### Constraints
Protected reviews/checks unchanged; concurrent independent PRs authorized. Preserve prse's #5/#8/#9 and jovi's #7/#10 ownership.
### Repository state
Branches codex/windows-zip-startup (#20) and codex/moonlit-sample-candidate (#23), each reconciled against main 7d003c6.
Main includes Mike's #21; live vocal/listening acceptance still remains on #3. Audit/review records stay in PR #22.
Both branches use this same consolidated handoff to avoid conflicting status rewrites on the next merge.
### Work completed and decisions
#20 preserves the original 7b9dd2b ZIP identity/65-file startup rehearsal alongside Mike's vocal evidence; no new ZIP acceptance claimed.
#23 retains the original Moonlit WAV/PNG, hashes/provenance and candidate status; final manifest/library/ZIP acceptance still belongs to jovi.
The Moonlit preview index entry belongs to #23's results README; #20 keeps only its ZIP evidence additions.
Reconciliation changes docs/handoff only; inherited application code matches main. No prse task or assignment is taken over.
### Validation
Merged-main baseline: 128 tests and four CI checks passed; prior media decoding/preview and ZIP observations retain their original scope.
Run python scripts/dev.py --check and git diff --check for each reconciled head; exact results/head IDs are posted on #20/#23.
No class-service generation, new media, credentials or user uploads were introduced during reconciliation.
### Blockers and unchecked areas
Fresh review is required after these updates; request MSpanny on both heads and keep normal protection in force.
No published prse branch/PR was affected; unpublished local work is not visible. Her task ownership remains unchanged.
#3 live vocal acceptance, #8 instrumental fix, DJ/reference features, final samples and independent ZIP remain incomplete; NOT READY.
### Next steps
1. Mike re-reviews the updated #20/#23 heads; merge normally only after eligible approval and green CI.
2. Recheck the remaining PR against main after the first merge; retain all distinct evidence and task notes.
3. Continue normal-launch vocal acceptance on main; prse's feature/recovery work and jovi's sample/ZIP work can proceed separately.
### References
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
