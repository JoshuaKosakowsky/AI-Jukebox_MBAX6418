# Curated sample library

The manifest selects two Joshua-approved class-generated samples. They play
locally without service settings. The three-song target remains **two finished
vocals plus one instrumental**; the second vocal is awaiting its original files.

| Selection | Retained media and approval |
|---|---|
| Afterglow Avenue | 45 s hopeful synth-pop vocal; original Qwen lyrics, ACE-Step WAV and curated wordless FLUX cover. Joshua approved the audio, then the cover/selection on 2026-11-01 America/Denver. |
| Moonlit Reflection | Original 30 s reflective ambient-piano instrumental and FLUX lake/pianist cover. Prior Joshua listening retained; final selection confirmed on 2026-11-01 America/Denver. |
| Moonlit Rehearsal — pending | Mike's retained 30 s acoustic-indie-pop vocal is proposed for the third slot. Await original WAV, cover, Qwen lyrics and full provenance; no regeneration requested. Mike's prior listening is distinct from Joshua's pending final check. |

[Afterglow provenance](afterglow-avenue.candidate.json) links the exact production
HTTP run, returned lyrics, source, model names and hashes. Actual Afterglow calls:
text1/music1/art2/speech0, three music polls and one download, no automatic retries.
The first app-generated cover still rendered incorrect lettering after #40 and is
[preserved unchanged](../../results/afterglow-avenue-initial-cover.png). One separate
visual-only FLUX request produced the selected wordless scene; app code is unchanged.
This curation does not establish a general lettering fix for #36.

[Selected-library checks](../../results/a3-07-selected-library-checks.json) record
full decoding, exact HTTP media/lyrics, isolated session URLs, actual browser
playback/pause/resume and reload on the normal launcher with all services missing.
These checks cover the two available selections. Integrated-main three-song and
independent final GitHub ZIP acceptance remain pending; #7 stays open.

Joshua coordinates current curation/integration under the owner's explicit
instruction. Mike keeps his separate #3/#6 run and source handoff. Preserve each
contributor's source and evidence; don't repeat generation to replace missing files.
Desert Drive remains an unselected instrumental alternate with its original
lettering limitation. The historical [inventory](../../results/a3-07-sample-inventory.json)
and genre scorecard are supporting evidence, not additional approved entries.

A fourth sample needs a focused capacity change: the runtime accepts at most
three entries and the release checker requires exactly three, within the existing
64 MB media budget. Finish the core set before optional range additions.

## Moonlit Reflection candidate (#7)

[Audio](moonlit-reflection.wav), [cover](moonlit-reflection.png), and
[candidate/provenance record](moonlit-reflection.candidate.json) are selected by Joshua. This is the original 30-second ambient-piano instrumental
and matching
FLUX cover from main 7cc9645. Both hashes match the earlier acceptance record;
full WAV/PNG decoding and a muted browser asset-preview play/pause/resume passed.
Joshua's prior listening confirmation is attributed separately. No new media was generated.

The candidate record's `sample` object has the fields needed for the final
manifest. It is included in manifest.json with its original style and mood.
Keep the other two
samples distinct; verify all three through the normal launcher and exact final
GitHub ZIP before closing #7. The loader below supplies the integration path;
the candidate record itself does not approve the final set or change the manifest. [Asset preview](../../results/moonlit-candidate-preview.jpg).

## Desert Drive candidate (#7)

[Audio](desert-drive.wav), [cover](desert-drive.png), and
[candidate/provenance record](desert-drive.candidate.json) package the second
retained acceptance track: 20 seconds, Upbeat funk, Energetic and optimistic.
The original title is Desert Drive (previous chat shorthand Desert Dawn was incorrect).
Audio/cover hashes match the original acceptance; full decoding and muted local
preview play/pause/resume passed. Joshua's original listening confirmation is
attributed as prior evidence; no new listening or generation is claimed.

The original cover says **DESSERT DRIIVE** and has distorted small lettering.
The sample lead should consider that known limitation when selecting the final samples;
this candidate preserves the original media rather than silently editing it.
If selected, its `sample` object is ready for the manifest. Final sample-library
and independent ZIP checks remain pending; this alternate is not selected in manifest.json.
[Actual local preview](../../results/desert-candidate-preview.jpg).

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
are not scanned. After Joshua approves an entry, copy its `sample` object into
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
