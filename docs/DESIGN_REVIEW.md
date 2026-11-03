# Compare the jukebox designs

All six layouts are merged into main (PRs #60/#62), along with the local
Surprise me helper (#63). They use the same songs and controls. This is a
preference comparison, not a randomized experiment or release sign-off.

Use a clean checkout of current main, or the selected GitHub ZIP, then follow
the README launcher. In an existing clone, preserve uncommitted work and use a
separate checkout if someone is actively working there; do not switch their branch.
For a clean clone with no pending changes:

```powershell
git fetch origin
git switch main
git pull --ff-only origin main
python scripts/dev.py
```

For an extracted ZIP, skip Git and run `python scripts/dev.py` from its inner
source folder. Open http://127.0.0.1:8000/ on your own computer. Joshua's localhost
URL only works on his machine. Bundled songs/artwork/lyrics and Surprise me need
no service keys; actual generation and DJ introductions need private class settings.
If port 8000 is occupied, choose another with `--port` and adjust the links below.

Use **Layout** and **Appearance** at the top:

| Option | What to compare | Link on your local app |
|---|---|---|
| A · Record sleeve | Compact cover rows, editorial type, DJ on the right | [Dark A](http://127.0.0.1:8000/?design=sleeve&theme=dark) |
| B · Cover gallery | Larger artwork, a grid for browsing | [Dark B](http://127.0.0.1:8000/?design=gallery&theme=dark) |
| C · Studio console | Denser list, smaller artwork, DJ on the left | [Dark C](http://127.0.0.1:8000/?design=console&theme=dark) |
| D · Listening room | Featured first track, compact DJ strip, smaller supporting tracks | [Dark D](http://127.0.0.1:8000/?design=room&theme=dark) |
| E · Record shop | Side navigation and a horizontally browsable album rack | [Dark E](http://127.0.0.1:8000/?design=shop&theme=dark) |
| F · Workbench | Queue, playable library and creation form in three desktop panes | [Dark F](http://127.0.0.1:8000/?design=workbench&theme=dark) |

Every option supports Light and Dark. In Workbench the studio opens automatically;
leaving Workbench restores its prior open/closed state without clearing your inputs.
At narrow widths the three panes stack; the record rack keeps its own horizontal
scrolling, and keyboard focus brings off-screen sleeves into view.

Dark is the initial default. Browser-local
preferences persist when storage is available; an explicit URL choice wins.
The URL updates when you switch, so you can share an exact design/theme choice
(replace the localhost port if yours differs). Switching does not reload the page,
regenerate anything, or replace audio elements. Workbench only opens/restores the
existing studio disclosure; it never submits the form. Private recordings/session data
are never stored as appearance preferences.

For a quick comparison, use the same bundled song in each layout:

1. Find and play it with the song's own audio player, then pause it.
2. Find its lyrics, creation form, DJ style and optional voice settings.
3. Switch layouts and Light/Dark. Try a narrow window too.
4. Open Create a song and try Surprise me with your own starting idea; edit the
   fields and confirm switching layouts does not clear the draft. Do not Generate.
5. Note which layout makes finding music and controls easiest, and any text,
   contrast, scrolling or keyboard-focus problems. Include layout, theme and width.

Do not generate songs/intros or upload a recording for this visual comparison.
Report your preferred layout/theme and the most useful change on
[issue #9](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/issues/9).
No number of votes or completed comparisons is required; do not change the final
ZIP acceptance record based on this design comparison.
