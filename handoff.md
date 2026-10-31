# Agent handoff

## Session — final DJ integration and clarity, 2026-10-30 America/Denver
Codex for Joshua; PR27 pre-head0a05942, main81042a1 after normal #25/#28/#24 merges.
No newer Mike #26/#29 fixes or Matt readiness published at start; draft/readiness/ownership remain unchanged.
Claim: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/27#issuecomment-6538451792
Merged current main; resolved only handoff overlap while preserving DJ, failed-vocal, sample and credit records.
Addressed Preethi's non-blocking README note: manual players independent only when idle, suppressed while DJ active/paused.
Corrected related user notice that incorrectly said pausing the DJ would permit manual players; notice-only JS change.
Playback logic/providers/tests/contracts/dependencies/manifest unchanged from0a05942; existing media/evidence bytes unchanged.
Preethi's0a05942 review was COMMENTED/no blockers; new-head code review/approval still needed when Matt promotes.
Earlier failed live runs predate successful real2Qwen+2speech HTTP/store correction; normal-launch controls/listening remain pending.
No new class-service calls, credentials, sample selection, reference implementation or budget reset.
Safeguards/coverage/whitespace, source/evidence equivalence, affected frontend checks and new-head CI recorded on PR.
Joshua contributes and cannot approve; leave draft and readiness with Matt, coordinate one tester/head/budget with Preethi.
Next: publish/freeze this head, finish normal-launch/browser/control/listening acceptance, eligible independent review then normal merge.

## Preserved task and main notes (current facts above supersede historical status)

## Session — DJ main reconciliation, Joshua, 2026-10-30 America/Denver
Task: remove current-main integration blocker from existing #27 draft; pre-head bee7209, main9d84dab.
Claim: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/27#issuecomment-6538108304
Only handoff conflicts required resolution; retained DJ, Qwen, loader, recovery and shared configuration notes.
Runtime/tests/contracts/dependencies/approved manifest unchanged from bee7209; original DJ evidence/media unchanged.
Shared credential/live-run guide from #33 and recovery evidence from #22 now present on this branch.
#33 merged normally after Preethi approved1490da1 and CI4/4 passed; no new configuration requirement introduced.
Current #25/#28 heads6276b29/66daf4f are green and frozen for eligible independent review.
Mike's #26 head57fd24a has 161 passing tests/green CI but three reproduced validation/parser blockers;
#29 safe diagnostic findings and #24 one-file credit integration conflict remain with Mike.
Joshua stays zero-commit reviewer on #24/#26/#29; Matt retains #27 lead, draft state and readiness.
No provider calls, new credentials, sample selection, reference UI implementation or ownership changes here.
Normal-launch DJ browser/control/listening acceptance remains separately coordinated with Matt/Preethi.
Prior real-adapter HTTP/store correction and offline fixtures do not establish that missing acceptance.
Verifier/coverage/whitespace, exact source equivalence and locked-suite/CI outcomes recorded on PR.
Next: publish checked head, stop integration edits, let eligible zero-commit reviewer inspect code/evidence.
Never self-approve or merge this contributor PR; do not turn a docs sync into repeated live generation.

## Preserved task and merged-main notes (current facts above supersede historical status)

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

## Preserved merged-main notes

## Session — A3-09 README slice, 2026-10-30 America/Denver
prse4479 (A3-09 lead). Claim on #9: branch codex/a3-09-readme-findings from main 81042a1, README-only +50 (failure/recovery observed results, R29 design choice, R30 limitation).
PR #34 reviews: Joshua requested two P2 factual corrections — capacity slots are shared across browser sessions (not per-session), and the retry guarantee is per requested stage (not one generation per action) — plus one non-blocking toolchain qualification (129-test figure historical; Node optional). All batched in this commit; head frozen for re-review by Joshua (reported zero-commit) or Mike. No source/test changes, no provider calls, no .env involvement. #9 stays open for vocal/DJ/reference/results sections; R31 team wording verification happens in the PR review.

## Session — final contribution review head, 2026-10-30 America/Denver
Codex for Joshua; PR24 preparation c7c5504, final mainca9fc83 after protected PR25 merge.
Preethi renewed exact45d24bd approval; #25 merged normally with four green checks; candidate remains unselected/#7 open.
Followed planned merge order, then final-synced #24; only handoff conflict, preserving both tasks' notes.
All three original Mike rows remain byte-for-byte, every main row retained exactly once (including candidate review credit).
Against main only CONTRIBUTIONS +3 rows and this handoff differ; runtime/tests/contracts/dependencies/assets/evidence equal main.
Safeguards/coverage/whitespace/source+credit equivalence recorded on PR; no new tests for documentation-only work.
No new provider calls/listening, sample approval, credentials, dependency or ownership changes.
Joshua now contributes to #24 and cannot approve; request eligible Preethi/Matt/Jovi and freeze this head for review.
Mike retains author/implementation/review credit and can focus on #26 validation and #29 safe diagnostics.
Do not merge without final current-head approval, passing required checks and resolved conversations.
Next: publish final checked head, request eligible review, normal merge once ready; do not push during review.

## Preserved preparation and main notes (current facts above supersede historical status)

## Session — contribution-record reconciliation, 2026-10-30 America/Denver
Codex for Joshua; PR24 pre-head5c436d1, mainfed0add. Mike retains author credit and all three original rows.
Claim: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/24#issuecomment-6538295333
Resolved only docs/CONTRIBUTIONS.md conflict by retaining all three Mike rows and every distinct main row exactly once.
Added this current handoff; all other incoming files are already-merged main documentation/evidence.
Runtime/tests/contracts/dependencies/assets/approved manifest match main; no app/provider behavior or generation changes.
Existing row evidence/prior reviews retain their original offline/live scope; no new listening or acceptance claimed.
Joshua now contributes to #24 and cannot approve; choose eligible Preethi/Matt/Jovi with zero commits.
Mike can focus #26 local validation fixes and #29 safe diagnostics; no edits to those branches here.
**Merge order: #25 first, then final-sync/review #24.** Do not merge this ahead of frozen #25 and invalidate its next approval.
#25 is frozen45d24bd with four green checks and fresh review pending; do not push to that branch.
Validation: repo safeguards, coverage structure, whitespace and source/credit equivalence recorded on PR.
No new tests for docs-only reconciliation. Ownership/protection unchanged; #3/#5/#6/#7 acceptance stays open.
Next: publish this preparation head, await #25 merge, do one final main sync, then request eligible current-head review.

## Preserved merged-main notes (current facts above supersede historical status)

## Session — final sample review follow-through, 2026-10-30 America/Denver
Codex for Joshua; PR25 pre-head6276b29, required mainfed0add after normal PR28 merge.
Preethi approved6276b29 and independently verified source hashes/decoded media/provenance; Mike approved a prior package.
Main update required handoff-only conflict resolution; preserved candidate and failed-vocal evidence/notes.
Confirmed original cover visually: exact generated lettering is DESSERT DRIIVE; corrected two JSON note strings and README.
No artwork/audio/preview edit or new generation; title/settings/source hashes/timestamps/request reconstruction remain unchanged.
Added one related packaging/review credit row; no attribution to new listening or final sample approval.
App/tests/contracts/dependencies match current main; approved manifest remains unchanged and candidate unselected.
Validation: verifier/coverage/whitespace, full WAV/PNG/JPEG decode, media hashes and provenance-equivalence recorded on PR.
Normal protection dismisses the old-head approval after this required push; request fresh eligible review and freeze.
Do not self-approve, bypass protection, silently select samples or close #7.
No new class-service calls, keys, uploaded voice references, assignment changes or app behavior changes.
Next: publish checked head, eligible reviewer verifies narrow delta, normal merge when approval and CI are current.

## Preserved task and main notes (current facts above supersede historical status)

## Session — shared integration and independent review follow-through
2026-10-30 America/Denver; Codex for Joshua. PRs #25/#28 sync, pre-heads 4d724c2/e42e5de.
Main is 9d84dab after protected #33 merge under Preethi's final-head1490da1 approval and 4/4 CI PASS.
Canonical credentials/live guide is now on main; Preethi independently reported all four roles configured, no new generation.
Merged current main into these two evidence branches; resolved only handoff/index overlaps, retaining both tasks' notes/links.
Runtime/tests/contracts/dependencies and approved manifest remain identical to current main.
Original Desert Drive candidate media/provenance/preview and failed vocal evidence/media retain their exact prior bytes.
No sample approval, successful vocal claim, new generation, credential copying or ownership change.
Independent #26 review on Mike's new57fd24a: 161 locked tests/verifier99/coverage36-11-19 PASS.
Original disk-spooling and header-only WAV fixed; three blockers remain: incomplete MP3 accepted,
valid multipart header order rejected, and inconsistent WAV byte_rate bypasses60s cap.
Review: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/26#pullrequestreview-5720684891
#24 credit delta remains sound; Mike asked to resolve only CONTRIBUTIONS overlap while retaining both sides.
No Joshua commits on #24/#26; independent re-review remains available. #29 safe-diagnostics findings still pending.
#27 remains Matt's draft; coordinate existing budget/tester before any live acceptance, no duplicate requests.
This sync needs fresh eligible review after green CI; do not self-approve or bypass protection.
Next: publish both frozen heads, request review, merge normally when ready. #3/#5/#6/#7 acceptance remains open.
Verifier/coverage/whitespace/source/media-equivalence results are recorded on each PR; no new tests for prose sync.

## Preserved task and main notes (current facts above supersede historical status)

## Session — final live-run guide refinement
2026-10-30 America/Denver; Codex for Joshua. PR #33, pre-update 408c6cb; merged current main 976d98d (#22).
Resolved only handoff overlap, retaining both tasks. Runtime/provider/test code remains current main.
Refined primary safe check to Python stdlib GET /api/status services of the actual running app.
This avoids checking a second process's configuration or creating a Windows long-path uv environment just for status.
Source ROOT, inherited precedence, missing-role names and separate process diagnostics remain explained.
Normal-launch dummy/placeholder check rehearsals and repo checks recorded in PR; no actual credentials/provider calls used.
Tagged team message already delivered on #3, cross-linked #5/#8, with guide/PR links; update its command to match.
Guide is documentation only: no extra file/permission gate, no task-budget reset, no A3-03 pass claim.
Mike/Preethi requested for independent review. Main's #22 merge also retains the authorized Preethi #7 plan entry.
Next: publish final guide/head, finalize message and check CI; no self-approval or direct-main push.

## Session
2026-10-30/31 America/Denver; Hermes for MSpanny (Mike). Task: A3-03 lyrics parser diagnostics (#3 lead; follow-up to Joshua's failed live run, PR #28). Branch codex/a3-03-lyrics-diagnostics. Rounds: (1) distinct guard labels; (2) whitelisted metadata + malformed message=[] fix; (3) per Joshua's re-review of 086ac6b: returned model ids are NEVER echoed (fixed unexpected-model message — a length bound is not a whitelist; short-string marker regression through provider AND session snapshot), and #27's text(..., thinking=False) DJ call absorbed into the _chat refactor (chat_template_kwargs added only when thinking is not None; probe-identical defaults preserved). Suite 189 tests, verifier 118 files, coverage 36/11/19, gate PASS, CI green. AT-04 live root-cause remains pending class .env; no token-budget/schema guesses.

## Constraints
Task branch + reviewed PR; no main/protection/assignment changes. Fix is offline-only: NO speculative token-budget/schema changes; bounded live rerun stays pending class .env.

## Repository state
Main 770ce62 = #23 Moonlit + #20 ZIP evidence merged. Open: #22 audit, #24 contributions, #25 Desert Drive candidate, #26 A3-06 references (MSpanny; CI green), #28 failure record. no other PR touches providers.py/tests/test_providers.py.

## Work completed and decisions
text()/lyrics() refactored onto a shared `_chat` guard whose SafeError names the exact failing condition: unexpected model id, missing/empty content (finish included), or non-stop finish (e.g. length). Safe metadata only (model ids + finish_reason; never raw content/reasoning). Behavior unchanged: content accepted only when present, non-empty, stop. Reasoning fields never leak. 3 new MockTransport guard tests; probe-fidelity test still byte-identical. Docs: TEST_RESULTS diagnostics section; this handoff.

## Validation
python scripts/dev.py --check PASS: 131 tests (128 prior + 3 new), verifier 74 files, coverage 36/11/19. No live calls.

## Blockers and unchecked areas
Live cause still unknown until the bounded rerun with class keys (.env absent here). AT-04/#3 remain open/failed (Joshua's run on 770ce62 failed at the lyrics guard). Human listening pending. #6 lead discrepancy (issue says MSpanny; Josh handoff text says Matt) flagged on #20 review; issue remains authoritative.

## Next steps
1. Open PR (Refs #3, honest: diagnostics only, live rerun pending), request Matt's review.
2. When .env exists: bounded normal-launch vocal rerun — the parser now reports which guard fired (or succeeds); then decoded-media + browser + listening acceptance for AT-04.
3. If the cause is finish=length: decide with team whether to raise the lyrics budget further (documented live-evidence change), not blind.

## References
Issue #3; PR #28 (Joshua's failure record); docs/TEST_RESULTS.md diagnostics section; tests/test_providers.py.

### Session (Codex for Joshua, #20/#22 integration)
2026-10-29 America/Denver; Codex for Joshua. Independent integration support: #20 ZIP evidence and #22 recovery audit.
## Constraints
Normal protected reviews/checks; no app changes or class calls. Matt leads #5/#6, Mike #3, prse #8/#9, jovi #7/#10.
2026-10-30 America/Denver; Codex for Joshua. PR #25 reconciliation while Mike/Preethi are available.
## State and completed work
Mike approved #31 and this PR's prior 4d41b9a head; #31 merged normally at main 31dc9e4.
Merged that main into #25; resolved only handoff conflict while preserving candidate/loader/prse notes.
Corrected Mike's non-blocking screenshot filename: original JPEG bytes renamed .png -> .jpg, references updated.
WAV/cover bytes, sample/provenance objects and approved manifest unchanged; no sample selection or generation.
Current PR app/tests/contracts/dependencies match main; loader implementation remains the independently reviewed #31 code.
## Validation and remaining review
Verifier/coverage/whitespace, media/provenance/preview byte checks and full decode recorded in PR; new-head CI required.
Previous current-head approval will need renewal after this push; Preethi requested as eligible zero-commit reviewer.
No self-approval or protection changes; #7's final three samples/normal-main/ZIP acceptance stay open.
## Current parallel work
Joshua owns #27 integration with loader seams; no new provider generation in that integration.
Mike can fix #29 then #26; Preethi may take claimed #5 browser acceptance afterward using existing backup coverage.
Do not duplicate Matt's active/unpublished acceptance; coordinate exact head and request budget first.
## Next
1. Preethi reviews the small #25 sync/rename delta, then normal protected merge after green CI.
2. Jovi retains final sample selection; retain original media instead of regenerating on agent switches.
3. Follow #27 integration handoff; no assignment change was made in this task.

## Preserved historical task notes (superseded where noted above)

## Session
## Preserved candidate notes

2026-10-30 America/Denver; Codex for Joshua. Catch-up: PR #25, Desert Drive candidate packaging.
## Repository state
Branch codex/desert-drive-sample-candidate; pre-sync 2cb5e01; merged main c6e1273 after normal #32 approval/merge.
## Work and decisions
Resolved only documentation/index/handoff integration conflicts; preserved both branches' evidence and prior notes.

2026-10-30 America/Denver; Codex for Joshua. Collaboration follow-through on PR #28.

## Preserved clarification task notes

2026-10-30 America/Denver; Codex for Joshua. Task: shared credential/live-rerun clarification for Mike/everyone.
Branch codex/a3-live-run-clarification from main 31dc9e4; no application changes or new live generation.
## Work and decisions
Read config.py, launcher, status/routes, .env.example and AT-04/R10 requirements; do not assume remote teammates' settings.
README links a canonical TESTING credentials/live guide; AGENTS points future agents there.
Guide explains source-root .env + inherited overrides, safe role-only check, checkout/process/worktree differences.
Clarifies all-four aggregate flags versus vocal text/art/music needs, dummy fixtures, browser-session isolation and real evidence.
One coordinated bounded tester; valid existing config is sufficient, no extra .env/approval gate; prior task limits still apply.
Includes normal-launch vocal path, stop/no-duplicate submission, media/browser/listening and exact safe blocker reporting.
No keys/raw config printed/copied, no provider requests, no budgets/ownership/protection changes in this docs task.
## Verification
Cross-checked every supported variable/command against current source and existing config tests.
Safe command rehearsed with all-placeholder and one dummy configured role; only labels printed, marker absent, no provider calls.
Repo safeguards/coverage/whitespace pass; runtime/tests/contracts/dependencies unchanged; no new tests for prose-only changes.
## Remaining
Primary team message delivered on #3 tagging Mike/Matt/Preethi/Jovi; cross-linked #5/#8.
Message: https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/3#issuecomment-6537867158
Request eligible independent docs review; attach guide/PR to the delivered message once published. Agents can use the message now.
Do not claim that configuration or this clarification completes A3-03; current code/review findings and AT-04 still apply.
No collaborator credentials or successful normal-live evidence was inspected on their machines.

## Preserved prior handoff from main

## Session


## Preserved merged integration notes

2026-10-30 America/Denver; Codex for Joshua. Collaboration follow-through on PR #22.
## Current facts
User explicitly added Preethi/prse4479 to #7; confirmed Jovi remains lead, Mike backup (3 assignees).
Assignment/comment: issue #7 issuecomment-6537704666; retained-file confirmation precedes third-candidate preparation.
Main is 31dc9e4 after normal #31 merge under Mike's exact-head approval; #7 final selection/ZIP still open.
#25 is synchronized at 4d724c2, 4/4 CI green, awaiting fresh eligible review after main sync and JPEG filename correction.
#27 is integrated at bee7209 with 183 tests/4 CI checks PASS; draft/readiness and coordinated browser/listening work remain.
## This branch
Merged current main into #28; only handoff conflict resolved, all evidence/loader/prse notes retained.

Merged current main into #22; only handoff conflict resolved, all evidence/loader/prse notes retained.
Runtime/tests/contracts/dependencies match main. Original historical/failed evidence media and JSON unchanged.
Safeguards, coverage, whitespace, source-equivalence and final current-head CI/review status recorded on PR.
## Next work lanes
Joshua handles integration/returned findings and independent review of Mike/Preethi code.
Mike finishes current review work, fixes #29 safe parsing and #26 local upload validation; those heads remain unchanged.
Preethi reviews #25 and can claim third-sample preparation; #5 acceptance uses existing backup coverage with Matt handoff.
No duplicate live runs; no new generation, assignment beyond authorized #7 addition, or protection changes here.
Next: eligible current-head review, then normal merge; no self-approval. Submission NOT READY.

## Preserved historical task notes (current facts above supersede older status)

## Session
## Preserved prior evidence task notes

2026-10-30 America/Denver; Codex for Joshua. Catch-up: PR #28, failed vocal acceptance evidence.
## Repository state
Branch codex/a3-03-live-acceptance; pre-sync 0bb7fea; merged main c6e1273 after normal #32 approval/merge.
## Work and decisions
Resolved only documentation/index/handoff integration conflicts; preserved both branches' evidence and prior notes.

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
PR #25; merged #32; current draft #27 diagnosis and reviewer coordination on GitHub.

PR #28; merged #32; current draft #27 diagnosis and reviewer coordination on GitHub.

PR #22; merged #32; current draft #27 diagnosis and reviewer coordination on GitHub.

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


## Preserved loader integration notes

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
