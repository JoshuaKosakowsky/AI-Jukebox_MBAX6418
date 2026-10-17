# Plan - AI Jukebox (Assignment 3)

Status: local scaffold; no app yet. These IDs are milestones, not GitHub issue
numbers or a requirement for one large PR each. Use small child work items;
routine related fixes stay in the current change (CONTRIBUTING.md).

Integration owner: unassigned. Each claimed work item needs an owner and review
buddy; before publication record them here, afterward use its GitHub issue.

## Delivery order

1. A3-01: agree runtime/dependencies and merge minimal track/job/service contracts.
   Confirm documented service requests before adapters diverge. Record discovery
   separately from actual generation success; models-list checks are insufficient.
2. First user flow across A3-02/A3-03: UI -> instrumental generation -> session
   library -> play. Add a correctly paired cover, then vocals/AI lyrics.
3. A3-04: add song-specific DJ speech and automatic sequencing; exercise pause,
   skip and no-overlap behavior early. Define playback transitions in A3-01.
4. Complete reference voice, required samples, recovery, evidence and ZIP checks.

Parallel work uses merged contracts. Keep one substantial PR active per person.
The integration owner verifies each combined flow on main before its milestone
is marked done. A component-only PR may close a child issue, not the whole flow.

| ID | Phase | Owner | Status |
|---|---|---|---|
| A3-00 | Local repository and collaboration | Setup agent | Done |
| A3-01 | Team decisions, endpoints, runnable skeleton | Unassigned | Pending |
| A3-02 | Custom song generation and lyrics | Unassigned | Pending |
| A3-03 | Matching covers and session library | Unassigned | Pending |
| A3-04 | DJ speech, queue, playback controls | Unassigned | Pending |
| A3-05 | Three pregenerated samples and provenance | Unassigned | Pending |
| A3-06 | Reliability, evidence, design judgment | Unassigned | Pending |
| A3-07 | Independent ZIP deployment and submission | Unassigned | Pending |
| A3-GH | Public GitHub publication and protection | Joshua/team | Awaiting authorization |

## A3-00 - Local setup

- [x] Read Assignment 2 root guidance and actual main protection settings.
- [x] Read the local three-page Assignment 3 brief; preserve starter language.
- [x] Adapt AGENTS, CONTRIBUTING, PLAN, README and supporting templates/docs.
- [x] Add mandatory cross-agent/model handoff protocol and handoff.md.
- [x] Prepare offline scaffold validation, CI, local guards, protection payload.
- [x] Initialize local Git on main, create bootstrap commit and working branch.
- [x] Validate scaffold and local guards without service calls or remote writes.
- [ ] Application exists and runs (belongs to A3-01, not setup).

## A3-01 - Decisions, connection contract, runnable skeleton

- [ ] Team agrees UI/runtime, dependency versions, platform requirements,
      service-adapter interfaces, track schema, and playback state machine.
- [ ] Obtain class-endpoints.txt privately; confirm hosts/routes/auth/payloads,
      response schemas, polling/async behavior, duration limits and timeouts.
- [ ] Keep the starter prompt unchanged; record team additions separately.
- [ ] Add verified installation/launch commands, a reproducible dependency lock,
      agreed runtime versions and offline tests; check supported Windows setup.
- [ ] Missing config returns an understandable safe error without leaking keys.
- **Done:** teammate can install and launch a skeleton with no undocumented
  machine-local files; assumptions and decisions are documented.

## A3-02 - Custom songs

- [ ] Style, mood, duration and instrumental/vocal controls.
- [ ] Qwen AI lyrics for vocals and ACE-Step playable audio for both modes.
- [ ] Generation status, bounded waits/timeouts, failure recovery and safe retry.
- [ ] Offline contract tests and deliberate documented real-service tests.
- **Done:** both track modes play, requested settings are verified against
  observed output, and new tracks join the session library.

## A3-03 - Covers and library

- [ ] New FLUX cover per custom song reflects theme/style/mood.
- [ ] Stable track IDs bind each title, audio, lyrics, cover and status.
- [ ] Session persistence covers subsequent playback and generation failures.
- [ ] Failed covers support recovery without mismatching track metadata.
- **Done:** two or more generated tracks retain the correct audio/cover pairing
  through queue changes and retries; evidence saved.

## A3-04 - Integrated DJ and playback

- [ ] Qwen commentary uses the specific upcoming/queued track context.
- [ ] Chatterbox default voice works without upload.
- [ ] MP3 and WAV voice-reference uploads supported, temporary and excluded
      from Git and submission; validate input and document cleanup behavior.
- [ ] Play/pause, skip, automatic advancement and end-of-queue behavior.
- [ ] One controller serializes speech and music; no overlap, including skip,
      pause/resume, delayed generation and failures. Respect browser audio start.
- **Done:** observe a multi-track queue in default and reference voice modes;
  verify sequencing and controls in the actual supported browser.

## A3-05 - Ready-to-play samples

- [ ] Three titled songs generated in advance with class ACE-Step and FLUX;
      any lyrics generated with Qwen. No third-party assets or voice samples.
- [ ] Actual audio and covers tracked under assets/samples/; provenance recorded.
- [ ] Load samples without generating them at startup or using private paths.
- [ ] Samples play from a fresh extracted GitHub ZIP.
- **Done:** three playable tracks and their matching images ship with the app;
  class-generation provenance and relevant inputs are documented without keys.

## A3-06 - Reliability, report and evidence

- [ ] Record inputs, expected/actual results for all three features and at least
      one failure case; add screenshots of core flows in results/.
- [ ] Test missing credentials, invalid voice media, service failure/timeout,
      playback ordering, retries and session-library integrity as applicable.
- [ ] Justify one important design choice with observed test evidence.
- [ ] Investigate a limitation/failure and explain what was learned.
- [ ] README accurately describes setup/use, findings and unchecked behavior;
      teammates verify wording in their own words.
- **Done:** offline tests pass; real-service evidence is explicit; no unchecked
  claims are reported as successful functionality.

## A3-07 - Independent deployment and final submission

- [ ] Teammate installs from extracted GitHub ZIP using README + class keys only.
- [ ] Verify all core features, three sample tracks, optional voice upload,
      queue controls and a failure/recovery case from that ZIP.
- [ ] Inspect tracked tree/archive for keys, uploads, voice references,
      third-party assets, missing sample media and machine-local dependencies.
- [ ] Record installer, platform, exact commit, commands, outcomes and fixes.
- [ ] Every teammate has meaningful contribution and teammate review evidence.
- [ ] Submit public repo URL, commit ID and GitHub ZIP of the same version.
- **Done:** independently reproduced features in the precise submission version;
  repo remains accessible through grading.

## A3-GH - Future publication (blocked by explicit do-not-push instruction)

- [ ] User explicitly authorizes remote creation, push and protection setup.
- [ ] Create public repository named AI-Jukebox_MBAX6418 and configure remote.
- [ ] Publish initial main; run CI, apply and verify exact saved protection.
- [ ] Set up teammates, issues and review ownership; do not invent usernames.
- [ ] Use branches + reviewed PRs for subsequent work.

## Open decisions

Team membership and ownership; service connection documentation; app framework;
track/session storage; playback state machine; sample themes; supported deployment
platforms; license. No decisions should be inferred from Assignment 2's RAG stack.
