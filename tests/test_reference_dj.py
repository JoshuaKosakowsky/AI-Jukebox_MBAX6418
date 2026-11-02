"""Reference chooser -> DJ job integration, synthetic providers only (not AT-08)."""
import unittest
from uuid import UUID, uuid4
from unittest.mock import patch

from jukebox.contracts import JobState
from jukebox.providers import MediaBytes
from jukebox.sessions import SESSION_COOKIE, SESSION_SECONDS
from tests import test_dj as dj
from tests.test_references import mp3_bytes, wav_bytes


class VoiceRecorders(dj.DjRecorders):
    def __init__(self):
        super().__init__()
        self.references = []
        self.fail_speech = False

    def speech(self, text, *, reference=None):
        self.spoken_inputs.append(text)
        self.references.append(reference)
        if self.fail_speech:
            raise RuntimeError("private-provider-marker")
        return MediaBytes(dj.speech_wav(), "audio/wav")


class ReferenceDjTests(unittest.TestCase):
    make_client = dj.DjTests.make_client
    create_track = dj.DjTests.create_track

    def ready(self, count=1):
        provider = VoiceRecorders()
        client, store = self.make_client(provider)
        tracks = [self.create_track(client, f"Synthetic song {i}")[0] for i in range(count)]
        for track in tracks:
            self.assertEqual(client.post("/api/playback/queue", json={"track_id": track}).status_code, 200)
        session = store.sessions[client.cookies.get(SESSION_COOKIE)]
        return provider, client, store, session, tracks

    def upload(self, client, content=None):
        response = client.post("/api/references/speech", files={"file": (
            "private-local-filename.wav", content or wav_bytes(), "application/octet-stream")})
        self.assertEqual(response.status_code, 201)
        return response.json()["id"]

    def assert_clean(self, session):
        self.assertEqual(session.references, {})
        self.assertEqual(session.speech_references, {})
        self.assertEqual(session.speech_prompts, {})
        self.assertEqual(session.active, set())

    def test_mp3_then_wav_then_default_through_start_and_advance(self):
        provider, client, _, session, _ = self.ready(3)
        for path, content in [("start", mp3_bytes()), ("advance", wav_bytes())]:
            reference = self.upload(client, content)
            result = client.post(f"/api/playback/{path}", json={"reference_id": reference})
            self.assertEqual(result.status_code, 200)
            self.assertEqual(provider.references[-1].content, content)
            self.assertNotIn(reference, client.get("/api/session").text)
            self.assertEqual(client.get(f"/api/media/{reference}").status_code, 404)
            self.assert_clean(session)
        self.assertEqual(client.post("/api/playback/advance").status_code, 200)
        self.assertIsNone(provider.references[-1])
        self.assertEqual(len(provider.references), 3)

    def test_missing_cross_session_or_consumed_id_never_falls_back(self):
        provider, client, _, session, _ = self.ready()
        reference = self.upload(client)
        cookie = client.cookies.get(SESSION_COOKIE)
        client.cookies.clear()
        result = client.post("/api/playback/start", json={"reference_id": reference})
        self.assertEqual(result.status_code, 404)
        client.cookies.clear()
        client.cookies.set(SESSION_COOKIE, cookie)
        self.assertEqual(client.post("/api/playback/start", json={"reference_id": str(uuid4())}).status_code, 404)
        self.assertEqual(session.playback.state, "idle")
        self.assertEqual(provider.references, [])
        self.assertEqual(client.post("/api/playback/start", json={"reference_id": reference}).status_code, 200)
        self.assertEqual(client.post("/api/playback/advance", json={"reference_id": reference}).status_code, 404)
        self.assertEqual(session.playback.index, 0)
        self.assertEqual(len(provider.references), 1)

    def test_text_and_speech_failures_release_recording_explicit_retry_only(self):
        for stage in ("text", "speech"):
            with self.subTest(stage=stage):
                provider, client, _, session, tracks = self.ready()
                provider.fail_text = stage == "text"
                provider.fail_speech = stage == "speech"
                reference = self.upload(client)
                self.assertEqual(client.post("/api/playback/start", json={"reference_id": reference}).status_code, 200)
                self.assertEqual(list(session.jobs.values())[-1].state, JobState.FAILED)
                self.assert_clean(session)
                self.assertNotIn("private-provider-marker", client.get("/api/session").text)
                # Replay, polling and reload do not retry failed commentary.
                client.post("/api/playback/advance", json={})
                client.post("/api/playback/start", json={})
                client.get("/api/session")
                self.assertEqual(len(provider.prompts), 1)
                provider.fail_text = provider.fail_speech = False
                new_reference = self.upload(client, mp3_bytes())
                retry = client.post("/api/playback/speech", json={"track_id": tracks[0], "reference_id": new_reference})
                self.assertEqual(retry.status_code, 202)
                self.assertEqual(provider.references[-1].content_type, "audio/mpeg")
                self.assert_clean(session)

    def test_rejected_busy_or_cached_intent_does_not_steal_upload(self):
        provider, client, _, session, tracks = self.ready(2)
        reference = self.upload(client)
        with patch("jukebox.sessions.MAX_ACTIVE_SPEECH", 0):
            result = client.post("/api/playback/speech", json={"track_id": tracks[0], "reference_id": reference})
            self.assertEqual(result.status_code, 429)
        self.assertIn(UUID(reference), session.references)
        self.assertEqual(client.post("/api/playback/start", json={"reference_id": reference}).status_code, 200)
        spare = self.upload(client)
        self.assertEqual(client.post("/api/playback/start", json={"reference_id": spare}).status_code, 409)
        client.post("/api/playback/advance", json={})
        client.post("/api/playback/advance", json={})
        client.post("/api/playback/start", json={"reference_id": spare})
        self.assertEqual(len(provider.references), 2, "cached intro is not regenerated with a different voice")
        self.assertIn(UUID(spare), session.references)
        self.assertEqual(client.delete(f"/api/references/speech/{spare}").status_code, 204)
        self.assert_clean(session)

    def test_claim_is_atomic_and_bounded_until_job_finishes(self):
        provider, client, store, session, tracks = self.ready(2)
        reference = UUID(self.upload(client))
        job = store.request_dj_speech(session, UUID(tracks[0]), reference)
        self.assertNotIn(reference, session.references)
        self.assertEqual(len(session.speech_references), 1)
        from jukebox.sessions import SessionFailure
        with self.assertRaises(SessionFailure):
            store.request_dj_speech(session, UUID(tracks[1]), reference)
        self.assertEqual(len(session.speech_references), 1)
        store.generate_dj_speech(session, job.id, provider)
        self.assert_clean(session)

    def test_expiry_and_delete_remove_pending_upload(self):
        provider, client, store, session, _ = self.ready()
        reference = self.upload(client)
        self.assertEqual(client.delete(f"/api/references/speech/{reference}").status_code, 204)
        self.assertEqual(client.post("/api/playback/start", json={"reference_id": reference}).status_code, 404)
        reference = self.upload(client)
        session.touched -= SESSION_SECONDS + 1
        result = client.post("/api/playback/start", json={"reference_id": reference})
        self.assertEqual(result.status_code, 404)
        self.assertNotIn(session.token, store.sessions)
        self.assertEqual(provider.references, [])

    def test_malformed_voice_body_cannot_start_a_default_job(self):
        provider, client, _, session, _ = self.ready()
        for body in ({"reference_id": "not-a-uuid"}, {"reference": "unexpected"}):
            self.assertEqual(client.post("/api/playback/start", json=body).status_code, 422)
        self.assertEqual(session.playback.state, "idle")
        self.assertEqual(provider.references, [])

    def test_media_capacity_failure_also_releases_reference(self):
        _, client, _, session, _ = self.ready()
        reference = self.upload(client)
        with patch("jukebox.sessions.MAX_MEDIA_BYTES", 0):
            self.assertEqual(client.post("/api/playback/start", json={"reference_id": reference}).status_code, 200)
        self.assertEqual(list(session.jobs.values())[-1].state, JobState.FAILED)
        self.assert_clean(session)

    def test_late_jobs_keep_their_own_reference_after_skip(self):
        provider, client, store, session, _ = self.ready(2)
        mp3 = UUID(self.upload(client, mp3_bytes()))
        wav = UUID(self.upload(client, wav_bytes()))
        _, first = store.start_playback(session, mp3)
        _, second = store.advance_playback(session, wav)
        store.generate_dj_speech(session, second.id, provider)
        store.generate_dj_speech(session, first.id, provider)
        self.assertEqual([item.content_type for item in provider.references], ["audio/wav", "audio/mpeg"])
        self.assertEqual(session.playback.current_track_id, second.track_id)
        self.assertIsNotNone(session.tracks[first.track_id].speech)
        self.assertIsNotNone(session.tracks[second.track_id].speech)
        self.assert_clean(session)
