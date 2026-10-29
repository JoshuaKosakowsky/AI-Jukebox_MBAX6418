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
| Locked offline command: python scripts/dev.py --check | Default suite collected and passing; coverage retained | PASS, verifier 61 files, coverage 36 requirements/11 tasks/19 cases, all 96 tests (76 merged baseline + 20 new music/contract tests) |
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
hardening/regression), verifier 62 files, coverage 36/11/19; schema regenerated
byte-identical; diff whitespace clean. The two real-generation records in
instrumental-live-record.json are untouched and still describe the 4c30a88-era
live run; interactive browser playback remains a teammate step.
