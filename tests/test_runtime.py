"""Offline config, domain and actual HTTP-shell behavior; no provider calls."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from pydantic import ValidationError

from jukebox.app import create_app
from jukebox.config import ConfigurationError, ROOT, Settings
from jukebox.contracts import GenerationJob, JobState, MediaRef, Playback, SafeError, SessionSnapshot, SongSettings, Track, schema


def configured_values():
    return {key: value for role, port in {"TEXT": 9001, "ART": 9006, "MUSIC": 9007, "SPEECH": 9008}.items()
            for key, value in [(f"JUKEBOX_{role}_ENDPOINT", f"http://dobolyi.com:{port}/v1"),
                               (f"JUKEBOX_{role}_API_KEY", "local-test-marker-never-public")]}


class ConfigTests(unittest.TestCase):
    def test_missing_and_example_settings_launch_as_unconfigured(self):
        self.assertEqual(set(Settings.load(None, {}).public_status().values()), {"missing"})
        self.assertEqual(Settings.load(ROOT / ".env.example", {}).services, {})

    def test_environment_overrides_explicit_dotenv_and_does_not_interpolate(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / ".env"
            path.write_text('JUKEBOX_TEXT_ENDPOINT=http://dobolyi.com:9001/v1\nJUKEBOX_TEXT_API_KEY="${SECRET}"\n')
            settings = Settings.load(path, {})
            self.assertEqual(settings.services["text"].key.get_secret_value(), "${SECRET}")
            settings = Settings.load(path, {"JUKEBOX_TEXT_API_KEY": "override"})
            self.assertEqual(settings.services["text"].key.get_secret_value(), "override")

    def test_wrong_origin_port_path_and_embedded_key_are_rejected_safely(self):
        for endpoint in ("http://dobolyi.com:9000/v1", "https://other.example:9001/v1",
                         "http://user:secret@dobolyi.com:9001/v1", "http://dobolyi.com:9001/v1?secret=oops",
                         "http://dobolyi.com:9001/other", "http://dobolyi.com:bad/v1"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ConfigurationError) as caught:
                Settings.load(None, {"JUKEBOX_TEXT_ENDPOINT": endpoint})
            self.assertNotIn(endpoint, str(caught.exception))
            self.assertNotIn("oops", str(caught.exception))

    def test_public_status_and_repr_do_not_expose_key(self):
        settings = Settings.load(None, configured_values())
        self.assertEqual(set(settings.public_status().values()), {"configured"})
        self.assertNotIn("local-test-marker-never-public", repr(settings))
        self.assertNotIn("dobolyi.com", json.dumps(settings.public_status()))

    def test_header_injection_key_is_rejected(self):
        values = configured_values()
        values["JUKEBOX_TEXT_API_KEY"] = "private\nheader"
        with self.assertRaises(ConfigurationError) as caught:
            Settings.load(None, values)
        self.assertNotIn("private", str(caught.exception))


class ContractTests(unittest.TestCase):
    def settings(self):
        return SongSettings(style="Piano", mood="Calm", duration_seconds=10)

    def test_track_identity_survives_round_trip_and_requires_ready_audio(self):
        track = Track(title="First", settings=self.settings())
        self.assertEqual(Track.model_validate_json(track.model_dump_json()).id, track.id)
        with self.assertRaises(ValidationError):
            Track(title="Missing audio", settings=self.settings(), status="ready")

    def test_media_urls_are_local_and_match_asset_ids(self):
        asset = uuid4()
        self.assertEqual(MediaRef(id=asset, url=f"/api/media/{asset}", content_type="audio/wav").id, asset)
        for url in ("https://other.example/file", "/v1/audio?path=private", f"/api/media/{uuid4()}"):
            with self.assertRaises(ValidationError):
                MediaRef(id=asset, url=url, content_type="audio/wav")

    def test_job_transitions_are_monotonic_and_terminal(self):
        queued = GenerationJob(track_id=uuid4(), kind="music")
        running = queued.transition(JobState.RUNNING, progress=.5)
        done = running.transition(JobState.SUCCEEDED)
        self.assertEqual(done.progress, 1)
        for previous, target in ((queued, JobState.SUCCEEDED), (done, JobState.RUNNING)):
            with self.assertRaises(ValueError):
                previous.transition(target)
        with self.assertRaises(ValueError):
            running.transition(JobState.FAILED, progress=.1, error=SafeError(code="timeout", message="Timed out"))

    def test_failed_jobs_need_safe_errors(self):
        with self.assertRaises(ValidationError):
            GenerationJob(track_id=uuid4(), kind="music", state="failed")
        failed = GenerationJob(track_id=uuid4(), kind="music").transition(JobState.FAILED, error=SafeError(code="timeout", message="Timed out"))
        self.assertEqual(failed.error.code, "timeout")

    def test_playback_cannot_speak_and_play_simultaneously_and_pause_has_origin(self):
        track = uuid4()
        playing = Playback(state="playing", queue=[track], current_track_id=track)
        self.assertEqual(playing.state, "playing")
        with self.assertRaises(ValidationError):
            Playback(state="paused", queue=[track], current_track_id=track)
        with self.assertRaises(ValidationError):
            Playback(state="speaking", queue=[track], current_track_id=uuid4())
        with self.assertRaises(ValidationError):
            Playback(state="playing", queue=[track], current_track_id=track, speech_playing=True)

    def test_session_rejects_dangling_ids_and_duplicate_tracks(self):
        track = Track(title="One", settings=self.settings())
        with self.assertRaises(ValidationError):
            SessionSnapshot(tracks=[track, track])
        with self.assertRaises(ValidationError):
            SessionSnapshot(jobs=[GenerationJob(track_id=uuid4(), kind="art")])
        with self.assertRaises(ValidationError):
            SessionSnapshot(playback=Playback(queue=[uuid4()]))

    def test_invalid_duration_and_blank_style_are_rejected(self):
        for duration in (0, 601):
            with self.assertRaises(ValidationError):
                SongSettings(style="Piano", mood="Calm", duration_seconds=duration)
        with self.assertRaises(ValidationError):
            SongSettings(style="  ", mood="Calm", duration_seconds=10)

    def test_checked_in_schema_matches_model(self):
        self.assertEqual(json.loads((ROOT / "contracts/app.schema.json").read_text()), schema())


class AppTests(unittest.TestCase):
    def client(self, settings=None):
        return TestClient(create_app(settings or Settings.load(None, {})), base_url="http://localhost")

    def test_normal_startup_and_gets_never_call_provider_methods(self):
        with patch("jukebox.providers.ClassProviders._request", side_effect=AssertionError("No service calls on startup")):
            with self.client() as client:
                self.assertEqual(client.get("/api/health").json()["status"], "ok")
                self.assertEqual(client.get("/api/session").json()["tracks"], [])
                self.assertFalse(client.get("/api/status").json()["configured"])
                self.assertIn("$defs", client.get("/api/contracts").json())
                self.assertEqual(client.get("/static/app.js").status_code, 200)
                self.assertIn("Session library", client.get("/").text)

    def test_configured_status_is_not_connectivity_or_secret_disclosure(self):
        with self.client(Settings.load(None, configured_values())) as client:
            response = client.get("/api/status")
            self.assertTrue(response.json()["configured"])
            self.assertFalse(response.json()["connectivity_checked"])
            self.assertFalse(response.json()["generation_available"])
            for path in ("/api/status", "/api/openapi.json", "/api/contracts", "/"):
                text = client.get(path).text
                self.assertNotIn("local-test-marker-never-public", text)
                self.assertNotIn("dobolyi.com", text)

    def test_private_files_and_host_rebinding_are_not_served(self):
        with self.client() as client:
            for path in ("/.env", "/class-endpoints.txt", "/static/../.env", "/.git/config"):
                self.assertEqual(client.get(path).status_code, 404)
            self.assertEqual(client.get("/", headers={"host": "evil.example"}).status_code, 400)
            self.assertEqual(client.post("/api/session", headers={"origin": "http://evil.example"}).status_code, 403)

    def test_same_origin_security_headers_and_no_global_mutable_library(self):
        with self.client() as client:
            response = client.get("/")
            self.assertEqual(response.headers["x-content-type-options"], "nosniff")
            self.assertIn("connect-src 'self'", response.headers["content-security-policy"])
            self.assertEqual(response.headers["cache-control"], "no-store")
            snapshot = client.get("/api/session").json()
            snapshot["tracks"].append({"title": "local mutation"})
            self.assertEqual(client.get("/api/session").json()["tracks"], [])
