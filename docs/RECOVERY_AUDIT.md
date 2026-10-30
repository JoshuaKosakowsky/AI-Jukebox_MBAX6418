# Instrumental failure and recovery audit

2026-10-29 America/Denver; JoshuaKosakowsky directing Codex. Support for
[A3-08 / #8](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/8),
whose lead remains prse4479. Tested main `7b9dd2b2702d7280a231cdcbfbd1afad136f3f56`.
Application files, contracts, service configuration and assignments were untouched.

## Confirmed finding: retry stays disabled after temporary capacity rejection

**P2, required failure/recovery behavior.** With both music slots occupied,
a track's Generate instrumental request returns HTTP 429 and the safe message
"Music generation is busy. Try again shortly." The track's button stays disabled
after the other jobs finish and after Refresh status succeeds. The API itself
accepts a retry once capacity frees. A full page reload restores the control;
an explicit retry then succeeds without losing the existing tracks/covers.

Reproduction using the offline harness below:

1. Hold two music jobs pending; create `OFFLINE busy A` and `OFFLINE busy B`
   through the normal form (style Fixture, mood Audit, duration 10 seconds).
2. Create `OFFLINE retry target`. Its cover succeeds; its automatic music
   request is rejected 429. Click that card's Generate instrumental once while busy.
3. Release the held jobs. A and B become ready; click Refresh status.
4. Observe the target still has no instrumental and its Generate instrumental
   is disabled. Expected: retry becomes usable once no job is active for it.
5. Reload the page: the button is enabled. Click it; the target becomes ready.

Rejected requests and status refresh did not cause extra submissions:
only A/B were submitted before reload, and the explicit target retry was the
third submission. The button disabled state is captured in the
[actual offline browser screenshot](../results/a3-08-capacity-disabled.jpg) and
[structured observations](../results/a3-08-recovery-audit.json).

Likely cause, checked against the tested source: `jukebox/web/app.js` disables
retryMusic before POST (line 126). A rejected request adds no job, so the next
snapshot is unchanged; renderLibrary skips that cached card (line 148).
syncAfterMutation refreshes the snapshot but does not reset that button.

**Suggested focused fix for prse4479:** restore the affected control after a
rejected POST, or invalidate only that card before the refresh. Preserve existing
audio nodes and keep real active jobs disabled; do not clear the whole library
cache. Add a browser regression for 429 -> capacity freed -> Refresh status ->
retry enabled, with no automatic submission. Inspect the cover/resume handlers
for the same pattern; those capacity-rejection variants were not reproduced here.
Coordinate `app.js` edits with Mike's vocal [PR #21](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/21).
No fix to shared application code was made during this audit.

Related review update: Mike fixed the new lyrics-control instance in PR #21
at `04650a5`; independent 128-test and offline browser verification passed,
and the [correction was approved](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/21#pullrequestreview-5707544155).
This does not change the instrumental finding above on main 7b9dd2b; its fix
still belongs to #8. [Corrected lyrics control](../results/pr21-lyrics-retry-enabled.jpg).

## Passing checks

Seven offline backend probe groups passed through real app routes, SessionStore
and the production ClassProviders parsers with httpx.MockTransport:

| Fault/check | Observed result |
|---|---|
| Two consecutive polling timeouts, then resume | One original submission; third poll succeeds; ticket/active state cleaned |
| Download timeout, then resume | Same submission; download retries once; state cleaned |
| Submission times out before ticket confirmation | Resume rejected 409 with no new job/submission; deliberate new request succeeds |
| Invalid replacement audio and cover HTTP 503 | Existing track/media preserved; explicit cover retry succeeds with original audio |
| Foreign-origin audio download path | Rejected before any download request |
| Music capacity full, then freed | Rejection 429 has no snapshot side effects; subsequent API retry succeeds |
| Foreign session, cross-origin POST, private-file paths | Foreign resume/media 404, cross-origin mutation 403, private files 404 |

The real browser also showed safe HTTP-503 cover failure and successful Retry
cover, preserving both old media references during failure and the audio through
recovery ([screenshot](../results/a3-08-cover-failure.jpg)). A polling timeout
kept existing audio/art, displayed Resume check, and recovered with zero new
submissions from the resume action. Its combined explicit new request + resume
used one submission, two polls and one download. No console errors were observed.

## Reproduce without class-service calls

These are **manual exploratory probes**, not CI tests or the normal launcher.
They deliberately inject faults and synthetic PNG/WAV fixtures. The helper adds
an audit-only counter route on loopback; none of this is wired into the app.
Use a checkout of this report branch and the locked dependency environment.
For Windows, keep that environment outside the long OneDrive path:

```powershell
$env:UV_PROJECT_ENVIRONMENT = Join-Path $env:LOCALAPPDATA 'AI-Jukebox_MBAX6418-audit'
$env:UV_LINK_MODE = 'copy'
uv run --locked python scripts/audit_recovery_probes.py .
New-Item -ItemType Directory -Force results/raw | Out-Null
Set-Content results/raw/a3-08-control.json '{"mode":"capacity","release":false}'
uv run --locked python scripts/audit_fault_harness.py --source . --control results/raw/a3-08-control.json --port 8168
```

Open http://127.0.0.1:8168 and follow steps 1-3 above. In a second terminal,
release the held jobs with:

```powershell
Set-Content results/raw/a3-08-control.json '{"mode":"success"}'
```

The backend probe defaults its safe output to ignored results/raw; an optional
second positional argument chooses another output path. No `.env` is read:
Settings.load receives explicit synthetic settings, and every provider request
uses MockTransport. The harness poll interval is shortened from 3 seconds to
0.1 seconds; its timings/poll totals are not provider-performance evidence.
Stop the harness with Ctrl+C when done. A later code revision must be re-tested;
the result JSON's reference base identifies this audit's baseline, not a claim
that future runs used that same version.

## Limits and handoff

All 65 source files in the isolated snapshot remained byte-identical to the
GitHub ZIP; no real class keys, requests, generated songs or voice references were
used. Screenshots show the actual app UI with explicitly offline fixtures; no
listening or music-quality assessment was performed.

This is partial evidence for AT-10/AT-12, not normal-launch/live acceptance.
#8 stays open: prse4479 still needs the shared-frontend correction, relevant
regressions, and a normal-launch failure/recovery record as the remaining vocal,
DJ and reference features integrate. Full submission remains NOT READY.

## Cover-retry and resume variants on main e2b1e52 (2026-10-29)

Both previously unchecked variants reproduce the same P2 disabled-control problem.
The real browser/app/adapters ran against an isolated 71-file main snapshot,
byte-identical before/after. Only MockTransport/synthetic PNG/WAV were used;
no .env, class calls, new songs or app changes. This is offline evidence, not
normal-launch/live acceptance. [Record](../results/a3-08-retry-variants.json).

The manual harness seeds three tracks: two blockers and one failed target. It
reserves two real queue slots without scheduling blockers, making the production
capacity guard reject the target action. This is deterministic slot injection,
not a claim about provider timing/concurrency. The audit-only release runs the
two queued blockers; the target snapshot remains unchanged.

| Target action | Initially enabled | After busy rejection | After release + Refresh | After reload |
|---|---|---|---|---|
| Retry cover (earlier cover-503 failure) | Yes | Disabled | Still disabled | Enabled |
| Resume check (earlier polling timeout) | Yes | Disabled | Still disabled | Enabled |

Expected: rejected actions restore their control, and a deliberate retry is
possible without reload once capacity is available. Actual: each handler sets
its button disabled, but its catch does not restore it; unchanged target data
makes renderLibrary skip rebuilding the card. Mike's merged lyrics retry catch
already restores its control; cover, resume and instrumental still need the
corresponding correction. Preserve active-job guards/audio nodes; never auto-submit.

Workaround verified: reload, then explicitly use the same control. Cover request
counts: 4 before release, 6 after two blockers complete, 7 only after the explicit
retry. Resume submissions: 1 before release, 3 after the two blockers run, still
3 after explicit resume; target audio download succeeds, all active slots clear.
Refresh/rejection did not introduce an extra provider operation. The busy-message
branch maps to HTTP 429 in production code; browser tooling did not separately
retain the response status. Actual screenshots:
[cover retry](../results/cover-retry-disabled.png), [resume](../results/resume-retry-disabled.png).

Reproduce from this branch with the locked environment (manual; not CI):

```powershell
uv run --locked python scripts/audit_retry_variants.py --source . --case cover --port 8171
# Separate terminal/browser: open http://127.0.0.1:8171/audit/enter
# On OFFLINE target click Retry cover; the busy notice appears and control disables.
Invoke-RestMethod http://127.0.0.1:8171/audit/release -Method Post
# Refresh status: target control remains disabled. Reload, then retry explicitly.
# Read /audit/state for safe counters; stop harness with Ctrl+C.
# Repeat with --case resume --port 8172 and target Resume check.
```

Helper routes exist only in this standalone audit harness, never production.
Prse retains #8; coordinate a focused app.js correction/regressions with Matt's
#5 frontend work. No issue is closed by this evidence.
