# Test results and evidence

## Local setup - 2026-10-15 America/Denver

Scope: repository scaffold only. No service calls, generated samples, or app
tests. Validation runs `python scripts/verify_repo.py` after staging files,
checks local Git configuration/hooks, and verifies the preserved prompt.
Final outcomes are recorded in handoff.md after execution.

## Application evidence (not run)

| Case | Inputs | Expected | Actual | Status |
|---|---|---|---|---|
| Vocal song | TBD style/mood/duration | AI lyrics, playable ACE-Step song, library entry | Not run | Pending |
| Instrumental song | TBD style/mood/duration | Playable instrumental, library entry | Not run | Pending |
| Matching cover | Generated song context | New FLUX image with correct track | Not run | Pending |
| Default DJ | Queue of multiple tracks | Song-specific speech, then music; no overlap | Not run | Pending |
| Reference DJ | MP3 and WAV reference cases | Customized voice with safe temporary upload handling | Not run | Pending |
| Playback controls | Pause/resume/skip/end | Correct sequential automatic advancement | Not run | Pending |
| Failure/recovery | TBD timeout or failed request | Safe useful error and successful recovery | Not run | Pending |
| Sample collection | Fresh install | Three actual songs/titles/covers play | Not run | Pending |
| Independent ZIP | Exact submission commit ZIP | Core features work using README + keys only | Not run | Pending |

For each executed case add date/time, tester, OS/browser/runtime, commit,
commands, exact safe inputs, expected/actual behavior, pass/fail and evidence
paths. Do not include credentials, user recordings, or raw unsafe logs.

## Design judgment and investigated limitation

Pending. Record one decision supported by testing and one investigated failure
or limitation, including alternatives, observed result, and lesson learned.
Summarize verified findings in the final README in the team's own words.
