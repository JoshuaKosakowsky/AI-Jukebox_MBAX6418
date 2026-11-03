"""Offline regressions for owner-reported seeking, queue editing and lyrics."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.contracts import Playback
from jukebox.sessions import SESSION_COOKIE

ROOT = Path(__file__).resolve().parents[1]


class PlaybackUxTests(unittest.TestCase):
    def setUp(self):
        self.guard = patch("jukebox.providers.ClassProviders._request",
                           side_effect=AssertionError("No provider calls"))
        self.guard.start()
        self.addCleanup(self.guard.stop)
        self.app = create_app(Settings.load(None, {}))
        self.client = TestClient(self.app, base_url="http://localhost")
        self.client.__enter__()
        self.addCleanup(self.client.__exit__, None, None, None)
        self.tracks = self.client.get("/api/session").json()["tracks"]
        self.store = self.app.state.sessions
        self.session = self.store.resolve(self.client.cookies.get(SESSION_COOKIE))
        self.ids = [track.id for track in self.session.tracks.values()]

    def queue(self):
        for identifier in self.ids:
            self.store.queue_playback(self.session, identifier)

    def remove(self, identifier):
        return self.client.post("/api/playback/queue/remove",
                                json={"track_id": str(identifier)})

    def test_native_media_full_head_and_byte_ranges(self):
        url = self.tracks[0]["audio"]["url"]
        full = self.client.get(url)
        self.assertEqual(full.status_code, 200)
        self.assertEqual(full.headers["accept-ranges"], "bytes")
        size = len(full.content)
        for requested, first, last in [
            ("bytes=0-31", 0, 31), ("bytes=100-", 100, size - 1),
            ("bytes=-64", size - 64, size - 1),
            (f"bytes={size - 8}-{size + 20}", size - 8, size - 1),
            (f"bytes=-{size + 100}", 0, size - 1),
        ]:
            with self.subTest(requested=requested):
                part = self.client.get(url, headers={"Range": requested})
                self.assertEqual(part.status_code, 206)
                self.assertEqual(part.content, full.content[first:last + 1])
                self.assertEqual(part.headers["content-range"], f"bytes {first}-{last}/{size}")
                self.assertEqual(int(part.headers["content-length"]), last - first + 1)
                self.assertEqual(part.headers["cache-control"], "no-store")
        head = self.client.head(url, headers={"Range": "bytes=0-31"})
        self.assertEqual(head.status_code, 200)
        self.assertEqual(head.content, b"")
        self.assertEqual(int(head.headers["content-length"]), size)

    def test_bad_ranges_and_foreign_media_cannot_disclose_bytes(self):
        url = self.tracks[0]["audio"]["url"]
        size = len(self.client.get(url).content)
        for requested in (f"bytes={size}-", "bytes=10-5", "bytes=-0", "bytes=-", "bytes=bad"):
            with self.subTest(requested=requested):
                result = self.client.get(url, headers={"Range": requested})
                self.assertEqual(result.status_code, 416)
                self.assertEqual(result.headers["content-range"], f"bytes */{size}")
                self.assertEqual(result.content, b"")
        for requested in ("items=0-1", "bytes=0-1,5-8"):
            self.assertEqual(self.client.get(url, headers={"Range": requested}).status_code, 200)
        # No server validator is advertised: conditional ranges fall back to
        # the complete representation instead of trusting a stale validator.
        conditional = self.client.get(url, headers={"Range": "bytes=0-31", "If-Range": '"old"'})
        self.assertEqual(conditional.status_code, 200)
        self.assertEqual(len(conditional.content), size)
        with TestClient(self.app, base_url="http://localhost") as other:
            foreign = other.get(url, headers={"Range": "bytes=0-31"})
            self.assertEqual(foreign.status_code, 404)
            self.assertNotIn("content-range", foreign.headers)

    def test_idle_queue_can_be_emptied_without_removing_library_or_generating(self):
        self.queue()
        media = dict(self.session.media)
        for identifier in self.ids:
            self.assertEqual(self.remove(identifier).status_code, 200)
        self.assertEqual(self.session.playback.queue, [])
        self.assertEqual(self.session.playback.state, "idle")
        self.assertEqual(self.session.playback.index, 0)
        self.assertEqual(list(self.session.tracks), self.ids)
        self.assertEqual(self.session.media, media)
        self.assertEqual(self.session.jobs, {})
        self.store.queue_playback(self.session, self.ids[0])
        self.assertEqual(self.session.playback.queue, [self.ids[0]])
        self.assertEqual(self.remove(uuid4()).status_code, 404)

    def test_active_queue_removal_preserves_current_song_and_index(self):
        self.queue()
        self.session.playback = Playback(state="playing", queue=self.ids,
                                         index=1, current_track_id=self.ids[1])
        self.assertEqual(self.remove(self.ids[0]).status_code, 200)
        self.assertEqual(self.session.playback.index, 0)
        self.assertEqual(self.session.playback.current_track_id, self.ids[1])
        self.assertEqual(self.remove(self.ids[2]).status_code, 200)
        before = self.session.playback.model_dump()
        self.assertEqual(self.remove(self.ids[1]).status_code, 409)
        self.assertEqual(self.session.playback.model_dump(), before)
        self.assertEqual(self.session.jobs, {})

    def test_paused_queue_removal_stays_paused_and_is_session_private(self):
        self.queue()
        self.session.playback = Playback(state="paused", paused_from="playing",
                                         queue=self.ids, index=0, current_track_id=self.ids[0])
        with TestClient(self.app, base_url="http://localhost") as other:
            result = other.post("/api/playback/queue/remove", json={"track_id": str(self.ids[2])})
            self.assertEqual(result.status_code, 404)
        self.assertEqual(self.remove(self.ids[2]).status_code, 200)
        self.assertEqual(self.session.playback.state, "paused")
        self.assertEqual(self.session.playback.paused_from, "playing")
        self.assertEqual(self.session.playback.current_track_id, self.ids[0])
        self.assertEqual(self.session.jobs, {})

    def test_display_lyrics_follow_owner_corrections_and_preserve_original_drafts(self):
        manifest = json.loads((ROOT / "assets/samples/manifest.json").read_text(encoding="utf-8"))
        samples = {row["title"]: row for row in manifest["samples"]}
        afterglow = samples["Afterglow Avenue"]["lyrics"]
        original = json.loads((ROOT / "assets/samples/afterglow-avenue.candidate.json").read_text(encoding="utf-8"))["sample"]["lyrics"]
        self.assertEqual(afterglow.splitlines(), original.splitlines()[:-3])
        antler = samples["Antlercover"]["lyrics"]
        self.assertIn("Coffee steam rises, keeping it tight.", antler)
        self.assertNotIn("cold gray light", antler)
        self.assertNotIn("Trying to blend in", antler)
        self.assertNotIn("Sarah", antler)
        original = json.loads((ROOT / "assets/samples/antlercover.candidate.json").read_text(encoding="utf-8"))["sample"]["lyrics"]
        self.assertIn("A gentle nod from Sarah down the hall", original)

    @unittest.skipUnless(shutil.which("node"), "Optional Node runtime unavailable")
    def test_production_seek_and_queue_handlers(self):
        result = subprocess.run([shutil.which("node"), str(ROOT / "tests/frontend_playback_ux_probe.cjs"),
                                 str(ROOT / "jukebox/web/app.js")],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
