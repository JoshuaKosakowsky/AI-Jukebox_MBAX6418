"""Presentation preference: no generation on changes; immutable job/cache wording."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest.mock import patch
from uuid import UUID
import httpx
from fastapi.testclient import TestClient
from jukebox.app import create_app
from jukebox.config import ROOT, Settings
from jukebox.providers import ClassProviders, PROBES
from jukebox.samples import load_samples
from jukebox.sessions import DJ_PRESENTATIONS, MAX_MEDIA_BYTES, SessionFailure, SessionStore
from tests.test_dj import DjRecorders, speech_wav
from tests.test_references import wav_bytes

class DjPresentationTests(unittest.TestCase):

    def test_preference_changes_preserve_media_jobs_playback_and_need_no_services(self):
        with TestClient(create_app(Settings({})), base_url='http://localhost') as client:
            before = client.get('/api/session').json()
            self.assertEqual(before['dj_presentation'], 'relaxed')
            with patch.object(ClassProviders, '_request', side_effect=AssertionError('must not generate')) as wire:
                for style in DJ_PRESENTATIONS:
                    response = client.post('/api/playback/presentation', json={'style': style})
                    self.assertEqual(response.status_code, 200)
                    self.assertEqual(response.json(), {**before, 'dj_presentation': style})
                    self.assertEqual(client.get('/api/session').json(), response.json())
                wire.assert_not_called()

    def test_invalid_and_extra_preference_fields_are_rejected_without_mutation(self):
        with TestClient(create_app(Settings({})), base_url='http://localhost') as client:
            before = client.get('/api/session').json()
            for value in [{}, {'style': 'other'}, {'style': None}, {'style': 1}, {'style': 'upbeat', 'reference_id': 'unexpected'}]:
                with self.subTest(value=value):
                    self.assertEqual(client.post('/api/playback/presentation', json=value).status_code, 422)
                    self.assertEqual(client.get('/api/session').json(), before)

    def test_preference_is_session_local_and_reloads_without_new_jobs(self):
        app = create_app(Settings({}))
        with TestClient(app, base_url='http://localhost') as client:
            first = client.post('/api/playback/presentation', json={'style': 'playful'}).json()
            token = client.cookies.get('jukebox_session')
            self.assertEqual(client.get('/api/session').json(), first)
            client.cookies.clear()
            self.assertEqual(client.get('/api/session').json()['dj_presentation'], 'relaxed')
            client.cookies.set('jukebox_session', token)
            self.assertEqual(client.get('/api/session').json(), first)
            self.assertEqual(first['jobs'], [])

    def test_styles_reach_qwen_and_preserve_default_and_reference_speech_contracts(self):
        settings = Settings.load(None, {f'JUKEBOX_{role}_{suffix}': value for role, port in [('TEXT', 9001), ('SPEECH', 9008)] for suffix, value in [('ENDPOINT', f'http://dobolyi.com:{port}/v1'), ('API_KEY', 'synthetic-only')]})
        wires = []

        def wire(request):
            value = json.loads(request.content)
            wires.append((request.url.port, value))
            if request.url.port == 9001:
                self.assertEqual(value['max_completion_tokens'], 192)
                self.assertEqual(value['chat_template_kwargs'], {'enable_thinking': False})
                return httpx.Response(200, json={'model': PROBES['text']['request']['model'], 'choices': [{'message': {'content': 'Synthetic commentary only.'}, 'finish_reason': 'stop'}]})
            self.assertEqual(request.url.port, 9008)
            return httpx.Response(200, content=speech_wav(), headers={'content-type': 'audio/wav'})
        with TestClient(create_app(settings), base_url='http://localhost') as client:
            app = client.app
            app.state.providers.close()
            app.state.providers = ClassProviders(settings, transport=httpx.MockTransport(wire))
            tracks = client.get('/api/session').json()['tracks']
            for track in tracks:
                client.post('/api/playback/queue', json={'track_id': track['id']})
            first_speech = None
            for index, style in enumerate(['relaxed', 'upbeat', 'playful']):
                before = len(wires)
                self.assertEqual(client.post('/api/playback/presentation', json={'style': style}).status_code, 200)
                self.assertEqual(len(wires), before)
                payload = {}
                if style == 'playful':
                    upload = client.post('/api/references/speech', files={'file': ('synthetic.wav', wav_bytes(), 'audio/wav')})
                    self.assertEqual(upload.status_code, 201)
                    payload = {'reference_id': upload.json()['id']}
                response = client.post('/api/playback/start' if index == 0 else '/api/playback/advance', json=payload)
                self.assertEqual(response.status_code, 200)
                qwen, speech = wires[-2:]
                self.assertIn(DJ_PRESENTATIONS[style], qwen[1]['messages'][0]['content'])
                self.assertIn(tracks[index]['title'], qwen[1]['messages'][0]['content'])
                self.assertEqual(speech[1]['input'], 'Synthetic commentary only.')
                if style == 'playful':
                    self.assertTrue(speech[1]['ref_audio'].startswith('data:audio/wav;base64,'))
                else:
                    self.assertNotIn('ref_audio', speech[1])
                snapshot = client.get('/api/session').json()
                self.assertEqual(snapshot['jobs'][-1]['state'], 'succeeded')
                if index == 0:
                    first_speech = snapshot['tracks'][0]['speech']
                self.assertEqual(snapshot['tracks'][0]['speech'], first_speech)
            calls = len(wires)
            client.post('/api/playback/advance', json={})
            client.post('/api/playback/start', json={})
            self.assertEqual(len(wires), calls, 'cached replay must not regenerate after a style change')
            self.assertEqual(len(client.get('/api/session').json()['jobs']), 3)

    def test_inflight_job_keeps_captured_style_and_next_job_uses_new_style(self):
        store = SessionStore(load_samples(ROOT, max_bytes=MAX_MEDIA_BYTES))
        session = store.resolve(None)
        first, second = list(session.tracks)[:2]
        store.queue_playback(session, first)
        store.queue_playback(session, second)
        store.set_dj_presentation(session, 'upbeat')
        _, job = store.start_playback(session)
        captured = session.speech_prompts[job.id]
        store.set_dj_presentation(session, 'playful')
        self.assertEqual(session.speech_prompts[job.id], captured)
        provider = DjRecorders()
        store.generate_dj_speech(session, job.id, provider)
        self.assertIn(DJ_PRESENTATIONS['upbeat'], provider.prompts[0])
        _, next_job = store.advance_playback(session)
        self.assertIn(DJ_PRESENTATIONS['playful'], session.speech_prompts[next_job.id])
        with self.assertRaises(SessionFailure):
            store.set_dj_presentation(session, 'unknown')
        self.assertEqual(session.dj_presentation, 'playful')

    def test_explicit_retry_uses_current_style_after_failed_intro(self):
        store = SessionStore(load_samples(ROOT, max_bytes=MAX_MEDIA_BYTES))
        session = store.resolve(None)
        first = list(session.tracks)[0]
        store.set_dj_presentation(session, 'upbeat')
        original = store.request_dj_speech(session, first)
        provider = DjRecorders()
        provider.fail_text = True
        store.generate_dj_speech(session, original.id, provider)
        self.assertEqual(session.jobs[original.id].state, 'failed')
        store.set_dj_presentation(session, 'playful')
        self.assertEqual(len(session.jobs), 1, 'changing style must not retry a failed intro')
        retry = store.request_dj_speech(session, first)
        self.assertNotEqual(retry.id, original.id)
        self.assertIn(DJ_PRESENTATIONS['playful'], session.speech_prompts[retry.id])
        self.assertEqual(store.snapshot(session).dj_presentation, 'playful')

    @unittest.skipUnless(shutil.which('node'), 'Node is unavailable')
    def test_production_style_handler_saves_rolls_back_and_never_uploads_voice(self):
        result = subprocess.run(['node', str(ROOT / 'tests/frontend_dj_style_probe.cjs'), str(ROOT / 'jukebox/web/app.js')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
