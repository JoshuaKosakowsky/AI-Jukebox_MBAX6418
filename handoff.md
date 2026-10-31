# Agent handoff

## Session
2026-10-30 America/Denver; Codex for Joshua. Catch-up: PR #25, Desert Drive candidate packaging.
## Repository state
Branch codex/desert-drive-sample-candidate; pre-sync 2cb5e01; merged main c6e1273 after normal #32 approval/merge.
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
PR #25; merged #32; current draft #27 diagnosis and reviewer coordination on GitHub.

## Preserved prior task notes

## Session
2026-10-30 America/Denver; Codex for Joshua. Task: review Mase's latest update, then prepare #25 for Jovi.
## Constraints
MSpanny = Mike; mase7919/Mase = Matt. Protected PR/review workflow; no self-approval or assignments changed.
No new generation, class calls, media edits, listening or final sample selection.
## Repository state
Branch codex/desert-drive-sample-candidate; pre-handoff 7ac548d, synchronized with main 2a19ecf.
Resolved only handoff/results index conflicts; app/tests/dependencies/contracts match current main.
## Work completed and decisions
Mase #27 2cdfe38 removes one handoff marker only; CI 4/4 green, playback findings/draft remain.
Preserved Desert Drive's original WAV/PNG/candidate record/preview byte-for-byte, including DESSERT DRIVE lettering disclosure.
Preserved both candidate and Windows ZIP evidence indexes; manifest remains empty and unchanged.
#30 retry fix is integrated; #22 audit is separate and awaiting review. Mike's #24/#26/#29 remain unchanged.
## Validation
Rechecked original acceptance SHA-256s, full WAV frame data and PNG decode; results reported on #25's checked head.
Locked suite/verifier/coverage/whitespace and conflict-marker scan run before push; no live/browser/listening rerun claimed.
Prior candidate preview/listening remain historical, with their original tester/scope in the untouched provenance.
## Blockers and unchecked areas
Jovi or another eligible zero-commit teammate must review the current head before normal merge.
Candidate packaging does not select an approved sample, populate the manifest, load it in-app or satisfy final ZIP acceptance.
#3 live vocals, #5/#6 DJ/references and full #8/#7/#10 acceptance remain; submission NOT READY.
## Next steps
1. Jovi/eligible teammate reviews #25 current head; merge normally after approval, current CI and resolved conversations.
2. Jovi selects the final three pairs and implements/verifies the sample library; reuse retained media.
3. Preserve #22/#24 credit/evidence when reconciling later PRs; do not rerun class generation on session changes.
## References
assets/samples/desert-drive.candidate.json; results/main-instrumental-acceptance.json; PR #25; issue #7.

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
