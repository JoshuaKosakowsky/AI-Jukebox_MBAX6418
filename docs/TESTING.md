# Testing - AI Jukebox

Current runnable check: `python scripts/verify_repo.py` (offline, standard library).
CI job `test` currently validates the scaffold, not application functionality.

## Match verification to the change

| Change | Verification |
|---|---|
| Docs, labels, formatting | Read the diff, check links and whitespace; no new app tests |
| Logic or bug fix | Focused tests of changed behavior and a meaningful failure case |
| Wiring/shared contract | Offline smoke check of both sides using the same contract |
| User feature | Actual browser flow against required services, with recorded results |

Use unit/smoke/e2e tiers. If Python is selected, use pytest markers and default
to offline unit + smoke; document commands when those tests exist. Mock providers
and external-tool presence/absence. Never call services from offline tests or CI.
Real-service checks are deliberate opt-in, bounded, and skip without credentials.

Run focused checks while iterating, then the applicable offline suite before
review. Once checks pass, repeat only for new changes or unresolved concerns.
Keep checks deterministic; do not add tests that mirror implementation details.
Agree runtime versions and lock dependencies; test supported Windows behavior
as well as CI. Retain the required `test` context when extending CI.

## Prove the user flow

Observe generated audio/cover pairing, session retention, vocals/instrumentals,
default and MP3/WAV-reference DJ voices, play/pause/skip, automatic advancement,
and speech/music sequencing without overlap. Check failures and recovery.
Stubs do not prove audible playback. Record stage timings before diagnosing
slowness; avoid duplicate generation and unbounded retries.

Record date, tester, environment, commit, command/inputs, expected/actual results
and safe screenshots in docs/TEST_RESULTS.md and results/. Never include keys,
user recordings or raw unsafe logs. Distinguish untested behavior from failures.

A teammate must also verify the exact submission GitHub ZIP from README + class
credentials alone, including three actual sample songs/covers and all core flows.
Inspect that ZIP for missing assets, secrets, uploads and developer-only files.
