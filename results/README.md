# Reviewed evidence

Add safe screenshots, comparison results and test summaries here as work is
verified. The [service probe record](service-contract-probes.json) contains safe
live smoke measurements. Integrated normal-launch generation and playback
evidence is listed below. Record metadata in docs/TEST_RESULTS.md.
Never commit credentials, raw unsafe logs, user uploads or voice recordings.
Required sample audio/images belong in assets/samples/, not this directory.

Local Surprise me controls (2026-11-02, branch `codex/a3-surprise-song`):
[idea-generator browser/variability record](a3-song-ideas.json). Production handler
probe:1950 distinct titles/2000 full ideas in2000 fixed-seed rolls. Normal
no-credentials browser checks cover all6 layouts in both themes at1265/465px,
custom seed/keep/edit/Enter behavior and345px wrapping. Zero generation calls;
this is input/UI evidence, not music quality or independent ZIP acceptance.

Reference-voice browser privacy/recovery regression (2026-11-02, main `3f65954`):
[safe18-observation record and reproduction](a3-08-reference-browser.json),
[malformed upload](a3-08-reference-malformed.jpg), [clear/default](a3-08-reference-default.jpg),
[full offline view](a3-08-reference-full.jpg). Actual UI with synthetic clips and
MockTransport; class calls0. This does not establish real reference-voice quality,
normal-launch/live AT-08 or independent final ZIP acceptance.

Public GitHub ZIP preflight (2026-11-02, main `78fb007`):
[safe archive/media/startup record and reproduction](a3-08-source-zip-preflight.json).
All169 archived source files match Git, three selected songs/two vocals ship,
and normal extracted-ZIP HTTP startup passes without Git metadata or class
settings. Zero class calls. Developer-directed; independent final ZIP/live
acceptance is still pending and the incomplete release record stays NOT READY.

Current six-layout guide captures (2026-11-02, main `e17997d`):
[safe author UI record](a3-09-guide-ui.json),
[Gallery/Dark](a3-09-layout-gallery.jpg), [editable song ideas](a3-09-song-ideas.jpg),
[DJ settings](a3-09-dj-settings.jpg), [Workbench/Light](a3-09-layout-workbench-light.jpg).
Actual normal-launch browser with all class roles missing; existing bundled
assets, seeded Enter/custom settings and layout/theme/presentation retention
were observed. Zero generation jobs, class calls or uploads. No new listening,
full playback, live service or independent teammate/ZIP acceptance is claimed.

Historical README/UI documentation before the layout update (2026-11-02, main `fcdda54`):
[safe normal-launch record](a3-09-current-ui.json),
[full interface/library](a3-09-current-library.jpg),
[bundled lyrics/player](a3-09-current-lyrics.jpg),
[DJ presentation/reference chooser](a3-09-current-dj.jpg).
Actual browser screenshots with all service roles missing; only existing sample
playback and presentation/reload were exercised, with zero generation jobs or
class calls. These do not replace live DJ/reference/vocal or final ZIP evidence.

Integrated-main offline browser regression (2026-10-31):
[27-check record](main-browser-regression.json),
[paused playback](main-browser-paused.jpg),
[recovered library](main-browser-recovered.jpg).
[Method, findings and reproduction](../docs/MAIN_BROWSER_REGRESSION.md) distinguish
synthetic browser coverage from live acceptance. No class calls or app changes.

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
| Style / assessed target | Category | Notes / work status |
|---|---|---|
| Country | Minor improvement | Some unwanted funk influence. |
| Swing jazz | Good to go | No notes. |
| House | Minor improvement | Tempo feel needs work; desired BPM not specified. |
| Rap/Hip-hop instrumental | Good to go | Beat suitable for rap/hip-hop lyrics; vocals untested. |
| Heavy metal/deathcore (Joshua's tested heavier target) | Major update / completely misses mark | Known limitation; tuning deferred for a future revisit. |
<!-- genre-scorecard:end -->

[Machine-readable scorecard and exact round1 evidence](a3-35-genre-scorecard.json):
source7ebd861,4 music submissions/8 polls/4downloads,0other services/retries.
Unmodified production seed defaults; four full non-silent48kHz stereoPCM16 WAVs,
20s each. Raw clips rendered in chat and retained privately under results/raw.
Metal's earlier [failed heavier case](a3-35-deathcore-candidate.json) is preserved;
its deferral is a user priority decision, not a repaired or closed issue. No
further generation under the completed round1 budget.

User playback review fixes (2026-11-02): [safe record](a3-playback-ux.json),
[normal sample seeking](a3-playback-seeking.jpg), [synthetic DJ queue/seek controls](a3-playback-queue.jpg).
Normal no-credentials browser verifies sample ranges/metadata, paused5-second
seeking and exact owner display-lyric corrections. Separate synthetic-provider
browser verifies card/player preservation, queue order/removal, paused DJ seeking,
current-entry protection, empty-queue reload and cached playback. Zero class calls;
fixture speech is silence, not real DJ quality/listening acceptance. Original
sample media and lyric provenance are retained. A runtime merge needs an explicitly
selected/tested new ZIP; it does not certify the older0a34502 candidate.
