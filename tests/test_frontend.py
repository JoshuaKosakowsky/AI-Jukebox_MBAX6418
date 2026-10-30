"""Static frontend regression guards for library rendering.

The repository deliberately has no Node build or JavaScript test runner (see
README), so these guards verify source-level invariants of jukebox/web/app.js
that protect against reintroducing destructive full-library rebuilds which
interrupt in-progress audio playback. They check structure, not runtime DOM
behavior; interactive browser verification is a documented teammate step.
"""
import re
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
        self.assertIn("promise.finally", self.source)
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
