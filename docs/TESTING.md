# Verification and submission readiness

## Fast checks (offline)

```powershell
python scripts/dev.py --check
```

This uses uv.lock and runs the following in its isolated environment:

```powershell
uv run --locked python scripts/verify_repo.py
uv run --locked python scripts/check_readiness.py
uv run --locked python -m unittest discover -s tests -p 'test_*.py'
```

On Windows, prefer scripts/dev.py: it selects a short environment path, avoiding
native-extension import failures in long course folders. See README for setup.
The suite covers the release gate, Git guards, app contracts/configuration,
provider success/error parsing, session-scoped cover and music jobs, media,
failure/retry and concurrency, and an actual child-process startup over loopback.
It never calls class services. Dependency installation needs initial internet
access; already-synced tests do not. CI tests 3.12 Windows/Linux and 3.14 Linux;
the aggregate required context stays test and fails if any matrix run fails.

When Node is available, default test discovery also executes the actual cover,
music and resume click handlers in a small dependency-free JavaScript harness.
It checks rejected-request recovery, explicit retries, unchanged audio nodes,
configuration guards and no automatic submissions. Without Node that optional
check is explicitly skipped; Node is not an application dependency. Browser
verification remains separate from this minimal DOM simulation.

Use focused behavior/failure tests for logic and contract/normal-launch checks for
wiring. Include new tests in the default discovery command. Media fixtures must
fully decode, not merely have headers. Offline fixture results never count as
live feature acceptance; browser playback, reference voices and the independent
ZIP still require their specific cases. Rerun passing checks for relevant changes
or open risk rather than generating media repeatedly.

## Credentials and live acceptance

A “.env-backed live rerun” means verifying the assigned workflow against the real
class services using private server configuration. A literal `.env` file is not
an A3-03 / AT-04 acceptance requirement. This app supports the repo-root `.env`
and inherited environment variables; it does not fetch a secrets manager itself.
An external secret tool works only if it supplies the supported variables to the
same app process. Existing valid configuration can be used without creating a
second credential file or asking for the keys again.

### Check configuration without making provider requests

Work in the intended A3 checkout/extraction, containing `jukebox/`,
`pyproject.toml` and `scripts/dev.py`. Identify its branch/commit where Git is
available. The chat's working folder or a different Assignment folder may not
be that checkout. Each clone/worktree has its own ignored files: Git pull does
not transfer `.env`, and a private file on one teammate's machine does not
configure another machine.

`jukebox/config.py` loads `.env` relative to the application source root, not
the terminal's current directory. It then overlays the process environment;
environment values win, including empty/example values that mask a valid file.
The supported names are:

| Role | Endpoint variable | Key variable |
|---|---|---|
| Text / lyrics | `JUKEBOX_TEXT_ENDPOINT` | `JUKEBOX_TEXT_API_KEY` |
| Cover art | `JUKEBOX_ART_ENDPOINT` | `JUKEBOX_ART_API_KEY` |
| Music | `JUKEBOX_MUSIC_ENDPOINT` | `JUKEBOX_MUSIC_API_KEY` |
| DJ speech | `JUKEBOX_SPEECH_ENDPOINT` | `JUKEBOX_SPEECH_API_KEY` |

From that source folder, this prints only the app root, file-existence boolean
and configured/missing role labels; it makes no provider calls:

```powershell
python -m uv run --locked python -c "from jukebox.config import ROOT, Settings; print('App root:', ROOT); print('Root .env exists:', (ROOT / '.env').is_file()); print(Settings.load().public_status())"
```

If uv was installed as a standalone executable, use `uv run --locked` instead
of `python -m uv run --locked`. Do not replace the safe status call with an
environment dump, `.env` contents, keys, auth headers or raw configuration objects.
`Settings.load(None, {})` deliberately means no file and no inherited variables;
it is an offline-test fixture, not a check of the real application's credentials.

Also inspect the **running** app's Service setup or `/api/status` at its actual
local port. The CLI above describes a new process; an already running server
may have started from another checkout or terminal environment. Use the normal
`python scripts/dev.py --port 8000` launcher in the intended checkout. After
configuration/code changes, restart the intended server; Refresh status does
not reload settings. Restart clears generated session data, so preserve any
needed evidence first. A parent terminal's variables do not automatically reach
an agent or server process that was started elsewhere or earlier.

For missing roles, reuse the authorized existing local private configuration,
or obtain the class settings through the approved private class/team channel.
Copy `.env.example` only when `.env` is absent; never overwrite valid settings.
Check inherited placeholders and the documented endpoint/port allowlist before
concluding that the key is missing. A diagnostic harness may explicitly load
an existing private file with `Settings.load(path)`; that harness alone is not
normal-launch/browser acceptance. Do not invent an unsupported launcher flag.

### Configured is different from verified

- `services` and the role-specific availability flags mean settings were loaded,
  not that authentication, connectivity or generation succeeded. Startup and
  Refresh status do not call providers. The aggregate `configured` requires all
  four roles; legacy `generation_available=false` is not the per-feature gate.
- A3-03's normal vocal-create flow needs **text, art and music**. Missing DJ speech
  settings alone do not block that flow. DJ testing separately needs text/speech
  and playable tracks. Bundled sample playback needs no provider credentials.
- A models-list HTTP 200, an open UI, offline/MockTransport tests, CI success or
  a standalone adapter call does not establish a completed live browser feature.
- Read existing evidence in the **same browser session** before submitting again.
  A fresh HTTP client or another browser profile has a different library; its
  empty `/api/session` response does not show that the original run made no calls.
  Do not print or post session cookies to investigate that difference.

### Complete the assigned A3-03 check

First check the current issue/PR findings and existing run evidence. Available
credentials do not resolve a parser defect or turn a failed run into a pass.
Coordinate one tester, exact checkout/head, inputs and finite request budget in
#3; other agents may check their configuration without all starting new runs.
Use the already authorized task scope; this terminology is not an extra file or
approval gate. Prior explicit stop/budget limits still apply.

For a single normal-browser vocal-create attempt, plan at most one Qwen lyrics
request, one ACE-Step music submission and its one automatic FLUX cover. Polling
and downloading the same confirmed music task are different from submitting a
new task. Stop on failure or uncertain submission and record the safe stage/error;
do not repeatedly click Generate. Fix/review the cause before a separately scoped
retry. Never remove model/completeness checks just to obtain a success label.

AT-04 requires **Qwen AI lyrics -> playable ACE-Step vocal song using the selected
settings**, in live/browser modes. Verify through `python scripts/dev.py` and the
actual form: lyrics and music jobs succeed, real audio fully decodes and plays,
a listener confirms sung vocals, and title/style/mood/duration/mode and the new
matching cover stay associated with the correct track. Record reload retention
without another generation. Use the related cover/library cases for their own
acceptance; don't close other issues from this one run.

Report the tested head, normal launch/port, configuration source **type** (no
values), role labels, inputs, actual stage/job results, submission counts, media
checks, browser/listening observations, safe evidence paths and remaining gaps.
If blocked, name the exact missing variable **names** or failing safe stage; do
not ask users to paste keys. Keep #3 open until its required live/browser evidence
is actually satisfied. No successful live run is claimed by this guide.

## Deliberate service contract probes

The four live requests are frozen in [SERVICE_CONTRACTS.md](SERVICE_CONTRACTS.md)
and [service-probes.json](../contracts/service-probes.json). Reuse them when
an assigned task needs a live compatibility check; generation is opt-in and
bounded, never triggered by offline checks, CI or app startup. Record new
expected/actual results and schema changes together. Do not treat schema-only
reference upload support or decoded smoke media as completed browser features.

## Acceptance evidence

[acceptance.json](acceptance.json) is the requirement/task/case index;
[ISSUES.md](ISSUES.md) contains scope and closure criteria. AT-01-AT-19 cover the
whole brief, including both reference formats, playback transitions, samples,
documentation, teamwork and the independent ZIP. Missing/blocked/skipped is not
pass. A models-list request is not a successful feature request. A fake provider
is only offline evidence, even if its screenshots look convincing.

As each flow works, record date, tester, environment, commit, exact safe inputs,
expected/actual results and evidence in TEST_RESULTS.md and results/. Listen to
the output, inspect new cover/track pairing and observe speech/music without
overlap. Include progress/error/recovery and stage timings before diagnosing
slowness. Keep course keys, uploads, voice references and unsafe logs out of Git.

Reconcile the full requirement list at each PLAN milestone. Rehearse independent
installation after the three core features first work; fix the gaps then. Any
local pre-publication rehearsal is useful but cannot satisfy the GitHub ZIP rule.

## Final candidate and ZIP

1. Commit reviewed code, assets, dependencies, README and earlier evidence to main.
   Select the full candidate SHA. No missing mandatory requirements may be waived.
2. Download GitHub's source ZIP for that SHA, not a local build/working-tree ZIP.
   A different teammate installs it using only README and class credentials and
   exercises all required flows, references, controls and three actual samples.
3. Keep the final verification record outside the frozen candidate (an external
   path or ignored results/raw/). This avoids changing the tested commit merely
   to record its own SHA. Generate a blank record, then fill only observed results:

```powershell
python scripts/check_readiness.py --template results/raw/release-record.json
# Fill the record after independent checks. Do not change not-run to pass by assumption.
python scripts/check_readiness.py --release --evidence results/raw/release-record.json --archive C:/path/to/GitHub-source.zip
```

The record identifies the full tested SHA, GitHub repo/archive URLs, archive
SHA-256, preparer, different installer, environment, normal launch command, all teammates'
contribution/review evidence, and AT cases with required modes/variants and
evidence paths already committed in the candidate. Live/browser labels must
describe what actually ran. Share the final record with the team; after publication
authorization it may be attached to the release/acceptance issue without a new
code commit. Do not put secrets in the record or count it as an app feature test.

The release check refuses incomplete evidence, missing sample media/provenance,
a candidate not on main, wrong ZIP inventory/bytes or prohibited archive paths.
It validates the record and archive identity, not the truth of human observations,
audio/image quality or ongoing GitHub access. Teammate review is still essential.
Keep the public repo accessible through grading. Submit its URL, that SHA and
that exact GitHub ZIP per team on Canvas; the checker does not submit anything.

Code, assets or dependency changes after testing create a new candidate: rerun
affected checks and independent ZIP installation. Documentation fixes that alter
the candidate also change its SHA; recheck the final ZIP rather than submitting
an archive that no longer matches the recorded version.
