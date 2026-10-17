# Agent handoff

## Session
2026-10-17 00:28 MDT (America/Denver); Codex. Task: full-brief A2 audit and A3 delivery safeguards.

## Constraints
Local commits authorized. No GitHub writes/pushes, A2 edits, app build or class calls.

## Repository state
Branch: codex/project-setup; pre-handoff commit: 12d56820ec68e3947e61d9155d0a9f468d46e1c2. Clean on entry.
This session's protocol/docs/gate changes are to be committed locally; inspect Git.

## Work completed and decisions
Audited A2 main dfc0fc4 and late PRs #30/#31; see docs/A2_LESSONS.md for bounded findings.
Mapped all A3 brief pages into 36 requirements, 11 task briefs and 19 acceptance
cases. Added continuous coverage/rehearsal/frozen-ZIP gates and empty sample manifest.
Preserved concise in-task fixes, review exceptions, labels, completion record and
the original starter. CI checks structure/gate regressions, not app readiness.

## Validation
Coverage: PASS, 36 requirements / 11 tasks / 19 cases. Gate regressions: 18 passed.
Release without evidence correctly returns NOT READY. Original starter matches
the PDF word-for-word after whitespace normalization; source PDF hash matches.
Full Git/ZIP test uses isolated synthetic repos; fixed its Windows line-ending
assumption with local core.autocrlf=false. No production settings were changed.
Final staged scaffold/hygiene: PASS (30 files); staged whitespace: PASS.
Original assignment/protection payload unchanged; no remote and allowPush=false.
No A3 app or service calls. A2's remote snapshot was reviewed, not runtime-tested.

## Blockers and unchecked areas
Submission NOT READY: no app/samples/independent ZIP evidence. Owners/runtime and
generation contracts remain pending; inherited discovery below is not generation proof.

## Next steps
1. Read docs/ISSUES.md and claim A3-01; choose integration owner and review buddies.
2. Deliver the normal-launch instrumental/cover flow, then vocals and DJ playback.
3. Reconcile R01-R36 each milestone; rehearse ZIP early; no publication without authorization.

## References
PLAN.md; docs/acceptance.json; docs/ISSUES.md; docs/TESTING.md; docs/A2_LESSONS.md.

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
