"""Offline cover integration through real HTTP routes; no class-service calls."""
from concurrent.futures import ThreadPoolExecutor
import io
from threading import Event
import time
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
import wave

from fastapi.testclient import TestClient
from PIL import Image

from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.contracts import MediaRef, Playback, SafeError, SongSettings, Track
from jukebox.providers import MediaBytes, ProviderFailure
from jukebox.sessions import SESSION_COOKIE, SESSION_SECONDS, SessionFailure, SessionStore


def png(color):
    content = io.BytesIO()
    Image.new("RGB", (512, 512), color).save(content, format="PNG")
    return MediaBytes(content.getvalue(), "image/png")


def art_settings():
    return Settings.load(None, {"JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1",
                                "JUKEBOX_ART_API_KEY": "private-offline-test-marker"})


def body(title="Moonlit lake", style="Ambient piano", mood="Reflective"):
    return {"title": title, "settings": {"style": style, "mood": mood, "duration_seconds": 30, "mode": "instrumental"}}


class CoverHttpTests(unittest.TestCase):
    def test_two_tracks_keep_distinct_covers_and_reload_without_regeneration(self):
        with patch("jukebox.providers.ClassProviders.cover", side_effect=[png("blue"), png("orange")]) as cover:
            with TestClient(create_app(art_settings()), base_url="http://localhost") as client:
                response = client.get("/api/session")
                self.assertIn("HttpOnly", response.headers["set-cookie"])
                self.assertIn("SameSite=strict", response.headers["set-cookie"])
                jobs = [client.post("/api/tracks", json=data) for data in (
                    body(), body("Desert sunrise", "Funk", "Energetic"))]
                self.assertTrue(all(response.status_code == 202 for response in jobs))
                self.assertTrue(all(response.json()["state"] == "queued" for response in jobs))
                snapshot = client.get("/api/session").json()
                self.assertEqual([track["title"] for track in snapshot["tracks"]], ["Moonlit lake", "Desert sunrise"])
                self.assertEqual([job["state"] for job in snapshot["jobs"]], ["succeeded", "succeeded"])
                self.assertEqual({job["track_id"] for job in snapshot["jobs"]}, {track["id"] for track in snapshot["tracks"]})
                self.assertEqual(len({track["cover"]["id"] for track in snapshot["tracks"]}), 2)
                for track, color in zip(snapshot["tracks"], [(0, 0, 255), (255, 165, 0)]):
                    response = client.get(track["cover"]["url"])
                    self.assertEqual(response.headers["content-type"], "image/png")
                    self.assertEqual(response.headers["cache-control"], "no-store")
                    with Image.open(io.BytesIO(response.content)) as image:
                        image.load()
                        self.assertEqual(image.size, (512, 512))
                        self.assertEqual(image.getpixel((0, 0)), color)
                client.get("/")
                self.assertEqual(client.get("/api/session").json(), snapshot)
                self.assertEqual(cover.call_count, 2)
                for prompt, data in zip([call.args[0] for call in cover.call_args_list], [body(), body("Desert sunrise", "Funk", "Energetic")]):
                    for value in [data["title"], data["settings"]["style"], data["settings"]["mood"]]:
                        self.assertIn(value, prompt)
                self.assertNotIn("private-offline-test-marker", str(snapshot))

    def test_browser_sessions_cannot_read_or_change_each_others_track_or_media(self):
        app = create_app(art_settings())
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")) as cover:
            with TestClient(app, base_url="http://localhost") as first:
                first.post("/api/tracks", json=body())
                track = first.get("/api/session").json()["tracks"][0]
                token = first.cookies.get(SESSION_COOKIE)
                first.cookies.clear()
                self.assertEqual(first.get("/api/session").json()["tracks"], [])
                self.assertNotEqual(first.cookies.get(SESSION_COOKIE), token)
                self.assertEqual(first.get(track["cover"]["url"]).status_code, 404)
                self.assertEqual(first.post(f'/api/tracks/{track["id"]}/cover', json={}).status_code, 404)
                self.assertEqual(cover.call_count, 1)

    def test_failure_preserves_audio_old_cover_other_tracks_and_retry_uses_new_job(self):
        app = create_app(art_settings())
        with patch("jukebox.providers.ClassProviders.cover", side_effect=[png("blue"), png("green"),
                ProviderFailure(SafeError(code="timeout", message="Art request timed out.", retryable=True)), png("orange")]) as cover:
            with TestClient(app, base_url="http://localhost") as client:
                client.post("/api/tracks", json=body())
                client.post("/api/tracks", json=body("Other"))
                session = app.state.sessions.sessions[client.cookies.get(SESSION_COOKIE)]
                track = next(iter(session.tracks.values()))
                audio_id = uuid4()
                audio = MediaRef(id=audio_id, url=f"/api/media/{audio_id}", content_type="audio/wav")
                buffer = io.BytesIO()
                with wave.open(buffer, "wb") as wav:
                    wav.setparams((1, 2, 8000, 0, "NONE", "not compressed"))
                    wav.writeframes(b"\x01\x00" * 800)
                session.media[audio_id] = MediaBytes(buffer.getvalue(), "audio/wav")
                session.tracks[track.id] = Track.model_validate({**track.model_dump(), "audio": audio, "status": "ready", "lyrics": "Existing lyrics"})
                session.playback = Playback(state="playing", queue=[track.id], current_track_id=track.id)
                before = app.state.sessions.snapshot(session)
                failed = client.post(f"/api/tracks/{track.id}/cover", json={})
                after = client.get("/api/session").json()
                self.assertEqual(after["tracks"], before.model_dump(mode="json")["tracks"])
                self.assertEqual(after["playback"], before.model_dump(mode="json")["playback"])
                self.assertEqual(after["jobs"][-1]["state"], "failed")
                self.assertTrue(after["jobs"][-1]["error"]["retryable"])
                retry = client.post(f"/api/tracks/{track.id}/cover", json={})
                final = client.get("/api/session").json()
                self.assertNotEqual(failed.json()["id"], retry.json()["id"])
                self.assertEqual(final["tracks"][0]["audio"], audio.model_dump(mode="json"))
                self.assertEqual(final["tracks"][0]["lyrics"], "Existing lyrics")
                self.assertEqual(final["tracks"][0]["status"], "ready")
                self.assertEqual(final["tracks"][1], before.model_dump(mode="json")["tracks"][1])
                self.assertNotEqual(final["tracks"][0]["cover"], before.model_dump(mode="json")["tracks"][0]["cover"])
                self.assertEqual(client.get(track.cover.url).status_code, 404)
                self.assertEqual(client.get(audio.url).content, buffer.getvalue())
                self.assertEqual(cover.call_count, 4)

    def test_running_job_is_visible_duplicate_is_rejected_and_no_poll_resubmits(self):
        entered, release = Event(), Event()
        def delayed(prompt):
            entered.set()
            if not release.wait(5):
                raise AssertionError("Test worker was not released")
            return png("blue")
        with patch("jukebox.providers.ClassProviders.cover", side_effect=delayed) as cover:
            with TestClient(create_app(art_settings()), base_url="http://localhost") as client:
                client.get("/api/session")
                with ThreadPoolExecutor(max_workers=1) as executor:
                    pending = executor.submit(client.post, "/api/tracks", json=body())
                    try:
                        self.assertTrue(entered.wait(5))
                        snapshot = client.get("/api/session").json()
                        self.assertEqual(snapshot["jobs"][0]["state"], "running")
                        identifier = snapshot["tracks"][0]["id"]
                        duplicate = client.post(f"/api/tracks/{identifier}/cover", json={})
                        self.assertEqual(duplicate.status_code, 409)
                        client.get("/api/session")
                        self.assertEqual(cover.call_count, 1)
                    finally:
                        release.set()
                    self.assertEqual(pending.result(timeout=5).status_code, 202)

    def test_missing_art_and_bad_inputs_never_invoke_providers(self):
        with patch("jukebox.providers.ClassProviders.cover", side_effect=AssertionError("No service call")):
            with TestClient(create_app(Settings.load(None, {})), base_url="http://localhost") as client:
                self.assertFalse(client.get("/api/status").json()["cover_generation_available"])
                self.assertEqual(client.post("/api/tracks", json=body()).status_code, 502)
                self.assertEqual(client.get("/api/session").json()["tracks"], [])
            with TestClient(create_app(art_settings()), base_url="http://localhost") as client:
                for data in [body(title="  "), body(style=""), body(mood="x" * 121), {**body(), "provider_url": "private"}]:
                    self.assertEqual(client.post("/api/tracks", json=data).status_code, 422)
                self.assertEqual(client.post("/api/tracks/not-a-uuid/cover", json={}).status_code, 422)
                self.assertEqual(client.post(f"/api/tracks/{uuid4()}/cover", json={}).status_code, 404)
                self.assertEqual(client.post("/api/tracks", json=body(), headers={"origin": "http://evil.example"}).status_code, 403)
                self.assertEqual(client.get("/api/session").json()["tracks"], [])

    def test_unexpected_failure_is_sanitized_and_app_restart_clears_library(self):
        with patch("jukebox.providers.ClassProviders.cover", side_effect=RuntimeError("private-offline-test-marker")):
            with TestClient(create_app(art_settings()), base_url="http://localhost") as client:
                client.post("/api/tracks", json=body())
                snapshot = client.get("/api/session").json()
                self.assertEqual(snapshot["jobs"][0]["state"], "failed")
                self.assertNotIn("private-offline-test-marker", str(snapshot))
                old_cookie = client.cookies.get(SESSION_COOKIE)
            with TestClient(create_app(art_settings()), base_url="http://localhost") as client:
                client.cookies.set(SESSION_COOKIE, old_cookie)
                self.assertEqual(client.get("/api/session").json()["tracks"], [])


class CoverStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.session = self.store.resolve(None)
        self.settings = SongSettings(style="Piano", mood="Calm", duration_seconds=30)

    def test_out_of_order_completion_attaches_images_to_original_track_ids(self):
        first = self.store.create_cover_track(self.session, "Blue lake", self.settings)
        second = self.store.create_cover_track(self.session, "Orange desert", self.settings)
        self.store.generate_cover(self.session, second.id, Mock(cover=Mock(return_value=png("orange"))))
        self.store.generate_cover(self.session, first.id, Mock(cover=Mock(return_value=png("blue"))))
        for job, expected in [(first, png("blue")), (second, png("orange"))]:
            ref = self.session.tracks[job.track_id].cover
            self.assertEqual(self.store.get_media(self.session, ref.id), expected)
        self.assertFalse(self.session.active)

    def test_capacity_rejection_has_no_orphan_track_or_job_and_slots_are_released(self):
        first = self.store.create_cover_track(self.session, "One", self.settings)
        self.store.create_cover_track(self.session, "Two", self.settings)
        with self.assertRaises(SessionFailure) as caught:
            self.store.create_cover_track(self.session, "Three", self.settings)
        self.assertEqual(caught.exception.status, 429)
        self.assertEqual(len(self.session.tracks), 2)
        self.assertEqual(len(self.session.jobs), 2)
        self.store.generate_cover(self.session, first.id, Mock(cover=Mock(side_effect=RuntimeError("private"))))
        self.store.create_cover_track(self.session, "Three", self.settings)
        self.assertEqual(len(self.session.tracks), 3)

    def test_track_and_job_limits_are_enforced_before_generation(self):
        first = self.store.create_cover_track(self.session, "One", self.settings)
        self.store.generate_cover(self.session, first.id, Mock(cover=Mock(return_value=png("blue"))))
        with patch("jukebox.sessions.MAX_TRACKS", 1), self.assertRaises(SessionFailure):
            self.store.create_cover_track(self.session, "Two", self.settings)
        with patch("jukebox.sessions.MAX_JOBS", 1), self.assertRaises(SessionFailure):
            self.store.queue_cover(self.session, first.track_id)
        self.assertEqual(len(self.session.jobs), 1)

    def test_global_media_budget_failure_retains_previous_cover(self):
        first = self.store.create_cover_track(self.session, "One", self.settings)
        self.store.generate_cover(self.session, first.id, Mock(cover=Mock(return_value=png("blue"))))
        old = self.session.tracks[first.track_id].cover
        retry = self.store.queue_cover(self.session, first.track_id)
        with patch("jukebox.sessions.MAX_MEDIA_BYTES", 1):
            self.store.generate_cover(self.session, retry.id, Mock(cover=Mock(return_value=png("orange"))))
        self.assertEqual(self.session.tracks[first.track_id].cover, old)
        self.assertEqual(self.session.jobs[retry.id].state, "failed")
        self.assertEqual(len(self.session.media), 1)

    def test_expiry_clears_inactive_media_but_never_discards_running_jobs(self):
        job = self.store.create_cover_track(self.session, "One", self.settings)
        self.session.touched = time.monotonic() - SESSION_SECONDS - 1
        self.assertIs(self.store.resolve(self.session.token), self.session)
        self.store.generate_cover(self.session, job.id, Mock(cover=Mock(return_value=png("blue"))))
        self.session.touched = time.monotonic() - SESSION_SECONDS - 1
        replacement = self.store.resolve(self.session.token)
        self.assertNotEqual(replacement.token, self.session.token)
        self.assertEqual(self.store.snapshot(replacement).tracks, [])
        self.assertNotIn(self.session.token, self.store.sessions)

    def test_session_limit_and_snapshot_mutation_are_isolated(self):
        self.store.create_cover_track(self.session, "One", self.settings)
        with patch("jukebox.sessions.MAX_SESSIONS", 1), self.assertRaises(SessionFailure):
            self.store.resolve(None)
        snapshot = self.store.snapshot(self.session)
        snapshot.tracks.clear()
        snapshot.jobs.clear()
        self.assertEqual(len(self.store.snapshot(self.session).tracks), 1)
        self.assertEqual(len(self.store.snapshot(self.session).jobs), 1)
