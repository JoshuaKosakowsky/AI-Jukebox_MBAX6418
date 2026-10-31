# Agent handoff

## Session — Joshua integration lane (2026-10-30 America/Denver)
User has Mike and Preethi available; asks how to split work and whether to reassign. No assignees changed.
Mike approved exact #31 cc90d293 and #25 4d41b9a. Merged #31 normally at main 31dc9e4; #7 remains open.
Claimed #25 sync/byte-identical preview rename, pushed 4d724c2 and requested eligible Preethi review.
Claimed #27 integration with loader main; pre-integration head 81daed3. Matt retains lead/draft/readiness.
Resolved APP_CONTRACTS/TEST_RESULTS conflicts preserving both loader and DJ evidence. Handoff history retained below.
Code seams auto-merged; changed DJ speech budget attachment to common _media_bytes so retained sample bytes count once.
Isolated DJ HTTP fixture catalog from approved manifest; added real-HTTP sample/DJ pairing/isolation and retained-catalog cap regressions.
New cap regression fails pre-integration speech accounting and passes with common helper; 183 locked tests PASS.
No provider payload, frozen schema, approved manifest, dependency or new live-request change in this integration.
Prior Qwen fix remains 81daed3: bounded real HTTP/store 2 text + 2 speech passed, not normal-launch/listening acceptance.
Validation: safeguards/coverage/whitespace, complete suite and final CI recorded on current PR head.
Current lanes: Joshua integration + independent review of Mike/Preethi code; Mike finishes reviews then #29/#26 fixes.
Preethi can review #25 now, then claim #5 acceptance with Matt handoff or prepare a third #7 sample from retained #32 media if available.
No duplicate live runs: coordinate tester/head/request cap; do not treat silence as an abandoned claim.
Recommendation only: add Preethi as #7 preparation contributor if desired; keep existing leads and backups.
Next: push checked integration, notify exact head, let Preethi/Matt coordinate normal browser/control/listening acceptance.
No self-approval on #27 (Joshua/Matt contributors); eligible Mike/Jovi/zero-commit reviewer needed after author readiness.
#5/#7/final ZIP remain open; submission NOT READY. Existing ownership/protection unchanged.

## Session — Joshua Qwen-fix support (2026-10-30 America/Denver)
User explicitly requested help on #27 and coordination with Matt; pre-change head c06cd0b.
Claim posted: #27 issuecomment-6537399622; exact seam/budget follow-up issuecomment-6537415884.
No newer competing published provider commit/claim; no Matt acknowledgment claimed. Matt retains draft/readiness and acceptance.
Read current deployed ChatCompletionRequest schema and official Qwen3.6/quantization non-thinking guidance.
Added optional ClassProviders.text(thinking=None); default preserves frozen probe, DJ calls thinking=False.
Only request delta is chat_template_kwargs.enable_thinking=false; original model/prompt/192-token/temperature/stream retained.
Strict model/nonempty-final/stop validation and no-auto-retry stay; Mike's lyrics method/#29 unchanged.
Changed providers.py, one sessions.py call, provider/DJ tests, contracts/test docs, safe evidence and this handoff.
165 locked tests PASS (3 new); provider/store regression fails on old DJ call and passes with the fix.
New live task used exactly 2 Qwen + 2 default Chatterbox, no retries/music/art; first/transition jobs succeeded.
Qwen returned complete final content at 36/52 tokens. Speech fully decoded: PCM16 mono 24 kHz, 7.96/10.88 s.
Retained class music/covers were seeded in memory; TestClient drove production routes; replay/reload added no calls.
No raw text/audio or credentials retained in Git; schema fingerprint and safe facts in results/a3-05-qwen-fix-verification.json.
Scope: real-adapter/HTTP-store correction, NOT normal scripts/dev.py browser/control/listening or full acceptance.
Next: Matt pulls current head, avoids a duplicate provider fix, updates author summary and completes bounded normal-launch AT-07/09.
Eligible zero-commit Mike/Jovi/prse review after Matt readiness; Joshua contributes and cannot approve. #5 remains open.
No ownership/protection change or new dependency/schema/frontend change; final checks/CI recorded in PR.
Prior failed runs/diagnoses and Matt/prse notes are preserved below as history.

## Session — Joshua returned-blocker support (2026-10-30 America/Denver)
PR #27, pre-change c4404dd. Matt retains lead and draft/readiness control; Joshua already contributes and cannot approve.
Bounded diagnostic completed: exactly 1 Qwen + 1 Chatterbox, no retries/music/art or acceptance rerun.
Qwen matched model but returned no string content, finish_reason length, 192/192 completion tokens; fixed text guard rejected it.
Independent default speech accepted/fully decoded: PCM16 mono 24 kHz, 3.96 s. No raw text/audio or secrets retained.
Safe permanent record: results/a3-05-provider-diagnostic.json; posted exact facts to #27.
Offline actual-function probes verify Matt's stale timer, permission and manual/DJ exclusivity corrections; no browser/listening claim.
Found/fixed explicit request_dj_speech bypass of MAX_ACTIVE_SPEECH/MAX_JOBS; guarded before allocation with safe 429s.
Added 2 real-HTTP cap/isolation/no-side-effect regressions and optional executable Node playback probe.
Baseline checks fail as expected; patched locked suite 162 PASS; verifier/coverage/whitespace and final CI reported in PR.
No provider payload/model/token-budget or shared schema changes; no additional live requests in this support task.
Merged main c6e1273 after docs-only conflicts, preserving Matt/diagnostic/prse records; pre-sync b444eeb.
Runtime/tests remain byte-identical to b444eeb (162 locked tests passed); safeguards/coverage/whitespace rechecked.
Own #22/#25/#28/#31 were synchronized; eligible Matt/prse review requests added to unblock that separate queue.
Next: Matt corrects the Qwen request against documented deployed contract, preserves complete-output validation, updates stale PR body/handoff.
Then bounded normal-launch DJ/control/listening acceptance and eligible zero-commit review; #5 and submission NOT READY.
Coordinate _media_bytes with loader #31 and reference interfaces with #26; do not guess unmerged seams.
Preserve the older implementation/live-failure entries below as history; newer observations above supersede their pending claims.

## Session — Joshua integration check (2026-10-30 America/Denver)
Local recheck of 2f872b4 found one missing djReady stub in the merged #30
retry probe; corrected only that test fixture, not the DJ implementation.
PASS after correction: 153 locked tests, verifier 82, coverage 36-11-19; whitespace clean.
Actual-function timer probes still reproduce stale retry after Pause and
persistent-rejection segment completion; posted both to #27, no class calls.
Joshua now contributes to this PR and cannot approve it; Mike/Jovi remain
eligible if they have no commits. Prior Matt implementation/handoff follows.

## Session
2026-10-30 America/Denver; Codex for mase7919. A3-05 default AI DJ queue
implementation on `codex/a3-05-dj-queue` (draft PR #27) — now synchronized
with main `770ce62` (includes PR #20's Windows ZIP evidence, merged after
E2B1E52). This file consolidates the A3-05 entry with PR #20's ZIP-evidence
entry and preserves #23's Moonlit candidate notes below.

## Constraints
Protected reviews/checks unchanged. User-controlled workflow: the A3-05 draft
PR must stay DRAFT until mase7919 authorizes readiness/review; no
self-approval, no branch-protection bypass, no merge. Keep prse's #8/#9 and
jovi's #7/#10 ownership; A3-06 (#6, MSpanny, PR #26) is excluded from A3-05 —
its branch is untouched and its speech(reference=None) seam is backward
compatible. #20 remains as the recorded ZIP startup evidence; no new ZIP
acceptance is claimed.

## Repository state
Main `770ce62` (includes #18 instrumentals, #19 acceptance evidence, #21
vocals, #23 Moonlit candidate, and #20 Windows ZIP evidence). Open PRs: #22
recovery audit (dirty on handoff only), #24 vocal credits, #25/#26 teammate
PRs, and #27 (A3-05, DRAFT, MERGEABLE). A3-05 branch `codex/a3-05-dj-queue`
= main + playback controller (queue + AI DJ commentary) + concurrency
hardening; the branch was merged with main `770ce62` after #20 landed; the
only merge conflicts were the shared docs (TEST_RESULTS.md, handoff.md),
resolved by keeping both entries.

## Work completed and decisions
A3-05 implemented end-to-end: queue endpoints, DJ speech jobs (Qwen text ->
Chatterbox default-voice speech, voice omitted per contract), playback state
machine on the existing Playback contract (no schema change; track.speech
reused as the per-track introduction), one persistent browser audio element +
engine loop for sequencing, play/pause/resume/skip in both phases, automatic
advancement, end-of-queue, reload without regeneration. Every transition
including the first is DJ-introduced (documented design choice; same code
path for all transitions). Commentary speech attaches to the TRACK so stale
jobs from skipped tracks can never play out of turn.
Concurrency audit (delayed/reordered requests) found and fixed three real
races: stale phase-after-skip rejected via track-scoped preconditions (409),
stale pause records the current track's true phase, advance-from-paused no
longer 500s. Browser: single-flight advances (a Skip coalesces into an
in-flight automatic advance for the same track; rapid skips serialize), a
FIFO for user intents, pause-failure un-halting, crash-proof engine loop.
Final edge cases: a skip while paused during music keeps the queue paused
and resumes with the NEXT song's introduction (paused_from is always
"speaking" after a paused advance — carrying the old track's "playing"
phase bypassed the introduction), and a failed advance request no longer
creates an unobserved orphan promise (in-flight slot cleared inside the
advance promise; controller recovers).
#20 notes (historical): original 7b9dd2b ZIP identity/65-file startup
rehearsal recordings remain intact on main and in this branch after the
merge; #23: original Moonlit WAV/PNG candidate material. Neither is touched
by A3-05.

## Validation
A3-05 head: 151/151 tests (14 tests/test_dj.py incl. concurrency races and
edge cases, 21 frontend guards incl. DJ guards) plus real-Chrome offline
harness runs with fixture providers: 18/18 functional, 12/12 deterministic
concurrency, plus edge-case browser checks (paused-music -> Skip -> Resume
-> next-song intro -> music; forced advance failure with no unhandled
rejection) — evidence retained outside the repo (dj-browser-evidence.json,
dj-concurrency-evidence.json). Baseline gates on merged main 770ce62:
`python scripts/dev.py --check` PASS; CI 4/4 on the PR head. #20's ZIP
evidence and #23's Moonlit files are byte-preserved through the merge. No
class service, no .env, no credentials were used in A3-05 development; no
new live generation was requested.

## Blockers and unchecked areas
Live Qwen/Chatterbox acceptance (AT-07, AT-09 live portion) is NOT done —
authorized separately, planned on the normal launcher. Not claimed: audible
listening, headed-browser listening, class-service connectivity. #22 remains
dirty (handoff-only conflict; sync + current-head CI before its formal
review). #8's instrumental retry P2 is unfixed on main and out of A3-05
scope. Not ready for submission: vocals live acceptance, reference voices
(A3-06 integration wiring is a coordinated follow-up after #27/#26 merge),
samples, ZIP acceptance.

## Next steps
1. mase7919 authorizes readiness/review of the A3-05 draft; MSpanny is the
   preferred independent reviewer if eligible.
2. Propose the bounded live acceptance procedure (normal launcher, one
   2-track queue, real commentary + speech + sequencing in a browser) for
   authorization — no live calls before then.
3. After #27 merges, wire A3-06's take_reference into generate_dj_speech
   (coordinate with MSpanny; the reference=None default keeps the seam
   compatible), reconcile #22's handoff, and re-verify current-head CI.

## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/27
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/26
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/22
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/20
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/5

## A3-08 retry controls (PR #30, merged into main 2026-10-30)
2026-10-30 America/Denver; Codex for Joshua. Task: recheck Matt, then fix #8 retry controls.
### Constraints
MSpanny = Mike; mase7919/Mase = Matt. No ownership/protection changes or class calls.
Claim posted on #8; app.js edits confined to cover/music/resume rejection catches; no DJ code edits.
### Repository state
Branch codex/a3-08-retry-controls from main 770ce62. Existing #22/#24/#26/#28/#29 remain separate.
### Work completed and decisions
Matt #27 895a616 rejected-advance cleanup verified fixed; 151 locked tests PASS. Manual/DJ overlap remains open.
Restore the three rejected controls explicitly; retain cached cards, audio nodes, active/config guards and deliberate retry semantics.
Added dependency-free optional Node handler regression in default Python discovery; Node is not an app dependency.
### Validation
Node regression fails baseline and passes patch, including pending, configuration, same-node and no-auto-submit checks.
Real browser offline: cover/music/resume reject -> release -> refresh -> explicit retry all PASS without reload.
Fixture counters cover 4/6/7; resume submissions 1/3/3; music 0/2/3. Safe record/screenshot committed.
Sequential tabs avoid cross-port localhost cookie collisions; initial mixed setup discarded and cover rerun cleanly.
Final locked checks/CI reported in PR. No real providers, .env, user recordings or listening involved.
### Blockers and unchecked areas
#8 broader normal-launch/live acceptance stays open. Matt's overlap fix and Mike's #26/#29 findings remain separate.
Submission NOT READY; no issue closed and no self-approval.
### Next steps
1. Eligible teammate reviews this focused #8 patch; coordinate merge order with Matt's #27 shared app.js.
2. Rerun integrated browser regression after normal protected merge; preserve full acceptance gaps on #8.
3. Mike/Matt continue their existing follow-ups; do not repeat generation on session switches.
### References
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
payload schemas for 9007/9008 (music/TTS) — still need class-endpoints.txt
before building adapters.


## Preserved prse recovery handoff from main c6e1273

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
