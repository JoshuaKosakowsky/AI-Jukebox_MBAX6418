# Agent handoff

## Session
2026-10-29 America/Denver; Codex for Joshua. Task: publish Moonlit candidate and allow independent concurrent PRs.
## Constraints
Joshua explicitly authorized parallel independent PRs now; keep protected reviews/checks and issue ownership.
## Repository state
Branch codex/moonlit-sample-candidate from main 7b9dd2b; original candidate commit 586025f is pushed.
PR #20 remains independent. Audit/review work is on codex/a3-08-recovery-audit; no app code shared here.
## Work completed and decisions
Moonlit WAV/PNG are unchanged originals with a candidate record, model/settings/provenance and README guidance.
Both full decodes and muted asset-preview play/pause/resume passed; Joshua's earlier listening is attributed.
Updated AGENTS/CONTRIBUTING: concurrent independent PRs allowed; coordinate overlap/dependencies as needed.
The audit PR carries the identical guide update, so either merge order works; reconcile handoff text on integration.
Shared manifest is still empty. Jovi owns candidate selection, sample-library integration and the full three-song set.
## Validation
Candidate hashes match the original normal-launch record; 30 s/48 kHz/stereo/PCM16 WAV and 512x512 PNG.
Prior candidate gates passed: 69 tracked files, coverage 36/11/19, whitespace clean; no new generation.
Final guide/handoff checks passed: verifier 69 files, coverage 36/11/19, whitespace clean; runtime/protection untouched.
## Blockers and unchecked areas
This is a candidate, not final sample/ZIP acceptance. The #21 retry finding last reproduced on 3245fcd remains in its review.
Full submission NOT READY; no new listening or class-service calls claimed. No dependency on #20's approval.
## Next steps
1. Teammate reviews the candidate PR; merge normally after approval and green CI.
2. Jovi adopts the candidate if selected, completes the other samples and verifies normal-app/final ZIP playback.
3. Preserve all task notes when reconciling shared handoff text after another PR merges.
## References
https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/7#issuecomment-6513289437
Candidate: assets/samples/moonlit-reflection.candidate.json; source: results/main-instrumental-acceptance.json.

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
