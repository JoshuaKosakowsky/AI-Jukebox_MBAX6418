# Local issue briefs

These are proposed tasks, not existing GitHub issue numbers. Create them only
after publication is authorized; record real issue links, owner and review buddy
in PLAN. Acceptance IDs are defined once in [acceptance.json](acceptance.json).
Split a large task into focused child PRs without dropping its user outcome.
A3-08 and A3-09 run throughout the build; they are not final cleanup phases.

## A3-01 - Verify startup and shared service contracts

Owner / review buddy: unassigned. Type: `infrastructure`. Dependencies: none.

**User outcome:** A teammate launches the empty app from documented commands; minimal track/job/adaptor contracts and one documented real request per required service are recorded.

**Scope:** Choose one supported runtime/UI, lock dependencies, define stable track IDs and playback/job states, verify request/response formats and safe errors. Models-list success alone is insufficient.

**Completion checks:**

- [ ] Covered requirements: R01, R02, R03, R04, R05, R06.
- [ ] Applicable cases: AT-01, AT-02; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** Do not build optional architecture, guess APIs or claim that a skeleton is a working jukebox.

## A3-02 - Generate and play an instrumental from the UI

Owner / review buddy: unassigned. Type: `enhancement`. Dependencies: A3-01.

**User outcome:** The normal launch accepts style, mood and duration, generates ACE-Step audio, adds it to the session library and plays it.

**Scope:** Wire UI -> production adapter -> session track -> browser audio in this task. Preserve two tracks through subsequent actions. Include focused offline checks and a deliberate live browser check.

**Completion checks:**

- [ ] Covered requirements: R08, R09, R12.
- [ ] Applicable cases: AT-03, AT-06; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** No test provider in production, private launch fixture or backend-only completion claim.

## A3-03 - Generate vocal songs with AI lyrics

Owner / review buddy: unassigned. Type: `enhancement`. Dependencies: A3-02.

**User outcome:** A vocal request uses Qwen lyrics and ACE-Step to produce a playable vocal track with the selected settings.

**Scope:** Integrate the real lyrics/music responses, expose generation status safely, retain the resulting track and document observed limits.

**Completion checks:**

- [ ] Covered requirements: R10.
- [ ] Applicable cases: AT-04; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** No third-party lyrics; do not assume a successful HTTP response means playable audio.

## A3-04 - Generate and pair a new cover for every song

Owner / review buddy: unassigned. Type: `enhancement`. Dependencies: A3-01.

**User outcome:** Every custom song gets new FLUX art reflecting its theme/style/mood; multiple tracks keep their correct cover/audio associations.

**Scope:** Coordinate with A3-02 on the merged track contract. Integrate the cover in the real UI and test partial failure/retry without swapping covers.

**Completion checks:**

- [ ] Covered requirements: R11.
- [ ] Applicable cases: AT-05; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** No static cover standing in for generation; no new persistence subsystem beyond session needs.

## A3-05 - Play a queue with the default AI DJ and controls

Owner / review buddy: unassigned. Type: `enhancement`. Dependencies: A3-02, A3-04.

**User outcome:** Queued tracks advance automatically; Qwen writes track-specific commentary spoken by Chatterbox, followed by music without overlap.

**Scope:** One playback controller owns pause/resume, skip, advancement and end-of-queue. Exercise skip during speech and during music; controls remain usable during generation.

**Completion checks:**

- [ ] Covered requirements: R13, R14, R19, R20, R21.
- [ ] Applicable cases: AT-07, AT-09; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** Do not defer the real browser sequencing check to a final testing issue.

## A3-06 - Support MP3 and WAV DJ reference voices safely

Owner / review buddy: unassigned. Type: `enhancement`. Dependencies: A3-05.

**User outcome:** Both MP3 and WAV uploads customize Chatterbox DJ speech; default voice still works without an upload.

**Scope:** Validate inputs, keep references temporary, define cleanup and recovery, and exclude recordings/uploads from Git and source archives.

**Completion checks:**

- [ ] Covered requirements: R15, R16.
- [ ] Applicable cases: AT-08; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** Do not commit voice fixtures or use another paid speech service.

## A3-07 - Ship three class-generated sample tracks and covers

Owner / review buddy: unassigned. Type: `enhancement`. Dependencies: A3-02, A3-03, A3-04.

**User outcome:** Three titled, ready-to-play songs and matching covers are tracked and load from the source ZIP without regeneration.

**Scope:** Generate in advance with class services, record inputs/models/date/provenance and AI lyrics where used in assets/samples/manifest.json; listen and inspect each pair.

**Completion checks:**

- [ ] Covered requirements: R17, R18.
- [ ] Applicable cases: AT-11; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** A manifest or generation script without the actual audio/images does not satisfy this task.

## A3-08 - Verify failure recovery and public-file safeguards

Owner / review buddy: unassigned. Type: `testing`. Dependencies: A3-01.

**User outcome:** At least one actual UI failure and recovery is recorded; credentials and prohibited media stay out of browser outputs, Git and archives.

**Scope:** Starts with the first adapter and continues across feature PRs: safe configuration/provider errors, bounded waits, no duplicate generation on retry, no paid features or port 9000, archive/diff review.

**Completion checks:**

- [ ] Covered requirements: R07, R22, R23, R24, R25.
- [ ] Applicable cases: AT-02, AT-10, AT-12; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** This is not the only owner of feature tests; each feature ships its own checks. Avoid unrelated hardening after required flows work.

## A3-09 - Maintain verified README, screenshots and findings

Owner / review buddy: unassigned. Type: `documentation`. Dependencies: A3-01.

**User outcome:** README matches the finished app and explains setup/use, all core flows, observed results, a tested design choice and an investigated limitation.

**Scope:** Update as each user flow lands. Capture real screenshots, distinguish live/stubbed checks, record expected/actual behavior for all three core features plus a failure, and have the team verify findings in its own words.

**Completion checks:**

- [ ] Covered requirements: R26, R27, R28, R29, R30, R31.
- [ ] Applicable cases: AT-13, AT-14, AT-15; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** No fabricated UI screenshots or synthetic-only claims of class-service functionality. An SVG or A2-style RAG benchmark is not an A3 requirement.

## A3-10 - Rehearse ZIP installation and freeze the submission

Owner / review buddy: unassigned. Type: `testing`. Dependencies: A3-03, A3-05, A3-06, A3-07, A3-08, A3-09, A3-GH.

**User outcome:** A different teammate installs the exact GitHub ZIP from README + class credentials, verifies all core features and samples, and records the submitted commit/ZIP identity.

**Scope:** Rehearse once all core flows are connected, not on submission night. Fix missing files/steps. Freeze a merged main candidate, download its exact GitHub ZIP, run the release gate, and record every teammate contribution/review.

**Completion checks:**

- [ ] Covered requirements: R32, R33, R34, R35.
- [ ] Applicable cases: AT-11, AT-16, AT-17, AT-18; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** Do not substitute a local archive for the required GitHub download, waive a missing requirement, or modify candidate code after the independent check.

## A3-GH - Publish the public repo and verify main protection

Owner / review buddy: unassigned. Type: `infrastructure`. Dependencies: none.

**User outcome:** After explicit authorization, the public repo, labels, teammate access and protected main policy are configured and independently read back.

**Scope:** Use docs/GITHUB_SETUP.md; convert these local task IDs into real issues and fill owner/review buddy fields. Preserve the unavailable-reviewer exception.

**Completion checks:**

- [ ] Covered requirements: R36.
- [ ] Applicable cases: AT-19; record actual inputs/results, not only test counts.
- [ ] Relevant integration/failure checks complete (normal entrypoint for features); parent gaps stay open.

**Keep out of scope:** Blocked by the standing no-push instruction; this local setup does not authorize publication.
