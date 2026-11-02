# Curated sample library

No approved samples are registered in manifest.json yet. Actual class-generated
audio/covers must play from the GitHub source ZIP; a generator script alone is insufficient.

## Current selection target — 2026-11-01

Joshua's project target is **at least three finished songs, including at least two
vocal tracks with original Qwen-generated lyrics**, each with matching class-generated
artwork. The assignment requires three samples; the two-vocal mix is the owner's
additional curation requirement. More curated songs can showcase range after this
core set is complete and the catalog supports additional entries.

Joshua coordinates selection and manifest integration. Mike retains his #3/#6
acceptance run and existing third-candidate preparation; coordinate source handoffs
and exact candidate pieces before creating or packaging another song.

[Current offline inventory](../../results/a3-07-sample-inventory.json) checks main
`a1a41d1`: both packaged instrumental pairs fully decode and match their original
acceptance hashes. Both also load as ready tracks using the production loader in a
temporary two-entry catalog. This is an offline validation, not a new listening,
normal-launch library or final ZIP acceptance. The approved manifest stays empty.

| Candidate/source | Available evidence | Selection step |
|---|---|---|
| Moonlit Reflection | Original 30 s ambient-piano WAV/PNG; prior Joshua listening; matching lake/pianist cover inspected | Preferred retained instrumental option, subject to final curation |
| Desert Drive | Original 20 s upbeat-funk WAV/PNG; prior Joshua listening | Alternate instrumental; generated cover lettering differs from the title, so curate artwork before selection |
| Genre scorecard in [PR #43](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/pull/43) | 20 historical instrumental assessments, 10 rated Good to go; exact hashes/settings | Confirm retained source audio and matching artwork with Mike before packaging; these are additional range options |
| Vocal candidate 1 | Mike's coordinated #3/#6 run is authorized on a1a41d1; no finished vocal candidate is packaged here yet | Retain original lyrics/audio/art and provenance from a successful run, then listen and inspect before selection |
| Vocal candidate 2 | [Afterglow Avenue preparation](https://github.com/JoshuaKosakowsky/AI-Jukebox_MBAX6418/blob/79e55de93ce6b209ab76f9889e6b9987dd187826/results/a3-07-vocal-two-preparation.json): 45 s synth-pop draft; no generated sample media yet | Joshua prepares a contrasting style/theme with original AI lyrics and a matching class cover, without repeating Mike's run |

Finish the three-song set first: two vocal performances plus one selected
instrumental. A finished vocal sample must have intelligible sung performance of
its retained AI lyrics, coherent musical structure/ending, suitable genre/mood,
and matching artwork; a completed job or nonempty lyrics field alone is insufficient.
Human listening and cover approval remain required for every selected entry.

Retain the original safe prompts/settings, returned AI lyrics, model/date, full
SHA-256 hashes and source commit with each chosen song. Populate `style` and `mood`
from the original settings when copying a candidate into the manifest. Then verify
all three through the normal launcher, replay/reload without provider calls, and
the exact final GitHub ZIP. Keep temporary reference-voice clips out of the catalog.

**Additional range:** the current runtime accepts at most three entries and the
release checker requires exactly three. A fourth or later sample therefore needs a
focused loader/release-gate change, relevant tests and documentation before selection.
Retain the 64 MB shared-media budget and enough space for user-created tracks/DJ
speech. Candidate files outside the manifest can remain available for curation.
No new generation budget or sample approval follows from this inventory.

## Moonlit Reflection candidate (#7)

[Audio](moonlit-reflection.wav), [cover](moonlit-reflection.png), and
[candidate/provenance record](moonlit-reflection.candidate.json) are ready for
selection. This is the original 30-second ambient-piano instrumental and matching
FLUX cover from main 7cc9645. Both hashes match the earlier acceptance record;
full WAV/PNG decoding and a muted browser asset-preview play/pause/resume passed.
Joshua's prior listening confirmation is attributed separately. No new media was generated.

The candidate record's `sample` object has the fields needed for the final
manifest. The sample lead can review it, add that object to manifest.json if selected, and
integrate its local audio/cover into the sample library. Keep the other two
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
and independent ZIP checks remain pending; manifest.json is unchanged.
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
