"""Manual synthetic browser privacy audit; NEVER live/class acceptance.

Extends audit_main_browser's MockTransport harness without changing app files.
Run with --source <credential-free pinned checkout> --port <loopback port>.
Only synthetic local clips may be selected. No upload bytes, filenames, tokens
or reference IDs are returned by audit observations or written to disk.
"""
import argparse
import json
from pathlib import Path
import re
import socket
import sys
from unittest.mock import patch

import audit_main_browser


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--port', type=int, default=8176)
    args = parser.parse_args()
    source = Path(args.source).resolve()
    assert not (source / '.env').exists(), 'Use a credential-free pinned checkout'
    sys.path.insert(0, str(source))
    import httpx
    import jukebox.app as app_module
    from jukebox.providers import ClassProviders
    from jukebox.sessions import SESSION_COOKIE, SessionStore

    uploads, speech, names, identifiers = [], [], [], []
    network = {'blocked_external_attempts': 0}
    original_connect, original_dns = socket.socket.connect, socket.getaddrinfo
    original_upload = SessionStore.upload_reference
    original_speech = ClassProviders.speech
    original_extract = app_module._extract_file_part
    original_app = app_module.create_app

    def allow_local(address):
        if address not in {'127.0.0.1', 'localhost', '::1', b'localhost'}:
            network['blocked_external_attempts'] += 1
            raise OSError('External network disabled for this synthetic browser audit')

    def connect(sock, address):
        if isinstance(address, tuple):
            allow_local(address[0])
        return original_connect(sock, address)

    def dns(host, *rest, **kwargs):
        if host is not None:
            allow_local(host)
        return original_dns(host, *rest, **kwargs)

    def extract(raw, content_type):
        filenames = re.findall(rb'filename="([^"\r\n]*)"', raw)
        names.append({'fixed_reference_filename': filenames == [b'reference']})
        return original_extract(raw, content_type)

    def upload(store, session, content):
        result = original_upload(store, session, content)
        uploads.append({'bytes': len(content), 'media_type': result[1]})
        identifiers.append((session.token, result[0]))  # Memory only; never serialize.
        return result

    def speak(provider, text, *, reference=None):
        row = {'reference_media_type': reference.content_type if reference else None}
        speech.append(row)
        try:
            result = original_speech(provider, text, reference=reference)
            row['result'] = 'success'
            return result
        except Exception:
            row['result'] = 'failed'
            raise

    def create(settings):
        app = original_app(settings)

        @app.get('/audit/reference-evidence')
        async def evidence():
            store = app.state.sessions
            with store.lock:
                totals = {name: sum(len(getattr(s, name)) for s in store.sessions.values())
                          for name in ('references', 'speech_references', 'speech_prompts', 'active')}
            probes = []
            # Exercise the real media/session HTTP routes with the anonymous
            # session that uploaded each fixture. Only booleans/statuses leave.
            for token, identifier in identifiers:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app),
                        base_url='http://127.0.0.1', cookies={SESSION_COOKIE: token}) as client:
                    media = await client.get(f'/api/media/{identifier}')
                    snapshot = await client.get('/api/session')
                    probes.append({'media_http_status': media.status_code,
                                   'snapshot_contains_id': str(identifier) in snapshot.text})
            return {'uploads': uploads, 'multipart': names, 'speech': speech,
                    'memory_totals': totals, 'privacy_probes': probes,
                    'network': network, 'real_provider_requests': 0}

        return app

    sys.argv = [sys.argv[0], '--source', str(source), '--port', str(args.port)]
    with patch.object(app_module, 'create_app', create), \
         patch.object(app_module, '_extract_file_part', extract), \
         patch.object(SessionStore, 'upload_reference', upload), \
         patch.object(ClassProviders, 'speech', speak), \
         patch.object(socket.socket, 'connect', connect), \
         patch.object(socket, 'getaddrinfo', dns):
        audit_main_browser.main()


if __name__ == '__main__':
    main()
