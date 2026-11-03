# Compare the jukebox designs

D/E/F extend the A/B/C comparison merged in PR #60. This branch targets main.
A/B/C remain available. These are alternative layouts of the same app, using
the same songs and controls.
This is a preference comparison, not a randomized experiment or release sign-off.

To try the preview before it merges, use a clean, separate checkout of
`codex/a3-layouts-def`, then follow the normal README launcher:

```powershell
git fetch origin
git switch --track origin/codex/a3-layouts-def
python scripts/dev.py --port 8033
```

If that branch already exists locally, switch to it rather than creating it again.
Preserve uncommitted work; do not switch an active teammate's checkout.
Open http://127.0.0.1:8033/ on your own computer. Joshua's localhost URL only works
on his computer. All three bundled songs/artwork are available without service
keys; generation and DJ speech still need private class configuration.

Use **Layout** and **Appearance** at the top:

| Option | What to compare | Link on your local app |
|---|---|---|
| A · Record sleeve | Compact cover rows, editorial type, DJ on the right | [Dark A](http://127.0.0.1:8033/?design=sleeve&theme=dark) |
| B · Cover gallery | Larger artwork, a grid for browsing | [Dark B](http://127.0.0.1:8033/?design=gallery&theme=dark) |
| C · Studio console | Denser list, smaller artwork, DJ on the left | [Dark C](http://127.0.0.1:8033/?design=console&theme=dark) |
| D · Listening room | Featured first track, compact DJ strip, smaller supporting tracks | [Dark D](http://127.0.0.1:8033/?design=room&theme=dark) |
| E · Record shop | Side navigation and a horizontally browsable album rack | [Dark E](http://127.0.0.1:8033/?design=shop&theme=dark) |
| F · Workbench | Queue, playable library and creation form in three desktop panes | [Dark F](http://127.0.0.1:8033/?design=workbench&theme=dark) |

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
4. Note which layout makes finding music and controls easiest, and any text,
   contrast, scrolling or keyboard-focus problems. Include layout, theme and width.

Do not generate songs/intros or upload a recording for this visual comparison.
Report your preferred layout/theme and the most useful change in the PR discussion.
No number of votes or completed comparisons is required; do not change the final
ZIP acceptance record based on this design comparison.
