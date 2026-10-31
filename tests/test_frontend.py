"""Source-level rendering guards plus an optional, dependency-free Node probe.
The behavioral probe executes production click handlers with a minimal DOM;
real-browser verification remains separate evidence.
"""
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FrontendLibraryGuardTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "jukebox/web/app.js").read_text(encoding="utf-8")

    def test_track_cards_are_diffed_and_rebuilt_per_track(self):
        self.assertIn("const previousTracks = new Map()", self.source)
        self.assertIn("if (previousTracks.get(track.id) === input) continue;", self.source)
        self.assertIn("previousTracks.set(track.id, input);", self.source)

    def test_tracks_container_is_never_wholesale_replaced(self):
        # The destructive pattern destroys every <audio> element (and any playing
        # track) on every snapshot change; it must not reappear. The services
        # list may still rebuild (it holds no state).
        self.assertNotIn("library.replaceChildren", self.source)

    def test_audio_position_is_captured_and_restored_across_card_rebuilds(self):
        # Same underlying media => the ORIGINAL audio element is moved into the
        # rebuilt card (playback is never interrupted because the node never
        # leaves the document). This replaced the older capture/restore approach
        # because restoring positions cannot guarantee uninterrupted audio.
        self.assertIn("const oldAudio = existing.querySelector(\"audio\");", self.source)
        self.assertIn("const newAudio = card.querySelector(\"audio\");", self.source)
        self.assertIn("oldAudio.getAttribute(\"src\") === track.audio.url", self.source)
        self.assertIn("newAudio.replaceWith(oldAudio);", self.source)
        self.assertNotIn("function restoreAudio", self.source)
        self.assertNotIn("audio.play()", self.source,
                         "changed-media replacement must not auto-play the new element")

    def test_sync_after_mutation_does_not_invalidate_unrelated_cards(self):
        # Defect 2 regression: the post-mutation refresh must rely on the
        # per-track diff rather than clearing the whole cache (which would
        # rebuild every card and detach any playing player).
        mutation = self.source.split("async function syncAfterMutation")[1].split("function refresh")[0]
        self.assertNotIn("previousTracks.clear()", mutation)
        self.assertNotIn("previousLibrary", mutation)

    def test_music_stage_text_matches_server_progress_stages(self):
        # The UI must not claim downloading below the server's post-poll stage.
        self.assertIn("if (job.progress >= 0.8) return \"Downloading and validating audio…\";", self.source)
        self.assertIn("if (job.progress >= 0.35) return \"Generating instrumental music…\";", self.source)

    def test_resume_control_is_wired_to_the_resume_route(self):
        self.assertIn("\"Resume check\"", self.source)
        self.assertIn(f"/music/resume?from=${{musicJob.id}}", self.source)

    def test_dj_uses_one_persistent_audio_element(self):
        # The DJ timeline is driven by exactly one element declared once; a
        # second element or a recreated one would allow two sources to fight.
        self.assertEqual(self.source.count("document.querySelector(\"#dj-audio\")"), 1)
        self.assertIn("djPlayOnce(epoch, speech.url)", self.source)
        self.assertIn("djPlayOnce(epoch, track.audio.url)", self.source)
        # Speech always precedes music on that single element.
        speech_branch = self.source.split("async function djEngine")[1]
        self.assertLess(speech_branch.index("djPlayOnce(epoch, speech.url)"),
                        speech_branch.index("djPlayOnce(epoch, track.audio.url)"),
                        "speech must be played before music inside the engine")

    def test_dj_play_once_never_resolves_on_a_transient_play_rejection(self):
        # A navigation teardown (reload mid-queue) rejects the in-flight
        # audio play(); resolving djPlayOnce there let the engine post phase
        # transitions and fast-forward the whole queue while nothing was
        # audible. The rejection path must retry briefly (bounded) instead of
        # completing the segment; a scheduled retry must re-check the captured
        # epoch (a pause may have advanced it while keeping the src); and a
        # play-PERMISSION rejection must never complete the segment (it waits
        # for a user action instead).
        play_once = self.source.split("function djPlayOnce")[1].split(
            "async function djAdvanceOnce")[0]
        catch = play_once.split("djAudio.play().catch")[1]
        self.assertIn("setTimeout(startPlay, 350)", catch,
                      "transient play() rejection must retry, not resolve")
        self.assertIn('attempts >= 6', catch,
                      "retries must be bounded so a genuinely broken media "
                      "path still degrades to best-effort completion")
        # The first-rejection path must not complete the segment: resolve()
        # may only appear inside the bounded-exhausted branch, not as the
        # direct handler action. (The catch's first statements start with the
        # epoch guard and the retry counter.)
        self.assertNotIn("resolve()", catch[:90],
                         "the direct rejection path must retry, never resolve")
        start_play = play_once.split("const startPlay =")[1].split("startPlay();")[0]
        self.assertLess(start_play.index('epoch !== djEpoch'),
                        start_play.index('djAudio.play().catch'),
                        "a scheduled retry must re-check its captured epoch "
                        "before touching the player (pause keeps the src)")
        self.assertIn('err.name === "NotAllowedError"', play_once,
                      "play-permission rejection must be distinguished")
        blocked = play_once.split('err.name === "NotAllowedError"')[1].split(
            "if (++attempts")[0]
        self.assertNotIn("resolve()", blocked,
                         "a blocked segment must stay pending (user action "
                         "recovers it) instead of being treated as ended")

    def test_dj_audio_exclusivity_guards_exist(self):
        # Manual library players must never be audible while the DJ timeline
        # owns the audio: djPlayOnce pauses every other player when a DJ
        # segment starts, and a capture-phase document listener stops manual
        # players from starting while the DJ is active.
        play_once = self.source.split("function djPlayOnce")[1].split(
            "async function djAdvanceOnce")[0]
        self.assertIn('document.querySelectorAll("audio")', play_once)
        self.assertIn("el.pause()", play_once)
        self.assertIn('el !== djAudio', play_once)
        after_engine = self.source.split("djEngine();")[1]
        self.assertIn('document.addEventListener("play"', after_engine)
        self.assertIn('el.tagName !== "AUDIO"', after_engine)
        self.assertIn('el === djAudio', after_engine)
        self.assertIn("!djActive", after_engine)
        self.assertIn("el.pause()", after_engine)
        self.assertIn('djActive = false', self.source.split("let djPhase")[1])
        engine = self.source.split("async function djEngine")[1]
        self.assertIn('djActive = !!', engine,
                      "the engine must keep the DJ-active flag in sync "
                      "with the server playback state")

    def test_dj_retry_button_is_explicit_and_never_automatic(self):
        # A failed DJ introduction is only regenerated through the explicit
        # card button + endpoint; the engine loop never POSTs it, and the
        # button only appears for a FAILED speech job on a track without
        # commentary (replay/reload/advance stay silent server-side).
        card = self.source.split("function buildTrackCard")[1].split("function renderLibrary")[0]
        self.assertIn('"Retry DJ introduction"', card)
        self.assertEqual(card.count('"/api/playback/speech"'), 1,
                         "the retry endpoint is referenced only by the card button")
        self.assertIn('latestSpeech.state === "failed"', card)
        self.assertIn('!track.speech', card)
        engine = self.source.split("async function djEngine")[1].split("async function djStart")[0]
        self.assertNotIn('"/api/playback/speech"', engine,
                         "the engine must never invoke the retry automatically")
        # A REJECTED retry request creates no job, so the card is not rebuilt:
        # the catch must restore the button (permanent disable otherwise).
        catch_block = card.split('retrySpeech.addEventListener("click"')[1]
        self.assertIn("retrySpeech.disabled = false;", catch_block,
                      "a rejected retry must restore the button to a usable state")
        self.assertNotIn('latestSpeech.state === "failed" && !track.speech',
                         catch_block.split("await syncAfterMutation()")[0],
                         "the catch must not re-derive the disabled state from "
                         "an unchanged snapshot")

    def test_dj_engine_never_submits_generation_itself(self):
        # Polling/reloads must never trigger generation: only user actions POST
        # start/advance; the engine only posts the phase transition and reads
        # already-generated media. Advance is called by user actions.
        engine = self.source.split("async function djEngine")[1].split("async function djStart")[0]
        self.assertNotIn("\"/api/playback/start\"", engine)
        self.assertNotIn("\"/api/playback/advance\"", engine.split("async function djNext")[0])
        self.assertNotIn("\"/api/playback/queue\"", engine)
        for forbidden in ["request(\"/api/tracks", "generate", "lyrics"]:
            self.assertNotIn(forbidden, engine)

    def test_dj_stale_callbacks_are_epoch_guarded(self):
        # A late 'ended'/'error' callback from a skipped phase must not restart
        # the wrong audio: every continuation rechecks the epoch it captured.
        self.assertIn("const epoch = djEpoch;", self.source)
        self.assertIn("if (epoch === djEpoch)", self.source)
        self.assertIn("djAudio.addEventListener(\"dj-interrupt\", interrupt, {once: true});", self.source)

    def test_dj_pause_preserves_position_and_halts_the_engine(self):
        # Pause must freeze the element (no src wipe) so Resume continues, and
        # the engine must not re-enter playback before the server acknowledges.
        pause = self.source.split("async function djPause")[1].split("async function djResume")[0]
        self.assertIn("djAudio.pause();", pause)
        self.assertNotIn("removeAttribute(\"src\")", pause)
        self.assertIn("djHalted = true;", pause)
        self.assertIn("if (djHalted) {", self.source)

    def test_dj_render_shows_phase_and_controls(self):
        render = self.source.split("function renderDj")[1]
        self.assertIn("\"DJ speech\"", render)
        self.assertIn("`Now playing ${", render)
        self.assertIn("djReady()", self.source)

    def test_dj_advance_coalescing_and_fifo(self):
        # One Skip must advance at most once: when an automatic advance for
        # the SAME track is already in flight, a user Skip coalesces into it.
        # Rapid user skips still chain (serialized), and every user intent
        # travels in issue order so separate connections cannot reorder.
        self.assertIn("prior.automatic && prior.trackId === currentTrackId", self.source)
        self.assertIn("djAdvanceInFlight = {promise", self.source)
        # The in-flight slot is cleared inside the promise (try/finally) so a
        # failed advance has NO unobserved orphan promise.finally(...) whose
        # rejection could become an unhandled rejection.
        advance = self.source.split("async function djAdvanceOnce")[1].split("// User intents")[0]
        self.assertIn("} finally {", advance)
        self.assertNotIn("promise.finally(", advance)
        # The prior-await must sit INSIDE the try: if the awaited earlier
        # advance rejects, this promise still reaches its finally and clears
        # the in-flight slot — otherwise a rejected queued advance poisons
        # every subsequent advance (verified by the Node micro-test and the
        # S8 browser scenario).
        self.assertLess(advance.index("try {"),
                        advance.index("if (prior) await prior.promise"),
                        "prior-await must be inside the try/finally")
        self.assertIn("let djUserChain = Promise.resolve();", self.source)
        self.assertIn("djUserChain = next.catch(() => {});", self.source)
        skip = self.source.split("async function djSkip")[1].split("function djStatusIdleDone")[0]
        self.assertIn("djAdvanceOnce(current ? current.id : null, false)", skip)

    def test_dj_engine_survives_transient_failures(self):
        # A network or stale-409 failure must not kill the timeline loop.
        engine = self.source.split("async function djEngine")[1].split("async function djStart")[0]
        self.assertIn("catch (error) {", engine)
        self.assertIn("must never kill the timeline loop", engine)
        self.assertIn("await djSleep(250);", engine)

    def test_dj_phase_and_pause_carry_the_current_track(self):
        # The server rejects a stale transition (phase/pause for a track the
        # user has already skipped) — the browser must always tag its phase
        # and pause requests with the CURRENT track id.
        engine = self.source.split("async function djEngine")[1]
        self.assertIn("track_id: track.id", engine)
        pause = self.source.split("async function djPause")[1].split("async function djResume")[0]
        self.assertIn("track_id: trackId", pause)

    def test_dj_pause_failure_does_not_halt_the_engine(self):
        # A failed pause (network error) must un-halt the controller so the
        # timeline cannot be permanently frozen by a rejected request.
        pause = self.source.split("async function djPause")[1].split("async function djResume")[0]
        self.assertIn("djHalted = false;", pause)

    def test_vocal_controls_are_wired_and_music_label_is_mode_aware(self):
        self.assertIn("\"Generate lyrics\"", self.source)
        self.assertIn("Generate new lyrics", self.source)
        self.assertIn("\"Generate vocal song\"", self.source)
        self.assertIn("Generate new vocal song", self.source)
        self.assertIn("`/api/tracks/${track.id}/lyrics`", self.source)
        self.assertIn("Generating vocal music…", self.source)
        self.assertIn("Song draft · lyrics and vocal generation pending.", self.source)

    def test_vocal_lyrics_chain_never_re_submits_music(self):
        # The one-click vocal chain must fire only for a lyrics job observed
        # succeeding AFTER the page loaded (seeded set), and only when no music
        # job exists for the track yet. Reloads — even mid-chain — and retries
        # stay manual.
        self.assertIn("autoChained.add(job.id)", self.source)
        # Seeding includes every non-terminal-failed (pending or succeeded)
        # text job from the first snapshot, so reloading mid-chain cannot
        # continue an auto-chain either.
        self.assertIn("if (job.kind === \"text\" && job.state !== \"failed\") autoChained.add(job.id)", self.source)
        self.assertIn("session.jobs.some(job => job.track_id === track.id && job.kind === \"music\")", self.source)
        self.assertIn("track.settings.mode !== \"vocal\" || track.audio", self.source)

    def test_rejected_lyrics_request_re_enables_the_button(self):
        # A rejected lyrics POST (429 while another track holds the single text
        # slot, 502, ...) creates no job, so the per-track diff would skip
        # rebuilding the card: the handler must restore label and enabled state.
        mutation = self.source.split("retryLyrics.addEventListener")[1].split("});\n    detail.append(retryLyrics)")[0]
        self.assertIn("retryLyrics.disabled = !textConfigured;", mutation)
        self.assertIn("retryLyrics.textContent = previousLabel;", mutation)
        self.assertIn("\"Requesting…\"", mutation)

    def test_music_stage_thresholds_match_server_progress_bounds(self):
        server = (ROOT / "jukebox/sessions.py").read_text(encoding="utf-8")
        poll_cap = re.search(r"with_progress\(min\(job\.progress \+ \.05, (0?\.\d+)\)\)", server)
        self.assertIsNotNone(poll_cap, "poll progress cap must exist server-side")
        cap = float(poll_cap.group(1))
        self.assertLess(cap, 0.8, "polling progress must stay below the UI downloading stage")
        before_download = server.split("audio = providers.download_music(result)")[0]
        self.assertIn("with_progress(.9)", before_download,
                      "downloading stage must be set only after a successful poll")


class FrontendRetryBehaviorTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"), "Optional Node runtime is unavailable")
    def test_dj_retry_permission_and_manual_audio_exclusivity(self):
        result = subprocess.run(
            [shutil.which("node"), str(ROOT / "tests/frontend_dj_probe.cjs"),
             str(ROOT / "jukebox/web/app.js")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    @unittest.skipUnless(shutil.which("node"), "Optional Node runtime is unavailable")
    def test_rejected_controls_recover_without_redraw_or_resubmission(self):
        result = subprocess.run(
            [shutil.which("node"), str(ROOT / "tests/frontend_retry_probe.cjs"),
             str(ROOT / "jukebox/web/app.js")],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
