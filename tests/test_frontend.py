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
        # job exists for the track yet. Reloads and retries stay manual.
        self.assertIn("autoChained.add(job.id)", self.source)
        self.assertIn("if (job.kind === \"text\" && job.state === \"succeeded\") autoChained.add(job.id)", self.source)
        self.assertIn("session.jobs.some(job => job.track_id === track.id && job.kind === \"music\")", self.source)
        self.assertIn("track.settings.mode !== \"vocal\" || track.audio", self.source)

    def test_music_stage_thresholds_match_server_progress_bounds(self):
        server = (ROOT / "jukebox/sessions.py").read_text(encoding="utf-8")
        poll_cap = re.search(r"with_progress\(min\(job\.progress \+ \.05, (0?\.\d+)\)\)", server)
        self.assertIsNotNone(poll_cap, "poll progress cap must exist server-side")
        cap = float(poll_cap.group(1))
        self.assertLess(cap, 0.8, "polling progress must stay below the UI downloading stage")
        before_download = server.split("audio = providers.download_music(result)")[0]
        self.assertIn("with_progress(.9)", before_download,
                      "downloading stage must be set only after a successful poll")
