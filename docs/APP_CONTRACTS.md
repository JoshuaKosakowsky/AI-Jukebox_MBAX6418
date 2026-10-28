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

| GET route | Result |
|---|---|
| / | startup page and empty library |
| /static/app.js, /static/style.css | same-origin frontend assets only |
| /api/health | local process health, contract version; no provider health claim |
| /api/status | configured/missing per service, configured boolean, connectivity_checked=false, generation_available=false; no configuration values |
| /api/session | fresh empty SessionSnapshot; writable session storage arrives with A3-02 |
| /api/contracts | shared JSON Schema |
| /api/openapi.json | actual current API specification |

No generation, upload, playback-control or media-serving routes exist yet.
MediaRef's route prefix is reserved for A3-02's asset store; it returns 404 today.
The normal launcher has no fixture provider or fake tracks. A3-02 adds production
orchestration, per-browser session storage and the first playable instrumental.

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

No method is invoked by the startup shell. Offline tests use httpx.MockTransport,
never a provider substituted into the normal app. The earlier probes establish the frozen wire baseline; on 2026-10-27 all four
new production methods also passed a deliberate real-service smoke using those
inputs. See [runtime-adapter-smoke.json](../results/runtime-adapter-smoke.json).
Reference uploads/vocals and higher token limits still need their feature checks.

Each request has bounded time/size (20 MB and 180 seconds read budget), no implicit
retries or redirects, and no environment proxy forwarding. A3-02's orchestration
must impose an overall music-job deadline and retain tickets on ambiguous timeouts.
Bytes live only in the caller's memory; future storage must map them to local media
IDs and keep temporary outputs/uploads out of source archives.

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
