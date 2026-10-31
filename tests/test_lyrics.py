"""Offline A3-03 vocal-song integration through real HTTP routes and the store.

No class-service calls: text/art/music providers are mocked, mirroring the
test_covers/test_music conventions. Live Qwen/ACE-Step evidence is recorded in
docs/TEST_RESULTS.md from the deliberate acceptance run, not from these tests.
"""
import io
import unittest
from unittest.mock import Mock, patch
import wave

from fastapi.testclient import TestClient
from PIL import Image

from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.contracts import GenerationJob, SafeError, SongSettings, Track
from jukebox.providers import MediaBytes, MusicPoll, MusicTicket, ProviderFailure
from jukebox.sessions import SessionFailure, SessionStore
from uuid import uuid4


def png(color):
    content = io.BytesIO()
    Image.new("RGB", (512, 512), color).save(content, format="PNG")
    return MediaBytes(content.getvalue(), "image/png")


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b"\x01\x00" * 2400)
    return buffer.getvalue()


LYRICS = "Verse one\nVerse two\nChorus shine"


def full_settings():
    values = {"JUKEBOX_TEXT_ENDPOINT": "http://dobolyi.com:9001/v1", "JUKEBOX_TEXT_API_KEY": "private-offline-marker",
              "JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1", "JUKEBOX_ART_API_KEY": "private-offline-marker",
              "JUKEBOX_MUSIC_ENDPOINT": "http://dobolyi.com:9007/v1", "JUKEBOX_MUSIC_API_KEY": "private-offline-marker"}
    return Settings.load(None, values)


def art_settings():
    return Settings.load(None, {"JUKEBOX_ART_ENDPOINT": "http://dobolyi.com:9006/v1",
                                "JUKEBOX_ART_API_KEY": "private-offline-marker"})


def body(title="Moonlit lake", style="Ambient piano", mood="Reflective", mode="vocal"):
    return {"title": title, "settings": {"style": style, "mood": mood, "duration_seconds": 30, "mode": mode}}


class VocalHttpTests(unittest.TestCase):
    def test_vocal_request_uses_qwen_lyrics_and_the_real_lyrics_in_acestep_request(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.lyrics", return_value=LYRICS) as lyrics, \
             patch("jukebox.providers.ClassProviders.submit_music", return_value=MusicTicket("private-ticket")) as submit, \
             patch("jukebox.providers.ClassProviders.poll_music", return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music", return_value=MediaBytes(wav_bytes(), "audio/wav")):
            with patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
                with TestClient(create_app(full_settings()), base_url="http://localhost") as client:
                    art_job = client.post("/api/tracks", json=body())
                    self.assertEqual(art_job.status_code, 202)
                    track_id = art_job.json()["track_id"]
                    lyrics_job = client.post(f"/api/tracks/{track_id}/lyrics", json={})
                    self.assertEqual(lyrics_job.status_code, 202)
                    music_job = client.post(f"/api/tracks/{track_id}/music", json={})
                    self.assertEqual(music_job.status_code, 202)
                    snapshot = client.get("/api/session").json()
                    track = snapshot["tracks"][0]
                    self.assertEqual(track["settings"]["mode"], "vocal")
                    self.assertEqual(track["lyrics"], LYRICS)
                    self.assertEqual(track["status"], "ready")
                    self.assertIsNotNone(track["audio"])
                    self.assertIsNotNone(track["cover"])
                    self.assertEqual([job["state"] for job in snapshot["jobs"]], ["succeeded", "succeeded", "succeeded"])
                    prompt = submit.call_args.args[0]
                    self.assertIn("vocals", prompt)
                    self.assertIn("Moonlit lake", prompt)
                    self.assertEqual(submit.call_args.kwargs["lyrics"], LYRICS)
                    self.assertEqual(submit.call_args.kwargs["duration_seconds"], 30)
                    self.assertEqual(lyrics.call_count, 1)
                    self.assertNotIn("private-offline-marker", str(snapshot))
                    self.assertEqual(client.get(track["audio"]["url"]).content, wav_bytes())

    def test_instrumental_flow_still_sends_the_frozen_marker_and_prompt(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", return_value=MusicTicket("private-ticket")) as submit, \
             patch("jukebox.providers.ClassProviders.poll_music", return_value=MusicPoll("succeeded", "/v1/audio?path=x")), \
             patch("jukebox.providers.ClassProviders.download_music", return_value=MediaBytes(wav_bytes(), "audio/wav")):
            with patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
                with TestClient(create_app(full_settings()), base_url="http://localhost") as client:
                    job = client.post("/api/tracks", json=body(mode="instrumental")).json()
                    client.post(f"/api/tracks/{job['track_id']}/music", json={})
                    prompt = submit.call_args.args[0]
                    self.assertIn("no vocals", prompt)
                    self.assertEqual(submit.call_args.kwargs["lyrics"], "[Instrumental]")

    def test_vocal_music_without_lyrics_is_rejected_with_zero_side_effects(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", side_effect=AssertionError("No submission")):
            with TestClient(create_app(full_settings()), base_url="http://localhost") as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                rejected = client.post(f"/api/tracks/{track_id}/music", json={})
                self.assertEqual(rejected.status_code, 409)
                self.assertIn("lyrics", rejected.json()["error"]["message"])
                snapshot = client.get("/api/session").json()
                self.assertEqual(len(snapshot["jobs"]), 1)  # only the cover job
                self.assertEqual(snapshot["jobs"][0]["kind"], "art")
                self.assertIsNone(snapshot["tracks"][0]["lyrics"])

    def test_lyrics_failure_preserves_the_track_and_a_retry_uses_a_new_job(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.lyrics", side_effect=[
                 ProviderFailure(SafeError(code="timeout", message="The text service timed out.", retryable=True)),
                 LYRICS]) as lyrics:
            with TestClient(create_app(full_settings()), base_url="http://localhost") as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                failed = client.post(f"/api/tracks/{track_id}/lyrics", json={})
                snapshot = client.get("/api/session").json()
                self.assertEqual(snapshot["jobs"][1]["state"], "failed")
                self.assertTrue(snapshot["jobs"][1]["error"]["retryable"])
                self.assertIsNone(snapshot["tracks"][0]["lyrics"])
                retried = client.post(f"/api/tracks/{track_id}/lyrics", json={})
                self.assertNotEqual(failed.json()["id"], retried.json()["id"])
                final = client.get("/api/session").json()
                self.assertEqual(final["tracks"][0]["lyrics"], LYRICS)
                self.assertEqual(final["jobs"][-1]["state"], "succeeded")

    def test_missing_text_configuration_never_invokes_a_provider(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.lyrics", side_effect=AssertionError("No service call")):
            with TestClient(create_app(art_settings()), base_url="http://localhost") as client:
                self.assertFalse(client.get("/api/status").json()["lyrics_generation_available"])
                job = client.post("/api/tracks", json=body()).json()
                response = client.post(f"/api/tracks/{job['track_id']}/lyrics", json={})
                self.assertEqual(response.status_code, 502)
                self.assertEqual(response.json()["error"]["code"], "not_configured")
                self.assertEqual(len(client.get("/api/session").json()["tracks"]), 1)
                self.assertEqual(len(client.get("/api/session").json()["jobs"]), 1)


class VocalStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.session = self.store.resolve(None)

    def vocal_track(self, lyrics=None):
        track = Track(title="Night drive", settings=SongSettings(style="Synth", mood="Bold", duration_seconds=30, mode="vocal"))
        if lyrics is not None:
            track = Track.model_validate({**track.model_dump(), "lyrics": lyrics})
        self.session.tracks[track.id] = track
        return track

    def test_marker_model_metadata_never_reaches_the_session_snapshot(self):
        # The review repro: a synthetic MODEL OBJECT must not be
        # repr-interpolated into the SafeError that lands in the public
        # session snapshot after generate_lyrics.
        import httpx
        from jukebox.providers import ClassProviders
        env = {"JUKEBOX_TEXT_ENDPOINT": "http://dobolyi.com:9001/v1",
               "JUKEBOX_TEXT_API_KEY": "private-offline-marker"}

        def reply(request):
            return httpx.Response(200, json={"model": {"debug": "PRIVATE-MARKER"},
                                             "choices": [{"finish_reason": "stop",
                                                          "message": {"content": "ok"}}]})

        providers = ClassProviders(Settings.load(None, env), transport=httpx.MockTransport(reply))
        try:
            track = self.vocal_track()
            job = self.store.queue_lyrics(self.session, track.id)
            self.store.generate_lyrics(self.session, job.id, providers)
        finally:
            providers.close()
        failed = self.session.jobs[job.id]
        self.assertEqual(failed.state.value, "failed")
        self.assertIsNotNone(failed.error)
        self.assertNotIn("PRIVATE-MARKER", failed.error.message)
        self.assertNotIn("{", failed.error.message)
        snapshot = self.store.snapshot(self.session)
        self.assertNotIn("PRIVATE-MARKER", str(snapshot.model_dump(mode="json")))

    def test_queue_lyrics_validations_have_no_side_effects(self):
        instrumental = Track(title="Instr", settings=SongSettings(style="Piano", mood="Calm", duration_seconds=30))
        self.session.tracks[instrumental.id] = instrumental
        with self.assertRaises(SessionFailure) as mode_error:
            self.store.queue_lyrics(self.session, instrumental.id)
        self.assertEqual(mode_error.exception.status, 422)
        with self.assertRaises(SessionFailure) as not_found:
            self.store.queue_lyrics(self.session, uuid4())
        self.assertEqual(not_found.exception.status, 404)
        track = self.vocal_track()
        first = self.store.queue_lyrics(self.session, track.id)
        with self.assertRaises(SessionFailure) as duplicate:
            self.store.queue_lyrics(self.session, track.id)
        self.assertEqual(duplicate.exception.status, 409)
        other = self.vocal_track()
        other = Track.model_validate({**other.model_dump(), "title": "Other vocal"})
        with patch("jukebox.sessions.MAX_ACTIVE_TEXT", 1), self.assertRaises(SessionFailure) as busy:
            self.store.queue_lyrics(self.session, other.id)
        self.assertEqual(busy.exception.status, 429)
        self.assertEqual(len(self.session.jobs), 1)
        self.assertEqual(len(self.session.active), 1)

    def test_generate_lyrics_attaches_text_and_replacement_replaces_it(self):
        job = self.store.queue_lyrics(self.session, self.vocal_track().id)
        providers = Mock(lyrics=Mock(return_value=LYRICS))
        self.store.generate_lyrics(self.session, job.id, providers)
        track = self.session.tracks[job.track_id]
        self.assertEqual(track.lyrics, LYRICS)
        self.assertEqual(self.session.jobs[job.id].state.value, "succeeded")
        self.assertFalse(self.session.active)
        replacement = self.store.queue_lyrics(self.session, job.track_id)
        self.store.generate_lyrics(self.session, replacement.id, Mock(lyrics=Mock(return_value="New words")))
        self.assertEqual(self.session.tracks[job.track_id].lyrics, "New words")

    def test_empty_or_failed_lyrics_never_attach(self):
        job = self.store.queue_lyrics(self.session, self.vocal_track().id)
        self.store.generate_lyrics(self.session, job.id, Mock(lyrics=Mock(return_value="   ")))
        self.assertIsNone(self.session.tracks[job.track_id].lyrics)
        self.assertEqual(self.session.jobs[job.id].state.value, "failed")
        retry = self.store.queue_lyrics(self.session, job.track_id)
        self.store.generate_lyrics(self.session, retry.id, Mock(
            lyrics=Mock(side_effect=ProviderFailure(SafeError(code="timeout", message="Timed out.", retryable=True)))))
        self.assertIsNone(self.session.tracks[job.track_id].lyrics)
        self.assertTrue(self.session.jobs[retry.id].error.retryable)

    def test_music_submission_requires_lyrics_even_at_generate_time(self):
        # Defensive guard: even if a music job already exists without lyrics
        # (e.g. created before this feature), it must not silently submit an
        # instrumental with the frozen marker.
        track = self.vocal_track()  # lyrics None
        job = GenerationJob(track_id=track.id, kind="music")
        self.session.jobs[job.id] = job
        self.session.active.add((track.id, "music"))
        providers = Mock(submit_music=Mock(side_effect=AssertionError("No submission")))
        self.store.generate_music(self.session, job.id, providers)
        self.assertEqual(self.session.jobs[job.id].state.value, "failed")
        self.assertIn("lyrics", self.session.jobs[job.id].error.message.lower())
        self.assertFalse(self.session.active)

    def test_vocal_submission_sends_lyrics_and_releases_the_slot(self):
        track = self.vocal_track(lyrics=LYRICS)
        job = self.store.queue_music(self.session, track.id)
        providers = Mock()
        providers.submit_music.return_value = MusicTicket("private-ticket")
        providers.poll_music.return_value = MusicPoll("succeeded", "/v1/audio?path=x")
        providers.download_music.return_value = MediaBytes(wav_bytes(), "audio/wav")
        with patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, job.id, providers)
        self.assertEqual(providers.submit_music.call_args.kwargs["lyrics"], LYRICS)
        self.assertIn("vocals", providers.submit_music.call_args.args[0])
        self.assertEqual(self.session.tracks[track.id].status, "ready")
        self.assertFalse(self.session.active)
