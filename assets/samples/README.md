# Three required sample tracks

No approved samples are registered in manifest.json yet. Actual class-generated
audio/covers must play from the GitHub source ZIP; a generator script alone is insufficient.

## Moonlit Reflection candidate for jovi (#7)

[Audio](moonlit-reflection.wav), [cover](moonlit-reflection.png), and
[candidate/provenance record](moonlit-reflection.candidate.json) are ready for
selection. This is the original 30-second ambient-piano instrumental and matching
FLUX cover from main 7cc9645. Both hashes match the earlier acceptance record;
full WAV/PNG decoding and a muted browser asset-preview play/pause/resume passed.
Joshua's prior listening confirmation is attributed separately. No new media was generated.

The candidate record's `sample` object has the fields needed for the final
manifest. Jovi can review it, add that object to manifest.json if selected, and
integrate its local audio/cover into the sample library. Keep the other two
samples distinct; verify all three through the normal launcher and exact final
GitHub ZIP before closing #7. The loader below supplies the integration path;
the candidate record itself does not approve the final set or change the manifest. [Asset preview](../../results/moonlit-candidate-preview.jpg).

## Final sample records

For each of three entries in manifest.json record: id, title, audio and cover
paths from repo root, instrumental (true/false), lyrics (AI text for vocals),
generated_at, generation_notes (safe prompts/settings), and generated_with:
music = ACE-Step 1.5 XL Turbo; cover = FLUX.2 klein 4B; lyrics = Qwen3.6-35B-A3B
for vocals. Preserve the advertised model names; no invented generation claims.

Listen to every song and inspect its cover association. Record provenance and
playback evidence for AT-11. No credentials, third-party media, user uploads or
voice references may be bundled. Temporary experiments stay in ignored generated/.

## Local manifest loader

Only `manifest.json` selects samples; candidate records and directory contents
are not scanned. After Jovi approves an entry, copy its `sample` object into
`{"samples": [...]}` and restart the normal launcher. Use a stable UUID `id`,
ISO calendar date `generated_at`, nonempty title/notes, boolean `instrumental`,
and the exact class model names above. Instrumentals use `lyrics: null`; vocals
require nonempty AI lyrics plus Qwen provenance. Optional `style` and `mood`
(1-120 characters each) retain original settings for future deliberate generation;
omitting them displays “Class-generated sample” / “Pregenerated”.

The runtime accepts 0-3 records while the final release gate still requires three.
Each record needs its own distinct audio and cover beneath `assets/samples/`:
fully decodable PCM WAV (mono/stereo, 10-600 seconds) and 512x512 PNG. No absolute,
parent-traversal, outside symlink, duplicate identity or aliased asset paths.
The manifest is limited to 128 KB, each asset to 20 MB and the full catalog to
the existing 64 MB media budget. Invalid metadata or any missing/corrupt asset
rejects the entire catalog with a fixed setup warning; fix the files and restart.

New sessions receive ready tracks via the existing session-owned `/api/media/UUID`
routes, with different media URLs per session. Refresh/reload never create jobs
or call a provider. Session expiry/restart reseeds the approved catalog; changing
a sample's media in one session leaves other sessions and the source files intact.
Samples count toward the 20-track limit. Immutable sample bytes are shared and
counted once in the 64 MB retained-media budget, including after replacements.
No service keys are needed for local sample playback.
