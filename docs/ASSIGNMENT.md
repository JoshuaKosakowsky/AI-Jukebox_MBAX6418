# Assignment 3 requirements and starter prompt

Source: the local three-page `MBAX 6418 Assignment 3.pdf`, read during setup on
2026-10-15 (America/Denver). The PDF stays outside this repository. The starter
prompt below preserves the existing wording; paragraph wrapping is normalized.
Retain all existing language when making the team version. Put additions after it.

## Original starter prompt

```text
# Overarching Task: Build an AI Jukebox
Build an app that (1) generates customizable songs, (2) generates
matching cover art, and (3) plays a song collection with AI-generated
spoken DJ commentary between tracks.

# Required Class Services
- Qwen3.6-35B-A3B on port 9001 for text generation.
- FLUX.2 klein 4B on port 9006 for cover art.
- ACE-Step 1.5 XL Turbo on port 9007 for music.
- Chatterbox Multilingual V3 on port 9008 for DJ speech.
Use the supplied class-endpoints.txt for connection details, or ask our
team if it is unavailable. Follow each service's documented request
format. Use these class services for the required features. You may use
other class endpoints for optional features, but the core app must work
with class services and credentials alone. Do not use paid services for
any app features, including optional features. Do not use port 9000 for
app requests.

# Safeguards
- Keep credentials server-side and out of GitHub, submission archives,
browser code, logs, and documentation. Use placeholders in configuration
examples.
- Never commit user uploads or voice-reference recordings to GitHub or
include them in submission archives.
- Do not bundle third-party music, lyrics, cover art, or voice samples
with the app.
```

## Team additions (setup instructions; product choices still pending)

- Follow AGENTS.md, CONTRIBUTING.md, PLAN.md and handoff.md.
- This session prepares a local repository only; do not build or call services
  until the corresponding task is assigned. Do not push or create a remote.
- Implement the detailed required features and submission checks below when
  building the app. Do not replace the prompt above with this summary.
- Confirm service contracts from the class file; never guess API formats.
- Treat all claimed functionality and test results as unverified until observed.

## Additional requirements from pages 2-3

- Choose song style, mood and duration. ACE-Step audio must be playable and
  added to the library. Support instrumental and vocal songs; generate lyrics
  with AI for vocals.
- Generate a new FLUX cover for each custom song, reflecting its theme, style
  or mood, and display it with the correct track.
- Qwen writes song-specific commentary; Chatterbox speaks between queued
  tracks. Support its default voice and uploaded MP3/WAV reference voices.
- Include three pregenerated, titled sample songs with covers using class
  endpoints; any lyrics must be AI-generated. Bundle the actual audio/images.
- Newly generated songs remain in the playable library during the session.
- Play/pause and skip; automatic queue advancement after playback starts;
  speech and music play sequentially without overlap.
- Show generation status, understandable errors and recovery from failed requests.
- README is the starting point for documentation/report. Include screenshots,
  dependencies/software, endpoint and secure credential configuration, launch
  instructions and how to exercise each core feature.
- Record test inputs, expected behavior and actual results for all three core
  features and at least one failure case. State unresolved and unchecked areas.
- Justify an important design choice using tests. Investigate a limitation or
  failure and discuss what was learned. Team verifies docs against the finished
  app and explains findings in its own words.
- Submit one shared repo URL, commit ID and GitHub-downloaded ZIP of that same
  version. User requires this repository to be public and protected on main.
  Keep it accessible through grading.
- ZIP includes code, dependencies, config examples, docs and generated sample
  audio/images. Exclude credentials, user uploads and voice references.
- A teammate independently installs from the extracted ZIP with only docs and
  class credentials, tests all core features, and resolves undocumented setup,
  missing assets and dependencies on developer-only files.
- Use GitHub issues and PRs for substantial work. Each teammate makes a
  meaningful contribution and reviews a teammate's work.
- Reproducible functionality determines grading; screenshots are supporting
  evidence. Explain sample generation, independent deployment, usability,
  reliability, test evidence and design judgment.
