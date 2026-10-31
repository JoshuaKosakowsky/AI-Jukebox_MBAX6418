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
