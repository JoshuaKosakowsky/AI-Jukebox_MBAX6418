"""Approved local catalog, isolation and failure handling; no provider calls."""
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import time
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
import wave

from fastapi.testclient import TestClient
from PIL import Image

from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.contracts import Track
from jukebox.providers import MediaBytes
from jukebox.samples import ERROR_MESSAGE, SampleLibraryError, load_samples
from jukebox.sessions import MAX_MEDIA_BYTES, SESSION_COOKIE, SESSION_SECONDS, SessionFailure, SessionStore


def fixture(root, name="Blue fixture", *, vocal=False, color="blue"):
    """Synthetic silence/solid cover; never represents a class-generated sample."""
    folder = root / "assets/samples"
    folder.mkdir(parents=True, exist_ok=True)
    stem = str(uuid4())
    with wave.open(str(folder / f"{stem}.wav"), "wb") as audio:
        audio.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
        audio.writeframes(b"\x00\x00" * 80000)
    Image.new("RGB", (512, 512), color).save(folder / f"{stem}.png")
    return {"id": stem, "title": name, "audio": f"assets/samples/{stem}.wav",
            "cover": f"assets/samples/{stem}.png", "instrumental": not vocal,
            "lyrics": "Synthetic test lyrics only" if vocal else None,
            "generated_at": "2026-10-30", "generation_notes": "Synthetic offline fixture; not class provenance.",
            "generated_with": {"music": "ACE-Step 1.5 XL Turbo", "cover": "FLUX.2 klein 4B",
                               **({"lyrics": "Qwen3.6-35B-A3B"} if vocal else {})}}


def manifest(root, records):
    folder = root / "assets/samples"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "manifest.json").write_text(json.dumps({"samples": records}))


class SampleCatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def load(self):
        return load_samples(self.root, max_bytes=MAX_MEDIA_BYTES)

    def rejected(self):
        with self.assertRaises(SampleLibraryError) as caught:
            self.load()
        self.assertEqual(str(caught.exception), ERROR_MESSAGE)

    def test_empty_manifest_does_not_scan_candidates(self):
        fixture(self.root)
        (self.root / "assets/samples/private.candidate.json").write_text("not valid JSON")
        manifest(self.root, [])
        self.assertEqual(self.load(), ())

    def test_instrumental_and_vocal_are_ready_with_matching_bytes_and_metadata(self):
        records = [fixture(self.root), fixture(self.root, "Orange fixture", vocal=True, color="orange")]
        records[0].update(style="Ambient piano", mood="Calm")
        manifest(self.root, records)
        loaded = self.load()
        for sample, record in zip(loaded, records):
            self.assertEqual(str(sample.track.id), record["id"])
            self.assertEqual(sample.track.title, record["title"])
            self.assertEqual(sample.track.status, "ready")
            self.assertEqual(sample.track.settings.duration_seconds, 10)
            self.assertEqual(sample.track.lyrics, record["lyrics"])
            self.assertEqual(sample.audio.content, (self.root / record["audio"]).read_bytes())
            self.assertEqual(sample.cover.content, (self.root / record["cover"]).read_bytes())
        self.assertEqual(loaded[0].track.settings.style, "Ambient piano")
        self.assertEqual(loaded[1].track.settings.mode, "vocal")

    def test_bad_metadata_and_provenance_reject_entire_catalog(self):
        record = fixture(self.root)
        for change in ({"id": "invalid"}, {"title": " "}, {"instrumental": "true"},
                       {"generated_at": "yesterday"}, {"generated_with": {}}, {"generation_notes": " "},
                       {"instrumental": False}, {"lyrics": "Not instrumental"},
                       {"extra": "private-marker"}, {"style": "x" * 121}):
            with self.subTest(change=change):
                manifest(self.root, [{**record, **change}])
                self.rejected()

    def test_invalid_vocal_lyrics_provenance_rejected(self):
        record = fixture(self.root, vocal=True)
        for lyrics, models in [(" ", record["generated_with"]), (record["lyrics"], {"music": "ACE-Step 1.5 XL Turbo", "cover": "FLUX.2 klein 4B"})]:
            manifest(self.root, [{**record, "lyrics": lyrics, "generated_with": models}])
            self.rejected()

    def test_missing_corrupt_truncated_and_wrong_shape_assets_reject(self):
        for kind in ("missing", "bad-wav", "truncated", "bad-png", "wrong-size", "short"):
            with self.subTest(kind=kind):
                record = fixture(self.root)
                manifest(self.root, [record])
                audio, cover = self.root / record["audio"], self.root / record["cover"]
                if kind == "missing": audio.unlink()
                if kind == "bad-wav": audio.write_bytes(b"RIFF" + b"private-marker" * 8)
                if kind == "truncated": audio.write_bytes(audio.read_bytes()[:-10])
                if kind == "bad-png": cover.write_bytes(b"private-marker")
                if kind == "wrong-size": Image.new("RGB", (32, 32)).save(cover)
                if kind == "short":
                    with wave.open(str(audio), "wb") as wav:
                        wav.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
                        wav.writeframes(b"\x00\x00" * 8000)
                self.rejected()

    def test_manifest_and_asset_size_and_catalog_budget_are_bounded(self):
        record = fixture(self.root)
        manifest(self.root, [record])
        with self.assertRaises(SampleLibraryError):
            load_samples(self.root, max_bytes=1)
        with patch("jukebox.samples.MAX_ASSET_BYTES", 100): self.rejected()
        manifest(self.root, [fixture(self.root) for _ in range(4)])
        self.rejected()
        (self.root / "assets/samples/manifest.json").write_bytes(b" " * 128001)
        self.rejected()

    def test_malformed_and_missing_manifests_have_fixed_safe_error(self):
        self.rejected()
        manifest(self.root, [])
        for value in (b"{private-marker", b"[]", b'{"samples": null}', b'\xff', b'[' * 2000):
            (self.root / "assets/samples/manifest.json").write_bytes(value)
            self.rejected()

    def test_paths_cannot_escape_or_use_unexpected_formats(self):
        record = fixture(self.root)
        for name in ("/private/secret.wav", "assets/samples/../../secret.wav", "assets\\samples\\secret.wav", "README.md", "assets/samples/secret.mp3"):
            with self.subTest(name=name):
                manifest(self.root, [{**record, "audio": name}])
                self.rejected()

    def test_symlinks_cannot_escape_catalog_and_aliases_cannot_duplicate_assets(self):
        record = fixture(self.root)
        outside = self.root / "outside.wav"
        outside.write_bytes((self.root / record["audio"]).read_bytes())
        link = self.root / "assets/samples/link.wav"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("Symlinks unavailable on this platform")
        manifest(self.root, [{**record, "audio": "assets/samples/link.wav"}])
        self.rejected()
        link.unlink()
        link.symlink_to(self.root / record["audio"])
        other = fixture(self.root)
        manifest(self.root, [record, {**other, "audio": "assets/samples/link.wav"}])
        self.rejected()
        (self.root / "assets/samples/manifest.json").unlink()
        (self.root / "outside.json").write_text('{"samples": []}')
        (self.root / "assets/samples/manifest.json").symlink_to(self.root / "outside.json")
        self.rejected()

    def test_duplicate_ids_and_assets_reject_before_session_allocation(self):
        first, second = fixture(self.root), fixture(self.root)
        for field in ("id", "audio", "cover"):
            manifest(self.root, [first, {**second, field: first[field]}])
            self.rejected()


class SampleHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        records = [fixture(self.root), fixture(self.root, "Orange fixture", vocal=True, color="orange")]
        manifest(self.root, records)
        (self.root / "jukebox/web").mkdir(parents=True)
        self.root_patch = patch("jukebox.app.ROOT", self.root)
        self.root_patch.start()
        self.addCleanup(self.root_patch.stop)
        self.request_patch = patch("jukebox.providers.ClassProviders._request", side_effect=AssertionError("No provider request permitted"))
        self.provider_request = self.request_patch.start()
        self.addCleanup(self.request_patch.stop)

    def test_new_session_media_reload_and_foreign_isolation_without_providers(self):
        app = create_app(Settings.load(None, {}))
        with TestClient(app, base_url="http://localhost") as client:
            self.assertEqual(client.get("/api/status").json()["sample_library"], {"count": 2, "error": None})
            response = client.get("/api/session")
            self.assertIn("HttpOnly", response.headers["set-cookie"])
            snapshot = response.json()
            self.assertEqual(len(snapshot["tracks"]), 2)
            self.assertEqual(snapshot["jobs"], [])
            for track in snapshot["tracks"]:
                for kind, mime in (("audio", "audio/wav"), ("cover", "image/png")):
                    media = client.get(track[kind]["url"])
                    self.assertEqual(media.status_code, 200)
                    self.assertEqual(media.headers["content-type"], mime)
                    self.assertEqual(media.headers["cache-control"], "no-store")
            self.assertEqual(client.get("/api/session").json(), snapshot)
            client.cookies.clear()
            new = client.get("/api/session").json()
            self.assertEqual([t["id"] for t in new["tracks"]], [t["id"] for t in snapshot["tracks"]])
            for old, fresh in zip(snapshot["tracks"], new["tracks"]):
                self.assertNotEqual(old["audio"]["url"], fresh["audio"]["url"])
                self.assertEqual(client.get(old["audio"]["url"]).status_code, 404)
                self.assertEqual(client.get(old["cover"]["url"]).status_code, 404)
        self.provider_request.assert_not_called()

    def test_bad_catalog_is_all_or_nothing_and_creation_still_works(self):
        record = json.loads((self.root / "assets/samples/manifest.json").read_text())["samples"][1]
        (self.root / record["cover"]).unlink()
        settings = Settings.load(None, {"JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1", "JUKEBOX_ART_API_KEY": "offline-fixture-only"})
        app = create_app(settings)
        with patch("jukebox.providers.ClassProviders.cover", return_value=MediaBytes(b"fixture", "image/png")):
            with TestClient(app, base_url="http://localhost") as client:
                self.assertEqual(client.get("/api/status").json()["sample_library"], {"count": 0, "error": ERROR_MESSAGE})
                self.assertEqual(client.get("/api/session").json()["tracks"], [])
                created = client.post("/api/tracks", json={"title": "Still usable", "settings": {"style": "Piano", "mood": "Calm", "duration_seconds": 10}})
                self.assertEqual(created.status_code, 202)
                self.assertEqual(len(client.get("/api/session").json()["tracks"]), 1)
        self.provider_request.assert_not_called()

    def test_expiry_reseeds_and_session_mutation_does_not_change_catalog(self):
        store = SessionStore(load_samples(self.root, max_bytes=MAX_MEDIA_BYTES))
        first = store.resolve(None)
        original = store.snapshot(first)
        first.tracks.clear()
        first.media.clear()
        first.touched = time.monotonic() - SESSION_SECONDS - 1
        replacement = store.resolve(first.token)
        self.assertNotEqual(first.token, replacement.token)
        self.assertNotIn(first.token, store.sessions)
        self.assertEqual([t.id for t in store.snapshot(replacement).tracks], [t.id for t in original.tracks])
        self.assertFalse(replacement.jobs)

    def test_generation_alongside_samples_and_replacement_stay_session_local(self):
        settings = Settings.load(None, {"JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1", "JUKEBOX_ART_API_KEY": "offline-fixture-only"})
        app = create_app(settings)
        with patch("jukebox.providers.ClassProviders.cover", return_value=MediaBytes(b"new-cover", "image/png")) as cover:
            with TestClient(app, base_url="http://localhost") as client:
                initial = client.get("/api/session").json()
                token = client.cookies.get(SESSION_COOKIE)
                sample = initial["tracks"][0]
                client.cookies.clear()
                other = client.get("/api/session").json()
                other_token = client.cookies.get(SESSION_COOKIE)
                client.cookies.clear()
                client.cookies.set(SESSION_COOKIE, token)
                created = client.post("/api/tracks", json={"title": "New draft", "settings": {"style": "Piano", "mood": "Calm", "duration_seconds": 10}})
                self.assertEqual(created.status_code, 202)
                before = client.get("/api/session").json()
                self.assertEqual(before["tracks"][:2], initial["tracks"])
                self.assertEqual(len(before["tracks"]), 3)
                self.assertEqual(client.post(f'/api/tracks/{sample["id"]}/cover', json={}).status_code, 202)
                updated = client.get("/api/session").json()
                self.assertEqual(updated["tracks"][0]["audio"], sample["audio"])
                self.assertNotEqual(updated["tracks"][0]["cover"], sample["cover"])
                self.assertEqual(client.get(sample["cover"]["url"]).status_code, 404)
                client.cookies.clear()
                client.cookies.set(SESSION_COOKIE, other_token)
                self.assertEqual(client.get("/api/session").json(), other)
                self.assertEqual(client.get(other["tracks"][0]["cover"]["url"]).status_code, 200)
                client.cookies.clear()
                fresh = client.get("/api/session").json()
                self.assertEqual(len(fresh["tracks"]), 2)
                self.assertNotEqual(client.get(fresh["tracks"][0]["cover"]["url"]).content, b"new-cover")
        self.assertEqual(cover.call_count, 2)
        self.provider_request.assert_not_called()

    def test_shared_catalog_counts_once_and_replaced_bytes_remain_budgeted(self):
        catalog = load_samples(self.root, max_bytes=MAX_MEDIA_BYTES)
        store = SessionStore(catalog)
        size = sum(len(s.audio.content) + len(s.cover.content) for s in catalog)
        with patch("jukebox.sessions.MAX_MEDIA_BYTES", size):
            first, second = store.resolve(None), store.resolve(None)
            self.assertEqual(store._media_bytes(), size)
            for session in (first, second):
                session.media.clear()
                session.tracks.clear()
            self.assertEqual(store._media_bytes(), size)
            # A deliberate new cover cannot consume bytes beyond retained samples.
            job = store.create_cover_track(first, "New", catalog[0].track.settings)
            store.generate_cover(first, job.id, Mock(cover=Mock(return_value=MediaBytes(b"new", "image/png"))))
            self.assertEqual(first.jobs[job.id].state, "failed")
        with patch("jukebox.sessions.MAX_MEDIA_BYTES", 1), self.assertRaises(SessionFailure):
            store.resolve(None)
        self.assertEqual(len(store.sessions), 2)

    def test_samples_count_towards_track_limit_without_orphan_job(self):
        store = SessionStore(load_samples(self.root, max_bytes=MAX_MEDIA_BYTES))
        session = store.resolve(None)
        with patch("jukebox.sessions.MAX_TRACKS", 2), self.assertRaises(SessionFailure):
            store.create_cover_track(session, "New", next(iter(session.tracks.values())).settings)
        self.assertEqual(len(session.tracks), 2)
        self.assertFalse(session.jobs)

    def test_dj_speech_counts_catalog_retained_after_session_media_are_gone(self):
        catalog = load_samples(self.root, max_bytes=MAX_MEDIA_BYTES)
        store = SessionStore(catalog)
        session = store.resolve(None)
        session.media.clear()
        session.tracks.clear()
        track = Track(title="DJ catalog capacity", settings=catalog[0].track.settings)
        session.tracks[track.id] = track
        job = store.request_dj_speech(session, track.id)
        size = sum(len(s.audio.content) + len(s.cover.content) for s in catalog)
        providers = Mock(text=Mock(return_value="Short introduction"),
                         speech=Mock(return_value=MediaBytes(b"new-speech", "audio/wav")))
        with patch("jukebox.sessions.MAX_MEDIA_BYTES", size):
            store.generate_dj_speech(session, job.id, providers)
        self.assertEqual(session.jobs[job.id].state, "failed")
        self.assertEqual(session.jobs[job.id].error.code, "generation_failed")
        self.assertIsNone(session.tracks[track.id].speech)
        self.assertFalse(session.media)
        self.assertEqual(store._media_bytes(), size)

    def test_loaded_samples_use_dj_queue_without_altering_original_media_or_other_sessions(self):
        settings = Settings.load(None, {
            "JUKEBOX_TEXT_ENDPOINT": "http://dobolyi.com:9001/v1", "JUKEBOX_TEXT_API_KEY": "offline-fixture-only",
            "JUKEBOX_SPEECH_ENDPOINT": "http://dobolyi.com:9008/v1", "JUKEBOX_SPEECH_API_KEY": "offline-fixture-only"})
        speech = load_samples(self.root, max_bytes=MAX_MEDIA_BYTES)[0].audio
        with patch("jukebox.providers.ClassProviders.text", return_value="Short introduction") as text, \
             patch("jukebox.providers.ClassProviders.speech", return_value=speech) as spoken:
            with TestClient(create_app(settings), base_url="http://localhost") as client:
                before = client.get("/api/session").json()
                for track in before["tracks"]:
                    self.assertEqual(client.post("/api/playback/queue", json={"track_id": track["id"]}).status_code, 200)
                for index, track in enumerate(before["tracks"]):
                    path = "/api/playback/start" if index == 0 else "/api/playback/advance"
                    self.assertEqual(client.post(path, json={}).status_code, 200)
                    current = client.get("/api/session").json()["tracks"][index]
                    self.assertEqual(current["audio"], track["audio"])
                    self.assertEqual(current["cover"], track["cover"])
                    self.assertEqual(client.get(current["speech"]["url"]).content, speech.content)
                    self.assertEqual(client.post("/api/playback/phase", json={"phase": "playing", "track_id": track["id"]}).status_code, 200)
                completed = client.get("/api/session").json()
                self.assertEqual([j["state"] for j in completed["jobs"]], ["succeeded", "succeeded"])
                self.assertEqual(text.call_count, 2)
                self.assertEqual(spoken.call_count, 2)
                self.assertTrue(all(call.kwargs == {"thinking": False} for call in text.call_args_list))
                client.cookies.clear()
                fresh = client.get("/api/session").json()
                self.assertEqual(len(fresh["tracks"]), 2)
                self.assertTrue(all(t["speech"] is None for t in fresh["tracks"]))
                self.assertFalse(fresh["jobs"])
                self.assertEqual(client.get(completed["tracks"][0]["speech"]["url"]).status_code, 404)
        self.provider_request.assert_not_called()
