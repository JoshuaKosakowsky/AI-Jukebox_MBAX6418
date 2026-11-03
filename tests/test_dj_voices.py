"""Offline speaker choice, captured jobs, reference precedence and cache safety."""
import json
import shutil
import subprocess
import unittest
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient

from jukebox.app import create_app
from jukebox.config import ROOT, Settings
from jukebox.providers import ClassProviders, DJ_VOICES, PROBES
from jukebox.samples import load_samples
from jukebox.sessions import MAX_MEDIA_BYTES, SessionStore
from tests.test_dj import DjRecorders, speech_wav
from tests.test_references import wav_bytes


def settings():
    return Settings.load(None, {
        f"JUKEBOX_{role}_{suffix}": value
        for role, port in [("TEXT", 9001), ("SPEECH", 9008)]
        for suffix, value in [("ENDPOINT", f"http://dobolyi.com:{port}/v1"), ("API_KEY", "synthetic-only")]
    })


class SavedVoiceTests(unittest.TestCase):
    def test_preferences_are_local_validated_and_do_not_generate_or_clear_media(self):
        with TestClient(create_app(Settings({})), base_url="http://localhost") as client:
            initial = client.get("/api/session").json()
            self.assertEqual(initial["dj_voice"], "default")
            with patch.object(ClassProviders, "_request", side_effect=AssertionError("no generation")) as wire:
                for voice in DJ_VOICES:
                    response = client.post("/api/playback/voice", json={"voice": voice})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {**initial, "dj_voice": voice})
                    self.assertEqual(client.get("/api/session").json(), response.json())
                before = client.get("/api/session").json()
                for body in [{}, {"voice": "unlisted"}, {"voice": DJ_VOICES["female"]},
                             {"voice": None}, {"voice": 1}, {"voice": "female", "reference_id": "extra"}]:
                    self.assertEqual(client.post("/api/playback/voice", json=body).status_code, 422)
                    self.assertEqual(client.get("/api/session").json(), before)
                token = client.cookies.get("jukebox_session")
                client.cookies.clear()
                self.assertEqual(client.get("/api/session").json()["dj_voice"], "default")
                client.cookies.set("jukebox_session", token)
                self.assertEqual(client.get("/api/session").json(), before)
                wire.assert_not_called()

    def test_all_choices_reach_speech_and_cached_replay_never_regenerates(self):
        calls = []

        def wire(request):
            body = json.loads(request.content)
            calls.append((request.url.port, body))
            if request.url.port == 9001:
                return httpx.Response(200, json={"model": PROBES["text"]["request"]["model"],
                    "choices": [{"message": {"content": "Offline introduction."}, "finish_reason": "stop"}]})
            return httpx.Response(200, content=speech_wav(), headers={"content-type": "audio/wav"})

        with TestClient(create_app(settings()), base_url="http://localhost") as client:
            app = client.app
            app.state.providers.close()
            app.state.providers = ClassProviders(settings(), transport=httpx.MockTransport(wire))
            tracks = client.get("/api/session").json()["tracks"]
            for track in tracks:
                self.assertEqual(client.post("/api/playback/queue", json={"track_id": track["id"]}).status_code, 200)
            first_media = None
            for index, choice in enumerate(DJ_VOICES):
                count = len(calls)
                client.post("/api/playback/voice", json={"voice": choice})
                self.assertEqual(len(calls), count)
                result = client.post("/api/playback/start" if index == 0 else "/api/playback/advance", json={})
                self.assertEqual(result.status_code, 200)
                self.assertEqual([port for port, _ in calls[-2:]], [9001, 9008])
                speech = calls[-1][1]
                self.assertNotIn("ref_audio", speech)
                expected = {**PROBES["speech"]["request"], "input": "Offline introduction."}
                if choice != "default":
                    expected["voice"] = {"id": DJ_VOICES[choice]}
                self.assertEqual(speech, expected)
                snapshot = client.get("/api/session").json()
                self.assertEqual(snapshot["jobs"][-1]["state"], "succeeded")
                first_media = first_media or snapshot["tracks"][0]["speech"]
                self.assertEqual(snapshot["tracks"][0]["speech"], first_media)
                self.assertNotIn(DJ_VOICES["female"], json.dumps(snapshot))
            count = len(calls)
            client.post("/api/playback/advance", json={})
            client.post("/api/playback/voice", json={"voice": "default"})
            client.post("/api/playback/start", json={})
            self.assertEqual(len(calls), count)

    def test_inflight_job_keeps_its_voice_and_new_job_uses_current_choice(self):
        class Recorder(DjRecorders):
            def speech(self, text, **kwargs):
                self.choices.append(kwargs)
                return super().speech(text)

        store = SessionStore(load_samples(ROOT, max_bytes=MAX_MEDIA_BYTES))
        session = store.resolve(None)
        for track in list(session.tracks)[:2]:
            store.queue_playback(session, track)
        store.set_dj_voice(session, "female")
        _, first = store.start_playback(session)
        store.set_dj_voice(session, "alternate")
        provider = Recorder()
        provider.choices = []
        store.generate_dj_speech(session, first.id, provider)
        _, second = store.advance_playback(session)
        store.generate_dj_speech(session, second.id, provider)
        self.assertEqual(provider.choices, [{"voice": "female"}, {"voice": "alternate"}])
        self.assertEqual(session.speech_voices, {})
        self.assertEqual(store.snapshot(session).dj_voice, "alternate")

    def test_failed_saved_voice_has_no_default_fallback_or_automatic_retry(self):
        calls = []

        def wire(request):
            calls.append(json.loads(request.content))
            if request.url.port == 9001:
                return httpx.Response(200, json={"model": PROBES["text"]["request"]["model"],
                    "choices": [{"message": {"content": "Offline introduction."}, "finish_reason": "stop"}]})
            return httpx.Response(404, json={"private": "UPSTREAM-PRIVATE-MARKER"})

        with TestClient(create_app(settings()), base_url="http://localhost") as client:
            client.app.state.providers.close()
            client.app.state.providers = ClassProviders(settings(), transport=httpx.MockTransport(wire))
            track = client.get("/api/session").json()["tracks"][0]["id"]
            client.post("/api/playback/voice", json={"voice": "female"})
            client.post("/api/playback/queue", json={"track_id": track})
            client.post("/api/playback/start", json={})
            snapshot = client.get("/api/session").json()
            self.assertEqual(snapshot["jobs"][-1]["state"], "failed")
            self.assertIsNone(snapshot["tracks"][0]["speech"])
            self.assertNotIn("UPSTREAM-PRIVATE-MARKER", json.dumps(snapshot))
            self.assertEqual(len(calls), 2)
            self.assertEqual(client.app.state.sessions.resolve(client.cookies.get("jukebox_session")).speech_voices, {})
            client.post("/api/playback/advance", json={})
            client.post("/api/playback/voice", json={"voice": "alternate"})
            client.post("/api/playback/start", json={})
            client.get("/api/session")
            self.assertEqual(len(calls), 2)
            client.post("/api/playback/speech", json={"track_id": track})
            self.assertEqual(len(calls), 4)
            self.assertEqual(calls[-1]["voice"], {"id": DJ_VOICES["alternate"]})

    def test_reference_overrides_saved_voice_without_changing_preference(self):
        calls = []

        def wire(request):
            body = json.loads(request.content)
            calls.append(body)
            if request.url.port == 9001:
                return httpx.Response(200, json={"model": PROBES["text"]["request"]["model"],
                    "choices": [{"message": {"content": "Offline introduction."}, "finish_reason": "stop"}]})
            return httpx.Response(200, content=speech_wav(), headers={"content-type": "audio/wav"})

        with TestClient(create_app(settings()), base_url="http://localhost") as client:
            client.app.state.providers.close()
            client.app.state.providers = ClassProviders(settings(), transport=httpx.MockTransport(wire))
            track = client.get("/api/session").json()["tracks"][0]["id"]
            client.post("/api/playback/voice", json={"voice": "female"})
            upload = client.post("/api/references/speech", files={"file": ("synthetic.wav", wav_bytes(), "audio/wav")})
            response = client.post("/api/playback/speech", json={"track_id": track, "reference_id": upload.json()["id"]})
            self.assertEqual(response.status_code, 202)
            self.assertIn("ref_audio", calls[-1])
            self.assertNotIn("voice", calls[-1])
            self.assertEqual(client.get("/api/session").json()["dj_voice"], "female")

    def test_provider_refuses_unknown_ids_and_ambiguous_reference_without_network(self):
        with patch.object(ClassProviders, "_request", side_effect=AssertionError("no network")) as wire:
            provider = ClassProviders(settings())
            try:
                for choice in ["unlisted", DJ_VOICES["female"]]:
                    with self.assertRaises(ValueError):
                        provider.speech("Offline.", voice=choice)
                from jukebox.providers import MediaBytes
                with self.assertRaises(ValueError):
                    provider.speech("Offline.", reference=MediaBytes(wav_bytes(), "audio/wav"), voice="female")
                wire.assert_not_called()
            finally:
                provider.close()

    @unittest.skipUnless(shutil.which("node"), "Node is unavailable")
    def test_frontend_choice_handler_serializes_rolls_back_and_preserves_failure_reference(self):
        result = subprocess.run(["node", str(ROOT / "tests/frontend_dj_voice_probe.cjs"),
                                 str(ROOT / "jukebox/web/app.js")], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
