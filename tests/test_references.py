"""Offline A3-06 reference-voice integration through real HTTP routes and the store.

No class-service calls: the speech provider is exercised through MockTransport
with synthesized WAV/MP3 fixtures. Uploaded bytes must be validated, kept out
of every snapshot and Git, consumed once, and cleaned up with the session.
Live Chatterbox verification of the reference path is pending acceptance.
"""
import base64
import io
import json
import time
import unittest
from unittest.mock import patch
import wave

import httpx

from fastapi.testclient import TestClient
from jukebox.app import create_app
from jukebox.config import Settings
from jukebox.providers import ClassProviders, MediaBytes
from jukebox.sessions import (MAX_REFERENCES, SESSION_COOKIE, SESSION_SECONDS,
                              SessionFailure, SessionStore)


def wav_bytes(seconds=2.0, rate=8000, marker=b"\x01\x00"):
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(rate)
        audio.writeframes(marker * int(seconds * rate))
    return buffer.getvalue()


def mp3_bytes(seconds_hint=2):
    # Structural MP3 fingerprint: an ID3v2 header declaring zero tag bytes, then
    # minimal valid-looking MPEG-1 Layer III frame headers with stub payloads.
    # Validation is structural (reachable frame required), not a full decode.
    frame = b"\xff\xfb\x90\x00" + b"\x00" * 26
    return b"ID3\x04\x00\x00\x00\x00\x00\x00" + frame * max(1, seconds_hint * 7)


def speech_settings():
    return Settings.load(None, {"JUKEBOX_SPEECH_ENDPOINT": "http://dobolyi.com:9008/v1",
                                "JUKEBOX_SPEECH_API_KEY": "private-offline-marker"})


class ReferenceHttpTests(unittest.TestCase):
    def upload(self, client, content, filename="voice.wav", media_type="audio/wav"):
        return client.post("/api/references/speech",
                           files={"file": (filename, content, media_type)})

    def test_wav_and_mp3_uploads_validate_and_stay_out_of_every_snapshot(self):
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            wav = self.upload(client, wav_bytes() + b"PRIVATE-MARKER")
            self.assertEqual(wav.status_code, 201)
            ref_id = wav.json()["id"]
            self.assertEqual(wav.json()["media_type"], "audio/wav")
            mp3 = self.upload(client, mp3_bytes(), filename="voice.mp3", media_type="audio/mpeg")
            self.assertEqual(mp3.status_code, 201)
            self.assertEqual(mp3.json()["media_type"], "audio/mpeg")
            snapshot = str(client.get("/api/session").json())
            self.assertNotIn("PRIVATE-MARKER", snapshot)
            self.assertNotIn(ref_id, snapshot)
            self.assertNotIn("references", snapshot)
            self.assertEqual(client.delete(f"/api/references/speech/{ref_id}").status_code, 204)
            self.assertEqual(client.delete(f"/api/references/speech/{ref_id}").status_code, 404)

    def test_invalid_oversize_and_bad_duration_references_are_rejected(self):
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            self.assertEqual(self.upload(client, b"not audio at all").status_code, 422)
            self.assertEqual(self.upload(client, b"RIFFriffWAVEgarbage").status_code, 422)
            too_long = wav_bytes(seconds=61, rate=8000)
            self.assertEqual(self.upload(client, too_long).status_code, 422)
            too_short = wav_bytes(seconds=0.1, rate=8000)
            self.assertEqual(self.upload(client, too_short).status_code, 422)
            with patch("jukebox.sessions.MAX_REFERENCE_BYTES", 100):
                self.assertEqual(self.upload(client, wav_bytes(seconds=2, rate=8000)).status_code, 422)
            self.assertEqual(len(client.get("/api/session").json()["tracks"]), 0)

    def test_session_isolation_and_capacity_limits(self):
        app = create_app(speech_settings())
        with TestClient(app, base_url="http://localhost") as first:
            uploaded = self.upload(first, wav_bytes()).json()
            token = first.cookies.get(SESSION_COOKIE)
            self.assertIsNotNone(token)
            first.cookies.clear()
            self.assertEqual(self.upload(first, wav_bytes()).status_code, 201)
            self.assertEqual(first.delete(f"/api/references/speech/{uploaded['id']}").status_code, 404)
            first.cookies.set(SESSION_COOKIE, token)
            self.assertEqual(first.delete(f"/api/references/speech/{uploaded['id']}").status_code, 204)
            with patch("jukebox.sessions.MAX_REFERENCES", 1):
                self.assertEqual(self.upload(first, wav_bytes()).status_code, 201)
                self.assertEqual(self.upload(first, wav_bytes()).status_code, 429)

    def test_reference_bytes_are_never_served_back_or_leaked(self):
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            uploaded = self.upload(client, wav_bytes(seconds=1, rate=8000)).json()
            # No read route exists: GET on the reference path is 405 and the
            # bytes cannot be retrieved through media either.
            self.assertEqual(client.get(f"/api/references/speech/{uploaded['id']}").status_code, 405)
            self.assertEqual(client.get(f"/api/media/{uploaded['id']}").status_code, 404)

    def test_multipart_uploads_never_touch_disk_even_above_one_megabyte(self):
        # A real multi-MB PCM WAV, larger than the framework's 1 MB spool
        # boundary; any temp-file usage anywhere in the request path fails.
        big = wav_bytes(seconds=12, rate=44100)
        self.assertGreater(len(big), 1_000_000)
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            with patch("tempfile.SpooledTemporaryFile", side_effect=AssertionError("disk spool used")) as spool, \
                 patch("tempfile.TemporaryFile", side_effect=AssertionError("disk temp used")) as tmp:
                response = self.upload(client, big)
            self.assertEqual(response.status_code, 201)
            spool.assert_not_called()
            tmp.assert_not_called()

    def test_oversized_upload_is_rejected_without_touching_disk(self):
        over = b"\x00" * 5_000_001
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            with patch("tempfile.SpooledTemporaryFile", side_effect=AssertionError("disk spool used")) as spool, \
                 patch("tempfile.TemporaryFile", side_effect=AssertionError("disk temp used")) as tmp:
                response = self.upload(client, over)
            self.assertEqual(response.status_code, 422)
            spool.assert_not_called()
            tmp.assert_not_called()

    def test_oversized_stream_is_aborted_before_parsing(self):
        boundary = b"X-boundary"
        body = (b"--" + boundary + b"\r\n"
                b'Content-Disposition: form-data; name="file"; filename="big.wav"\r\n'
                b"Content-Type: audio/wav\r\n\r\n"
                + b"\x00" * 6_000_000 +
                b"\r\n--" + boundary + b"--\r\n")
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            response = client.post(
                "/api/references/speech", content=body,
                headers={"Content-Type": "multipart/form-data; boundary=X-boundary"})
            self.assertEqual(response.status_code, 422)

    def test_header_only_wav_with_declared_but_missing_frames_is_rejected(self):
        fmt = (b"\x01\x00"        # PCM
               b"\x01\x00"        # mono
               b"\x44\xac\x00\x00"   # 44100 Hz
               b"\x88\x58\x01\x00"   # byte rate
               b"\x02\x00"        # block align
               b"\x10\x00")       # 16 bit
        header_only = (b"RIFF" + (36 + 64_000).to_bytes(4, "little") + b"WAVE"
                       + b"fmt " + (16).to_bytes(4, "little") + fmt
                       + b"data" + (64_000).to_bytes(4, "little"))
        self.assertLess(len(header_only), 100)
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            self.assertEqual(self.upload(client, header_only).status_code, 422)

    def test_bare_id3_and_truncated_mp3_are_rejected(self):
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            self.assertEqual(self.upload(client, b"ID3", filename="voice.mp3",
                                         media_type="audio/mpeg").status_code, 422)
            # ID3v2 tag declares 1000 bytes but the upload stops after 24.
            truncated = b"ID3\x04\x00\x00" + b"\x00\x00\x07\xd0" + b"\x00" * 24
            self.assertEqual(self.upload(client, truncated, filename="voice.mp3",
                                         media_type="audio/mpeg").status_code, 422)

    def test_mp3_without_reachable_frames_is_rejected(self):
        tags_only = b"ID3\x04\x00\x00\x00\x00\x00\x00" + b"TAG" * 10
        self.assertEqual(tags_only[10:13], b"TAG")  # no MPEG sync anywhere
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            self.assertEqual(self.upload(client, tags_only, filename="voice.mp3",
                                         media_type="audio/mpeg").status_code, 422)

    def test_missing_chunks_and_non_pcm_wavs_are_rejected(self):
        no_data = b"RIFF" + (36).to_bytes(4, "little") + b"WAVE" + b"fmt " + (16).to_bytes(4, "little") + b"\x01" * 16
        with TestClient(create_app(speech_settings()), base_url="http://localhost") as client:
            self.assertEqual(self.upload(client, no_data).status_code, 422)
            float_wav = b"RIFF" + (36).to_bytes(4, "little") + b"WAVE" \
                + b"fmt " + (16).to_bytes(4, "little") \
                + b"\x03\x00\x01\x00\x44\xac\x00\x00\x88\x58\x01\x00\x02\x00\x20\x00" \
                + b"data" + (8000).to_bytes(4, "little") + b"\x00" * 8000
            self.assertEqual(self.upload(client, float_wav).status_code, 422)


class ReferenceStoreTests(unittest.TestCase):
    def setUp(self):
        self.store = SessionStore()
        self.session = self.store.resolve(None)

    def test_upload_take_delete_cycle(self):
        identifier, media_type = self.store.upload_reference(self.session, wav_bytes())
        self.assertEqual(media_type, "audio/wav")
        taken = self.store.take_reference(self.session, identifier)
        self.assertIsNotNone(taken)
        self.assertEqual(taken.content, wav_bytes())
        self.assertIsNone(self.store.take_reference(self.session, identifier))
        second, _ = self.store.upload_reference(self.session, wav_bytes())
        self.store.drop_reference(self.session, second)
        with self.assertRaises(SessionFailure):
            self.store.drop_reference(self.session, second)

    def test_expiry_clears_references_with_the_session(self):
        identifier, _ = self.store.upload_reference(self.session, wav_bytes())
        self.session.touched = time.monotonic() - SESSION_SECONDS - 1
        replacement = self.store.resolve(self.session.token)
        self.assertNotEqual(replacement.token, self.session.token)
        self.assertNotIn(identifier, replacement.references)

    def test_snapshot_never_contains_reference_state(self):
        self.store.upload_reference(self.session, wav_bytes() + b"PRIVATE-MARKER")
        snapshot = self.store.snapshot(self.session)
        self.assertNotIn("PRIVATE-MARKER", str(snapshot.model_dump(mode="json")))


class ProviderReferenceTests(unittest.TestCase):
    def make(self, callback):
        env = {"JUKEBOX_SPEECH_ENDPOINT": "http://dobolyi.com:9008/v1",
               "JUKEBOX_SPEECH_API_KEY": "private-test-key"}
        provider = ClassProviders(Settings.load(None, env), transport=httpx.MockTransport(callback))
        self.addCleanup(provider.close)
        return provider

    def test_speech_without_reference_stays_byte_identical_to_the_probe(self):
        def reply(request):
            from jukebox.providers import PROBES
            self.assertEqual(json.loads(request.content), PROBES["speech"]["request"])
            return httpx.Response(200, content=wav_bytes(seconds=1, rate=24000),
                                  headers={"content-type": "audio/wav"})
        # Same input as the frozen probe: the payload must be byte-identical.
        self.assertEqual(self.make(reply).speech("Welcome to the jukebox.").content_type, "audio/wav")

    def test_speech_with_reference_sends_a_data_uri_and_decodes(self):
        seen = {}
        def reply(request):
            seen["payload"] = json.loads(request.content)
            return httpx.Response(200, content=wav_bytes(seconds=1, rate=24000),
                                  headers={"content-type": "audio/wav"})
        reference = MediaBytes(wav_bytes(seconds=1, rate=8000), "audio/wav")
        result = self.make(reply).speech("Speak like me.", reference=reference)
        self.assertEqual(result.content_type, "audio/wav")
        self.assertIn("ref_audio", seen["payload"])
        prefix, b64 = seen["payload"]["ref_audio"].split(",", 1)
        self.assertEqual(prefix, "data:audio/wav;base64")
        self.assertEqual(base64.b64decode(b64), reference.content)
        self.assertEqual(seen["payload"]["input"], "Speak like me.")
