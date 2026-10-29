"""Offline instrumental music integration through real HTTP routes and the store; no class-service calls."""
from concurrent.futures import ThreadPoolExecutor
import io
from threading import Event
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4
import wave

from fastapi.testclient import TestClient

from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.contracts import MediaRef, Playback, SafeError, SongSettings, Track
from jukebox.providers import MediaBytes, MusicPoll, MusicTicket, ProviderFailure
from jukebox.sessions import SESSION_COOKIE, SessionFailure, SessionStore


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(48000)
        audio.writeframes(b"\x01\x00" * 960)
    return buffer.getvalue()


def png(color):
    from PIL import Image
    buffer = io.BytesIO()
    Image.new("RGB", (512, 512), color).save(buffer, format="PNG")
    return MediaBytes(buffer.getvalue(), "image/png")


def art_music_settings():
    values = {"JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1", "JUKEBOX_ART_API_KEY": "private-offline-marker",
              "JUKEBOX_MUSIC_ENDPOINT": "http://dobolyi.com:9007/v1", "JUKEBOX_MUSIC_API_KEY": "private-offline-marker"}
    return Settings.load(None, values)


def art_only_settings():
    return Settings.load(None, {"JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1",
                                "JUKEBOX_ART_API_KEY": "private-offline-marker"})


def body(title="Moonlit lake", style="Ambient piano", mood="Reflective", duration=30):
    return {"title": title, "settings": {"style": style, "mood": mood, "duration_seconds": duration, "mode": "instrumental"}}


def track(title="Sample", duration=10):
    return Track(title=title, settings=SongSettings(style="Ambient", mood="Calm", duration_seconds=duration))


class MusicStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.session = self.store.resolve(None)

    def add_track(self, title="Song", duration=10):
        item = track(title, duration)
        self.session.tracks[item.id] = item
        return item

    def music_providers(self, polls=("succeeded",), submit_failure=None):
        providers = Mock()
        providers.submit_music.return_value = MusicTicket("private-ticket")
        if submit_failure is not None:
            providers.submit_music.side_effect = submit_failure
        providers.poll_music.side_effect = [MusicPoll(state, "/v1/audio?path=x" if state == "succeeded" else None)
                                            for state in polls]
        providers.download_music.return_value = MediaBytes(wav_bytes(), "audio/wav")
        return providers

    def test_instrumental_submission_uses_settings_prompt_and_lyrics_marker(self):
        item = self.add_track("Midnight piano", 15)
        job = self.store.queue_music(self.session, item.id)
        self.assertEqual(job.kind, "music")
        self.assertEqual(job.state.value, "queued")
        providers = self.music_providers()
        self.store.generate_music(self.session, job.id, providers)
        prompt = providers.submit_music.call_args.args[0]
        for value in ("Midnight piano", "Ambient", "Calm"):
            self.assertIn(value, prompt)
        self.assertIn("[Instrumental]", providers.submit_music.call_args.kwargs["lyrics"])
        self.assertEqual(providers.submit_music.call_args.kwargs["duration_seconds"], 15)
        self.assertEqual(providers.submit_music.call_count, 1)
        self.assertEqual(providers.download_music.call_count, 1)

    def test_bounded_polling_advances_progress_then_attaches_ready_audio(self):
        item = self.add_track()
        job = self.store.queue_music(self.session, item.id)
        with patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            providers = self.music_providers(polls=("running", "running", "succeeded"))
            self.store.generate_music(self.session, job.id, providers)
        self.assertEqual(providers.poll_music.call_count, 3)
        latest = self.session.jobs[job.id]
        self.assertEqual(latest.state.value, "succeeded")
        self.assertEqual(latest.progress, 1)
        current = self.session.tracks[item.id]
        self.assertEqual(current.status, "ready")
        self.assertIsNotNone(current.audio)
        self.assertEqual(self.store.get_media(self.session, current.audio.id).content_type, "audio/wav")
        self.assertFalse(self.session.active)
        self.assertNotIn(job.id, self.session.tickets)

    def test_poll_deadline_fails_retryable_releases_capacity_and_keeps_ticket(self):
        item = self.add_track()
        job = self.store.queue_music(self.session, item.id)
        providers = Mock()
        providers.submit_music.return_value = MusicTicket("private-ticket")
        providers.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, job.id, providers)
        latest = self.session.jobs[job.id]
        self.assertEqual(latest.state.value, "failed")
        self.assertTrue(latest.error.retryable)
        self.assertEqual(latest.error.code, "generation_failed")
        self.assertIn("class service queue", latest.error.message)
        self.assertNotIn("private-ticket", str(latest))
        self.assertFalse(self.session.active)
        self.assertIn(job.id, self.session.tickets)
        retry = self.store.queue_music(self.session, item.id)
        self.assertNotEqual(retry.id, job.id)

    def test_submit_failure_is_sanitized_and_never_repolls_or_resubmits(self):
        item = self.add_track()
        job = self.store.queue_music(self.session, item.id)
        providers = self.music_providers(submit_failure=ProviderFailure(
            SafeError(code="timeout", message="The class service timed out. Check the existing job before retrying.", retryable=True)))
        self.store.generate_music(self.session, job.id, providers)
        latest = self.session.jobs[job.id]
        self.assertEqual(latest.state.value, "failed")
        self.assertTrue(latest.error.retryable)
        self.assertEqual(providers.poll_music.call_count, 0)
        self.assertEqual(providers.submit_music.call_count, 1)
        self.assertFalse(self.session.active)

    def test_manual_retry_after_uncertain_submit_creates_new_job_and_new_task(self):
        item = self.add_track()
        first = self.store.queue_music(self.session, item.id)
        failed = self.music_providers(submit_failure=ProviderFailure(
            SafeError(code="unavailable", message="Could not reach the class service.", retryable=True)))
        self.store.generate_music(self.session, first.id, failed)
        self.assertEqual(failed.submit_music.call_count, 1)
        second = self.store.queue_music(self.session, item.id)
        self.assertNotEqual(second.id, first.id)
        ok = self.music_providers()
        self.store.generate_music(self.session, second.id, ok)
        self.assertEqual(ok.submit_music.call_count, 1)
        self.assertEqual(self.session.jobs[second.id].state.value, "succeeded")
        self.assertEqual(failed.submit_music.call_count + ok.submit_music.call_count, 2)

    def test_audio_replacement_preserves_cover_and_cleans_old_audio(self):
        item = self.add_track()
        cover_id, audio_id = uuid4(), uuid4()
        cover = MediaRef(id=cover_id, url=f"/api/media/{cover_id}", content_type="image/png")
        audio = MediaRef(id=audio_id, url=f"/api/media/{audio_id}", content_type="audio/wav")
        self.session.media[cover_id] = png("blue")
        self.session.media[audio_id] = MediaBytes(wav_bytes(), "audio/wav")
        self.session.tracks[item.id] = Track.model_validate(
            {**item.model_dump(), "cover": cover, "audio": audio, "status": "ready", "lyrics": "kept lyric"})
        self.session.playback = Playback(state="playing", queue=[item.id], current_track_id=item.id)
        job = self.store.queue_music(self.session, item.id)
        self.store.generate_music(self.session, job.id, self.music_providers())
        current = self.session.tracks[item.id]
        self.assertEqual(current.cover.id, cover_id)
        self.assertEqual(current.lyrics, "kept lyric")
        self.assertEqual(current.status, "ready")
        self.assertNotEqual(current.audio.id, audio_id)
        self.assertNotIn(audio_id, self.session.media)
        self.assertIsNotNone(self.store.get_media(self.session, current.audio.id))
        self.assertEqual(self.session.playback.state, "playing")

    def test_cover_and_music_completion_in_either_order_preserves_both(self):
        for order in ("music-first", "cover-first"):
            with self.subTest(order=order):
                store = SessionStore()
                session = store.resolve(None)
                item = track()
                session.tracks[item.id] = item
                art_job = store.queue_cover(session, item.id)
                music_job = store.queue_music(session, item.id)
                if order == "music-first":
                    store.generate_music(session, music_job.id, self.music_providers())
                    store.generate_cover(session, art_job.id, Mock(cover=Mock(return_value=png("orange"))))
                else:
                    store.generate_cover(session, art_job.id, Mock(cover=Mock(return_value=png("orange"))))
                    store.generate_music(session, music_job.id, self.music_providers())
                current = session.tracks[item.id]
                self.assertEqual(current.status, "ready")
                self.assertIsNotNone(current.audio, order)
                self.assertIsNotNone(current.cover, order)
                self.assertNotEqual(current.audio.id, current.cover.id)
                self.assertEqual(len(session.media), 2)
                self.assertFalse(session.active)

    def test_music_jobs_cannot_duplicate_on_track_and_global_cap_applies(self):
        item = self.add_track()
        first = self.store.queue_music(self.session, item.id)
        with self.assertRaises(SessionFailure) as caught:
            self.store.queue_music(self.session, item.id)
        self.assertEqual(caught.exception.status, 409)
        other_session = self.store.resolve(None)
        other_item = track()
        other_session.tracks[other_item.id] = other_item
        self.store.queue_music(other_session, other_item.id)
        second_item = self.add_track("Second")
        with patch("jukebox.sessions.MAX_ACTIVE_MUSIC", 2), self.assertRaises(SessionFailure) as caught:
            self.store.queue_music(self.session, second_item.id)
        self.assertEqual(caught.exception.status, 429)
        self.store.generate_music(self.session, first.id, self.music_providers())
        self.store.queue_music(self.session, second_item.id)
        self.assertEqual(len(self.session.active), 1)

    def test_media_budget_failure_preserves_existing_assets(self):
        item = self.add_track()
        audio_id = uuid4()
        audio = MediaRef(id=audio_id, url=f"/api/media/{audio_id}", content_type="audio/wav")
        self.session.media[audio_id] = MediaBytes(wav_bytes(), "audio/wav")
        self.session.tracks[item.id] = Track.model_validate({**item.model_dump(), "audio": audio, "status": "ready"})
        job = self.store.queue_music(self.session, item.id)
        with patch("jukebox.sessions.MAX_MEDIA_BYTES", 1):
            self.store.generate_music(self.session, job.id, self.music_providers())
        self.assertEqual(self.session.jobs[job.id].state.value, "failed")
        self.assertEqual(self.session.tracks[item.id].audio.id, audio_id)
        self.assertIn(audio_id, self.session.media)
        self.assertFalse(self.session.active)

    def test_duration_outside_operational_range_rejected_without_job(self):
        item = self.add_track("Long", 61)
        with self.assertRaises(SessionFailure) as caught:
            self.store.queue_music(self.session, item.id)
        self.assertEqual(caught.exception.status, 422)
        self.assertEqual(len(self.session.jobs), 0)
        self.assertFalse(self.session.active)

    def test_snapshot_never_exposes_tickets_or_private_task_ids(self):
        item = self.add_track()
        job = self.store.queue_music(self.session, item.id)
        self.session.tickets[job.id] = MusicTicket("private-task-id-12345")
        snapshot = self.store.snapshot(self.session)
        self.assertNotIn("private-task-id-12345", snapshot.model_dump_json())
        self.assertEqual(len(snapshot.jobs), 1)


class MusicHttpTests(unittest.TestCase):
    def client(self, settings=None):
        return TestClient(create_app(settings or Settings.load(None, {})), base_url="http://localhost")

    def test_create_and_two_songs_with_covers_and_audio_survive_reload(self):
        covers = [png("blue"), png("orange")]
        submissions, downloads = [], []
        def cover(prompt):
            return covers.pop(0)
        def submit(prompt, *, duration_seconds, lyrics):
            self.assertEqual(lyrics, "[Instrumental]")
            submissions.append((duration_seconds, prompt))
            return MusicTicket(f"ticket-{len(submissions)}")
        def poll(ticket):
            return MusicPoll("succeeded", "/v1/audio?path=x")
        def download(result):
            downloads.append(result)
            return MediaBytes(wav_bytes(), "audio/wav")
        with patch("jukebox.providers.ClassProviders.cover", side_effect=cover), \
             patch("jukebox.providers.ClassProviders.submit_music", side_effect=submit), \
             patch("jukebox.providers.ClassProviders.poll_music", side_effect=poll), \
             patch("jukebox.providers.ClassProviders.download_music", side_effect=download):
            with self.client(art_music_settings()) as client:
                first = client.post("/api/tracks", json=body("Moonlit Reflection", "Ambient piano", "Calm", 10)).json()
                client.post(f"/api/tracks/{first['track_id']}/music", json={})
                second = client.post("/api/tracks", json=body("Desert Drive", "Upbeat funk", "Energetic", 20)).json()
                client.post(f"/api/tracks/{second['track_id']}/music", json={})
                snapshot = client.get("/api/session").json()
                self.assertEqual([t["title"] for t in snapshot["tracks"]], ["Moonlit Reflection", "Desert Drive"])
                self.assertEqual([j["state"] for j in snapshot["jobs"] if j["kind"] == "music"], ["succeeded", "succeeded"])
                self.assertEqual([s[0] for s in submissions], [10, 20])
                self.assertIn("Ambient piano", submissions[0][1])
                self.assertIn("Upbeat funk", submissions[1][1])
                tracks = snapshot["tracks"]
                self.assertEqual(len({t["audio"]["id"] for t in tracks}), 2)
                self.assertEqual(len({t["audio"]["url"] for t in tracks}), 2)
                self.assertTrue(all(t["status"] == "ready" and t["cover"] for t in tracks))
                for item in tracks:
                    audio = client.get(item["audio"]["url"])
                    self.assertEqual(audio.headers["content-type"], "audio/wav")
                    self.assertEqual(audio.content, wav_bytes())
                    self.assertEqual(client.get(item["cover"]["url"]).status_code, 200)
                client.get("/")
                self.assertEqual(client.get("/api/session").json()["tracks"], snapshot["tracks"])
                self.assertEqual(len(submissions), 2)
                self.assertEqual(len(downloads), 2)

    def test_reload_and_media_gets_never_resubmit(self):
        with patch("jukebox.providers.ClassProviders.submit_music",
                   return_value=MusicTicket("ticket")), \
             patch("jukebox.providers.ClassProviders.poll_music",
                   return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")), \
             patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")):
            with self.client(art_music_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                client.post(f"/api/tracks/{job['track_id']}/music", json={})
                with patch("jukebox.providers.ClassProviders.submit_music") as later:
                    for _ in range(3):
                        client.get("/api/session")
                    client.get("/")
                    client.get("/static/app.js")
                    later.assert_not_called()

    def test_http_rejects_duplicate_active_music_and_unknown_track(self):
        entered, release = Event(), Event()
        def delayed_submit(prompt, *, duration_seconds, lyrics):
            entered.set()
            if not release.wait(5):
                raise AssertionError("submit was not released")
            return MusicTicket("ticket")
        with patch("jukebox.providers.ClassProviders.submit_music", side_effect=delayed_submit), \
             patch("jukebox.providers.ClassProviders.poll_music",
                   return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")), \
             patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")):
            with self.client(art_music_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                with ThreadPoolExecutor(max_workers=1) as executor:
                    pending = executor.submit(client.post, f"/api/tracks/{track_id}/music", json={})
                    self.assertTrue(entered.wait(5))
                    duplicate = client.post(f"/api/tracks/{track_id}/music", json={})
                    self.assertEqual(duplicate.status_code, 409)
                    self.assertEqual(client.post("/api/tracks/00000000-0000-0000-0000-000000000000/music", json={}).status_code, 404)
                release.set()
                self.assertEqual(pending.result(timeout=5).status_code, 202)

    def test_art_and_music_jobs_coexist_on_the_same_track(self):
        entered, release = Event(), Event()
        def delayed_cover(prompt):
            entered.set()
            if not release.wait(5):
                raise AssertionError("cover was not released")
            return png("blue")
        with patch("jukebox.providers.ClassProviders.cover", side_effect=delayed_cover), \
             patch("jukebox.providers.ClassProviders.submit_music", return_value=MusicTicket("ticket")), \
             patch("jukebox.providers.ClassProviders.poll_music",
                   return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")):
            with self.client(art_music_settings()) as client:
                client.get("/api/session")
                with ThreadPoolExecutor(max_workers=1) as executor:
                    pending_post = executor.submit(client.post, "/api/tracks", json=body())
                    self.assertTrue(entered.wait(5))
                    track_id = client.get("/api/session").json()["tracks"][0]["id"]
                    music = client.post(f"/api/tracks/{track_id}/music", json={})
                    self.assertEqual(music.status_code, 202)
                    duplicate_cover = client.post(f"/api/tracks/{track_id}/cover", json={})
                    self.assertEqual(duplicate_cover.status_code, 409)
                    release.set()
                self.assertEqual(pending_post.result(timeout=5).status_code, 202)
                snapshot = client.get("/api/session").json()
                current = next(t for t in snapshot["tracks"] if t["id"] == track_id)
                self.assertIsNotNone(current["cover"])
                self.assertIsNotNone(current["audio"])
                self.assertEqual(current["status"], "ready")

    def test_missing_music_configuration_is_safe_and_never_submits(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music",
                   side_effect=AssertionError("No submission without music configuration")):
            with self.client(art_only_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                self.assertFalse(client.get("/api/status").json()["music_generation_available"])
                rejected = client.post(f"/api/tracks/{job['track_id']}/music", json={})
                self.assertEqual(rejected.status_code, 502)
                self.assertEqual(client.get("/api/session").json()["tracks"][0]["title"], "Moonlit lake")
            with self.client(Settings.load(None, {})) as client:
                status = client.get("/api/status").json()
                self.assertFalse(status["cover_generation_available"])
                self.assertFalse(status["music_generation_available"])
                self.assertEqual(client.post("/api/tracks", json=body()).status_code, 502)

    def test_music_failure_keeps_cover_and_retry_uses_new_job(self):
        attempts = {"count": 0}
        def submit(prompt, *, duration_seconds, lyrics):
            attempts["count"] += 1
            if attempts["count"] == 1:
                raise ProviderFailure(SafeError(code="unavailable", message="Could not reach the class service.", retryable=True))
            return MusicTicket("ticket")
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", side_effect=submit), \
             patch("jukebox.providers.ClassProviders.poll_music",
                   return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")):
            with self.client(art_music_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                failed = client.post(f"/api/tracks/{track_id}/music", json={}).json()
                self.assertEqual(failed["state"], "queued")
                snapshot = client.get("/api/session").json()
                current = next(t for t in snapshot["tracks"] if t["id"] == track_id)
                self.assertIsNotNone(current["cover"])
                self.assertIsNone(current["audio"])
                music_job = next(j for j in snapshot["jobs"] if j["kind"] == "music")
                self.assertEqual(music_job["state"], "failed")
                self.assertTrue(music_job["error"]["retryable"])
                retried = client.post(f"/api/tracks/{track_id}/music", json={}).json()
                self.assertNotEqual(retried["id"], failed["id"])
                final = client.get("/api/session").json()
                current = next(t for t in final["tracks"] if t["id"] == track_id)
                self.assertEqual(current["status"], "ready")
                self.assertIsNotNone(current["audio"])
                self.assertEqual(current["cover"]["id"], snapshot["tracks"][0]["cover"]["id"])
                self.assertEqual(attempts["count"], 2)

    def test_session_isolation_media_and_tracks(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", return_value=MusicTicket("ticket")), \
             patch("jukebox.providers.ClassProviders.poll_music",
                   return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")):
            app = create_app(art_music_settings())
            with TestClient(app, base_url="http://localhost") as first:
                job = first.post("/api/tracks", json=body()).json()
                first.post(f"/api/tracks/{job['track_id']}/music", json={})
                track = first.get("/api/session").json()["tracks"][0]
                first.cookies.clear()
                self.assertEqual(first.get("/api/session").json()["tracks"], [])
                self.assertEqual(first.get(track["audio"]["url"]).status_code, 404)
                self.assertEqual(first.get(track["cover"]["url"]).status_code, 404)
                self.assertEqual(first.post(f"/api/tracks/{track['id']}/music", json={}).status_code, 404)

    def test_error_responses_reuse_session_cookie(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music",
                   side_effect=ProviderFailure(SafeError(code="unavailable", message="Busy.", retryable=True))):
            app = create_app(art_music_settings())
            with TestClient(app, base_url="http://localhost") as client:
                job = client.post("/api/tracks", json=body()).json()
                for _ in range(3):
                    response = client.post(f"/api/tracks/{job['track_id']}/music", json={})
                    self.assertIn("HttpOnly", response.headers["set-cookie"])
                self.assertEqual(len(app.state.sessions.sessions), 1)
                self.assertEqual(len(app.state.sessions.sessions[next(iter(app.state.sessions.sessions))].tracks), 1)
