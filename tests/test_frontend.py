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
        self.assertIn("function restoreAudio(card, saved)", self.source)
        self.assertIn("const audio = existing.querySelector(\"audio\");", self.source)
        self.assertIn("saved = audio && !audio.paused ? {time: audio.currentTime} : null", self.source)
        self.assertIn("audio.play()", self.source)
        self.assertIn("restoreAudio(card, saved)", self.source)

    def test_music_stage_text_matches_server_progress_stages(self):
        # The UI must not claim downloading below the server's post-poll stage.
        self.assertIn("if (job.progress >= 0.8) return \"Downloading and validating audio…\";", self.source)
        self.assertIn("if (job.progress >= 0.35) return \"Generating instrumental music…\";", self.source)

    def test_resume_control_is_wired_to_the_resume_route(self):
        self.assertIn("\"Resume check\"", self.source)
        self.assertIn(f"/music/resume?from=${{musicJob.id}}", self.source)

    def test_music_stage_thresholds_match_server_progress_bounds(self):
        server = (ROOT / "jukebox/sessions.py").read_text(encoding="utf-8")
        poll_cap = re.search(r"with_progress\(min\(job\.progress \+ \.05, (0?\.\d+)\)\)", server)
        self.assertIsNotNone(poll_cap, "poll progress cap must exist server-side")
        cap = float(poll_cap.group(1))
        self.assertLess(cap, 0.8, "polling progress must stay below the UI downloading stage")
        before_download = server.split("audio = providers.download_music(result)")[0]
        self.assertIn("with_progress(.9)", before_download,
                      "downloading stage must be set only after a successful poll")
