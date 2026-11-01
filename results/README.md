# Reviewed evidence

Add safe screenshots, comparison results and test summaries here as work is
verified. The [service probe record](service-contract-probes.json) contains safe
live smoke measurements. Integrated normal-launch generation and playback
evidence is listed below. Record metadata in docs/TEST_RESULTS.md.
Never commit credentials, raw unsafe logs, user uploads or voice recordings.
Required sample audio/images belong in assets/samples/, not this directory.

Moonlit sample candidate: [moonlit-candidate-preview.jpg](moonlit-candidate-preview.jpg)
shows the retained media in a muted local asset preview. Provenance and
selection/integration notes are in [the sample guide](../assets/samples/README.md);
this does not establish normal-app sample-library or final ZIP acceptance.

Runtime foundation evidence (A3-01): runtime-adapter-smoke.json contains the safe
2026-10-27 real-client results; startup-configured.jpg, startup-library.jpg and
startup-missing-settings.jpg are actual normal-launch browser screenshots. They
show startup/configuration only, not accepted generation/playback features.

A3-04 cover evidence: cover-generation.jpg is an actual normal-launch browser
screenshot with two new FLUX covers on their own song drafts. The safe inputs
and DOM observations after reload are in cover-browser-record.json. These are
not approved sample songs, live audio-pairing or release acceptance evidence.

A3-02 integrated-main evidence: main-instrumental-acceptance.json records the
two real normal-launch music/cover requests, browser checks and Joshua's listening
confirmation on 7cc9645. main-instrumental-library.jpg is the actual browser view.
Raw clips/images stay ignored under results/raw; they are not approved sample assets.

Desert Drive candidate: [desert-candidate-preview.jpg](desert-candidate-preview.jpg)
shows the original retained pair in a muted local preview; [provenance and selection
notes](../assets/samples/README.md#desert-drive-candidate-for-jovi-7) include the known cover-lettering limitation. Not final library/ZIP acceptance.

Offline retry variants: [a3-08-retry-variants.json](a3-08-retry-variants.json),
[cover screenshot](cover-retry-disabled.png), [resume screenshot](resume-retry-disabled.png).
See [reproduction and limitations](../docs/RECOVERY_AUDIT.md#cover-retry-and-resume-variants-on-main-e2b1e52-2026-10-29); no app fix or live acceptance claimed.


A3-08 normal-launch failure/recovery evidence: [a3-08-normal-launch-recovery.json](a3-08-normal-launch-recovery.json)
records two live normal-launcher AT-10 cases (real UI busy-capacity rejection
then explicit retry; missing-music-configuration error then fix/restart/recreate)
with five unique decoded 60 s WAV/PNG pairs. Screenshots:
[failure/music not configured](a3-08-failure-music-not-configured.jpg),
[recovered 5-track library](a3-08-recovery-library.jpg),
[recovery success](a3-08-recovery-success.jpg). No vocals/DJ/reference flows
or release acceptance.

Early Windows ZIP startup evidence: [windows-zip-startup.json](windows-zip-startup.json)
records the exact GitHub archive identity, untouched source comparison and
missing/placeholder/invalid/configured checks on main 7b9dd2b. The actual browser
views are [missing settings](windows-zip-missing-settings.jpg) and
[configured](windows-zip-configured.jpg). This developer-directed rehearsal
does not satisfy independent final ZIP or feature acceptance.


A3-03 live vocal failure: [vocal-live-failure-record.json](vocal-live-failure-record.json)
and [actual browser card](vocal-live-failure.jpg) record one real normal-launch
attempt on main 770ce62. Cover succeeded, lyrics failed validation, and no music
was submitted. Reload retained the draft without retrying. AT-04 remains failed.


Genre follow-up #35: [initial ambient/funk comparison](a3-35-genre-comparison.json)
records a limited two-clip listening improvement. Broader user app testing then
found metal/rap unsuitable; [planning revision](a3-35-genre-fidelity.json) records
those exact inputs and two bounded music-only requests on 9871e7b. Both decode
fully, but Joshua judged neither genre convincing: both FAIL. The subsequent
[concrete-cue comparison](a3-35-concrete-cues.json), explicitly requested by Joshua,
used exactly two more music submissions on e62fe17; both decoded fully, but
Joshua again judged neither genre convincing. Previous run records are preserved;
no further generation in this new run. Neither record establishes
general genre fidelity, integrated-main browser or final sample acceptance.


Shared music-path audit: [a3-35-shared-conditioning.json](a3-35-shared-conditioning.json)
records three offline freeform-genre route/media cases and a bounded live test
(2 music-service format calls +2 music jobs,0 other services/retries). Joshua
confirmed both title-free piano/DnB controls match their descriptions. This
limited positive result preserves earlier metal/rap failures; #35 stays open.


Within-genre caption comparison: [stopped-run record](a3-35-caption-ab.json) on
c97045f records1 completed music job /3 polls /0 downloads. A diagnostic checked
`seed` instead of the documented `seed_value` and stopped before the second job.
Corrected response-shape/stop guards pass offline. No audio or genre verdict;
this does not establish a music-service failure or resolve #35.


Corrected within-genre pair: [caption A/B v2](a3-35-caption-ab-v2.json) on2eb81db,
explicitly authorized after the stopped run. Exactly2 music jobs /6 polls /2
downloads,0other services/retries; only the caption differs. Both returned the
requested seed and fully decoded20s. Joshua judged both FAIL: A has the better rhythm; B starts heavier then
turns light/happy. Neither delivers the expected heavy riff/bass impact.
No broad-genre or integrated-main acceptance claimed.


Caption-rewrite-off control: [one-flag record](a3-35-literal-caption.json) onac529fd,
1 music job /2 polls /1 download,0other services/retries. Exact retained B caption
and controls except use_cot_caption=false; thinking stays true. Joshua reports
C "leaning more metal"; partial improvement, full genre/mood acceptance unconfirmed.
Production settings unchanged; earlier failed records retained.


Explicit deathcore target: [Iced Coffee candidate](a3-35-deathcore-candidate.json)
on2c77732,1 music job /2 polls /1 download,0other services/retries. Actual production
caption with clarified style/mood, planning on / rewriting off; full20s WAV decode.
Joshua listened and replied "Still misses the target": heavier-target FAIL.
No finer per-trait diagnosis or all-genre conclusion; no further generation.


## Genre listening scorecard

Joshua's three categories describe the assessed instrumental clips. One20s
sample per style is provisional; a positive category does not establish every
song, subgenre, vocal mode or integrated-main flow. Joshua rated round1: two Good to go and two Minor improvement. Only human
listening assigns a quality grade; completed files, hashes and service metadata do not.

| Category | Meaning |
|---|---|
| Good to go | Recognizable requested genre/mood, acceptable to use in this sample. |
| Minor improvement | Recognizable, with some detail, mood or consistency needing work. |
| Major update / completely misses mark | Substantially wrong or unconvincing for the requested sound. |

<!-- genre-scorecard:start -->
| Style / assessed target | Category | Notes / work status | Round |
|---|---|---|---|
| Country | Minor improvement | Sounds like it has funk in it. | 1 |
| Swing jazz | Good to go | No notes. | 1 |
| House | Minor improvement | Does not hit the BPM in my head; desired BPM and direction were not specified. | 1 |
| Rap/Hip-hop instrumental | Good to go | User: "I can hear a rap/hip hop lyric behind this." Instrumental assessment only; no vocal acceptance inferred. | 1 |
| Funk | Minor improvement | Needs more bass. | 2 |
| Blues | Good to go | Clip completed; not yet quality-rated. | 2 |
| Reggae | Good to go | Clip completed; not yet quality-rated. | 2 |
| Salsa | Good to go | Clip completed; not yet quality-rated. | 2 |
| Classical string quartet | Minor improvement | Too synthetic. | 2 |
| Contemporary R&B | Good to go | Clip completed; not yet quality-rated. | 2 |
| Pop | Minor improvement | Too synthetic and not catchy enough. | 2 |
| Drum and bass | Good to go | Clip completed; not yet quality-rated. | 2 |
| Classic rock | Major update / completely misses mark | Sounded like funk and Donkey Kong Jungle. | 3 |
| Punk rock | Major update / completely misses mark | The worst so far; no finer per-trait diagnosis supplied. | 3 |
| Disco | Good to go | Clip completed; not yet quality-rated. | 3 |
| Techno | Minor improvement | Sounds off, like Nintendo Wii music. | 3 |
| Trance | Good to go | Listener is not familiar with the genre. | 3 |
| Ambient | Good to go | Clip completed; not yet quality-rated. | 3 |
| Afrobeats | Minor improvement | Needs more drums. | 3 |
| Reggaeton | Minor improvement | Wants more Caribbean steel drum/pan sound. | 3 |
| Heavy metal/deathcore (Joshua tested target) | Major update / completely misses mark | Known limitation; tuning deferred for a future revisit. | Historical |
<!-- genre-scorecard:end -->

[Machine-readable scorecard and exact round1 evidence](a3-35-genre-scorecard.json):
source7ebd861,4 music submissions/8 polls/4downloads,0other services/retries.
Unmodified production seed defaults; four full non-silent48kHz stereoPCM16 WAVs,
20s each. Raw clips rendered in chat and retained privately under results/raw.
Metal's earlier [failed heavier case](a3-35-deathcore-candidate.json) is preserved;
its deferral is a user priority decision, not a repaired or closed issue. No
further generation under the completed round1 budget.


<!-- genre-rounds-summary:start -->
Across rounds1-3: **20 sampled styles**, **20 rated**, **0 awaiting ratings**,
plus the separately deferred heavy metal/deathcore target. No quality category is
assigned automatically. Round1: [original record/index](a3-35-genre-scorecard.json);
round2: [eight additional styles](a3-35-genre-round2.json);
round3: [eight further styles](a3-35-genre-round3.json).
<!-- genre-rounds-summary:end -->
