# Compare the jukebox designs

These are alternative layouts of the same app, using the same songs and controls.
This is a preference comparison, not a randomized experiment or release sign-off.

To try the preview before it merges, use a clean, separate checkout of
`codex/a3-ux-review`, then follow the normal README launcher:

```powershell
git fetch origin
git switch --track origin/codex/a3-ux-review
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

Every option supports Light and Dark. Dark is the initial default. Browser-local
preferences persist when storage is available; an explicit URL choice wins.
The URL updates when you switch, so you can share an exact design/theme choice
(replace the localhost port if yours differs). Switching does not reload the page,
regenerate anything, or replace audio elements. Private recordings/session data
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
