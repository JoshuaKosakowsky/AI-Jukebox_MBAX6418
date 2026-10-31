"""Manual OFFLINE browser harness; no .env, real credentials or provider network.

Run with --source an immutable main snapshot and --port a loopback port.
Actual app/routes/frontend/providers are retained. MockTransport supplies synthetic
media and responses. Audit-only routes control faults/capacity and collect events.
The root response adds an OFFLINE banner and observer script that mutes media;
no source files or production functions are rewritten.
"""
import argparse
import base64
from collections import Counter
from contextlib import contextmanager
import io
import json
from pathlib import Path
import sys
from unittest.mock import patch
from uuid import uuid4
import wave


OBSERVER = """'use strict';
const send = (value) => fetch('/audit/events', {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(value)}).catch(()=>{});
new MutationObserver(()=>document.querySelectorAll('audio').forEach(a=>a.muted=true)).observe(document.documentElement,{childList:true,subtree:true});
for (const type of ['play','playing','pause','ended','error']) document.addEventListener(type,e=>{
 if(e.target.tagName!=='AUDIO') return;
 const a=e.target; a.muted=true;
 send({type,element:a.id||a.getAttribute('aria-label'),src:a.getAttribute('src'),time:a.currentTime,paused:a.paused,error:a.error?.code??null,
 playingCount:[...document.querySelectorAll('audio')].filter(x=>!x.paused&&!x.ended).length});
},true);
window.addEventListener('error',e=>send({type:'window-error',message:e.message}));
window.addEventListener('unhandledrejection',e=>send({type:'unhandled-rejection',message:String(e.reason)}));
"""


def wav(seconds):
    stream = io.BytesIO()
    with wave.open(stream, 'wb') as w:
        w.setparams((1, 2, 16000, 0, 'NONE', 'not compressed'))
        w.writeframes(b'\x10\x00' * int(16000 * seconds))
    return stream.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--port', type=int, default=8175)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    assert not (source / '.env').exists(), 'Use a credential-free source snapshot'
    sys.path.insert(0, str(source))
    import httpx
    import uvicorn
    from PIL import Image
    from fastapi import Request
    from fastapi.responses import HTMLResponse, Response
    from jukebox.app import create_app
    from jukebox.config import Settings
    from jukebox.providers import ClassProviders, PROBES
    counts, events, posts = Counter(), [], []
    control = {'bad_model': False, 'art_fail': False, 'speech_fail': False, 'poll_fail': False}
    held = {}
    art = io.BytesIO()
    Image.new('RGB', (512, 512), '#345678').save(art, format='PNG')
    music, speech = wav(10), wav(6)

    def wire(request):
        path = request.url.path
        counts[path] += 1
        if path == '/v1/images/generations':
            if control['art_fail']:
                return httpx.Response(503, text='PRIVATE-SYNTHETIC-MARKER')
            return httpx.Response(200, json={'data': [{'b64_json': base64.b64encode(art.getvalue()).decode()}]})
        if path == '/v1/chat/completions':
            body = json.loads(request.content)
            kind = 'lyrics' if body.get('max_completion_tokens') == 512 else 'dj_text'
            counts[kind] += 1
            if kind == 'dj_text':
                assert body.get('chat_template_kwargs') == {'enable_thinking': False}
            model = 'PRIVATE-SYNTHETIC-MARKER' if control['bad_model'] else PROBES['text']['request']['model']
            return httpx.Response(200, json={'model': model, 'choices': [{'finish_reason': 'stop', 'message': {'content': 'Original offline lyrics\nAn entirely synthetic song' if kind == 'lyrics' else 'Here is the next original offline fixture track.'}}]})
        if path == '/v1/audio/speech':
            if control['speech_fail']:
                return httpx.Response(503, text='PRIVATE-SYNTHETIC-MARKER')
            return httpx.Response(200, content=speech, headers={'content-type': 'audio/wav'})
        if path == '/release_task':
            return httpx.Response(200, json={'code': 200, 'error': None, 'data': {'task_id': f'offline-{counts[path]}'}})
        if path == '/query_result':
            if control['poll_fail']:
                raise httpx.ReadTimeout('PRIVATE-SYNTHETIC-MARKER')
            ticket = json.loads(request.content)['task_id_list'][0]
            return httpx.Response(200, json={'code': 200, 'error': None, 'data': [{'task_id': ticket, 'status': 1, 'result': json.dumps([{'file': '/v1/audio?path=offline', 'dit_model': 'acestep-v15-xl-turbo', 'status': 1}])}]})
        if path == '/v1/audio':
            return httpx.Response(200, content=music, headers={'content-type': 'audio/wav'})
        raise AssertionError('Unexpected provider path: ' + path)

    env = {name: value for role, port in {'TEXT': 9001, 'ART': 9006, 'MUSIC': 9007, 'SPEECH': 9008}.items()
           for name, value in ((f'JUKEBOX_{role}_ENDPOINT', f'http://dobolyi.com:{port}/v1'), (f'JUKEBOX_{role}_API_KEY', 'offline-synthetic-only'))}
    settings = Settings.load(None, env)
    with patch('jukebox.app.ClassProviders', side_effect=lambda s: ClassProviders(s, transport=httpx.MockTransport(wire))):
        app = create_app(settings)

        @app.middleware('http')
        async def observe(request, call_next):
            response = await call_next(request)
            if request.method == 'POST' and request.url.path.startswith('/api/'):
                posts.append({'path': request.url.path, 'status': response.status_code})
            if request.url.path == '/':
                body = b''.join([part async for part in response.body_iterator]).decode()
                body = body.replace('</head>', '<script src="/audit/observe.js" defer></script></head>')
                body = body.replace('<body>', '<body><p style="padding:12px">OFFLINE REGRESSION: synthetic providers, muted media, zero class calls.</p>')
                headers = dict(response.headers)
                headers.pop('content-length', None)
                return HTMLResponse(body, status_code=response.status_code, headers=headers)
            return response

        @app.get('/audit/observe.js')
        def observer():
            return Response(OBSERVER, media_type='text/javascript')

        @app.post('/audit/events')
        async def event(request: Request):
            if len(events) < 1000:
                events.append(await request.json())
            return {'ok': True}

        @app.post('/audit/control')
        async def configure(request: Request):
            values = await request.json()
            assert all(k in control and isinstance(v, bool) for k, v in values.items())
            control.update(values)
            return control

        @app.post('/audit/capacity/{kind}/{state}')
        def capacity(kind: str, state: str):
            assert kind in ('art', 'music') and state in ('hold', 'release')
            store = app.state.sessions
            with store.lock:
                if state == 'hold':
                    assert kind not in held
                    session = store.resolve(None)
                    # Deterministic isolated capacity injection, not real jobs/provider concurrency.
                    session.active.update((uuid4(), kind) for _ in range(2))
                    held[kind] = session
                elif kind in held:
                    held.pop(kind).active.clear()
            return {'held': sorted(held)}

        @app.get('/audit/evidence')
        def evidence():
            return {'counts': dict(counts), 'events': events, 'posts': posts, 'control': control, 'held': sorted(held), 'real_provider_requests': 0}

        uvicorn.run(app, host='127.0.0.1', port=args.port, access_log=False)


if __name__ == '__main__':
    main()
