# Agent handoff

## Session
2026-10-30 America/Denver; Codex for Joshua. Catch-up: PR #22, historical recovery audit and integration status.
## Repository state
Branch codex/a3-08-recovery-audit; pre-sync 89a28a6; merged main c6e1273 after normal #32 approval/merge.
## Work and decisions
Resolved documentation/index/handoff conflicts; preserved evidence and prior notes.
Clarified #32 hash-prefix/vocal-implementation wording without changing observations; added its independent review credit.
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
PR #22; merged #32; current draft #27 diagnosis and reviewer coordination on GitHub.

## Preserved prior task notes

## Session
2026-10-30 America/Denver; Codex for Joshua. Task: new-push/review triage and protected integration.
## Constraints
MSpanny = Mike; mase7919/Mase = Matt. Protected reviews/checks; no assignment changes or class calls.
## Repository state
#30 merged normally at main 2a19ecf after Mike approved exact 62506de and CI 4/4 passed.
#22 reconciled with main; pre-handoff 149090c. Historical audit remains, with current correction status linked.
## Work completed and decisions
Mike's #30 approval independently reproduced baseline failure/patched success; recorded its review credit.
Updated PLAN/audit status and preserved #20 ZIP, #22 historical probes, #23 candidate and distinct review records.
Matt's new #27 74ebc0b adds partial live evidence only; AT-07/09 correctly remain failed/incomplete.
Posted qualification request: writing status is not successful Qwen/Chatterbox evidence; job accounting and both spoken introductions are unverified.
#27's 895a616 cleanup remains verified fixed; manual-player/DJ overlap remains open. No additional live run performed.
## Validation
#30 approved head: 129 locked tests, verifier 77, coverage 36/11/19; CI 4/4 green before normal merge.
#22 final checked head: tests/verifier/coverage/whitespace reported in its follow-up comment; app source matches merged main.
Prior #29 review: 131 tests; arbitrary error metadata + malformed-message findings remain. Prior #27: 151 tests.
No test servers started this session; no credentials, uploads, generated media or new listening.
## Blockers and unchecked areas
#22/#28 await independent review; #24 still needs Mike's main sync/fresh approval; #26/#29 unchanged with requested changes.
#25 Desert Drive remains a candidate awaiting review; manifest/library incomplete. #3 live acceptance failed; submission NOT READY.
## Next steps
1. Eligible teammate reviews current #22; reconcile remaining task branches with current main under normal protection.
2. Mike fixes #26/#29 and syncs #24; Matt syncs #27, fixes overlap and qualifies incomplete evidence before readiness.
3. Preserve #8's broader acceptance, #7 sample library and independent final ZIP requirements; no automatic new generation.
## References
PRs #22/#24/#25/#26/#27/#28/#29/#30; docs/RECOVERY_AUDIT.md; results/retry-control-fix.json.

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
