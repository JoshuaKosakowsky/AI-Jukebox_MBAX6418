# Teammate ZIP test — default DJ

Use this packet for an independent install and the three core features with the
**default Chatterbox voice**. Do not upload a voice recording. The existing upload
capability stays in the app; this checklist does not test or certify it.

## Before starting — Joshua coordinates

1. Name **one actual teammate other than Joshua** as installer and post the start
   claim on [#10](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/10).
   Previous code contributions do not disqualify them. They must use a clean ZIP
   extraction and the documentation, not their existing clone or developer files.
   JoshKozy/Hermes is another Joshua identity, not a different teammate.
2. Confirm Mike is not running overlapping live acceptance. Agree on this new
   run's limit before generation: **11 generation requests maximum, no retries**.
   This packet makes no calls and does not renew any earlier spent allowance.
3. Pin the candidate identity below. If choosing another merged SHA, replace the
   URL/hash/size before the test. Keep that version fixed throughout the run.

Ready baseline, verified 2026-11-02; these identify the ZIP, not completed testing:

- Commit: `29c5de17b0a0500f09bfbaa80badee7f22be741d`.
- [Download this exact GitHub ZIP](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/archive/29c5de17b0a0500f09bfbaa80badee7f22be741d.zip).
- Size: **31,520,975 bytes**; SHA-256:
  `8aa22e4ae97fa87db30ccb1b2098599b8ca8517682d1e909adcbabcddaefd752`.
- Main CI for that commit passed. No independent installation is claimed yet.

This separately supplied checklist can test that fixed baseline even if a later
documentation PR merges. Submit the tested version's original GitHub ZIP and SHA;
do not silently replace them with a later main archive.

## What the teammate does

1. **Download and extract into a brand-new folder** outside an existing clone.
   Keep the original ZIP. Verify its hash: Windows PowerShell
   `Get-FileHash -Algorithm SHA256 'C:\path\downloaded.zip'`; macOS
   `shasum -a 256 '/path/downloaded.zip'`. Record OS, Python version, ZIP hash/size
   and the commit above. Open a terminal in the extracted inner folder containing
   `README.md`, `pyproject.toml` and `scripts/`.
2. **Install and launch from the shipped README.** Use Python 3.12 (the app also
   supports 3.13/3.14). If uv is absent, run `python -m pip install uv==0.12.19`,
   then `python scripts/dev.py`. On macOS use `python3` for these commands if
   `python` is unavailable. Open `http://127.0.0.1:8000`. No Git, Node, previous
   virtual environment or files from a clone should be needed. If 8000 is busy,
   stop this launch and use `python scripts/dev.py --port 8001`.
3. **Check the bundled library before configuring services.** It must show
   Afterglow Avenue (45s vocal), Moonlit Reflection (30s instrumental) and
   Antlercover (60s vocal), each with its matching cover. Play each to its end;
   inspect both vocal lyric panels and exercise local pause/resume. Confirm the
   samples work without regeneration. Missing-service guidance should be clear.
4. **Configure privately.** Stop the server with Ctrl+C. In this new extraction,
   copy `.env.example` to `.env` and fill its eight values using class credentials
   from the private team source. Never post the file, keys or screenshots of it.
   Restart with the same launcher. All four service roles should show configured;
   that label alone is not proof of connectivity. Record whether README steps
   worked without undocumented help.
5. **Create one instrumental.** Title `ZIP Piano Check`, style `Ambient piano`,
   mood `Calm and reflective`, duration **20s**, mode **Instrumental**. Click Create
   once. Expect visible generation status, a new matching FLUX cover, playable
   instrumental audio and a persistent library card. Listen and record the actual
   result; do not treat a completed file as automatic quality approval.
6. **Create one vocal.** Title `ZIP Homecoming Check`, style `Synth-pop`, mood
   `Hopeful`, duration **30s**, mode **Vocal song with AI lyrics**. Click Create
   once. Expect original visible AI lyrics, a separate matching cover and audible,
   intelligible sung vocals that broadly fit the settings. Verify the earlier
   instrumental still plays. Record expected versus actual for music, lyrics and
   art; take safe screenshots of the completed cards and lyrics.
7. **Run the default DJ.** Stop local players; add those two new tracks and one
   bundled sample to the queue. Choose **Relaxed / Public Radio**. Leave the
   optional reference chooser empty; use **Use default voice** if a file was
   accidentally selected. Press **Play queue** once. Hear each introduction and
   confirm it fits the upcoming song. Test Pause/Resume during speech and music,
   then let the queue automatically advance and finish. Speech must precede music
   without overlapping playback. This first pass creates at most three intros.
8. **Replay the cached queue.** Press Play again. Skip during the first speech;
   on the next song let speech finish, then Skip during music. Pause, reload and
   confirm the queue/library survive without automatic generation. Resume cached
   playback as needed. Do not press new-generation or Retry-introduction buttons.
9. **Verify the docs and report in your own words.** Note one instruction that
   matched the app, any missing/wrong step, and a brief finding about the default
   DJ, generated output or a documented limitation. Existing real recovery
   evidence is linked in README; confirm the missing-settings/fix/restart behavior
   in steps 2–4. Do not manufacture a failure or mark an unrun case passed.
10. **Stop and return the record below**, safe screenshots and any error details
    to Joshua through the team workflow. Stop the server. Keep records outside
    the extraction and use the original downloaded ZIP for submission; do not
    repackage the folder containing your private `.env`.

## Limits and failure rule

| Action | Text | Art | Music | Speech |
|---|---:|---:|---:|---:|
| One new instrumental | 0 | 1 | 1 | 0 |
| One new vocal | 1 | 1 | 1 | 0 |
| Three default-DJ introductions | 3 | 0 | 0 | 3 |
| **Maximum** | **4** | **2** | **2** | **3** |

Normal bounded music polling/downloads are additional HTTP traffic, not additional
generation submissions. Sample playback, refresh, reload and cached replay should
not generate new output. On the first unexpected error, uncertain submission or
attempted duplicate, **stop**; save the exact safe UI/job error, step and actual
counts if observed. Do not retry, regenerate, switch models or spend the remaining
ceiling. Joshua coordinates a fix/new allowance if needed. If counts are not
observable, report that honestly instead of inventing them.

## Copy this completion record

```text
Installer name/GitHub login:
Date/time and timezone:
OS; Python; uv versions:
Candidate SHA; original ZIP URL; bytes; SHA-256:
Actual launch command and port:
Clean extraction; no clone/private developer files used: yes/no
Install + missing-settings/configuration recovery: pass/fail/not run; actual:
Three bundled songs/covers/lyric panels: pass/fail/not run; actual:
New instrumental + matching cover: pass/fail/not run; actual:
New AI lyrics + sung vocal + matching cover: pass/fail/not run; actual:
Default DJ: three intelligible, track-appropriate intros: pass/fail/not run; actual:
Pause/resume; automatic speech->music->next; no overlap: pass/fail/not run; actual:
Cached replay; Skip in speech/music; reload retention: pass/fail/not run; actual:
Voice upload comparison: NOT RUN — outside this checklist
Generation submissions observed (or say not observable): text / art / music / speech
Safe screenshots/evidence locations:
Exact errors and remaining untested steps:
README verification and findings in your own words:
Server stopped: yes/no
```

## Coordinator close-out

Use actual results to reconcile #3/#5/#7/#9/#10; preserve historical attribution.
Check every actual teammate's contribution and teammate-review evidence separately.
This default-DJ record is not an all-case release PASS: the unchanged
`docs/acceptance.json` and `check_readiness.py --release` still require AT-08's
MP3/WAV result, which this checklist leaves **not-run**. Do not mark it passed by
assumption or describe the current gate as green. Record remaining scope decisions
explicitly before claiming full readiness. Follow [the submission runbook](SUBMISSION_RUNBOOK.md)
for the external acceptance record, exact ZIP identity and final Canvas delivery.
