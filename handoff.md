# Agent handoff

## Session
2026-10-30 America/Denver; Codex for Joshua. Catch-up: PR #28, failed vocal acceptance evidence.
## Repository state
Branch codex/a3-03-live-acceptance; pre-sync 0bb7fea; merged main c6e1273 after normal #32 approval/merge.
## Work and decisions
Resolved only documentation/index/handoff integration conflicts; preserved both branches' evidence and prior notes.
Runtime source, tests, contracts, dependencies and hooks match current main; no new behavior in this sync.
Candidate assets and approved manifest unchanged; failed/historical observations retain their original tester and scope.
## Validation
Verifier, coverage, whitespace, source-equivalence and exact-head CI recorded on the PR; no new app/live/browser claim.
## Blockers and current routing
Own #22/#25/#28/#31 await eligible teammate review; no returned findings on them. Broaden pool beyond Mike/Jovi.
Mike #26/#29 still need their two requested corrections; #24 needs author sync and fresh approval.
Matt #27 draft: old retry/exclusivity fixes rechecked separately; real DJ Qwen exhausted 192 tokens with no content.
Separate bounded diagnosis used 1 text + 1 speech request, no retries/music/art; Chatterbox PCM decode passed.
Assignments already permit backup work and any zero-commit reviewer; no ownership/protection changes.
## Next steps
1. Review this exact head after green CI; merge only via normal protected approval.
2. Preserve remaining vocal/DJ/reference/sample acceptance gaps; submission NOT READY.
3. Use current issue handoffs for coordination; final sample selection/ZIP remain with Jovi.
## References
PR #28; merged #32; current draft #27 diagnosis and reviewer coordination on GitHub.

## Preserved prior task notes

## Session
2026-10-30 America/Denver; Codex for Joshua. Task: bounded live vocal acceptance after PR triage.
## Constraints
MSpanny = Mike; mase7919/Mase = Matt. Mike leads #3/#6; Matt #5; assignments unchanged.
One form request only: at most one lyrics, cover and music submission; no retry on uncertainty.
## Repository state
Clean tested main 770ce62; branch codex/a3-03-live-acceptance contains evidence/docs only.
#20 merged; #22 149090c fixes names/ownership and awaits review; #26 requests changes; #24 sync requested.
## Work completed and decisions
Normal launcher + real browser form: Morning Signal / Acoustic indie pop / Hopeful and upbeat / 30 s / Vocal.
Cover succeeded; lyrics returned safe invalid_response; zero music jobs/audio. No second generation attempted.
Before/after reload snapshots identical; Retry lyrics enabled; no browser error/warning entries observed.
Saved public JSON and actual card screenshot; raw generated cover ignored, no user recordings or keys committed.
## Validation
AT-04 FAIL; precise parser guard unknown because raw provider response/finish metadata was not retained.
Source rejects unexpected model, empty content or non-stop completion; no speculative budget/schema change.
Final repository/coverage/whitespace checks recorded in the PR; no application code/dependency changes.
Earlier independent #26 checks: 137 tests; #22 reconciliation: 128 tests, both CI 4/4 green at review.
## Blockers and unchecked areas
#3 live vocal/playback/listening acceptance still blocked. No music, speech or reference calls in this run.
#26 upload findings, draft #27 DJ, #8 control fixes, sample library and final ZIP remain; NOT READY.
## Next steps
1. Mike diagnoses #3 using safe response metadata in a separately bounded run; retain this failed case.
2. Mike fixes #26 and synchronizes #24; Matt finalizes #27 readiness; eligible teammates review #22.
3. Preserve current claim/ownership and coordinate shared files; do not repeat generation merely to refresh context.
## References
results/vocal-live-failure-record.json; docs/TEST_RESULTS.md; issue #3; PRs #20/#22/#24/#26/#27.

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


## Preserved prse recovery handoff from main c6e1273

## Session
2026-10-30 America/Denver; prse4479 (A3-08 lead). Task: normal-launch AT-10
failure/recovery evidence; lead continues #8 while Matt's #27 (DJ overlap) and
Joshua's merged #30 fix stay in place.

## Constraints
No source edits: evidence only (results JSON + screenshots, TEST_RESULTS,
results/README, handoff). No ownership/protection changes, no class-call
beyond the normal app flow, no port 9000/paid services. .env stays local and
gitignored (all four roles configured with the class key). Recheck that no
credential material enters diffs/archives before merging.

## Repository state
Clone at main `2a19ecf` (contains retry-control fix merge #30, vocal merge
#21, sample merge #23). Branch `codex/a3-08-normal-launch-recovery` carries
the evidence. PR #22 (recovery audit) remains open and separate.

## Work completed and decisions
Live normal-launcher evidence recorded on real services (dobolyi.com ports
9001/9006/9007/9008, models verified via /v1/models): (1) busy-capacity 429 in
the real UI - fifth 60 s instrumental rejected by the app guard with the safe
message "Music generation is busy. Try again shortly.", no job created, then
explicit Generate instrumental retry after slots freed succeeded - all five
tracks playable with five unique 60 s WAV/PNG pairs (sha256 recorded); (2)
deterministic missing-music-config case: safe "Missing settings" + actionable
notice, cover still generated, then .env restore + restart + recreate
succeeded. Combined with the existing offline audit (#22), this closes #8's
normal-launch AT-10 gap for instrumentals. Safeguards audit (R07/R23/R24/R25)
clean: allowlist-only config, no port 9000/credentials in tree or history,
no uploads/voice/third-party media; verify_repo.py enforces the same.

## Validation
Real browser (local Chrome) UI checks with actual screenshots; media decoded
from the app's own /api/media (sha256 + WAV header). Local suite caveat:
Apple git 2.39.3 (no `git hook run --to-stdin`, needs >= 2.40) and system node
v6.10.1 fail 7 hook tests + 1 frontend probe - environment, CI green.
Portable node 22.14.0 (arm64) and a NO_GETTEXT local git build under scratch
used to rerun the full suite (results appended to the evidence record). No
privacy leaks: no .env content, keys, or real media bytes in any artifact.

## Blockers and unchecked areas
Vocals/DJ/reference flows not yet on main - their failure/recovery paths stay
open on #8. Session-limit cases unchanged. No ZIP/release acceptance;
submission NOT READY. Homebrew on this machine cannot install (locks dir
permissions) - use portable/scratch toolchains, do not sudo-fix silently.

## Next steps
1. Eligible teammate (zero commits on the PR: MSpanny or jovi1214) reviews
   `codex/a3-08-normal-launch-recovery`; keep #8 open until vocals/DJ land.
2. When #27 (Matt) merges, coordinate shared app.js coverage for DJ retry
   controls; then re-run integrated failure cases for the DJ flow.
3. Fold the macOS tooling note (git >= 2.40, node >= 18) into TESTING.md when
   convenient; optional, not required for acceptance.

## References
Issue #8; results/a3-08-normal-launch-recovery.json (evidence record);
results/a3-08-*.jpg (screenshots); docs/TEST_RESULTS.md (A3-08 normal-launch
section); PR #22 (offline audit); PR #30 (retry-control fix).

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
