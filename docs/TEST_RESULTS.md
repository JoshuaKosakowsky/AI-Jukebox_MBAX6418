# Test results and evidence

## Local setup - 2026-10-15 America/Denver

Scope: repository scaffold only. No service calls, generated samples, or app
tests. Validation runs `python scripts/verify_repo.py` after staging files,
checks local Git configuration/hooks, and verifies the preserved prompt.
Verified 2026-10-15 19:15 MDT (America/Denver) by the Codex setup agent on Windows, Git 2.55.0.windows.5.
Baseline commit: `9d8ee0e2139cdbe623cfef8706b91e5bdcd75a65`; final handoff commit is available via git log.

| Setup check | Expected | Actual |
|---|---|---|
| Offline verifier | Required files, valid links, tracked safeguards, exact policy | PASS, 23 files |
| Starter prompt vs PDF | Identical original wording | PASS after whitespace normalization |
| Main pre-commit guard | Block after initial commit | PASS, blocked |
| Local-only pre-push guard | Block without explicit enablement | PASS, blocked |
| Main ref update/deletion | Block even with per-command enablement | PASS, both blocked |
| Working-branch hooks | Permit commit; permit branch ref under test enablement | PASS |
| Remote/config inspection | No remote; allowPush=false | PASS |

Hook tests invoke hooks directly without any push. An initial piped-input probe
was invalid because git hook run does not forward piped stdin; it was corrected
to --to-stdin and ref-specific checks reran successfully. Remote protection and
CI execution remain untested until publication. Secret-pattern checks are a
basic guard, not proof against every form of credential; inspect diffs manually.

## Application and release evidence (not run)

The complete checklist is AT-01-AT-19 in [acceptance.json](acceptance.json).
Generation/playback/upload user flows remain **not run**. AT-02 has live provider
contract evidence below; the startup foundation now has separate browser evidence.
No approved sample media or independent release acceptance exists yet.
Record one short entry per executed case: date/tester/environment/commit,
inputs/command, expected, actual, result, evidence paths and unchecked scope.
Consolidate repeated fixes; never turn an unrun case into a pass from test counts.

## Protocol verification - 2026-10-17 America/Denver

Full brief was read and mapped to 36 requirements, 11 tasks and 19 acceptance
cases. Offline readiness-gate regressions cover dropped/unmapped requirements,
dependency cycles, skipped/stub-only claims, missing results/evidence, both
reference formats, independent installation, absent media and wrong ZIP contents.
Commands: python scripts/check_readiness.py (36/11/19 coverage PASS), and
python -m unittest discover -s tests -p "test_*.py" (18 passed). The explicit
release command without actual evidence correctly returned NOT READY. This is protocol
verification, not jukebox/live/browser acceptance. The release check must report
NOT READY until actual independent evidence and sample assets exist.

## Design judgment and investigated limitation

Pending app work. Explain one important choice supported by observed tests and
one investigated limitation/failure with the lesson learned, then summarize
verified findings in README in the team's own words. Do not import A2's SVG or
RAG question-set requirements as mandatory A3 work.

## A3-01 contract probes - 2026-10-17 13:29 MDT

Tester: JoshuaKosakowsky directing Codex; Windows, bundled Python urllib/struct
and Pillow. Base commit d0d566238b184413960076985b5681576111737c;
branch codex/service-contract-probes. This documentation follows the probes;
the recorded base identifies the configuration/scaffold, not an app implementation.
Scope: partial AT-02 / R02-R06 provider compatibility, not overall acceptance.

Located the private course Misc/class-endpoints.txt, but its September version
did not document 9007/9008. Used the existing ignored .env, deployed OpenAPI for
each service and pinned official ACE-Step documentation before generation.
Four /v1/models and four /openapi.json GETs succeeded first; then exactly one
generation submission per required service. No port 9000, paid API or upload.

Exact safe inputs/routes: [canonical payloads](../contracts/service-probes.json).
Actual safe measurements: [probe record](../results/service-contract-probes.json).

| Service / input | Expected | Actual | Result |
|---|---|---|---|
| Qwen: exact marker, 192-token cap | JSON chat response with CONTRACT_OK content | HTTP 200, exact 13-character marker, finish_reason=stop; 1.078 s | PASS, minimal text contract |
| FLUX: one geometric cover, 512x512, 4 steps | Base64 PNG fully decodes at requested size | HTTP 200; full Pillow decode, 512x512 RGB PNG, 787271 bytes; 1.656 s | PASS, minimal art contract |
| ACE-Step: one 10 s piano instrumental, 8 steps | Accepted task -> successful poll -> fully decoded WAV | Submit/poll/download HTTP 200; status=1, one poll, result is JSON string array; XL Turbo confirmed; 10.0 s, 48 kHz stereo PCM16 WAV; 5.829 s total | PASS, minimal async music contract |
| Chatterbox: short welcome, omitted voice, WAV | Default voice returns fully decoded audio without upload | HTTP 200 audio/wav; 1.76 s, 24 kHz mono PCM16 WAV; 1.187 s request | PASS, minimal default speech contract |

Elapsed music time includes a three-second polling wait and download/decoding;
it is not an inference benchmark. All WAV samples were decoded and checked for
finite nonzero signal; HTTP/header checks alone were not counted as pass. Speech
RMS=0.101225/peak=0.603271; music RMS=0.142148/peak=0.891266. Raw responses and
media are ignored under generated/contracts/; keys, task IDs, server paths and
raw progress/error text are excluded from the committed record. Probe media
is disposable evidence, not approved sample assets or quality acceptance.

Unchecked: listening/music quality, semantic cover quality, vocals/lyrics JSON,
reference MP3/WAV, pending/failure responses, normal startup/browser flows,
credentials in a future app and deployment. Documented options are distinguished
from observed behavior in [SERVICE_CONTRACTS.md](SERVICE_CONTRACTS.md). A3-01
remains open for startup, runtime/dependency lock, shared objects and adapter
failure behavior. Dependent service work can use this baseline after review/merge;
the complete A3-01 dependency and app/release acceptance remain unsatisfied.

Repository validation for this contract documentation change: scaffold/links and
tracked-file safeguards PASS (33 files), coverage PASS (36/11/19), all 18 existing
offline gate tests PASS, staged whitespace check PASS. Exact frozen payloads,
measurements and OpenAPI fingerprints matched the private originals in an offline
comparison. No credentials, private task IDs or provider filesystem paths were
published. These checks add no further live or app acceptance claims.

## Historical preparation integration - 2026-10-17 America/Denver

Contract commit 75ea4aa reached main through the owner-controlled preparation
integration at ada2a6c. GitHub marked PR #12 merged; it had no independent reviews
and supplies implementation/testing evidence only. The historical CI run passed
26 tests. The preparation exception has been retired; it grants no ongoing
permission. Current work uses task branches, reviewed PRs and enforced protection.

The four original probe results above remain unchanged. No new service calls
were made to transition the workflow. Current guard validation is recorded below.

## Team workflow activation - 2026-10-17 America/Denver

Base: ada2a6cc66eaab24e87439627fa5fc8c7e5685f3; branch
codex/activate-team-workflow. Removed the preparation exception from current
guides, hooks and handoff; retained historical PR #12 implementation/testing
credit with no independent review claimed. No service or invitation calls.

Expected: no main commit, direct push, deletion or history rewrite is permitted;
the retired configuration cannot authorize any of them. Task-branch commits and
authorized pushes still work. Actual: all ten isolated Git hook regressions pass,
including a batch containing both task and main refs, plus 18 gate tests (28 total).
Scaffold/links/credential guards and 36/11/19 coverage pass. Original assignment
prompt and saved protection policy are unchanged; no retired setting is configured.
Read-only GitHub API verification confirms the live policy matches the saved
check/review/admin/conversation and force-push/deletion settings. No protection
settings, collaborator access, or lead/contributor assignments were changed. This transition
still needs normal PR review/merge; onboarding follows it. No app acceptance claimed.

## A3-01 runtime and shared contracts - 2026-10-27 America/Denver

Tester: JoshuaKosakowsky directing Codex. Branch codex/app-runtime-contracts,
base main 301585b667c59f972caf7f7aeca3a7b89f39c41a. Windows with managed Python
3.12.14, uv 0.12.19 and exact uv.lock dependencies. This evidence is task-branch
startup/provider integration, not completed browser generation or release acceptance.

| Check / safe input | Expected | Observed |
|---|---|---|
| Install/start: python scripts/dev.py --port 8000 from the original long course path | Locked install and usable local page | PASS, loopback server, four configured labels, empty library; Refresh status works |
| Source-only rehearsal: 54 tracked files copied without .git/.env/ignored assets; same launcher on 8001 | No developer-only state needed for startup | PASS, separate isolated install; browser shows four Missing settings labels, empty library and App connected; refresh works |
| Missing/example configuration | Empty app still starts, no provider call | PASS in normal launcher HTTP test and browser rehearsal |
| Wrong port/host, embedded key, query, invalid key characters | Safe diagnostic, no value/key disclosure | PASS, configuration rejects invalid inputs; actual CLI exits 2 with a role-only error |
| Invalid/busy app port | Actionable failure, no hang or service call | PASS via child-process tests; --port selects an alternate port |
| Domain contracts | Stable IDs, valid media/job/queue references and legal states | PASS, round trips, local media URLs, ready-audio constraint, job transitions/progress/errors, single playback phase and schema drift checks |
| Adapter failures through MockTransport | No raw errors, redirects, duplicate submissions or cross-origin auth | PASS for timeouts, network errors, 401/429/503, redirects, malformed JSON/results/URLs, wrong ticket/model, response caps and truncated PNG/WAV |
| Browser/private-file boundary | No server keys/URLs, no .env/Git file access | PASS for public responses, private paths, wrong Host, cross-origin mutations and CSP/no-store/nosniff headers |
| Locked offline command: python scripts/dev.py --check | Default suite collected and passing, coverage retained | PASS: verifier 54 files at rehearsal, coverage 36 requirements/11 tasks/19 cases, all 60 tests (28 existing plus 32 runtime/provider/startup) |

Actual browser evidence: [configured setup](../results/startup-configured.jpg),
[empty library](../results/startup-library.jpg), [missing configuration](../results/startup-missing-settings.jpg).
The browser check used the normal launcher; no fixture provider or generated
tracks were substituted into the UI. No keys/endpoint values appear in screenshots.

### New production adapters: deliberate live smoke

One generation submission per adapter used the unchanged canonical probe inputs
from contracts/service-probes.json. This checks the new client implementation,
not merely the earlier standalone harness. Safe exact measurements are in
[runtime-adapter-smoke.json](../results/runtime-adapter-smoke.json). Calls were
explicitly part of A3-01 testing, not startup, refresh, CI or offline tests.

| Service | Expected | Actual |
|---|---|---|
| Qwen | Exact marker in final complete content | PASS, CONTRACT_OK, prescribed model; 1.109 s |
| FLUX | One fully decoded PNG | PASS, 512x512 PNG, 787271 bytes; 1.344 s |
| Chatterbox | Default voice without upload, full PCM WAV | PASS, 1.88 s, 24 kHz mono PCM16, non-silent; request 1.562 s |
| ACE-Step | Submit -> same-job poll -> download, validate XL Turbo and PCM | PASS, one poll, 10.0 s, 48 kHz stereo PCM16, non-silent; 5.625 s including polling/download |

Raw media and the server ticket remain ignored under generated/a3-01; they are
not approved sample songs. There was no generation retry, port 9000, paid service
or voice upload. Timings describe these calls, not a performance benchmark.

### Design choice and investigated startup failure

FastAPI plus a same-origin, build-free HTML/JS shell keeps one Python process and
one locked environment for the team. Versioned typed objects and exported JSON
Schema give the dependent issues concrete interfaces. Missing settings do not
block the empty app; safe status explicitly distinguishes configuration from reachability.

The first Windows install into the repository's long .venv path failed to import
the native pydantic-core extension (a path lookup failed). The identical locked
packages imported from a shorter environment. The normal launcher now selects a
short per-checkout LOCALAPPDATA environment on Windows; the original long-path
checkout and separate source-only copy both launched successfully afterward.
No Windows security/path policy was changed. Linux retains .venv.

The locked Starlette TestClient currently emits an httpx deprecation warning;
tests pass, and production requests use the supported locked httpx client. No
warning suppression or extra test transport was introduced just to hide it.

Remaining: teammate review/startup verification on merged main (AT-01/02 closure),
instrumental/vocal UI generation, persistence, new cover pairing, reference voices,
actual playback controls/sequencing, failure/recovery user flows, sample assets
and an independent GitHub ZIP install. The source-only rehearsal was performed
by the same agent and is not AT-16 independent ZIP evidence. Submission NOT READY.

Pre-handoff implementation commit for this runtime evidence: 60853ac51a5386412723470209e7971bdd172871.
Final handoff/evidence bookkeeping is a separate commit; use the PR head for CI.

## A3-01 integration and review follow-up - 2026-10-27 America/Denver

Tester: JoshuaKosakowsky directing Codex; Windows, locked Python 3.12.14.
Matt independently approved PR #15 head 91eca84 after 60 offline tests and
normal-launch HTTP/security checks; his review did not claim interactive browser
verification. PR #15 merged normally at c635e86; all matrix jobs and required
[test on main](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/actions/runs/40627942656)
passed. Protection was unchanged; no bypass was used.

Merged-main input: python scripts/dev.py --port 8000 from the original course
checkout. Expected: empty local app, safe configuration labels, no generation.
Actual: normal browser launch showed all four services configured, App connected
and zero tracks. /api/health, /api/status and /api/session passed HTTP checks;
connectivity_checked and generation_available remained false. Server stopped
cleanly afterward. A3-01 closed; direct dependencies A3-02/04/08/09 became ready.
Other feature and release acceptance remain pending.

Follow-up branch codex/runtime-review-followups, base c635e86:

- Reject duplicate, blank and malformed music-download query parameters before
  authentication. Existing successful canonical payloads/routes remain unchanged.
- Reject reused media IDs across tracks or audio/cover/speech roles; export the
  identifier constraint into the shared schema description.
- Rename the three JPEG-encoded startup screenshots to .jpg and update links;
  Git reports 100% identical bytes, preserving the original browser evidence.
- Retain the safe httpx.InvalidURL handler: in locked HTTPX 0.28.1 it inherits
  directly from Exception, not HTTPError. Introspection plus a MockTransport
  regression confirms the handler is reachable and does not expose raw text.
- Keep speech output at the verified WAV contract. Other advertised formats
  require coordinated support in A3-05/06 if used; no guessed formats are added.

Validation: python scripts/dev.py --check PASS, verifier 56 tracked files,
coverage 36 requirements / 11 tasks / 19 cases, all 63 offline tests; staged
whitespace check PASS. No new service calls, generated media, assignments,
dependencies or protection changes. The existing TestClient warning remains.
This follow-up does not establish playback, generation UI or submission readiness.

## A3-04 matching covers - 2026-10-27 America/Denver

Tester: JoshuaKosakowsky directing Codex; Windows, locked Python 3.12.14.
Branch codex/matching-covers; base main c635e86; cover/browser implementation 264c391; cookie follow-up 5ccb371.
Scope: R11 / AT-05 cover generation and draft pairing. The parent issue stays
open for merged-main and playable-song integration with A3-02.

| Check / exact safe input | Expected | Actual |
|---|---|---|
| Normal python scripts/dev.py --port 8000; Moonlit mountain lake / Ambient piano / Calm and reflective / 30 s planned instrumental | New contextual 512x512 FLUX cover on that draft | PASS, blue mountains/lake with moonlight; loaded image, ready art job and matching title/settings |
| Same app; Desert sunrise / Upbeat desert funk / Warm and energetic / 30 s planned instrumental | Separate new cover reflecting contrasting context | PASS, warm orange desert/sunrise art, distinct track/media IDs; first cover retained |
| Reload actual browser after both complete | Both pairs retained; no automatic generation | PASS, two loaded 512x512 images and correct titles; console had no errors |
| Normal second launcher with art placeholders, localhost:8001 | Safe empty app with cover controls disabled | PASS, Missing settings for art, setup guidance and disabled submit; no service call |
| Offline default suite | Base tests plus focused cover integration regressions | PASS, 73 tests (60 merged-main baseline + 13 cover tests), 60 tracked files, 36/11/19 coverage |
| Offline partial failure/retry, ready-track fixture | Retain old cover/audio/lyrics/playback and other tracks; retry gets new job ID | PASS through real HTTP routes with mocked art only; replaced old cover removed after success |
| Offline concurrency and isolation | No cover swaps, duplicate active submission, foreign track/media access or orphan capacity failures | PASS, running-state HTTP check, opposite completion order, 409 duplicate, 404 foreign IDs, bounded jobs/media/sessions and expiry |

Exactly two deliberate class requests were made, both FLUX generation via the
normal browser form and existing real adapter. No music/text/speech calls,
uploads, paid services or port 9000. The adapter fully decodes each PNG before
accepting it; the browser also loaded each at 512x512. Safe DOM observations and
inputs: [cover-browser-record.json](../results/cover-browser-record.json).
Actual screenshot: [cover-generation.jpg](../results/cover-generation.jpg).

The art reflects both contexts, but FLUX added lettering despite the prompt's
no-lettering instruction (including imperfect lettering on the first cover).
Do not promise precise typography or absence of text from that instruction.
No extra generation was spent on optional visual polish.

Failure/retry and audio preservation were tested offline; no real outage or live
song/audio pairing was claimed. No fixture provider or fake audio enters the
normal app. Songs remain drafts until A3-02 supplies actual generated audio.
No approved samples, full AT-05/AT-06 closure, independent ZIP or release
acceptance is claimed. Submission NOT READY. Shared v1 objects/schema, service
payloads, dependencies and branch protection are unchanged. The existing
Starlette TestClient deprecation warning remains.

Follow-up 5ccb371 retains HttpOnly session cookies on error/media responses; its
HTTP regression confirms repeated failures reuse one session instead of consuming
slots. All 73 tests passed after this fix. Browser cover evidence remains the
264c391 feature run; no additional class generation was needed for cookie handling.

## PR #17 main reconciliation - 2026-10-28 America/Denver

Integrated main 2775f0b (merged PR #16) into codex/matching-covers without
rewriting its reviewed cover commits. Three documentation conflicts were
resolved: README uses the renamed .jpg evidence and the cover-era description;
TEST_RESULTS preserves both runtime-hardening and cover evidence; handoff
consolidates current state and inherited notes. Auto-merged contracts retain
media-ID uniqueness, the verified speech-format boundary and session integration.
Applied the deferred PR #16 grammar nit and consolidated completed review credit.
No app code, provider payload, dependency, CI or protection change was introduced
by the resolution. No new live generation or media was needed.

Matt approved the original cover head bcdfcb5 with 73 tests; that historical
review remains credited. The combined head requires current CI and independent
approval under the existing protection rules. Combined python scripts/dev.py
--check PASS: 76 tests (63 main + 13 cover), verifier 60 files, coverage 36/11/19.
Whitespace, local links, retired-term/stale screenshot-reference and conflict-marker
checks pass. Cover app/frontend/tests match the previously reviewed cover commit;
provider/contracts/schema and protected files match main exactly. Previous browser
evidence retains its original tested commits and is not relabeled as a new live run.

## A3-02 instrumentals - 2026-10-28 America/Denver

Tester: mase7919 directing Hermes; Windows, locked Python 3.12.14.
Branch codex/a3-02-instrumental-generation; base main 3e298fe.
Scope: R08/R09/R12 and the AT-03/AT-06 normal-launch instrumental flow. The
parent issue stays open for merged-main verification and independent review.

| Check / exact safe input | Expected | Actual |
|---|---|---|
| Locked offline command: python scripts/dev.py --check | Default suite collected and passing; coverage retained | PASS, verifier 62 files, coverage 36 requirements/11 tasks/19 cases, all 96 tests (76 merged baseline + 20 new music/contract tests) |
| New music routes offline (mocked adapters, real HTTP) | Submit once with instrumental marker, poll, download, attach WAV -> ready; no duplicates; safe failures; art+music concurrency; session isolation | PASS, two-track flow, 409 duplicates, 404 foreign media, 429 caps, deadline/retry, both completion orders, media budget, reload without regeneration |
| Normal launcher + real services; Song A: Moonlit Reflection / Ambient piano / Calm and reflective / 10 s instrumental | One ACE-Step task -> playable WAV on that track plus automatic FLUX cover; ready status | PASS, art and music jobs succeeded in ~6 s; 10.0 s 48 kHz stereo PCM16 WAV, non-silent (RMS 0.144); 512x512 cover paired; track ready |
| Same app; Song B: Desert Drive / Upbeat funk / Energetic and optimistic / 20 s instrumental | Second distinct song; first song not overwritten | PASS, ~6 s; 20.0 s 48 kHz stereo PCM16 WAV, non-silent (RMS 0.216); separate audio/cover media IDs; Song A intact |
| Reload-equivalent after both complete | Tracks, covers, audio and job states persist; no new generation | PASS, snapshot stable across reads; 2 tracks / 4 terminal jobs; no resubmission |
| Security/boundary | No keys, provider task IDs, opaque download paths or raw bodies reach the browser/snapshot; media stays session-private; no port 9000 | PASS, tickets kept server-side only (snapshot test), 404 for foreign media, safe fixed error messages, status flags cover/music availability only |

Safe measurements: [instrumental-live-record.json](../results/instrumental-live-record.json).
Raw WAV/PNG media stayed in an ignored temp location; it is not approved sample
material (Issue #7 owns samples). Instrumental duration bound: the app accepts
10-60 seconds (the class 20 MB response cap bounds a 48 kHz/16-bit/stereo WAV
at about 104 seconds; 60 s leaves margin). The shared SongSettings schema range
(10-600) is unchanged and documented in APP_CONTRACTS.md.

Limitations: interactive browser automation is unavailable in this environment,
so audible playback and visual UI verification were not independently performed;
the browser flow was exercised through the normal launcher over HTTP with fully
decoded WAV/PNG media, and the page renders a real <audio controls> element for
each ready track. That listener/browser step and the merged-main run remain for
teammate review and the issue's completion checks. Submission NOT READY.

### PR #18 hardening follow-up - 2026-10-28 America/Denver

Tester: mase7919 directing Hermes; Windows, locked Python 3.12.14. Same task
branch; base 4c30a88. No additional live ACE-Step or FLUX generation was made.

| Check | Expected | Actual |
|---|---|---|
| Frontend playback preservation | Playing audio survives unrelated library updates | FIXED and guarded: track cards are now diffed and rebuilt individually, and an in-progress audio position is carried across a same-card rebuild; static regression guards in tests/test_frontend.py |
| Music task recovery | Resume the retained ACE-Step ticket without a new submission | ADDED: POST /api/tracks/{id}/music/resume?from={job} continues poll/download of the same task (verified the SAME ticket object is polled, submit count stays 1); never-confirmed submissions return 409 with guidance; non-retryable/succeeded jobs are 404 |
| Truthful progress stages | UI never claims downloading while polling | FIXED: polling progress stays capped at 0.79; the 0.9 downloading stage is set only after a successful poll; covered by store-level and static-frontend tests |
| Concurrency test reliability | Duplicate/coexistence tests prove real in-flight concurrency | HARDENED: both thread-pool tests now assert the in-flight job is visibly running, release the gate in finally, and cannot pass on a timed-out mock |
| Configuration UX | Create button and messages match supported actions | FIXED: art-only mode creates draft+cover with an explanatory notice (label changes accordingly); music-only/neither modes explain what to configure; not_configured music errors give restart guidance |
| Credential hygiene | No keys in branch, evidence or docs | PASS, scan of tracked files and the full diff finds no key assignments; .env.example keeps placeholders; .env stays gitignored |

Locked python scripts/dev.py --check PASS here: all 109 tests (96 prior + 13
hardening/regression), verifier 63 files, coverage 36/11/19; schema regenerated
byte-identical; diff whitespace clean. The two real-generation records in
instrumental-live-record.json are untouched and still describe the 4c30a88-era
live run; interactive browser playback remains a teammate step.

### PR #18 three-defect correction - 2026-10-28 America/Denver

Tester: mase7919 directing Hermes; Windows, locked Python 3.12.14. Same task
branch; base f3b047f. Defects found by independent inspection after the
hardening pass; each reproduced against the base, then fixed with a regression
test. No additional live ACE-Step or FLUX generation was made.

| Defect | Reproduction (base f3b047f) | Fix | Regression tests |
|---|---|---|---|
| 1. Mismatched resume URL leaves an active job behind | POST /api/tracks/{B}/music/resume?from={A failed job} returned 404 but had ALREADY created a job and consumed the (A, music) active slot; A then refused both new-music and resume with 409 forever. Reproduced store-level and over HTTP | Track-ownership validation moved INTO SessionStore.resume_music before any allocation; a mismatched resume has zero side effects (job count, active set and tickets unchanged; the rightful track resumes normally) | test_resume_rejects_mismatched_track_without_side_effects (store), test_http_resume_wrong_track_has_no_side_effects (HTTP: 404, no new job, rightful resume succeeds to ready) |
| 2. Normal mutations can still interrupt an active audio player | syncAfterMutation() called previousTracks.clear(), so the next refresh rebuilt EVERY card after any mutation; a playing track's element was destroyed (verified by a dependency-free node DOM simulation: old app.js loses audio node identity and playback position on both unrelated-track creation and the tracked song's own job progress; media replacement still swaps deliberately) | syncAfterMutation() no longer clears the cache — refreshes rely on the per-track diff; renderLibrary() now MOVES the original (still playing) audio element into a rebuilt card whenever its media reference is unchanged, so the node never leaves the document; a genuinely changed media reference gets a fresh, never-auto-played element | Updated static guards in tests/test_frontend.py (no global clear in syncAfterMutation; same-src audio node moved via replaceWith; restoreAudio removed; no audio.play() auto-resume); 8-check node DOM simulation passes on new app.js and fails on the old |
| 3. Second resume attempt cannot locate the original provider ticket | After resume-1 failed, the ticket remained only under the ORIGINAL job; the UI's Resume check (from the LATEST failed job) hit 409 despite the valid ticket — reproduced with a single mocked task (deadline timeout, resume timeout, second resume) | Each resumed job now gets the ticket associated with its own id, so any number of resumes stay on the ONE original submission; provider-reported task failure during a resume is terminal (non-retryable) instead of endlessly resumable — only deadline/transport timeouts advertise Resume check; success removes every app-job association of the ticket | test_repeated_resumes_of_same_task_need_only_one_submission (store: r1 -> r2 succeeds, submit_music called exactly once, tickets empty after), test_resumed_terminal_service_failure_is_not_endlessly_resumable (store), test_http_repeated_resume_flow_uses_one_submission (HTTP: two resumes, one submission, track ready), test_resume_failure_keeps_ticket_chain_and_releases_capacity (updated) |

Locked python scripts/dev.py --check PASS here: all 115 tests (109 prior + 5
music chain/wrong-track + 1 updated frontend guard), verifier 63 files,
coverage 36/11/19; schema regenerated byte-identical; diff whitespace clean.
The two real-generation records in instrumental-live-record.json are untouched
and still describe the 4c30a88-era live run. Interactive browser playback
remains a teammate step; the node DOM simulation is behavioral evidence for
defect 2 but is not a substitute for a real browser.

### PR #18 real-browser acceptance - 2026-10-28 America/Denver

Tester: mase7919 directing Hermes; Windows; system Chrome via Playwright
(headless, autoplay-policy=no-user-gesture-required, muted). OFFLINE HARNESS:
the real FastAPI application (real session store, routes, cookies, media
serving and the real jukebox/web frontend) with ONLY the four class-provider
methods replaced by deterministic fixtures serving the genuine class-generated
WAV/PNG files from jukebox-live (Moonlit Reflection 10 s, Desert Drive 20 s).
No network requests to class services; nothing committed; NOT a substitute for
the normal-launch flow or for live generation claims. Dummy keys only; the
repo .env is never loaded (Settings.load(env_file=None), neutral cwd).

All 40 checks PASS / 0 FAIL, per mase7919's recount of the retained
`qa-browser-final.txt` transcript in the [PR #19 review](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/19#pullrequestreview-5692830523).
The full transcript and JSON evidence remain outside the repo; this correction
uses the reviewer's recount, not a new browser run:

- Test A (basic playback): song created through the real form; audio element
  rendered; play() accepted; readyState >= 1; currentTime advanced 0.00 ->
  1.25 s; pause froze the position; resume continued (no restart); zero media
  error events; real Moonlit WAV decoded (duration = 10 s).
- Test C (playing during another track's creation): while A played, Desert
  Drive was created from the form; A's audio element SURVIVED by node
  identity (same DOM node) and kept playing (1.72 -> 2.06 s, not paused,
  not reset); media URL unchanged; two players in the library.
- Test B (two-track library): correct titles and style/mood labels per card;
  distinct audio URLs and distinct covers; play B while A paused -> both
  independent and selectable; B's real Desert WAV decoded (duration = 20 s).
- Test D (paused position): seek+play+pause A at 4.527 s; create a third
  song; A stayed paused and its position was preserved exactly (4.527 ->
  4.527 s, tolerance 1.0 s); resume continued from ~4.5 s to ~5.5 s, not 0.
- Test E (changes to the playing track itself): regenerating A's cover while
  A played updated the artwork, kept the SAME audio node, kept it playing,
  and left exactly one audio element.
- Test F (genuine audio replacement): "Generate new instrumental" produced a
  NEW element (node identity changed), new media URL, old element removed,
  exactly one player, replacement NEVER auto-played (paused), and the new
  content genuinely was the other song (duration 20 s); A's cover pairing
  survived the music replacement.
- Console/network: no console errors or warnings beyond the app shipping no
  favicon (Chrome requests /favicon.ico twice per load; both 404s logged,
  confirmed by URL via CDP; cosmetic and pre-existing, unrelated to playback
  or PR #18's changes); zero unexpected HTTP >= 400 responses; zero uncaught
  page errors.

Limitations (unchanged, honest): engine-level playback evidence only. The
browser ran headless and muted, so audible output was NOT listened for; human
listening in a real (headed/audible) browser remains a teammate step. The
harness substitutes fixtures for the live providers, so this does not re-test
class-service connectivity (already covered by the two-song live record).

## A3-02 / A3-04 normal-launch acceptance - 2026-10-28 America/Denver

Tester: JoshuaKosakowsky directing Codex, with Joshua personally confirming the
listening result. Tested a clean checkout of merged **main
7cc96458fa4c99120380379d46b96592d3a3934e**, started with the documented
python scripts/dev.py --port 8000 and existing ignored class configuration.
No harness, fixture provider, imported track or alternate launcher was used.
PR #18 was still a draft; Joshua authorized merging it, so it was marked ready
and merged normally at the approved d1a1a92 head. Protection was unchanged.

| Input/check | Expected | Actual |
|---|---|---|
| Duration 9 s, otherwise valid form | Reject before a provider submission | PASS, browser says minimum 10; zero tracks; correcting to 30 recovers |
| Moonlit Reflection / Ambient piano / Calm and reflective / 30 s / Instrumental | Fresh ACE-Step audio and matching FLUX art | PASS, 30.0 s, 48 kHz stereo PCM16 WAV, 5760078 bytes, full decode/nonzero signal; 512x512 PNG; ready track |
| Native play -> pause -> resume | Audio plays, pause holds position, resume continues | PASS, readyState 4, unmuted/volume 1, no media errors; paused position held exactly at 3.599095 s |
| Desert Drive / Upbeat funk / Energetic and optimistic / 20 s, created while first plays | New independent audio/cover; first track keeps playing | PASS, first continued from 3.832261 to 24.597208 s on the same media URL; second generated as 20.0 s, 48 kHz stereo PCM16, 3840078 bytes with distinct 512x512 cover |
| Select/play second song | Both tracks independently playable without manual overlap | PASS, first stopped/ended, second advanced; both ultimately reached their 30/20 s ends with no errors |
| Normal page reload, then select/play both again | Keep the same tracks/media and do not regenerate | PASS, identical session snapshot before/after, two tracks/four succeeded jobs, same UUIDs and pairings; both players decoded and advanced after reload |
| Human listening | Audible instrumental output broadly fits the two requested styles | PASS, Joshua replied "Both play and broadly match" after receiving the actual 30/20 s clips |
| Offline suite and main CI | Relevant regressions/gates still pass on merged code | PASS, 115 tests; verifier 63 files; coverage 36/11/19; all four main CI checks green |

Safe full observations, request values, hashes, decoded-media measurements,
job/session state and listening attribution are in
[main-instrumental-acceptance.json](../results/main-instrumental-acceptance.json).
Actual screenshot: [two-song library](../results/main-instrumental-library.jpg).
Main CI: [run 40814391178](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/actions/runs/40814391178).

Exactly two deliberate music submissions and two automatic art submissions were
made. Text/speech generation, uploads, paid services and port 9000 were not used.
Startup, status refresh, downloading existing media and reload did not submit
generation. No browser console errors were observed. Public evidence contains
app UUIDs only, not private provider tickets, keys or filesystem routes.

The first cover shows a piano/lake scene; the second has a bright driving/car
theme. FLUX again added lettering despite the prompt, including "DESSERT DRIVE"
on the second image. This is a disclosed typography limitation, not polished
sample acceptance. Raw generated WAV/PNG files are retained locally under ignored
results/raw/a3-02-normal-launch-7cc9645 for possible later sample selection;
none are committed or declared approved samples.

AT-03, AT-05 and AT-06 now have actual normal-entrypoint/live-browser evidence on
integrated main. A3-02 acceptance is complete; A3-04's remaining live audio/cover
pairing gap is satisfied. This does not establish vocals, AI DJ sequencing,
reference voices, full failure-case coverage, sample completion or independent
GitHub ZIP/release acceptance. Full submission remains NOT READY. Recorded wall
times include browser/tool waits and must not be used as inference benchmarks.

## A3-03 vocal songs with AI lyrics - 2026-10-29 America/Denver

Tester: MSpanny directing Hermes. Branch codex/a3-03-vocal-songs; base main
7b9dd2b (post-#19). Scope: R10 / AT-04 vocal user outcome plus the shared
infrastructure it needs. The parent issue stays open for the live class-service
run and merged-main verification.

| Check / exact safe input | Expected | Actual |
|---|---|---|
| Locked offline command: python scripts/dev.py --check | Default suite collected and passing; coverage retained | PASS, verifier 65 files, coverage 36 requirements/11 tasks/19 cases, all 127 tests (115 merged baseline + 12 new) |
| Vocal create + lyrics + music over real HTTP routes (mocked Qwen/FLUX/ACE-Step) | Qwen lyrics attach to the track; the vocal ACE-Step request carries the REAL lyrics and a vocal-aware prompt; WAV attaches -> ready with cover | PASS, three succeeded jobs, lyrics on track, submit_music called once with the exact lyrics text and duration, audio+cover media served; no key material in snapshots |
| Instrumental regression over real HTTP | Instrumental path unchanged: frozen "[Instrumental]" marker and the no-vocals prompt | PASS, submit_music kwargs lyrics="[Instrumental]", prompt unchanged |
| Vocal music without lyrics | Reject before any provider submission, zero side effects | PASS, 409 "Generate the song's lyrics...", no submit call, one art job only |
| Submit-time guard (defensive) | A vocal music job without lyrics at generate time fails loudly, never falls back to the marker | PASS, job failed with a lyrics message, submit_music not called, slot released |
| Lyrics failure/retry | Failed text job is retryable, track/cover untouched, retry gets a NEW job id and attaches fresh lyrics | PASS through real HTTP routes with mocked providers |
| Missing text configuration | Safe not_configured error, no provider call, draft/cover unaffected | PASS, 502 lyrics_generation_available=false, only the art job ran |
| Static frontend guards | Vocal controls wired; one-click chain never re-submits after reload or when a music job exists | PASS, 3 new guards in tests/test_frontend.py plus the existing playback-preservation guards |

Design decision: vocals reuse the SAME verified ACE-Step release_task request
and only change the lyrics field (instrumentals send the frozen
"[Instrumental]" marker; vocals send the track's current AI lyrics) plus a
vocal-aware prompt. The probe already proved the lyrics field and the submit/poll/download flow; this is the smallest deviation from a verified
contract, and the lyrics token budget for Qwen is raised from 192 to 512 only
for this call so 10-60 second songs get complete lyrics. Both deviations are
recorded in SERVICE_CONTRACTS/APP_CONTRACTS and require the live acceptance
evidence below before issue closure.

One-click vocal chain: the browser starts the cover and lyrics jobs at create,
then asks for the vocal track exactly once when a lyrics job observed while the
page is open succeeds. The chain is seeded from the first snapshot, so reloading
the page never submits generation (README rule preserved); a music job that
already exists prevents re-chaining, so a failed vocal request is always a
deliberate button click.

### Real-browser acceptance (offline fixture harness) - 2026-10-29 America/Denver

System Chrome (headless, muted) against the REAL application with only the
four ClassProviders methods replaced by deterministic fixtures (generated
512x512 PNG cover; fixed lyric text with a per-call version suffix; ACE-Step
submit->immediate-succeed->WAV). Dummy keys, Settings.load(env_file=None),
no network to class services, nothing committed from generated/. All 12
checks PASS, per [vocal-browser-record.json](../results/vocal-browser-record.json):

- One-click vocal create auto-chained cover -> lyrics -> vocal music with a
  single form submit: three succeeded jobs, track ready, provider counters
  exactly 1/1/1/1/1 (cover/lyrics/submit/poll/download).
- Card showed cover, "Vocal track ready", "AI lyrics ready", the collapsible
  lyrics block and an <audio controls> element; the fixture WAV decoded in the
  engine (readyState 4) and playback advanced past zero.
- Page reload preserved the session and left every provider counter unchanged
  (no re-submission).
- A second song in instrumental mode still auto-started music at create.
- "Generate new lyrics" replaced the lyrics (version suffix 1 -> 2) WITHOUT
  resubmitting music; "Generate new vocal song" then resubmitted deliberately,
  exactly once.
- Final counters 2/2/3/3/3: each generation fired exactly once, no duplicates,
  no refresh/reload-triggered submissions.

Independent review of the branch diff (fresh-context reviewer): PASS, no
security or logic findings; one non-blocking suggestion about resume_music and
regenerated lyrics — resolved in the docstring (resume re-polls the SAME task
whose lyrics were fixed at submission; regenerated lyrics only enter through a
fresh deliberate submission). The create heading and resume error now use
mode-neutral "song" wording.

### Reviews and review-cycle fixes - 2026-10-30 America/Denver

PR #21 review by JoshuaKosakowsky flagged one blocking P2 plus two accuracy
notes; all resolved on this head:

| Review finding | Fix | Verification |
|---|---|---|
| P2: lyrics retry button stays disabled after a rejected request (429 while another track holds the single text slot) until reload | The click handler now restores the label and enabled state on failure — a rejected POST creates no job, so the per-track refresh diff would otherwise skip rebuilding that card. Focused on the lyrics control only (the broader instrumental instance is tracked in #8). | Static guard in tests/test_frontend.py plus real-browser offline regression (see below) |
| Accuracy: the blanket no-generation-on-reload claim failed for a mid-chain reload — a pending lyrics job completing after reload auto-posted the music request | The chain seed now covers every non-terminal-failed text job from the first snapshot, so a reload never starts OR continues an auto-chain; a reloaded vocal draft waits for the deliberate Generate vocal song button. README wording sharpened accordingly. | Static guard + real-browser offline regression (held lyrics job, reload, release -> submit_music stays 0) |
| Accuracy: APP_CONTRACTS said the 512-token deviation "is covered by the live A3-03 acceptance evidence" (live run had not happened) | Reworded to "requires live acceptance evidence, pending" | Docs only; git diff --check clean (also removed the flagged trailing space) |

Real-browser offline regressions (fixture harness, system Chrome headless/muted,
per [vocal-browser-record.json](../results/vocal-browser-record.json) checks 11-12):
a lyrics POST rejected while another track's lyrics job was HELD returns 429, the
rejected card's Generate lyrics re-enables after the holder completes and a
Refresh status (no reload); and a mid-chain reload (lyrics job held, then
released) leaves submit_music at zero — no auto-continuation after reload.

Unchecked (honest): the class services were NOT called — the live Qwen lyrics
and ACE-Step vocal run still requires the class .env (absent on this machine)
and is the remaining evidence for AT-04 / issue closure. Audible listening in a
headed browser and sample selection remain. Submission NOT READY.

## Early Windows GitHub ZIP startup rehearsal - 2026-10-29

Tester: JoshuaKosakowsky directing Codex. Downloaded GitHub's source ZIP of merged
main `7b9dd2b2702d7280a231cdcbfbd1afad136f3f56` into a fresh Windows folder,
then followed README's pinned uv installation, configuration and normal launcher.
No Git metadata or private `.env` shipped in the archive. All 65 source files
remained byte-identical to the downloaded archive after the checks.

Archive: [exact GitHub ZIP](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/archive/7b9dd2b2702d7280a231cdcbfbd1afad136f3f56.zip),
330089 bytes; SHA-256
`ffca71b88e7875985a95095043bac5dd93c5907021bb82f5e5b9c183086c1415`.
Environment: Windows 11 (10.0.26200), launcher Python 3.14.7, uv 0.12.19;
uv selected Python 3.12.14 and installed 19 locked packages into a fresh short
LOCALAPPDATA environment. Existing Python/Git tooling, internet and cached
Python 3.12 were available; this was a fresh extraction, not a clean OS.

| Input/check | Expected | Actual |
|---|---|---|
| `python -m pip install uv==0.12.19`, then `python scripts/dev.py` without `.env` | Install and launch directly from the ZIP | PASS; new environment created, app served on loopback 8000, browser connected with empty library |
| Missing settings, then Refresh status | Useful setup guidance; generation disabled | PASS; all four roles show Missing settings; create disabled; refresh stays connected with zero tracks |
| Copy `.env.example` unchanged to `.env`, restart | Placeholders allow empty-app startup | PASS; same missing-settings view; health/status/session HTTP 200, zero tracks/jobs; no browser console errors |
| Synthetic invalid art endpoint and synthetic key, normal launch | Reject safely without echoing values | PASS; exit 2, only "Invalid art endpoint. Use the documented class host, port and /v1 base URL."; no endpoint, key or traceback |
| Supply existing local class settings, then `python scripts/dev.py --port 8001` | Correcting settings recovers; alternate-port launch works | PASS; all four roles Configured, generation control enabled, health/status/session HTTP 200; connectivity_checked remains false |
| Configured Refresh status and page reload | Stay connected without starting generation | PASS; zero tracks/jobs and no browser console errors |
| Compare extraction with archive; stop servers and remove temporary `.env` | Preserve shipped source and private developer setup | PASS; all 65 files byte-identical, both rehearsal ports closed, only the temporary private settings copy removed |

[Safe structured record](../results/windows-zip-startup.json), actual browser
screenshots: [missing settings](../results/windows-zip-missing-settings.jpg),
[configured](../results/windows-zip-configured.jpg). No startup or configuration
fix was needed. No deliberate class-service generation was submitted.

This supports the startup/configuration portion of AT-16 and archive-identity
preparation for AT-18. Neither case is complete: Joshua was already involved in
implementation; a different teammate must still install the final candidate ZIP
and exercise every required feature and sample. No provider-connectivity,
generation/playback, vocal, DJ, reference-voice, sample or release acceptance was
performed here. Issue #10 stays blocked with jovi1214 as lead; full submission
remains NOT READY. The evidence documents the tested 7b9dd2b ZIP, not a later
candidate containing this documentation.
