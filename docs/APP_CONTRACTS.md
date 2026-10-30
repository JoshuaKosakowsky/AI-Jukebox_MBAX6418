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
| Track | stable UUID, title/settings, UTC created_at, generating/ready/failed status; ready means actual audio exists (set only when the instrumental attaches); cover/lyrics/DJ text/speech may still be pending |
| MediaRef | stable asset UUID and matching /api/media/UUID URL, MIME type; never a provider URL, filesystem path or credential |
| GenerationJob | separate app job UUID, track UUID, kind (text/art/music/speech), queued/running/succeeded/failed, progress 0-1 (advanceable inline via with_progress while running), optional SafeError |
| Playback | one phase: idle/speaking/playing/paused; queue of track UUIDs, current index/track, paused_from for resumption |
| SessionSnapshot | contract_version=1, tracks, jobs, playback; track/job IDs and all media-reference IDs are unique; job/queue references must exist in the snapshot |
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
| GET /api/status | configured/missing per service; connectivity_checked=false, generation_available=false; additive cover_generation_available, music_generation_available and lyrics_generation_available based on configured services |
| GET /api/session | this browser's SessionSnapshot, including track-specific art/music jobs |
| POST /api/tracks | JSON title + SongSettings; create a draft and fresh FLUX cover job, return queued GenerationJob with 202 |
| POST /api/tracks/{track_id}/cover | deliberate generation/replacement/retry for an existing session track; queued GenerationJob with 202 |
| POST /api/tracks/{track_id}/music | deliberate instrumental or vocal-music generation/replacement/retry for an existing session track; vocal tracks submit the track's current lyrics with the same verified request and are rejected with 409 while lyrics are missing; queued GenerationJob with 202 |
| POST /api/tracks/{track_id}/lyrics | deliberate Qwen lyrics generation/replacement/retry for a vocal session track (422 for instrumental tracks); attaches the text to the track on success; queued GenerationJob with 202 |
| POST /api/tracks/{track_id}/music/resume?from={job_id} | continue polling/downloading the SAME retained class-service task of a failed music job; never submits a new task; queued GenerationJob with 202 |
| GET /api/media/{media_id} | session-owned bytes with their validated MIME type; missing/foreign assets return 404 |
| GET /api/contracts | unchanged v1 shared JSON Schema |
| GET /api/openapi.json | actual current API specification, including request bodies |

The session dependency issues a random HttpOnly, SameSite=Strict cookie. Do not
put the token in URLs, browser JavaScript, snapshots or logs. Use the same origin
and retain cookies on API requests. Unknown/expired cookies create empty sessions;
missing track/media IDs return 404, duplicate active requests 409 and capacity
limits 429. Missing art configuration returns a safe 502 without creating a draft.

Cover jobs run after the 202 response, using only ClassProviders.cover and the
verified FLUX defaults. Music jobs run the same way through the verified
submit -> poll -> download ACE-Step flow. Read /api/session while a job is
queued/running (the UI polls once per second); GETs do not resubmit. A terminal
failure has SafeError. Retry creates a new job ID only on user action. Each
successful cover or instrumental gets a fresh MediaRef; replacing art or audio
changes only that field of that track. Existing audio, status, lyrics, speech,
other tracks and playback are preserved. Failed requests leave prior media
intact; obsolete replaced media bytes are removed on success. A track may have
an art job and a music job active at the same time; whichever completes last
re-reads the latest track and cannot overwrite the other's media.

Music orchestration: one ACE-Step task is submitted per job (lyrics fixed to
the instrumental marker). The returned provider task ID lives only in
server-private session tickets, never in snapshots, the browser or logs.
Polling reuses that ticket with a 3-second interval and a 300-second overall
deadline; an expired job fails retryable with a safe message that tells the
user to check the class queue before retrying. A failed retryable music job
keeps its ticket so a Resume check (POST /api/tracks/{id}/music/resume) can
continue polling/downloading the SAME task without any new submission; the
ticket is associated with each resumed job, so a second failed attempt is
itself resumable (any number of resumes stay on the one original submission).
A resume whose URL names the wrong track is rejected 404 with no side effects:
no job is created, no capacity consumed, and the rightful track remains
resumable. Only jobs with a retained ticket are resumable, and a submission
that was never confirmed returns 409 with guidance instead. When the class
service reports the task itself failed during a resume, the job becomes
terminal (not retryable) — Generate new instrumental is the explicit path to a
brand-new task, and no failed or terminal job ever misleadingly offers endless
resumability. Generating new instrumental is
the explicit path to a brand-new task. Poll/download failures never
auto-submit a second task; manual retry is a new app job and, after an
uncertain submission, a newly user-approved task. Instrumental durations are
operationally limited to 10-60 seconds (the class server's 20 MB response cap
bounds a 48 kHz/16-bit/stereo WAV at roughly 104 seconds; 60 seconds keeps
margin); the shared SongSettings schema keeps its documented 10-600 range,
and the narrower app bound is enforced before any provider work. The app-wide
media budget (64 MB) is checked before attaching each result.

Progress stages are truthful: submitting (up to 0.3), generating while polling
(capped at 0.79, so the UI never claims downloading during polling), downloading
(0.9, set only after the poll succeeds), succeeded (1). The frontend rebuilds
track cards individually when a track's own data changes and carries an
in-progress playback position across a rebuild, so generating one song never
interrupts playback of another.

## Music and cover orchestration (A3-02)

[SessionStore](../jukebox/sessions.py) is the single shared, process-local store.
A draft created through /api/tracks immediately queues fresh art from its
title/theme, style and mood; the browser then requests the instrumental through
/tracks/{id}/music using the same track ID, cookie and store. Do not create a
second cookie, library or duplicate cover submission. Per-kind active entries
(track id, kind) let art and music run concurrently on the same track: 409 is
returned only for a duplicate of the same kind. All updates run under
store.lock and re-read the latest Track before attaching a result, so whichever
job finishes last preserves the other's media (tests cover both completion
orders). Track status becomes ready only when audio is attached; a music
failure leaves the prior status, cover and audio untouched and is reported
through the job's SafeError. Provider tickets and media bytes stay server-side.

## Vocal songs and lyrics (A3-03)

Vocal tracks use the same store/route pattern: /api/tracks accepts
`settings.mode: "vocal"` and still queues the automatic cover; the browser then
calls /tracks/{id}/lyrics, which queues one Qwen text job. On success the text
attaches to `track.lyrics` (replacement generations replace it; a failed job
leaves the previous lyrics/audio/cover untouched and is retryable). The vocal
music request is the SAME verified ACE-Step payload with the track's current
lyrics in the lyrics field and a vocal-aware prompt; `queue_music` rejects a
vocal track that still has no lyrics (409) and `generate_music` re-checks at
submission time so a job can never silently fall back to the instrumental
marker. One text job may run app-wide (MAX_ACTIVE_TEXT=1); art/music/text jobs
for one track coexist. The lyrics token budget is raised to 512 for this call
only (the 192-token probe budget was for a short reply marker); this deviation
requires live A3-03 acceptance evidence, which is still pending (no class keys
on the development machine).

Store bounds: 32 sessions, two-hour inactivity expiry (active jobs are retained),
20 tracks/100 jobs per session, two active covers, two active music and one
active text (lyrics) job app-wide, 64 MB total retained media. Capacity failures
do not enqueue work or orphan new tracks.
The single-process launcher owns this memory; restart clears it. No persistence,
upload, fixtures or alternate generation provider is added to the normal launcher.
Metadata must remain stable while a job is generating; an editing feature
would need coordinated versioning of those updates.

## Adapter boundary

[ClassProviders](../jukebox/providers.py) is the real server-side client. It uses
the frozen service-probes.json defaults and exposes:

- text(prompt) -> final text only; reject incomplete output and wrong model.
- lyrics(prompt) -> song lyrics; the same chat endpoint/model with a 512-token
  budget for 10-60 second songs (documented deviation from the 192-token probe).
- cover(prompt) -> decoded PNG bytes/MIME; the baseline requests one 512x512 cover.
- speech(text) -> decoded PCM WAV bytes/MIME, default voice omitted.
- submit_music(prompt, duration_seconds=10, lyrics="[Instrumental]") -> MusicTicket.
- poll_music(ticket) -> running or succeeded with a private download path; status
  2 becomes a safe generation_failed error. Success parses the JSON string array,
  matches task ID and verifies XL Turbo. Each invocation performs only one poll.
- download_music(result) -> decoded PCM WAV bytes/MIME. Only the configured music
  origin's /v1/audio?path=... is accepted; redirects and alternate origins are rejected.

Only deliberate cover and music actions invoke the adapters; startup/refresh
invoke none. Offline tests use httpx.MockTransport,
never a provider substituted into the normal app. The earlier probes establish the frozen wire baseline; on 2026-10-27 all four
new production methods also passed a deliberate real-service smoke using those
inputs. See [runtime-adapter-smoke.json](../results/runtime-adapter-smoke.json).
Reference uploads/vocals and higher token limits still need their feature checks.
The current public MIME types reflect PNG covers and WAV/MP3 browser assets;
speech generation explicitly requests WAV. Additional documented service formats
are not promised by this client. A3-05/06 must coordinate additive MIME/decoder
support with actual responses if another output format is needed.

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
