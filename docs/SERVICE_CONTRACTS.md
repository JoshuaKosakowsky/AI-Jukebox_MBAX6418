# Verified class-service contracts

Contract v1, observed 2026-10-17 13:29 MDT (19:29 UTC), under A3-01 / issue #1.
One real generation submission per service succeeded, followed by full image
or audio decoding. These are the tested request subsets for adapters to start
from. They do not establish full API compatibility or completed app features.

Use [service-probes.json](../contracts/service-probes.json) for exact, reusable
JSON requests, absolute routes and observed response fields. Safe measurements
are in [service-contract-probes.json](../results/service-contract-probes.json);
expected versus actual and limitations are in [TEST_RESULTS.md](TEST_RESULTS.md).
Integrate changes through reviewed PRs under CONTRIBUTING. Coordinate shared
contract changes with affected consumers; team workflow is active.
Require new live evidence for a changed request format, model or response shape;
do not repeat generation merely because an agent/model changes.

## Connection and documentation

The local class-endpoints.txt was found in the course Misc directory, dated
2026-09-09. It predates music/speech and was insufficient for their request
schemas. The existing ignored .env provided the four service base URLs and keys.
All four authenticated /v1/models calls confirmed the required models. We then
read each deployed origin's /openapi.json before submitting the probes. Raw
discovery, responses and generated media remain ignored under generated/contracts/.
No port 9000 calls, paid services or reference recordings were used.

Configure JUKEBOX_{TEXT,ART,MUSIC,SPEECH}_ENDPOINT and corresponding _API_KEY
server-side as shown in [.env.example](../.env.example). Send Bearer auth and
Content-Type: application/json for JSON POSTs. Contract paths start at the
service origin: an endpoint ending /v1 still uses /release_task for ACE-Step.
Never append /v1 twice. Preserve each service's own port and credentials.

The deployed schemas are authoritative for that deployment. Fingerprints in
the JSON identify the locally saved, pretty-printed OpenAPI snapshots, not raw
HTTP bytes. ACE-Step's deployed OpenAPI did not define its JSON request body;
the matching [official API documentation](https://github.com/ace-step/ACE-Step-1.5/blob/ca1e85fe9430179831e6bc6be790c332190a3866/docs/en/API.md)
and [request model source](https://github.com/ace-step/ACE-Step-1.5/blob/ca1e85fe9430179831e6bc6be790c332190a3866/acestep/api/http/release_task_models.py)
filled that gap, and the actual generation verified this subset. Do not assume
every upstream option is available on the class server.

## Text: Qwen, port 9001

POST /v1/chat/completions with the exact model ID
cyankiwi/Qwen3.6-35B-A3B-AWQ-4bit, messages, max_completion_tokens=192,
temperature=0 and stream=false. The canonical request asks for CONTRACT_OK.
Read choices[0].message.content as text; the probe returned exactly that marker
and finish_reason=stop. Ignore unknown extra response fields. Do not depend on
reasoning fields or expose them. JSON-mode lyrics, structured output and DJ
prompt behavior have not been tested; this call does not verify those formats.

## Covers: FLUX, port 9006

POST /v1/images/generations with model black-forest-labs/FLUX.2-klein-4B,
prompt, n=1, size=512x512, num_inference_steps=4, response_format=b64_json,
output_format=png. Decode data[0].b64_json as base64, then decode the entire
image; a header or HTTP 200 alone is insufficient. The probe produced a complete
512x512 RGB PNG. Other sizes, formats, art quality and track pairing are unchecked.

## Music: ACE-Step, port 9007

1. POST /release_task with the frozen request: prompt, lyrics=[Instrumental],
   audio_duration=10, batch_size=1, inference_steps=8, audio_format=wav,
   thinking=false, use_cot_caption=false, use_cot_language=false, bpm=80,
   key_scale=C Major and time_signature="4". batch_size=1 avoids the documented
   default of two outputs. Omitting model selects the server's default; the
   completed result confirmed dit_model=acestep-v15-xl-turbo.
2. Check the HTTP response and wrapper code/error, then retain data.task_id.
   Submission success means queued work, not finished audio. Poll POST
   /query_result with {"task_id_list":["<the same task ID>"]}.
3. The documented statuses are 0 pending, 1 succeeded, 2 failed. Only status 1
   was observed live. Check wrapper errors, locate the matching task ID and
   handle failure/unknown/malformed states explicitly rather than waiting forever.
4. On success, data[0].result is a **JSON-encoded string containing an array**,
   not an audio object. Decode that string, require the expected single output,
   and read its file field. The probe's decoded item contained file, status,
   metas, dit_model, progress and stage, among additional fields.
5. GET the returned /v1/audio?path=... on the **same music service origin** with
   its Bearer header. Preserve the opaque encoded query; do not open a server
   filesystem path locally or assume it is a public browser URL. Reject other
   origins/routes and redirects before sending credentials. Fully decode the WAV.

The probe polled the same job once after three seconds, with a four-minute poll
deadline and no resubmission. Use bounded requests, capped response sizes and an
overall job deadline in adapters; keep task IDs for deliberate recovery. A timeout
does not prove submission failed: avoid automatically submitting duplicate jobs.
Do not show raw result/progress_text/errors to users; they can reveal server paths.

The ten-second output decoded as non-silent, 48 kHz stereo, 16-bit PCM WAV.
Duration range 10-600 seconds is documented upstream, not exhaustively verified
here. Vocals, AI lyrics, user-selected settings and musical quality remain feature
checks. Do not invent an OpenAI /v1/audio/generations request for this deployment.

### Production genre conditioning (#35)

The frozen probe above describes one slow piano example. Production music
requests omit its `bpm`, `key_scale` and `time_signature` fields so every style
is not forced to 80 BPM, C Major and 4/4. The requested duration, supplied lyrics,
single-output batch, WAV format, eight steps and existing thinking/CoT flags stay
unchanged. Both instrumental and vocal prompts explicitly request a groove,
tempo, rhythm and instrumentation characteristic of the selected style/mood.

The [matching request model](https://github.com/ace-step/ACE-Step-1.5/blob/ca1e85fe9430179831e6bc6be790c332190a3866/acestep/api/http/release_task_models.py)
defaults BPM to null and key/meter to empty. The
[API documentation](https://ace-step.github.io/ACE-Step-1.5/en/API#_4-create-generation-task)
explains that missing metadata may be inferred by the music service's own 5Hz
LM even with `thinking=false`; supplied duration still takes precedence. This
can add planning latency within the existing music task, not a separate Qwen
request. No model switch, extra submission or automatic retry is introduced.

On 2026-10-30 the deployed `/openapi.json` still omitted the release-task JSON
body; its raw SHA-256 was `232eda8eba8b7f1d574a0ccc2c5a9db8023ba27347b64ec60356361bbadb3bf9`.
A read-only `/health` check reported `llm_initialized=true`. These are discovery
observations, not generation/quality acceptance. The original probe fixture
remains unchanged. Actual request compatibility and human genre/rhythm quality
need the separately recorded bounded comparison; offline tests alone cannot
establish better sounding music.

## Speech: Chatterbox V3, port 9008

POST /v1/audio/speech with model=chatterbox-v3, input="Welcome to the jukebox."
and response_format=wav. **Omit voice for default speech**; no upload is required.
The response is a complete binary WAV, not JSON, base64 or an SSE stream. It fully
decoded as non-silent, 24 kHz mono, 16-bit PCM, 1.76 seconds for this text. These
sample rate/channel/duration values are observations, not hard-coded guarantees.
The deployed schema explicitly says SSE/native incremental streaming is unavailable.
Do not build the DJ queue around token/audio streaming from this endpoint.

Reference voice paths below are **schema-inspected only; not live verified**:

- POST /v1/audio/speech/upload is multipart with a file field and a request field
  containing the speech JSON string. Its schema requires both; omit saved voice
  and ref_audio when supplying the uploaded reference file.
- The JSON speech schema also accepts ref_audio as base64/data URI, not a local
  path or remote URL. Saved voice IDs use {"id":"..."}; do not guess voice names.
- POST /v1/voices can save a named reference using multipart name and file;
  persistence is unnecessary for temporary assignment uploads. Keep references
  out of Git and archives and define cleanup in A3-06.

The schema documents MP3/WAV support (and others), reference length 1-60 seconds
by default, input length 1-4096, response formats mp3/wav/opus/aac/flac/pcm,
and speed 0.25-4. Do not turn documented limits into verified app behavior.
Both required MP3 and WAV reference flows still need real feature acceptance.

## Using this baseline

Load each services.<role>.request object from the canonical JSON to reproduce
the probe deliberately, using local server-side credentials. Each POST creates
work; it must be opt-in, never a startup/CI/offline-test action. For music, follow
the submit/poll/download steps above. The original probe harness used Python
urllib with redirects disabled, a 20 MB response cap, up to 180-second initial
requests, and full PCM/image decoding. Do not print keys or raw provider failures.
Review any newly collected evidence before committing it.

This document freezes provider wire formats. The A3-01 runtime, shared objects
and adapter boundary are described in [APP_CONTRACTS.md](APP_CONTRACTS.md), with
startup and offline evidence in TEST_RESULTS.md. Review/merge that foundation
before dependent integration, then demonstrate one real instrumental flow. App and release readiness remain
NOT READY; no probe output counts as one of the three approved sample tracks.
