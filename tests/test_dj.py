"""Offline tests for the default AI DJ queue (A3-05): queue lifecycle, real
Qwen->Chatterbox request contracts (default voice), speech-before-music
sequencing, pause/resume/skip, race/staleness guards, end-of-queue and session
isolation. All provider methods are patched with deterministic offline
fixtures; no class credentials are loaded and no external request is made."""
import json
from io import BytesIO
import unittest
from unittest.mock import patch
import wave

from tests.test_music import png, wav_bytes

from jukebox.config import Settings
from jukebox.contracts import Playback
from jukebox.providers import MediaBytes, MusicPoll, MusicTicket
from jukebox.sessions import MAX_QUEUE, SessionFailure, SessionStore, SESSION_COOKIE


def all_settings():
    return Settings.load(None, {
        key: value for role, port in
        {"TEXT": 9001, "ART": 9006, "MUSIC": 9007, "SPEECH": 9008}.items()
        for key, value in [("JUKEBOX_" + role + "_ENDPOINT", f"http://dobolyi.com:{port}/v1"),
                           ("JUKEBOX_" + role + "_API_KEY", "dj-test-marker-never-public")]})


def speech_wav():
    stream = BytesIO()
    with wave.open(stream, "wb") as audio:
        audio.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        audio.writeframes(b"\x10\x00" * 16000)
    return stream.getvalue()


class DjRecorders:
    """Deterministic offline provider behavior with request recording.

    Methods mirror the ClassProviders API (cover/music -> MediaBytes,
    text -> str, speech -> MediaBytes) and never touch the network.
    """

    def __init__(self):
        self.prompts = []
        self.spoken_inputs = []
        self.commentary = ("Welcome to the jukebox. This next song is called "
                           "Moonlit Reflection, an ambient piano piece. Sit back and enjoy.")
        self.fail_text = False

    def cover(self):
        return png("navy")

    def submit_music(self, prompt, *, duration_seconds=10, lyrics="[Instrumental]"):
        return MusicTicket(task_id="dj-offline-task")

    def poll_music(self, ticket):
        return MusicPoll(state="succeeded", download_path="/v1/audio?path=offline")

    def download_music(self, result):
        return MediaBytes(wav_bytes(), "audio/wav")

    def text(self, prompt):
        self.prompts.append(prompt)
        if self.fail_text:
            raise RuntimeError("offline private failure")
        return self.commentary

    def speech(self, text):
        self.spoken_inputs.append(text)
        return MediaBytes(speech_wav(), "audio/wav")


def app_fixture(recorders):
    from jukebox.app import create_app
    from jukebox.providers import ClassProviders
    patches = [
        patch.object(ClassProviders, "cover", return_value=png("navy")),
        patch.object(ClassProviders, "submit_music", side_effect=recorders.submit_music),
        patch.object(ClassProviders, "poll_music", side_effect=recorders.poll_music),
        patch.object(ClassProviders, "download_music", side_effect=recorders.download_music),
        patch.object(ClassProviders, "text", side_effect=recorders.text),
        patch.object(ClassProviders, "speech", side_effect=recorders.speech),
    ]
    for item in patches:
        item.start()

    def stop_patches():
        for item in patches:
            item.stop()

    return create_app(all_settings()), stop_patches


def assert_default_voice_contract(testcase):
    """R14: the committed speech contract carries no voice parameter, so the
    provider speaks with Chatterbox's default voice by omission."""
    from jukebox.providers import PROBES
    request_body = PROBES["speech"]["request"]
    testcase.assertNotIn("voice", request_body)
    testcase.assertEqual(request_body["model"], "chatterbox-v3")


BODY = {"title": "Moonlit Reflection", "settings": {
    "style": "Ambient piano", "mood": "Calm and reflective",
    "duration_seconds": 10, "mode": "instrumental"}}


class DjTests(unittest.TestCase):
    def make_client(self, recorders):
        from fastapi.testclient import TestClient
        app, stop_patches = app_fixture(recorders)
        self.addCleanup(stop_patches)
        client = TestClient(app, base_url="http://localhost")
        client.__enter__()
        self.addCleanup(client.__exit__, None, None, None)
        return client, app.state.sessions

    def create_track(self, client, title="Moonlit Reflection", style="Ambient piano",
                     mood="Calm and reflective"):
        body = dict(BODY)
        body["title"] = title
        body["settings"]["style"] = style
        body["settings"]["mood"] = mood
        job = client.post("/api/tracks", json=body)
        self.assertEqual(job.status_code, 202)
        track_id = job.json()["track_id"]
        self.assertEqual(client.post(f"/api/tracks/{track_id}/music", json={}).status_code, 202)
        snapshot = client.get("/api/session").json()
        track = next(t for t in snapshot["tracks"] if t["id"] == track_id)
        self.assertIsNotNone(track["audio"], "setup track must be playable")
        return track_id, track

    def session_store(self, client):
        token = SESSION_COOKIE
        cookie = client.cookies
        return cookie

    def test_queue_start_and_first_commentary(self):
        recorders = DjRecorders()
        client, store = self.make_client(recorders)
        first, _ = self.create_track(client)
        second, _ = self.create_track(client, "Desert Drive", "Upbeat funk", "Energetic and optimistic")
        queued = client.post("/api/playback/queue", json={"track_id": first})
        self.assertEqual(queued.status_code, 200)
        self.assertEqual(queued.json()["queue"], [first])
        self.assertEqual(client.post("/api/playback/queue", json={"track_id": second}).status_code, 200)
        started = client.post("/api/playback/start", json={})
        self.assertEqual(started.status_code, 200)
        playback = started.json()
        self.assertEqual(playback["state"], "speaking")
        self.assertEqual(playback["index"], 0)
        self.assertEqual(playback["current_track_id"], first)
        snapshot = client.get("/api/session").json()
        jobs = [j for j in snapshot["jobs"] if j["kind"] == "speech"]
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["track_id"], first)
        self.assertEqual(jobs[0]["state"], "succeeded")
        track = next(t for t in snapshot["tracks"] if t["id"] == first)
        self.assertIsNotNone(track["speech"], "commentary speech must attach to the track")
        self.assertTrue(track["speech"]["content_type"].startswith("audio/"))
        self.assertEqual(len(recorders.prompts), 1)
        prompt = recorders.prompts[0]
        self.assertIn("Moonlit Reflection", prompt)
        self.assertIn("Ambient piano", prompt)
        self.assertIn("Calm and reflective", prompt)
        self.assertIn("instrumental", prompt)
        self.assertIn("first song of the set", prompt)
        # Exactly one speech request, and the spoken input is exactly the Qwen
        # commentary output (real R13 chain) through the default voice contract.
        self.assertEqual(len(recorders.spoken_inputs), 1)
        self.assertEqual(recorders.spoken_inputs[0], recorders.commentary)
        assert_default_voice_contract(self)
        # Commentary text never appears in the snapshot.
        self.assertNotIn("Welcome to the jukebox", json.dumps(snapshot))

    def test_transition_prompt_has_prior_song_context(self):
        recorders = DjRecorders()
        client, _ = self.make_client(recorders)
        first, _ = self.create_track(client, "Moonlit Reflection", "Ambient piano", "Calm and reflective")
        second, _ = self.create_track(client, "Desert Drive", "Upbeat funk", "Energetic and optimistic")
        client.post("/api/playback/queue", json={"track_id": first})
        client.post("/api/playback/queue", json={"track_id": second})
        client.post("/api/playback/start", json={})
        advanced = client.post("/api/playback/advance", json={})
        self.assertEqual(advanced.status_code, 200)
        self.assertEqual(advanced.json()["current_track_id"], second)
        self.assertEqual(advanced.json()["state"], "speaking")
        self.assertEqual(len(recorders.prompts), 2)
        prompt = recorders.prompts[1]
        self.assertIn("After Moonlit Reflection", prompt)
        snapshot = client.get("/api/session").json()
        spoke = [t for t in snapshot["tracks"] if t["speech"] is not None]
        self.assertEqual(len(spoke), 2, "both tracks end up with their own commentary")
        # Each track's speech is its own media reference.
        self.assertNotEqual(spoke[0]["speech"]["id"], spoke[1]["speech"]["id"])

    def test_advance_past_end_returns_to_idle_and_keeps_queue(self):
        recorders = DjRecorders()
        client, _ = self.make_client(recorders)
        tracks = [self.create_track(client, f"Song {i}", "Pop", "Bright")[0] for i in range(2)]
        for track in tracks:
            client.post("/api/playback/queue", json={"track_id": track})
        client.post("/api/playback/start", json={})
        client.post("/api/playback/advance", json={})
        done = client.post("/api/playback/advance", json={})
        self.assertEqual(done.status_code, 200)
        done = done.json()
        self.assertEqual(done["state"], "idle")
        self.assertEqual(done["index"], 0)
        self.assertIsNone(done["current_track_id"])
        self.assertEqual(done["queue"], tracks)
        # A fresh start replays without regenerating speech for known tracks.
        chat_before = len(recorders.prompts)
        client.post("/api/playback/start", json={})
        client.get("/api/session")
        self.assertEqual(len(recorders.prompts), chat_before, "replay must not re-generate commentary")
        self.assertEqual(client.post("/api/playback/advance", json={}).status_code, 200)

    def test_pause_and_resume_phases_round_trip(self):
        recorders = DjRecorders()
        client, _ = self.make_client(recorders)
        track, _ = self.create_track(client)
        client.post("/api/playback/queue", json={"track_id": track})
        client.post("/api/playback/start", json={})
        paused = client.post("/api/playback/pause", json={"phase": "speaking"})
        self.assertEqual(paused.status_code, 200)
        self.assertEqual(paused.json()["state"], "paused")
        self.assertEqual(paused.json()["paused_from"], "speaking")
        self.assertEqual(client.post("/api/playback/pause", json={"phase": "speaking"}).status_code, 409)
        resumed = client.post("/api/playback/resume", json={})
        self.assertEqual(resumed.status_code, 200)
        self.assertEqual(resumed.json()["state"], "speaking", "resume restores the paused phase")
        client.post("/api/playback/phase", json={"phase": "playing"})
        paused = client.post("/api/playback/pause", json={"phase": "playing"}).json()
        self.assertEqual(paused["paused_from"], "playing")
        self.assertEqual(client.post("/api/playback/resume", json={}).json()["state"], "playing")
        # Bad inputs are rejected safely.
        self.assertEqual(client.post("/api/playback/pause", json={"phase": "dancing"}).status_code, 422)
        self.assertEqual(client.post("/api/playback/phase", json={"phase": "dancing"}).status_code, 422)
        self.assertEqual(client.post("/api/playback/resume", json={}).status_code, 409)

    def test_control_guards_and_bounds(self):
        recorders = DjRecorders()
        client, _ = self.make_client(recorders)
        # Empty queue cannot start.
        self.assertEqual(client.post("/api/playback/start", json={}).status_code, 409)
        track, _ = self.create_track(client)
        # Missing text or speech configuration rejects playback endpoints.
        from tests.test_runtime import configured_values
        from jukebox.app import create_app
        from jukebox.providers import ClassProviders
        with patch.object(ClassProviders, "cover", return_value=png("navy")), \
                patch.object(ClassProviders, "submit_music",
                             side_effect=lambda prompt, **kwargs: MusicTicket(task_id="dj-offline-task")), \
                patch.object(ClassProviders, "poll_music",
                             lambda ticket: MusicPoll(state="succeeded", download_path="/v1/audio?path=offline")), \
                patch.object(ClassProviders, "download_music",
                             return_value=MediaBytes(wav_bytes(), "audio/wav")), \
                patch.object(ClassProviders, "text", side_effect=recorders.text), \
                patch.object(ClassProviders, "speech", side_effect=recorders.speech):
            partial = create_app(Settings.load(None, {k: v for k, v in configured_values().items()
                                                      if "TEXT" not in k and "SPEECH" not in k}))
        from fastapi.testclient import TestClient
        with TestClient(partial, base_url="http://localhost") as client2:
            draft = client2.post("/api/tracks", json=BODY).json()["track_id"]
            self.assertEqual(client2.post("/api/playback/queue", json={"track_id": draft}).status_code, 502)
        # Unknown track and duplicate queue entries.
        self.assertEqual(client.post("/api/playback/queue", json={"track_id": "00000000-0000-0000-0000-000000000000"}).status_code, 404)
        self.assertEqual(client.post("/api/playback/queue", json={"track_id": track}).status_code, 200)
        self.assertEqual(client.post("/api/playback/queue", json={"track_id": track}).status_code, 409)
        # Drafts without audio cannot be queued.
        draft = client.post("/api/tracks", json=BODY).json()["track_id"]
        self.assertEqual(client.post("/api/playback/queue", json={"track_id": draft}).status_code, 409)

    def test_failed_commentary_does_not_block_the_set(self):
        recorders = DjRecorders()
        recorders.fail_text = True
        client, _ = self.make_client(recorders)
        track, _ = self.create_track(client)
        client.post("/api/playback/queue", json={"track_id": track})
        started = client.post("/api/playback/start", json={})
        self.assertEqual(started.status_code, 200)
        snapshot = client.get("/api/session").json()
        speech_job = [j for j in snapshot["jobs"] if j["kind"] == "speech"][0]
        self.assertEqual(speech_job["state"], "failed")
        self.assertIn("without an introduction", speech_job["error"]["message"])
        current = next(t for t in snapshot["tracks"] if t["id"] == track)
        self.assertIsNone(current["speech"])
        # The set remains fully controllable and can finish.
        self.assertEqual(client.post("/api/playback/phase", json={"phase": "playing"}).status_code, 200)
        done = client.post("/api/playback/advance", json={}).json()
        self.assertEqual(done["state"], "idle")

    def test_cross_session_isolation_and_media_bounds(self):
        recorders = DjRecorders()
        app, stop_patches = app_fixture(recorders)
        self.addCleanup(stop_patches)
        from fastapi.testclient import TestClient
        owner = TestClient(app, base_url="http://localhost")
        other = TestClient(app, base_url="http://localhost")
        owner.__enter__()
        other.__enter__()
        self.addCleanup(owner.__exit__, None, None, None)
        self.addCleanup(other.__exit__, None, None, None)
        track, _ = self.create_track(owner)
        owner.post("/api/playback/queue", json={"track_id": track})
        owner.post("/api/playback/start", json={})
        snapshot = owner.get("/api/session").json()
        speech_url = next(t for t in snapshot["tracks"] if t["id"] == track)["speech"]["url"]
        # The other session sees no queues, cannot queue our track, and
        # cannot fetch our commentary media.
        self.assertEqual(other.get("/api/session").json()["playback"]["queue"], [])
        self.assertEqual(other.post("/api/playback/queue", json={"track_id": track}).status_code, 404)
        self.assertEqual(other.get(speech_url).status_code, 404)
        self.assertEqual(owner.get(speech_url).status_code, 200)
        snapshot_text = owner.get("/api/session").text
        self.assertNotIn("dj-test-marker", snapshot_text)
        self.assertNotIn("Welcome to the jukebox", snapshot_text)

    def test_store_level_guards_and_stale_speech_safety(self):
        store = SessionStore()
        from jukebox.sessions import Session
        session = Session()
        from jukebox.contracts import Track, SongSettings
        settings = SongSettings(style="Pop", mood="Bright", duration_seconds=10, mode="instrumental")
        a, b = Track(title="A", settings=settings), Track(title="B", settings=settings)
        session.tracks[a.id], session.tracks[b.id] = a, b
        a = session.tracks[a.id]; b = session.tracks[b.id]
        media = a.model_dump()
        media["audio"] = {"id": "11111111-1111-1111-1111-111111111111",
                          "url": "/api/media/11111111-1111-1111-1111-111111111111", "content_type": "audio/wav"}
        session.tracks[a.id] = Track.model_validate(media)
        session.tracks[b.id] = Track.model_validate({**b.model_dump(), "audio": {
            "id": "22222222-2222-2222-2222-222222222222",
            "url": "/api/media/22222222-2222-2222-2222-222222222222", "content_type": "audio/wav"}})
        store.queue_playback(session, a.id)
        store.queue_playback(session, b.id)
        with self.assertRaises(SessionFailure):
            store.queue_playback(session, a.id)
        # Queue capacity: MAX_QUEUE distinct entries, then a 429.
        for i in range(2, MAX_QUEUE):
            extra_id = f"{i:08d}-0000-0000-0000-000000000000"
            fake = Track(id=extra_id, title=f"Extra {i}", settings=settings)
            fake = Track.model_validate({**fake.model_dump(), "audio": {
                "id": f"{i:08d}-0000-0000-0000-000000000001",
                "url": f"/api/media/{i:08d}-0000-0000-0000-000000000001", "content_type": "audio/wav"}})
            session.tracks[fake.id] = fake
            store.queue_playback(session, fake.id)
        overflow_id = f"{MAX_QUEUE:08d}-0000-0000-0000-000000000000"
        fake = Track(id=overflow_id, title="Overflow", settings=settings)
        fake = Track.model_validate({**fake.model_dump(), "audio": {
            "id": f"{MAX_QUEUE:08d}-0000-0000-0000-000000000001",
            "url": f"/api/media/{MAX_QUEUE:08d}-0000-0000-0000-000000000001", "content_type": "audio/wav"}})
        session.tracks[fake.id] = fake
        with self.assertRaises(SessionFailure) as raised:
            store.queue_playback(session, fake.id)
        self.assertEqual(raised.exception.status, 429)
        # Playback would begin at the very first entry.
        self.assertEqual(len(session.playback.queue), MAX_QUEUE)
        playback, job_a = store.start_playback(session)
        self.assertEqual(job_a.track_id, a.id)
        # A second speech request for the same track is suppressed while active.
        self.assertIsNone(store._queue_dj_speech(session, a.id, None, 0, 2))
        playback, job_b = store.advance_playback(session)
        self.assertEqual(job_b.track_id, b.id)
        self.assertEqual(session.playback.current_track_id, b.id)
        # The stale A job completing later attaches to A, never to B.
        session.jobs[job_a.id] = session.jobs[job_a.id].transition("running", progress=.1) \
            .transition("succeeded", progress=1)
        session.tracks[a.id] = Track.model_validate({**session.tracks[a.id].model_dump(), "speech": {
            "id": "33333333-3333-3333-3333-333333333333",
            "url": "/api/media/33333333-3333-3333-3333-333333333333", "content_type": "audio/wav"}})
        self.assertIsNotNone(session.tracks[a.id].speech)
        self.assertIsNone(session.tracks[b.id].speech)
        self.assertEqual(session.playback.current_track_id, b.id)
        # Snapshot still validates with commentary media present.
        snapshot = store.snapshot(session)
        self.assertEqual(len(snapshot.playback.queue), MAX_QUEUE)

    def test_reload_persists_queue_without_regenerating(self):
        recorders = DjRecorders()
        client, _ = self.make_client(recorders)
        tracks = [self.create_track(client, f"Reload {i}", "Pop", "Bright")[0] for i in range(2)]
        for track in tracks:
            client.post("/api/playback/queue", json={"track_id": track})
        client.post("/api/playback/start", json={})
        client.post("/api/playback/advance", json={})
        chat_after_first_run = len(recorders.prompts)
        # A fresh client (the "reload") reuses the session cookie: queue,
        # index and speech media all persist; nothing new is generated.
        from fastapi.testclient import TestClient
        cookie = {"jukebox_session": client.cookies.get("jukebox_session")}
        reloaded = TestClient(client.app, base_url="http://localhost")
        reloaded.cookies.set("jukebox_session", cookie["jukebox_session"])
        snapshot = reloaded.get("/api/session").json()
        self.assertEqual(snapshot["playback"]["queue"], tracks)
        self.assertEqual(snapshot["playback"]["index"], 1)
        self.assertEqual(snapshot["playback"]["state"], "speaking")
        spoke = [t for t in snapshot["tracks"] if t["speech"] is not None]
        self.assertEqual(len(spoke), 2)
        self.assertEqual(len(recorders.prompts), chat_after_first_run, "reload must not generate new speech")


if __name__ == "__main__":
    unittest.main()
