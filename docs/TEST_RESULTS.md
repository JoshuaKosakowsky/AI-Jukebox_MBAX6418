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
settings, collaborators, assignees or review buddies were changed. This transition
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

Actual browser evidence: [configured setup](../results/startup-configured.png),
[empty library](../results/startup-library.png), [missing configuration](../results/startup-missing-settings.png).
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
