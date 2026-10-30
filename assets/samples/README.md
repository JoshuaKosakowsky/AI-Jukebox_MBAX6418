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
GitHub ZIP before closing #7. This branch does not add a sample loader, approve
the final set, or change the shared manifest. [Asset preview](../../results/moonlit-candidate-preview.jpg).

## Final sample records

For each of three entries in manifest.json record: id, title, audio and cover
paths from repo root, instrumental (true/false), lyrics (AI text for vocals),
generated_at, generation_notes (safe prompts/settings), and generated_with:
music = ACE-Step 1.5 XL Turbo; cover = FLUX.2 klein 4B; lyrics = Qwen3.6-35B-A3B
for vocals. Preserve the advertised model names; no invented generation claims.

Listen to every song and inspect its cover association. Record provenance and
playback evidence for AT-11. No credentials, third-party media, user uploads or
voice references may be bundled. Temporary experiments stay in ignored generated/.
