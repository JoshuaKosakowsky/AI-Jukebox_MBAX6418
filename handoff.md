# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Task: early Windows ZIP startup rehearsal, Refs #10.
## Constraints
Protected task-branch/PR workflow; no self-approval. No feature changes or service generation.
## Repository state
Branch codex/windows-zip-startup from merged main 7b9dd2b; PR #19 merged with Matt's approval and green main CI.
## Work completed and decisions
Downloaded exact GitHub ZIP; fresh extraction launched from README without .git or private config.
Missing/placeholders, invalid endpoint, configured recovery, alternate port and browser refresh/reload passed.
All 65 archived source files byte-identical; servers stopped and temporary .env removed; original preserved.
Added safe JSON/two actual screenshots, TEST_RESULTS evidence and concise README/results links; no launcher fix needed.
Mike/MSpanny now leads #3 per Joshua; #5 remains prse4479. Live issues own current assignments.
## Validation
Startup rehearsal passed on Windows, launcher Python 3.14.7 -> locked app Python 3.12.14, uv 0.12.19.
Locked checks passed: 115 tests, verifier 68 files, coverage 36 requirements/11 tasks/19 cases; diff clean.
## Blockers and unchecked areas
#10 remains blocked and led by jovi1214; this developer rehearsal is not the final independent installation.
Vocals, DJ flow, references, samples and full release verification remain incomplete; submission NOT READY.
## Next steps
1. Teammate reviews the focused evidence PR; merge only after approval and green CI.
2. Mike implements #3; prse4479 implements #5; avoid shared app-file changes in this docs task.
3. Record completed work/review credit when this PR merges; jovi performs final independent ZIP checks later.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/10

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
