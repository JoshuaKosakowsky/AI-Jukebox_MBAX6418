# AI Jukebox - MBAX 6418-801 (Assignment 3)

A team-built AI jukebox that will generate customizable songs and matching
cover art, then play a collection with spoken AI DJ commentary between tracks.

**Status: local collaboration scaffold only.** No application, service calls,
sample songs, or application tests exist yet. No GitHub repository has been
created, no remote is configured, and nothing has been pushed. The future
repository must be public. GitHub protection of `main` is pending publication.

## Start here

- Agents: read [AGENTS.md](AGENTS.md), then [handoff.md](handoff.md) every session.
- Teammates: read [CONTRIBUTING.md](CONTRIBUTING.md).
- Requirements and unchanged starter prompt: [docs/ASSIGNMENT.md](docs/ASSIGNMENT.md).
- Phases, ownership, acceptance checks: [PLAN.md](PLAN.md).
- Publication and exact Assignment 2 protection policy:
  [docs/GITHUB_SETUP.md](docs/GITHUB_SETUP.md).
- Test tiers and honest evidence: [docs/TESTING.md](docs/TESTING.md).

## Required product

1. Choose style, mood, duration, and instrumental/vocal mode. Generate playable
   songs with ACE-Step; generate lyrics with Qwen for vocal songs.
2. Generate a new FLUX cover for each song and bind it to the correct track.
3. Queue songs with song-specific Qwen commentary spoken by Chatterbox between
   tracks. Use the default DJ voice or an uploaded MP3/WAV voice reference.

Include three ready-to-play sample songs with titles and covers generated in
advance using class services; any sample lyrics must be AI-generated. Newly
generated songs remain playable during the session. Provide play/pause, skip,
automatic queue advancement, sequential speech/music without overlap, generation
status, understandable errors, and recovery.

## Required services

| Role | Class service | Port |
|---|---|---|
| Text and lyrics | Qwen3.6-35B-A3B | 9001 |
| Cover art | FLUX.2 klein 4B | 9006 |
| Music | ACE-Step 1.5 XL Turbo | 9007 |
| DJ speech | Chatterbox Multilingual V3 | 9008 |

Use the team's supplied `class-endpoints.txt` and each service's documented
request format. That file is unavailable at setup time. Hosts, routes, auth
formats, payloads, and response formats remain unverified; do not infer them
from Assignment 2. Core features must work with class credentials alone. No
paid services for any feature, including optional ones. Never use port 9000.

## Local setup and verification

Prerequisites for this scaffold: Git and Python 3.12+.

```powershell
# Run from this repository's root.
git config --local core.hooksPath .githooks
git config --local core.longpaths true
git config --local jukebox.allowPush false
python scripts/verify_repo.py
```

The verification is offline and uses only Python's standard library. It checks
repository structure, local documentation links, tracked-file safeguards, and
the saved protection policy. It does **not** test jukebox functionality.

Local hooks block commits to `main` after bootstrap, pushes to `main`, and all
pushes until publication is explicitly authorized and locally enabled. Hooks
are a local guard and can be bypassed; only GitHub can enforce branch protection.
The bootstrap commit is on `main`; development starts on `codex/project-setup`.

No app installation or launch command exists yet. Phase 1 must select the stack,
add dependency manifests, and verify setup instructions before implementation.
Never document a placeholder command as a working application entrypoint.

When application configuration is implemented, copy `.env.example` to `.env`
and fill it locally from the class connection details. Names in the example
are a proposed configuration contract, not a verified service client.

## Proposed architecture (team review required)

Browser controls -> server orchestration -> four class service adapters.
Server-managed track IDs associate audio, cover, lyrics, and generation status.
A session library feeds one playback controller that serializes DJ speech and
music. Keep credentials and provider calls server-side. Choose the UI framework
and precise state machine in Phase 1; this proposal is not an implemented app.

## Public repository and submission safeguards

Credentials stay server-side in environment variables or the ignored `.env`.
Do not expose them in browser code, logs, errors, screenshots, docs, GitHub, or
submission archives. Never commit user uploads or voice-reference recordings.
Do not bundle third-party music, lyrics, cover art, or voice samples.

Keep temporary generated media in ignored directories. Only the approved,
class-generated sample audio and covers belong in `assets/samples/`, with
provenance in [assets/samples/README.md](assets/samples/README.md).
Use synthetic fixtures for offline tests. Review all evidence before committing.

Submit the shared public repository URL, exact commit ID, and a GitHub ZIP of
that same version. A teammate must install from the extracted ZIP and verify
all core features using only the README and class credentials. Do not submit
a machine-local build in place of the required GitHub ZIP.

## Evidence and report (pending)

Record inputs, expected and actual behavior, screenshots, all three core
features, and at least one failure case in
[docs/TEST_RESULTS.md](docs/TEST_RESULTS.md). Explain a tested design choice and
an investigated limitation in the finished README. Every teammate must make a
meaningful contribution and review a teammate's work. Current app features and
independent deployment are **untested and unimplemented**.

## Baseline

Adapted from [Assignment 2](https://github.com/JoshuaKosakowsky/Course-Assistant_MBAX6418)
at commit `1a19c33ab9929dd2796ac7a5ea53247602a0cd32`: agent guide, human
contribution workflow, phased plan, README, commit/test guidance, issue and PR
templates, and CI. Assignment 2's RAG requirements, issue numbers, and stale
completion claims were replaced with Assignment 3 requirements.
