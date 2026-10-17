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
All end-to-end app cases remain **not run**. AT-02 has the partial live contract
evidence below. No approved sample media or application exists yet.
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
