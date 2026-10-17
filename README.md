# AI Jukebox - MBAX 6418-801 (Assignment 3)

A team-built app for custom songs, matching covers and spoken DJ commentary.
**Status: collaboration scaffold; no application or generated samples yet.**
Public repository: [AI-Jukebox_MBAX6418](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418).
The four minimal live generation requests are verified in
[service contracts](docs/SERVICE_CONTRACTS.md); app integration remains pending.
Initial CI and
main-protection verification are recorded in [publication issue #11](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/11).
Team workflow active: all changes use task branches and reviewed PRs.
Joshua/the team will arrange collaborator invitations and assignments.

## Start here

- Agents: [AGENTS.md](AGENTS.md) and [handoff.md](handoff.md).
- Team workflow and labels: [CONTRIBUTING.md](CONTRIBUTING.md).
- Required features and unchanged starter prompt: [docs/ASSIGNMENT.md](docs/ASSIGNMENT.md).
- Delivery order and ownership: [PLAN.md](PLAN.md).
- Full-brief coverage: [acceptance.json](docs/acceptance.json); concrete tasks:
  [ISSUES.md](docs/ISSUES.md); lessons applied: [A2_LESSONS.md](docs/A2_LESSONS.md).
- Tests/evidence: [docs/TESTING.md](docs/TESTING.md), [docs/TEST_RESULTS.md](docs/TEST_RESULTS.md).
- Publication/protection: [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md).

## Required app

Choose style, mood, duration and vocal/instrumental mode; generate playable
songs and matching covers; keep new songs in the session library. Provide
song-specific spoken DJ commentary, default/reference voices (MP3/WAV),
play/pause, skip and automatic speech/music sequencing without overlap.
Show generation status, useful errors and recovery. Bundle three class-generated
sample songs with titles, covers and AI-generated lyrics where applicable.

| Role | Required class service | Port |
|---|---|---|
| Text/lyrics | Qwen3.6-35B-A3B | 9001 |
| Art | FLUX.2 klein 4B | 9006 |
| Music | ACE-Step 1.5 XL Turbo | 9007 |
| Speech | Chatterbox Multilingual V3 | 9008 |

Use the [verified request baseline](docs/SERVICE_CONTRACTS.md) and current class
documentation; never guess API routes or schemas. No paid services, including
optional features; no app requests to port 9000. Core features must work with class services and credentials alone.

## Local scaffold setup

Git and Python 3.12+ are sufficient for the current offline scaffold check:

```powershell
git config --local core.hooksPath .githooks
git config --local core.longpaths true
git config --local jukebox.allowPush true
python scripts/verify_repo.py
python scripts/check_readiness.py
python -m unittest discover -s tests -p 'test_*.py'
```

This validates files, links, basic tracked-file safeguards and the saved policy;
it does not test app functionality. Local hooks block main commits and all
direct main updates/deletion. Task-branch pushes are enabled above; GitHub
enforces server protection. Create task branches from main and follow CONTRIBUTING. No app install/launch command exists yet;
A3-01 will add the chosen runtime, locked dependencies and verified instructions.

Keep keys server-side in ignored `.env` or environment variables; `.env.example`
contains placeholders. Never expose keys in browser code, logs, docs, screenshots
or archives. Never commit user uploads or voice references, or bundle third-party
music, lyrics, art or voice samples. Approved class-generated samples go in
[assets/samples/](assets/samples/README.md), with provenance and actual media.

## Implementation direction

Proposed: browser controls -> server orchestration -> four class adapters.
Stable track IDs associate audio, cover, lyrics and status. One playback controller
serializes speech/music. A3-01 chooses the UI/runtime and shared contracts;
PLAN.md prioritizes a small working user flow before polishing separate components.

## Evidence and submission (pending)

Record inputs, expected/actual results for all core features and a failure case,
safe screenshots, a tested design choice and an investigated limitation in
docs/TEST_RESULTS.md; summarize verified findings here in the team's own words.
No app functionality, playback or independent deployment has been verified yet.
Current submission status: **NOT READY**. Coverage/CI success is not completion;
the final candidate needs all AT cases and the independent GitHub ZIP check in
docs/TESTING.md. Do not leave that rehearsal until the submission deadline.

Submit the public repo URL, exact commit and GitHub ZIP of that same version.
A teammate must install from the extracted ZIP using only this README and class
credentials, exercising core features and the three bundled samples. Keep the
repo accessible through grading. Every teammate contributes and reviews.

## Baseline

Adapted from [Assignment 2](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418)
commit `1a19c33ab9929dd2796ac7a5ea53247602a0cd32`. Workflow was simplified after
reviewing its integration/review history; Assignment 2's RAG stack is not assumed.
