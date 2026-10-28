# App contracts v1

Python 3.12 is the default runtime; Python 3.12-3.14 is supported. FastAPI serves
one same-origin HTML/JS frontend with no Node build. Exact direct/transitive
dependencies and artifact hashes live in uv.lock; use the locked launcher in
README. The normal launcher binds only 127.0.0.1 and never generates on startup.

[jukebox/contracts.py](../jukebox/contracts.py) owns app objects. The checked-in
[app.schema.json](../contracts/app.schema.json) is generated from those models:

```powershell
python scripts/dev.py --schema
```

Review changes with consumers before merging. Additive optional fields retain v1;
breaking shapes/states require a coordinated version change. This is an app data
contract, distinct from the verified [provider formats](SERVICE_CONTRACTS.md).

## Shared objects

| Object | Meaning and invariants |
|---|---|
| SongSettings | style, mood, duration_seconds (10-600), instrumental/vocal mode; the range follows documented ACE limits, not exhaustive live verification |
| Track | stable UUID, title/settings, UTC created_at, generating/ready/failed status; ready means audio exists; cover/lyrics/DJ text/speech may still be pending |
| MediaRef | stable asset UUID and matching /api/media/UUID URL, MIME type; never a provider URL, filesystem path or credential |
| GenerationJob | separate app job UUID, track UUID, kind (text/art/music/speech), queued/running/succeeded/failed, progress 0-1, optional SafeError |
| Playback | one phase: idle/speaking/playing/paused; queue of track UUIDs, current index/track, paused_from for resumption |
| SessionSnapshot | contract_version=1, tracks, jobs, playback; IDs are unique and job/queue references must exist in the snapshot |
| SafeError | code, fixed safe message, retryable; never copy raw provider errors/progress to the browser |

Use GenerationJob.transition: queued -> running/failed; running -> succeeded/failed.
Terminal jobs cannot restart and progress cannot go backwards. Success has progress
1; failure requires an error. Retrying creates a new app job after deliberate user
action, not an automatic duplicate provider submission. Provider task IDs are
server-only MusicTicket values and are not app track/job IDs.

Playback's single phase prevents representing speech and music as independently
playing flags. The browser controller in A3-05 must still enforce sequencing,
pause/skip and no overlap; model validation is not a playback test.

Example empty snapshot (the current GET /api/session response):

```json
{"contract_version":1,"tracks":[],"jobs":[],"playback":{"state":"idle","queue":[],"index":0,"current_track_id":null,"paused_from":null}}
```

## Current HTTP surface

| Route | Result |
|---|---|
| GET / | cover form, configuration and session library |
| GET /static/app.js, /static/style.css | same-origin frontend assets only |
| GET /api/health | local process health, contract version; no provider health claim |
| GET /api/status | configured/missing per service; connectivity_checked=false, generation_available=false; additive cover_generation_available based on art settings |
| GET /api/session | this browser's SessionSnapshot, including track-specific art jobs |
| POST /api/tracks | JSON title + SongSettings; create a draft and fresh FLUX cover job, return queued GenerationJob with 202 |
| POST /api/tracks/{track_id}/cover | deliberate generation/replacement/retry for an existing session track; queued GenerationJob with 202 |
| GET /api/media/{media_id} | session-owned bytes with their validated MIME type; missing/foreign assets return 404 |
| GET /api/contracts | unchanged v1 shared JSON Schema |
| GET /api/openapi.json | actual current API specification, including request bodies |

The session dependency issues a random HttpOnly, SameSite=Strict cookie. Do not
put the token in URLs, browser JavaScript, snapshots or logs. Use the same origin
and retain cookies on API requests. Unknown/expired cookies create empty sessions;
missing track/media IDs return 404, duplicate active requests 409 and capacity
limits 429. Missing art configuration returns a safe 502 without creating a draft.

Cover jobs run after the 202 response, using only ClassProviders.cover and the
verified FLUX defaults. Read /api/session while a job is queued/running (the UI
polls once per second); GETs do not resubmit. A terminal failure has SafeError.
Retry creates a new job ID only on user action. Each successful cover gets a
fresh MediaRef; replacing art changes only that track.cover. Existing audio,
status, lyrics, speech, other tracks and playback are preserved. Failed requests
leave prior media intact. Obsolete replaced cover bytes are removed.

## A3-02 integration seam

[SessionStore](../jukebox/sessions.py) is the shared, process-local store, not a
second cover library. The normal app already creates real Track drafts with
generating status and no audio; the UI labels that limit explicitly. Creating a
draft queues fresh art from its title/theme, style and mood. Existing session
tracks can use the same /cover route, regardless of their audio readiness.

A3-02 should extend this store and POST /api/tracks orchestration to attach music
to the existing job.track_id, retaining the automatic art request and track ID.
Do not create a second cookie, library or duplicate cover submission. Use
store.lock for atomic updates, validate the latest Track rather than overwriting
a stale copy, and preserve cover when music completes (cover completion already
preserves audio). Keep ready conditional on actual audio. Extend the existing
media budget/lookup for decoded audio rather than exposing provider URLs. The
cover integration tests exercise ready audio/playback preservation with offline
fixtures; live audio/cover acceptance still waits for A3-02.

Store bounds: 32 sessions, two-hour inactivity expiry (active jobs are retained),
20 tracks/100 jobs per session, two active cover requests app-wide, 64 MB total
retained media. Capacity failures do not enqueue work or orphan new tracks.
The single-process launcher owns this memory; restart clears it. No persistence,
upload, fixtures or alternate generation provider is added to the normal launcher.
Metadata must remain stable while its cover is generating; an editing feature
would need coordinated versioning of those updates.

## Adapter boundary

[ClassProviders](../jukebox/providers.py) is the real server-side client. It uses
the frozen service-probes.json defaults and exposes:

- text(prompt) -> final text only; reject incomplete output and wrong model.
- cover(prompt) -> decoded PNG bytes/MIME; the baseline requests one 512x512 cover.
- speech(text) -> decoded PCM WAV bytes/MIME, default voice omitted.
- submit_music(prompt, duration_seconds=10, lyrics="[Instrumental]") -> MusicTicket.
- poll_music(ticket) -> running or succeeded with a private download path; status
  2 becomes a safe generation_failed error. Success parses the JSON string array,
  matches task ID and verifies XL Turbo. Each invocation performs only one poll.
- download_music(result) -> decoded PCM WAV bytes/MIME. Only the configured music
  origin's /v1/audio?path=... is accepted; redirects and alternate origins are rejected.

Only deliberate cover actions invoke the cover method; startup/refresh invoke none. Offline tests use httpx.MockTransport,
never a provider substituted into the normal app. The earlier probes establish the frozen wire baseline; on 2026-10-27 all four
new production methods also passed a deliberate real-service smoke using those
inputs. See [runtime-adapter-smoke.json](../results/runtime-adapter-smoke.json).
Reference uploads/vocals and higher token limits still need their feature checks.

Each request has bounded time/size (20 MB and 180 seconds read budget), no implicit
retries or redirects, and no environment proxy forwarding. A3-02's orchestration
must impose an overall music-job deadline and retain tickets on ambiguous timeouts.
Cover bytes now map to session-local media IDs in bounded memory; future audio
and uploads must use the same safe boundary and stay out of source archives.

## Configuration and browser boundary

Settings.load reads only the project-root .env (no interpolation) and overlays
environment variables. Missing/example values are unconfigured, not fatal. Invalid
URLs fail with a role-only diagnostic. Only the documented class hostname and
9001/9006/9007/9008 role ports are accepted, with /v1 or origin-only bases. Provider
requests resolve from the origin. Recheck class documentation before changing this
allowlist; no port 9000 or paid-provider fallback exists.

Keys use SecretStr internally and are sent only as server-side Bearer headers.
Public status contains booleans/labels, not keys or URLs. Only the web asset folder
is served; .env, Git, uploads and project files are not web directories. Host
validation, same-origin mutation checks and CSP constrain the local frontend.
This loopback-only development runtime has no deployment authentication and must
not be exposed on a public interface. Configuration status is not connectivity.
