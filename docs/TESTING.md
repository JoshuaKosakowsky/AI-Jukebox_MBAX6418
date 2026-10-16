# Testing - AI Jukebox

## Current scaffold check

Run `python scripts/verify_repo.py` from the root. It uses no credentials,
network, third-party packages or class services. CI's stable job name is
`test`, matching the saved Assignment 2 branch protection. Currently it checks
scaffold integrity and tracked-file safeguards only; it is not an app test.

## Application test policy (to implement with the app)

Carry forward Assignment 2's three tiers. If the team chooses Python, use
pytest markers `unit`, `smoke`, `e2e`, and configure default pytest to exclude
e2e. Add dependencies and runnable commands when tests actually exist. If the
team chooses another stack, document equivalent commands and preserve tiers.

| Tier | Network | Target |
|---|---|---|
| Unit | No | Track schema, generation state, queue transitions, pause/skip, retry rules, config handling |
| Smoke | No | Adapters with synthetic responses, library/cover associations, server/UI wiring and launch |
| E2E | Explicit opt-in | Four real class services, vocal/instrumental output, matching covers, default/reference DJ, actual browser sequencing |

New logic needs meaningful tests including failure cases. Wiring changes need
smoke checks. Offline tests must stub providers and never consume class capacity.
E2E must skip when credentials are unavailable, use bounded calls and record
inputs/results without keys. No real-service tests run in CI. Use original,
tiny synthetic fixtures, never user uploads or third-party media.

Playback verification must observe speech/music ordering, no overlap, automatic
advancement and controls in the real browser. Stubs alone cannot prove audible
playback. Check partial failures and retry without losing correct track links.

Record date, tester, environment, commit, command, inputs, expected/actual
results and safe evidence in docs/TEST_RESULTS.md. Reviewed screenshots and
metrics may go in results/. No raw logs, credentials, uploads or voice recordings.
Do not report queued tests as passed or absent tests as coverage.

## Independent deployment

A teammate tests the exact GitHub ZIP and commit being submitted, with only
README and class credentials. Verify dependencies, samples and all three core
features, voice input, controls and a failure/recovery case. Record findings and
fixes. Inspect the actual archive tree for excluded files and required media.
