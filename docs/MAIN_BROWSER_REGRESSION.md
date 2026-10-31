# Isolated main browser regression — 2026-10-31

**27 recorded checks PASS** on integrated main
`25f86179f82cad2f323a81970a27fc76dbdb22ae` (after #27/#29).
Tester: Codex for Joshua, actual in-app browser. Zero class-service calls.
This supports #8 recovery, #5 DJ controls and #3 lyrics recovery; it does not
close those issues or establish normal-launch/live acceptance.

The [safe record](../results/main-browser-regression.json) contains individual
checks, DOM observations, request-counter checkpoints, production POST statuses,
56 media events and source hashes. Actual screenshots show
[paused music](../results/main-browser-paused.png) and the
[recovered library](../results/main-browser-recovered.png).

## Results and team findings

| Browser scenario | Observed result |
|---|---|
| Empty session; create two instrumental drafts | Play disabled until queued; separate cards/media references |
| Start DJ while a manual player runs | Manual players pause; DJ owns playback, including while paused |
| Speech → music → next track | Natural progression and queue completion; at most one playing element in recorded events |
| Pause/resume speech and music | Position stays fixed while paused and advances on resume |
| Skip during music; skip during next speech | Advances to the next introduction, then finishes the queue |
| Reload and repeated cached playback | Cards/queue retained; no additional provider requests |
| Unexpected short model ID in lyrics response | Fixed safe error; synthetic marker absent; no premature vocal submission |
| Explicit lyrics retry | Lyrics and vocal card recover |
| Speech provider failure | Music fallback works; retry control persists through reload without another request |
| Explicit DJ introduction retry | One additional text/speech request; failed state clears |
| Cover, music and resume capacity rejection | Actual HTTP 429s; all three controls restore immediately |
| Cover failure and music polling timeout | Previously playable audio and covers remain unchanged |
| Release capacity, then explicit resume/retry | Resume polls the existing job without a new music submission; only targeted media changes |

No new blocking defect was reproduced in these scenarios. The disabled-control
problem documented in [the earlier recovery audit](RECOVERY_AUDIT.md) no longer
reproduces for the three tested controls on this main. This is additional
browser evidence for the merged correction, not a replacement for that history.
No media/window errors or unhandled rejections were recorded by the observer.

Final **mock** request totals: art 5; music submissions 4, polls 5, downloads 4;
text 6 (2 lyrics, 4 DJ); speech 4. These include deliberately failed requests.
The saved checkpoints distinguish explicit retries from replay/reload.

## Isolation and limits

Production app/routes/store/adapters/frontend ran from a credential-free main
snapshot. Every provider HTTP request used `httpx.MockTransport`; settings came
from explicit synthetic values, ignoring inherited credentials. Media were solid
PNGs, 10-second PCM music and 6-second PCM speech, with browser audio muted by a
test-only observer. No audio quality or human-listening claim is made.

Capacity tests injected two occupied slots in a separate synthetic session to
exercise the real guard. They do not measure real provider concurrency/timing.
An audit-only banner, event observer and fault-control routes existed only in
the manual harness. Production files were not rewritten. All app files matched
main byte-for-byte; of 118 source files, 112 matched exactly and six non-app
files differed only in CRLF/LF endings (listed in the record). No `.env` existed
in the snapshot. The loopback server was stopped and port 8175 verified closed.
Some exported DOM status punctuation has encoding artifacts; screenshots retain
the rendered UI. Behavioral checks use state, counters and stable labels.

PR #26 and its reference upload/chooser were not tested or changed. No sample
was approved and no release ZIP was tested. Existing live-vocal failure evidence
remains valid until a successful real rerun. #35 genre work stays separate;
#36 cover lettering remains unclaimed by Joshua. Ownership is unchanged.

## Reproduce manually, without class calls

Use the repo's locked Python environment. Extract a source snapshot without
copying `.env`; the helper refuses a source root containing that file:

```powershell
git archive --format=zip --output="$env:TEMP/a3-browser-source.zip" 25f86179f82cad2f323a81970a27fc76dbdb22ae
Expand-Archive "$env:TEMP/a3-browser-source.zip" "$env:TEMP/a3-browser-source-25f8617"
uv run --locked python scripts/audit_main_browser.py --source "$env:TEMP/a3-browser-source-25f8617" --port 8175
```

Open `http://127.0.0.1:8175/` in a fresh browser session. Create two 10-second
instrumental drafts, queue them, and exercise the controls above. Create a vocal
draft with `bad_model` enabled, then clear it and use Retry lyrics. Queue it with
`speech_fail` enabled to check fallback, then clear it and retry explicitly.
Inject cover failure/poll timeout for replacement jobs and verify original media
remain; clear faults and explicitly recover. Control examples (separate terminal):

```powershell
Invoke-RestMethod http://127.0.0.1:8175/audit/control -Method Post -ContentType application/json -Body '{"bad_model":true}'
# Other boolean fault keys: art_fail, speech_fail, poll_fail. Clear with false.
Invoke-RestMethod http://127.0.0.1:8175/audit/capacity/music/hold -Method Post
# Attempt the relevant music/resume action; expect 429 and an enabled control.
Invoke-RestMethod http://127.0.0.1:8175/audit/capacity/music/release -Method Post
# Repeat capacity hold/release with art for the cover action.
Invoke-RestMethod http://127.0.0.1:8175/audit/evidence
```

The helper is manual only: it does not drive the browser, assert the complete
matrix, or run in CI/startup. Capture observations/counters for any new run;
this report describes the recorded run above. Stop with Ctrl+C when finished.
