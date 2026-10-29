"""Real wire format/failure handling through MockTransport, without network access."""
import base64
import io
import json
import unittest
from unittest.mock import patch
import wave

import httpx
from PIL import Image

from jukebox.config import Settings
from jukebox.providers import ClassProviders, MusicPoll, MusicTicket, PROBES, ProviderFailure


def wav_bytes():
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(24000)
        audio.writeframes(b"\x01\x00" * 240)
    return buffer.getvalue()


def png_bytes():
    buffer = io.BytesIO()
    Image.new("RGB", (512, 512), "navy").save(buffer, format="PNG")
    return buffer.getvalue()


class ProviderTests(unittest.TestCase):
    def make(self, callback):
        env = {key: value for role, port in {"TEXT": 9001, "ART": 9006, "MUSIC": 9007, "SPEECH": 9008}.items()
               for key, value in [(f"JUKEBOX_{role}_ENDPOINT", f"http://dobolyi.com:{port}/v1"),
                                  (f"JUKEBOX_{role}_API_KEY", "private-test-key")]}
        provider = ClassProviders(Settings.load(None, env), transport=httpx.MockTransport(callback))
        self.addCleanup(provider.close)
        return provider

    def test_text_request_matches_verified_probe_and_returns_only_final_content(self):
        def reply(request):
            self.assertEqual(request.url.port, 9001)
            self.assertEqual(request.url.path, "/v1/chat/completions")
            self.assertEqual(json.loads(request.content), PROBES["text"]["request"])
            self.assertEqual(request.headers["authorization"], "Bearer private-test-key")
            return httpx.Response(200, json={"model": PROBES["text"]["request"]["model"], "choices": [{"finish_reason": "stop", "message": {"content": "CONTRACT_OK", "reasoning": "not public"}}]})
        provider = self.make(reply)
        self.assertEqual(provider.text(PROBES["text"]["request"]["messages"][0]["content"]), "CONTRACT_OK")

    def test_art_fully_decodes_and_request_matches_probe(self):
        def reply(request):
            self.assertEqual(json.loads(request.content), PROBES["art"]["request"])
            return httpx.Response(200, json={"data": [{"b64_json": base64.b64encode(png_bytes()).decode()}]})
        self.assertEqual(self.make(reply).cover(PROBES["art"]["request"]["prompt"]).content, png_bytes())

    def test_speech_omits_voice_and_decodes_wav(self):
        def reply(request):
            self.assertEqual(request.url.port, 9008)
            self.assertEqual(json.loads(request.content), PROBES["speech"]["request"])
            return httpx.Response(200, content=wav_bytes(), headers={"content-type": "audio/wav"})
        self.assertEqual(self.make(reply).speech("Welcome to the jukebox.").content_type, "audio/wav")

    def test_music_submit_poll_download_preserves_routes_and_nested_json(self):
        seen = []
        def reply(request):
            seen.append(request.url.path)
            self.assertEqual(request.url.port, 9007)
            if request.url.path == "/release_task":
                self.assertEqual(json.loads(request.content), PROBES["music"]["request"])
                return httpx.Response(200, json={"code": 200, "error": None, "data": {"task_id": "ticket"}})
            if request.url.path == "/query_result":
                self.assertEqual(json.loads(request.content), {"task_id_list": ["ticket"]})
                result = json.dumps([{"file": "/v1/audio?path=%2Fopaque.wav", "dit_model": "acestep-v15-xl-turbo", "status": 1}])
                return httpx.Response(200, json={"code": 200, "error": None, "data": [{"task_id": "ticket", "status": 1, "result": result}]})
            self.assertIn("path=%2Fopaque.wav", str(request.url))
            return httpx.Response(200, content=wav_bytes(), headers={"content-type": "audio/wav"})
        provider = self.make(reply)
        ticket = provider.submit_music(PROBES["music"]["request"]["prompt"])
        result = provider.poll_music(ticket)
        self.assertEqual(result.state, "succeeded")
        self.assertEqual(provider.download_music(result).content, wav_bytes())
        self.assertEqual(seen, ["/release_task", "/query_result", "/v1/audio"])

    def test_music_pending_and_failure_do_not_resubmit(self):
        for status in (0, 2):
            requests = []
            def reply(request):
                requests.append(request.url.path)
                return httpx.Response(200, json={"code": 200, "error": None, "data": [{"task_id": "ticket", "status": status, "result": "private provider details"}]})
            provider = self.make(reply)
            if status == 0:
                self.assertEqual(provider.poll_music(MusicTicket("ticket")).state, "running")
            else:
                with self.assertRaises(ProviderFailure) as caught:
                    provider.poll_music(MusicTicket("ticket"))
                self.assertEqual(caught.exception.error.code, "generation_failed")
                self.assertNotIn("private provider details", str(caught.exception))
            self.assertEqual(requests, ["/query_result"])

    def test_cross_origin_or_wrong_route_download_never_sends_a_request(self):
        provider = self.make(lambda request: self.fail("Request must be rejected before authentication"))
        for path in ("http://other.example/v1/audio?path=x", "http://[bad/v1/audio?path=x", "//other.example/v1/audio?path=x",
                     "/other?path=x", "/v1/audio?url=elsewhere", "/v1/audio?path=a&path=b",
                     "/v1/audio?path=a&path=", "/v1/audio?path=", "/v1/audio?path=%20", "/v1/audio?path=a&broken"):
            with self.subTest(path=path), self.assertRaises(ProviderFailure):
                provider.download_music(MusicPoll("succeeded", path))

    def test_provider_statuses_are_safe_and_never_automatically_retried(self):
        for status, code in ((302, "rejected"), (401, "rejected"), (429, "rate_limited"), (503, "unavailable")):
            calls = []
            def reply(request):
                calls.append(request)
                return httpx.Response(status, text="private-test-key /server/private", headers={"location": "http://other.example"})
            with self.subTest(status=status), self.assertRaises(ProviderFailure) as caught:
                self.make(reply).text("Hello")
            self.assertEqual(caught.exception.error.code, code)
            self.assertNotIn("private-test-key", str(caught.exception))
            self.assertNotIn("/server/private", str(caught.exception))
            self.assertEqual(len(calls), 1)

    def test_timeout_and_network_errors_are_sanitized(self):
        for error, code in ((httpx.ReadTimeout("private-test-key"), "timeout"), (httpx.ConnectError("private-test-key"), "unavailable")):
            def reply(request):
                raise error
            with self.assertRaises(ProviderFailure) as caught:
                self.make(reply).text("Hi")
            self.assertEqual(caught.exception.error.code, code)
            self.assertNotIn("private-test-key", str(caught.exception))

    def test_httpx_invalid_url_has_a_reachable_sanitized_handler(self):
        def reply(request):
            raise httpx.InvalidURL("private-test-key")
        with self.assertRaises(ProviderFailure) as caught:
            self.make(reply).text("Hello")
        self.assertEqual(caught.exception.error.code, "invalid_response")
        self.assertNotIn("private-test-key", str(caught.exception))

    def test_response_cap_and_malformed_json_fail_safely(self):
        with patch("jukebox.providers.MAX_BYTES", 10):
            provider = self.make(lambda request: httpx.Response(200, content=b"x" * 11))
            with self.assertRaises(ProviderFailure):
                provider.text("Hi")
        provider = self.make(lambda request: httpx.Response(200, content=b"not-json", headers={"content-type": "application/json"}))
        with self.assertRaises(ProviderFailure):
            provider.text("Hi")

    def test_mismatched_music_ticket_or_model_is_rejected(self):
        for ticket, model in (("other-ticket", "acestep-v15-xl-turbo"), ("ticket", "wrong-model")):
            value = {"code": 200, "error": None, "data": [{"task_id": ticket, "status": 1, "result": json.dumps([{"file": "/v1/audio?path=x", "dit_model": model, "status": 1}])}]}
            with self.assertRaises(ProviderFailure):
                self.make(lambda request: httpx.Response(200, json=value)).poll_music(MusicTicket("ticket"))

    def test_truncated_media_is_rejected_not_just_header_checked(self):
        for raw in (b"RIFF" + b"\0" * 4 + b"WAVE" + b"\0" * 40, wav_bytes()[:-5]):
            with self.assertRaises(ProviderFailure):
                ClassProviders._wav(raw, "audio/wav")
        value = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"garbage").decode()
        with self.assertRaises(ProviderFailure):
            self.make(lambda request: httpx.Response(200, json={"data": [{"b64_json": value}]})).cover("Cover")

    def test_missing_configuration_never_sends_a_request(self):
        provider = ClassProviders(Settings.load(None, {}), transport=httpx.MockTransport(lambda request: self.fail("No request allowed")))
        self.addCleanup(provider.close)
        with self.assertRaises(ProviderFailure) as caught:
            provider.text("Hi")
        self.assertEqual(caught.exception.error.code, "not_configured")
