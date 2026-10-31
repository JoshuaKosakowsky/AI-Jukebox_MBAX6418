# Agent handoff

## Session
2026-10-30 America/Denver; Codex for Joshua. Catch-up and current-main reconciliation of PR #31.
## Repository state
Branch codex/a3-07-sample-loader; pre-sync head 49c24ec; new main c6e1273 (normal protected merge of #32).
## Work and decisions
Independently reviewed/approved prse's evidence-only #32 with zero commits; normal merge succeeded. #8 stays open.
Merged its docs/evidence into this loader branch; preserved both sample-loader and prse recovery records/handoffs.
No runtime, schema, dependency, approved-manifest or candidate-asset changes in this reconciliation.
## Validation
Previous implementation: 145 locked tests and 4/4 CI on 49c24ec; final sync safeguards/CI recorded in PR.
No new sample generation or listening. Loader browser evidence remains explicitly synthetic.
## Current team blockers
Own #22/#25/#28/#31 need eligible reviews, not author fixes. Re-request after current-main sync.
Mike #26 upload/parser findings and #29 safe-diagnostic findings remain uncorrected at their old heads.
Matt #27 remains draft; second live run failed speech attachment. Joshua owns no formal approval there (contributor).
Separate #27 diagnostic finished: Qwen exhausted 192 tokens with length/no content; Chatterbox PCM decode passed. 1 call each, no retries/music/art.
Assignments already allow backup work and any zero-commit reviewer; no assignment/protection changes.
## Next steps
1. Finish current-head checks, push, and request Matt/prse as additional eligible loader reviewers.
2. Jovi selects three samples after normal merge; real-main/ZIP AT-11 remains pending.
3. Finish diagnosis/technical verification separately, coordinate Mike/Matt fixes; submission NOT READY.
## References
PR #31; merged #32; results/sample-loader-browser.json; docs/TEST_RESULTS.md.

## Preserved loader task notes

## Session
2026-10-30 America/Denver; Codex for Joshua. Task: sample-library loader, Refs #7 (R17/R18, AT-11 component).
## Constraints
MSpanny = Mike; Mase/mase7919 = Matt. Jovi owns final sample selection/#7; no generation or manifest approvals here.
## Repository state
Branch codex/a3-07-sample-loader from main 2a19ecf. No shared Track/schema changes or new dependencies.
## Work completed and decisions
Added bounded all-or-nothing local catalog validation; only manifest entries load, never candidates.
app.py loads once; SessionStore seeds ready tracks with fresh private media URLs, no jobs/provider requests.
Catalog bytes stay immutable/shared and counted once in existing media budget, including after replacements.
Isolated 4 existing HTTP suites (28 cases pass with a populated source-copy manifest); sample replacement stays private.
Fixed safe status/summary warning for bad catalogs; empty manifest keeps existing empty-library behavior.
Changed samples.py, app.py, sessions.py, app.js, tests/test_samples.py; updated README, asset/contract/test docs and safe evidence.
## Validation
Locked checks PASS: 145 tests (16 new); coverage 36/11/19. Schema, approved manifest and candidate media unchanged.
Normal-launch isolated source-copy browser: 3 synthetic silence/solid-cover samples, matching cards, each plays; first pause/resume, lyrics and reload PASS.
Missing-cover restart -> safe warning/zero tracks; approved empty-manifest restart -> no warning/zero tracks. Servers stopped.
## Blockers and unchecked areas
No final sample selection, class generation/listening, merged-main acceptance or exact final ZIP check; #7 remains open, submission NOT READY.
## Next steps
1. Eligible teammate reviews this focused loader PR; all contributors must have zero commits on it to approve.
2. After protected merge, Jovi registers three selected samples and verifies real-media playback/AT-11 on main and final ZIP.
3. Preserve pending #22/#24/#25/#26/#27/#28/#29 work; coordinate app/session seams when merging DJ/reference changes.
## References
Issue #7 claim: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/7#issuecomment-6530493708
results/sample-loader-browser.json; results/sample-loader-fixture.jpg; docs/TEST_RESULTS.md.

---

## Inherited prior task handoff

## Session
2026-10-30 America/Denver; Codex for Joshua. Task: recheck Matt, then fix #8 retry controls.
## Constraints
MSpanny = Mike; mase7919/Mase = Matt. No ownership/protection changes or class calls.
Claim posted on #8; app.js edits confined to cover/music/resume rejection catches; no DJ code edits.
## Repository state
Branch codex/a3-08-retry-controls from main 770ce62. Existing #22/#24/#26/#28/#29 remain separate.
## Work completed and decisions
Matt #27 895a616 rejected-advance cleanup verified fixed; 151 locked tests PASS. Manual/DJ overlap remains open.
Restore the three rejected controls explicitly; retain cached cards, audio nodes, active/config guards and deliberate retry semantics.
Added dependency-free optional Node handler regression in default Python discovery; Node is not an app dependency.
## Validation
Node regression fails baseline and passes patch, including pending, configuration, same-node and no-auto-submit checks.
Real browser offline: cover/music/resume reject -> release -> refresh -> explicit retry all PASS without reload.
Fixture counters cover 4/6/7; resume submissions 1/3/3; music 0/2/3. Safe record/screenshot committed.
Sequential tabs avoid cross-port localhost cookie collisions; initial mixed setup discarded and cover rerun cleanly.
Final locked checks/CI reported in PR. No real providers, .env, user recordings or listening involved.
## Blockers and unchecked areas
#8 broader normal-launch/live acceptance stays open. Matt's overlap fix and Mike's #26/#29 findings remain separate.
Submission NOT READY; no issue closed and no self-approval.
## Next steps
1. Eligible teammate reviews this focused #8 patch; coordinate merge order with Matt's #27 shared app.js.
2. Rerun integrated browser regression after normal protected merge; preserve full acceptance gaps on #8.
3. Mike/Matt continue their existing follow-ups; do not repeat generation on session switches.
## References
Issue #8; results/retry-control-fix.json; docs/TEST_RESULTS.md; tests/frontend_retry_probe.cjs.

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
