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

    def test_poll_progress_never_claims_downloading_while_still_generating(self):
        item = self.add_track()
        job = self.store.queue_music(self.session, item.id)
        observed = []
        def running_poll(ticket):
            observed.append(self.session.jobs[job.id].progress)
            return MusicPoll("running")
        providers = Mock()
        providers.submit_music.return_value = MusicTicket("ticket")
        providers.poll_music.side_effect = running_poll
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.1), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, job.id, providers)
        self.assertEqual(self.session.jobs[job.id].state.value, "failed")
        self.assertTrue(len(observed) >= 2)
        self.assertTrue(all(value < 0.8 for value in observed),
                        "polling progress must stay below the UI's downloading stage")
        # The first poll sees the just-submitted stage; later polls advance into
        # the generating stage but never into downloading.
        self.assertEqual(observed[0], 0.3)
        self.assertTrue(all(value >= 0.35 for value in observed[1:]))

    def test_download_stage_is_marked_only_after_a_successful_poll(self):
        item = self.add_track()
        job = self.store.queue_music(self.session, item.id)
        seen = {}
        def download(result):
            seen["progress_at_download"] = self.session.jobs[job.id].progress
            return MediaBytes(wav_bytes(), "audio/wav")
        providers = Mock()
        providers.submit_music.return_value = MusicTicket("ticket")
        providers.poll_music.return_value = MusicPoll("succeeded", "/v1/audio?path=x")
        providers.download_music.side_effect = download
        self.store.generate_music(self.session, job.id, providers)
        self.assertEqual(seen["progress_at_download"], 0.9)
        self.assertEqual(self.session.jobs[job.id].progress, 1)

    def test_resume_reuses_retained_ticket_without_resubmitting(self):
        item = self.add_track()
        first = self.store.queue_music(self.session, item.id)
        stuck = Mock()
        stuck.submit_music.return_value = MusicTicket("same-task-123")
        stuck.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, first.id, stuck)
        self.assertEqual(self.session.jobs[first.id].state.value, "failed")
        resumed, source = self.store.resume_music(self.session, first.id, item.id)
        self.assertEqual(source, first.id)
        resumed_providers = Mock()
        resumed_providers.submit_music.side_effect = AssertionError("Resume must never submit a new task")
        polled_tickets = []
        def poll(ticket):
            polled_tickets.append(ticket)
            return MusicPoll("succeeded", "/v1/audio?path=x")
        resumed_providers.poll_music.side_effect = poll
        resumed_providers.download_music.return_value = MediaBytes(wav_bytes(), "audio/wav")
        self.store.generate_music(self.session, resumed.id, resumed_providers, resume_from=source)
        self.assertEqual(self.session.jobs[resumed.id].state.value, "succeeded")
        self.assertEqual(self.session.tracks[item.id].status, "ready")
        self.assertEqual(polled_tickets, [stuck.submit_music.return_value],
                         "the resumed job must poll the SAME retained provider ticket")
        self.assertEqual(stuck.submit_music.call_count, 1)
        self.assertNotIn(first.id, self.session.tickets)
        self.assertNotIn(resumed.id, self.session.tickets)

    def test_resume_rejected_for_unresumable_jobs(self):
        item = self.add_track()
        # A failed job whose submission was never confirmed has no ticket.
        first = self.store.queue_music(self.session, item.id)
        failed_submit = Mock()
        failed_submit.submit_music.side_effect = ProviderFailure(
            SafeError(code="unavailable", message="Could not reach the class service.", retryable=True))
        self.store.generate_music(self.session, first.id, failed_submit)
        with self.assertRaises(SessionFailure) as caught:
            self.store.resume_music(self.session, first.id, item.id)
        self.assertEqual(caught.exception.status, 409)
        self.assertIn("never confirmed", caught.exception.error.message)
        # Successful jobs are terminal history, not resumable.
        good = self.store.queue_music(self.session, item.id)
        self.store.generate_music(self.session, good.id, self.music_providers())
        with self.assertRaises(SessionFailure) as caught:
            self.store.resume_music(self.session, good.id, item.id)
        self.assertEqual(caught.exception.status, 404)
        # Non-retryable failures are not resumable either.
        hard = self.store.queue_music(self.session, item.id)
        non_retryable = Mock()
        non_retryable.submit_music.return_value = MusicTicket("ticket")
        non_retryable.poll_music.side_effect = ProviderFailure(
            SafeError(code="generation_failed", message="Music generation failed. You can submit a new job.", retryable=True))
        self.store.generate_music(self.session, hard.id, non_retryable)
        self.session.jobs[hard.id] = self.session.jobs[hard.id].model_validate(
            {**self.session.jobs[hard.id].model_dump(), "error": SafeError(code="rejected", message="Denied.", retryable=False)})
        with self.assertRaises(SessionFailure) as caught:
            self.store.resume_music(self.session, hard.id, item.id)
        self.assertEqual(caught.exception.status, 404)

    def test_resume_rejects_mismatched_track_without_side_effects(self):
        """Defect 1 regression: a resume URL with the wrong track must not allocate
        a job or active slot, and the rightful track stays resumable."""
        other = self.add_track("Other")
        item = self.add_track("Rightful")
        first = self.store.queue_music(self.session, item.id)
        stuck = Mock()
        stuck.submit_music.return_value = MusicTicket("private-ticket")
        stuck.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, first.id, stuck)
        jobs_before = len(self.session.jobs)
        with self.assertRaises(SessionFailure) as caught:
            self.store.resume_music(self.session, first.id, other.id)
        self.assertEqual(caught.exception.status, 404)
        self.assertEqual(len(self.session.jobs), jobs_before, "mismatched resume must not create a job")
        self.assertFalse(self.session.active, "mismatched resume must not consume an active slot")
        self.assertIn(first.id, self.session.tickets, "the retained ticket must survive")
        resumed, source = self.store.resume_music(self.session, first.id, item.id)
        self.assertEqual(source, first.id)
        self.assertEqual(resumed.track_id, item.id)

    def test_resume_failure_keeps_ticket_chain_and_releases_capacity(self):
        item = self.add_track()
        first = self.store.queue_music(self.session, item.id)
        stuck = Mock()
        stuck.submit_music.return_value = MusicTicket("same-task-123")
        stuck.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, first.id, stuck)
        resumed, source = self.store.resume_music(self.session, first.id, item.id)
        failing = Mock()
        failing.submit_music.side_effect = AssertionError("Resume must never submit")
        failing.poll_music.side_effect = ProviderFailure(
            SafeError(code="generation_failed", message="The original music task failed on the service.", retryable=True))
        self.store.generate_music(self.session, resumed.id, failing, resume_from=source)
        self.assertEqual(self.session.jobs[first.id].state.value, "failed")
        self.assertEqual(self.session.jobs[resumed.id].state.value, "failed")
        # The ticket chain now covers BOTH the original job and the resumed job,
        # so the latest failed job is itself resumable (Defect 3 regression).
        self.assertIn(first.id, self.session.tickets)
        self.assertIn(resumed.id, self.session.tickets)
        self.assertFalse(self.session.active)

    def test_repeated_resumes_of_same_task_need_only_one_submission(self):
        """Defect 3 regression: any number of resumed attempts of the SAME task
        must stay based on the one retained ticket; only one submit_music call."""
        item = self.add_track()
        first = self.store.queue_music(self.session, item.id)
        original = Mock()
        original.submit_music.return_value = MusicTicket("single-task")
        original.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, first.id, original)
        # Resume 1 also times out.
        r1, _ = self.store.resume_music(self.session, first.id, item.id)
        stuck = Mock()
        stuck.submit_music.side_effect = AssertionError("Resume must never submit")
        stuck.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, r1.id, stuck, resume_from=first.id)
        self.assertEqual(self.session.jobs[r1.id].state.value, "failed")
        # Resume 2 (from the LATEST failed job) succeeds and downloads.
        r2, source2 = self.store.resume_music(self.session, r1.id, item.id)
        self.assertEqual(source2, r1.id)
        finishing = Mock()
        finishing.submit_music.side_effect = AssertionError("Resume must never submit")
        polled = []
        def poll(ticket):
            polled.append(ticket)
            return MusicPoll("succeeded", "/v1/audio?path=x")
        finishing.poll_music.side_effect = poll
        finishing.download_music.return_value = MediaBytes(wav_bytes(), "audio/wav")
        self.store.generate_music(self.session, r2.id, finishing, resume_from=source2)
        self.assertEqual(self.session.jobs[r2.id].state.value, "succeeded")
        self.assertEqual(self.session.tracks[item.id].status, "ready")
        self.assertEqual(original.submit_music.call_count, 1, "exactly one provider submission across all attempts")
        self.assertEqual(polled, [original.submit_music.return_value])
        self.assertFalse(self.session.tickets, "all ticket associations clean after success")
        self.assertFalse(self.session.active)

    def test_resumed_terminal_service_failure_is_not_endlessly_resumable(self):
        """A provider-reported task failure on a resumed poll is terminal: re-polling
        can never succeed, so the job must not advertise further resumability."""
        item = self.add_track()
        first = self.store.queue_music(self.session, item.id)
        original = Mock()
        original.submit_music.return_value = MusicTicket("single-task")
        original.poll_music.return_value = MusicPoll("running")
        with patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            self.store.generate_music(self.session, first.id, original)
        r1, _ = self.store.resume_music(self.session, first.id, item.id)
        dead_task = Mock()
        dead_task.submit_music.side_effect = AssertionError("Resume must never submit")
        dead_task.poll_music.side_effect = ProviderFailure(
            SafeError(code="generation_failed", message="The music task failed.", retryable=True))
        self.store.generate_music(self.session, r1.id, dead_task, resume_from=first.id)
        latest = self.session.jobs[r1.id]
        self.assertEqual(latest.state.value, "failed")
        self.assertFalse(latest.error.retryable, "task-level failure must be terminal")
        self.assertIn("failed on the class service", latest.error.message)
        self.assertIn(r1.id, self.session.tickets)
        # The job still exposes its ticket via the route-facing API, but the
        # non-retryable error means resume_music refuses it.
        with self.assertRaises(SessionFailure) as caught:
            self.store.resume_music(self.session, r1.id, item.id)
        self.assertEqual(caught.exception.status, 404)
        self.assertFalse(self.session.active)

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
                    try:
                        self.assertTrue(entered.wait(5), "music submission never started")
                        # The first music job must be visible as running while its
                        # submission is in flight, proving the 409 is a real
                        # duplicate rejection and not the result of a timed-out task.
                        snapshot = client.get("/api/session").json()
                        music_job = next(j for j in snapshot["jobs"] if j["kind"] == "music")
                        self.assertEqual(music_job["state"], "running")
                        duplicate = client.post(f"/api/tracks/{track_id}/music", json={})
                        self.assertEqual(duplicate.status_code, 409)
                        self.assertEqual(client.post("/api/tracks/00000000-0000-0000-0000-000000000000/music", json={}).status_code, 404)
                    finally:
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
                    try:
                        self.assertTrue(entered.wait(5), "cover generation never started")
                        # The art job must be visibly running while the POST is in
                        # flight; the music request below proves art+music coexist.
                        track_id = client.get("/api/session").json()["tracks"][0]["id"]
                        art_job = next(j for j in client.get("/api/session").json()["jobs"] if j["kind"] == "art")
                        self.assertEqual(art_job["state"], "running")
                        music = client.post(f"/api/tracks/{track_id}/music", json={})
                        self.assertEqual(music.status_code, 202)
                        duplicate_cover = client.post(f"/api/tracks/{track_id}/cover", json={})
                        self.assertEqual(duplicate_cover.status_code, 409)
                    finally:
                        release.set()
                self.assertEqual(pending_post.result(timeout=5).status_code, 202)
                snapshot = client.get("/api/session").json()
                current = next(t for t in snapshot["tracks"] if t["id"] == track_id)
                self.assertIsNotNone(current["cover"])
                self.assertIsNotNone(current["audio"])
                self.assertEqual(current["status"], "ready")

    def test_http_resume_continues_same_task_without_new_submission(self):
        state = {"submits": 0, "first_job_running": True}
        def submit(prompt, *, duration_seconds, lyrics):
            state["submits"] += 1
            return MusicTicket("same-task-123")
        def poll(ticket):
            if state["first_job_running"]:
                return MusicPoll("running")
            return MusicPoll("succeeded", "/v1/audio?path=x")
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", side_effect=submit), \
             patch("jukebox.providers.ClassProviders.poll_music", side_effect=poll), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")), \
             patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.1), \
             patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            with self.client(art_music_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                first = client.post(f"/api/tracks/{track_id}/music", json={}).json()
                snapshot = client.get("/api/session").json()
                failed_job = next(j for j in snapshot["jobs"] if j["id"] == first["id"])
                self.assertEqual(failed_job["state"], "failed")
                self.assertTrue(failed_job["error"]["retryable"])
                state["first_job_running"] = False
                resumed = client.post(f"/api/tracks/{track_id}/music/resume?from={first['id']}", json={})
                self.assertEqual(resumed.status_code, 202)
                final = client.get("/api/session").json()
                current = next(t for t in final["tracks"] if t["id"] == track_id)
                self.assertEqual(current["status"], "ready")
                self.assertIsNotNone(current["audio"])
                self.assertEqual(state["submits"], 1, "resuming must not create a new provider task")
                self.assertEqual(len([j for j in final["jobs"] if j["kind"] == "music" and j["state"] == "succeeded"]), 1)

    def test_http_resume_rejected_for_never_confirmed_submission(self):
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music",
                   side_effect=ProviderFailure(SafeError(code="unavailable", message="Could not reach the class service.", retryable=True))):
            with self.client(art_music_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                first = client.post(f"/api/tracks/{track_id}/music", json={}).json()
                rejected = client.post(f"/api/tracks/{track_id}/music/resume?from={first['id']}", json={})
                self.assertEqual(rejected.status_code, 409)
                self.assertIn("never confirmed", rejected.json()["error"]["message"])
                self.assertEqual(client.post(f"/api/tracks/{track_id}/music/resume?from=00000000-0000-0000-0000-000000000000", json={}).status_code, 404)

    def test_http_resume_wrong_track_has_no_side_effects(self):
        """Defect 1 regression over HTTP: resuming A's failed job via track B's URL
        returns 404, creates nothing, and does not block A's rightful resume."""
        state = {"first_job_running": True}
        def poll(ticket):
            if state["first_job_running"]:
                return MusicPoll("running")
            return MusicPoll("succeeded", "/v1/audio?path=x")
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", return_value=MusicTicket("ticket")), \
             patch("jukebox.providers.ClassProviders.poll_music", side_effect=poll), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")), \
             patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), \
             patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            with self.client(art_music_settings()) as client:
                job_a = client.post("/api/tracks", json=body("A", "Piano", "Calm", 10)).json()
                track_a = job_a["track_id"]
                client.post("/api/tracks", json=body("B", "Funk", "Energetic", 10)).json()
                failed = client.post(f"/api/tracks/{track_a}/music", json={}).json()
                snapshot_before = client.get("/api/session").json()
                self.assertEqual(next(j for j in snapshot_before["jobs"] if j["id"] == failed["id"])["state"], "failed")
                jobs_before = len(snapshot_before["jobs"])
                track_b = next(t for t in snapshot_before["tracks"] if t["title"] == "B")["id"]
                wrong = client.post(f"/api/tracks/{track_b}/music/resume?from={failed['id']}", json={})
                self.assertEqual(wrong.status_code, 404)
                snapshot_after = client.get("/api/session").json()
                self.assertEqual(len(snapshot_after["jobs"]), jobs_before,
                                 "mismatched track resume must not create a job")
                self.assertEqual(len([j for j in snapshot_after["jobs"] if j["kind"] == "music"]),
                                 len([j for j in snapshot_before["jobs"] if j["kind"] == "music"]))
                # The rightful track is not blocked: its resume still works.
                state["first_job_running"] = False
                right = client.post(f"/api/tracks/{track_a}/music/resume?from={failed['id']}", json={})
                self.assertEqual(right.status_code, 202)
                final = client.get("/api/session").json()
                current = next(t for t in final["tracks"] if t["id"] == track_a)
                self.assertEqual(current["status"], "ready")

    def test_http_repeated_resume_flow_uses_one_submission(self):
        """Defect 3 regression over HTTP: two consecutive resumes of the same task
        both work, and submit_music is called exactly once."""
        state = {"submits": 0, "fail_next_poll": True}
        def submit(prompt, *, duration_seconds, lyrics):
            state["submits"] += 1
            return MusicTicket("single-task")
        def poll(ticket):
            if state["fail_next_poll"]:
                return MusicPoll("running")
            return MusicPoll("succeeded", "/v1/audio?path=x")
        with patch("jukebox.providers.ClassProviders.cover", return_value=png("blue")), \
             patch("jukebox.providers.ClassProviders.submit_music", side_effect=submit), \
             patch("jukebox.providers.ClassProviders.poll_music", side_effect=poll), \
             patch("jukebox.providers.ClassProviders.download_music",
                   return_value=MediaBytes(wav_bytes(), "audio/wav")), \
             patch("jukebox.sessions.MUSIC_DEADLINE_SECONDS", 0.05), \
             patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.01):
            with self.client(art_music_settings()) as client:
                job = client.post("/api/tracks", json=body()).json()
                track_id = job["track_id"]
                first = client.post(f"/api/tracks/{track_id}/music", json={}).json()
                failed1 = next(j for j in client.get("/api/session").json()["jobs"] if j["id"] == first["id"])
                self.assertEqual(failed1["state"], "failed")
                self.assertTrue(failed1["error"]["retryable"])
                # First resume also times out ("fail_next_poll" stays True).
                resume1 = client.post(f"/api/tracks/{track_id}/music/resume?from={first['id']}", json={})
                self.assertEqual(resume1.status_code, 202)
                failed2 = next(j for j in client.get("/api/session").json()["jobs"] if j["id"] == resume1.json()["id"])
                self.assertEqual(failed2["state"], "failed")
                self.assertTrue(failed2["error"]["retryable"])
                # Second resume -- from the LATEST failed job -- succeeds.
                state["fail_next_poll"] = False
                resume2 = client.post(f"/api/tracks/{track_id}/music/resume?from={resume1.json()['id']}", json={})
                self.assertEqual(resume2.status_code, 202)
                final = client.get("/api/session").json()
                current = next(t for t in final["tracks"] if t["id"] == track_id)
                self.assertEqual(current["status"], "ready")
                self.assertIsNotNone(current["audio"])
                self.assertEqual(state["submits"], 1, "exactly one provider submission across three attempts")
                succeeded = [j for j in final["jobs"] if j["kind"] == "music" and j["state"] == "succeeded"]
                self.assertEqual(len(succeeded), 1)

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
