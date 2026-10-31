"""Manual OFFLINE audit: real app/adapters, MockTransport; never normal launch.

Usage: python scripts/audit_fault_harness.py --source . --control results/raw/a3-08-control.json --port 8168
The control file may contain {"mode":"capacity","release":false} or
{"mode":"success"}. No class credentials are loaded; no external HTTP occurs.
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
import wave


def load_source(source):
    sys.path.insert(0, str(Path(source).resolve()))


def fixture_png():
    from PIL import Image
    stream = io.BytesIO()
    Image.new("RGB", (512, 512), "navy").save(stream, format="PNG")
    return stream.getvalue()


def fixture_wav():
    stream = io.BytesIO()
    with wave.open(stream, "wb") as audio:
        audio.setparams((1, 2, 16000, 0, "NONE", "not compressed"))
        audio.writeframes(b"\x01\x00" * 160000)
    return stream.getvalue()


class Wire:
    def __init__(self, options=None, control=None):
        self.options = options or {}
        self.control = Path(control) if control else None
        self.counts = Counter()
        self.png, self.wav = fixture_png(), fixture_wav()

    def settings(self):
        from jukebox.config import Settings
        return Settings.load(None, {
            name: value for role, port in (("ART", 9006), ("MUSIC", 9007))
            for name, value in ((f"JUKEBOX_{role}_ENDPOINT", f"http://dobolyi.com:{port}/v1"),
                                (f"JUKEBOX_{role}_API_KEY", "offline-audit-synthetic-marker"))})

    def __call__(self, request):
        import httpx
        options = json.loads(self.control.read_text()) if self.control else self.options
        path = request.url.path
        self.counts[path] += 1
        if path == "/v1/images/generations":
            if options.get("cover_fail"):
                return httpx.Response(503, text="offline-private-provider-detail")
            return httpx.Response(200, json={"data": [{"b64_json": base64.b64encode(self.png).decode()}]})
        if path == "/release_task":
            if self.counts[path] <= options.get("submit_timeouts", 0):
                raise httpx.ReadTimeout("offline-private-provider-detail")
            return httpx.Response(200, json={"code": 200, "error": None,
                "data": {"task_id": f"offline-private-ticket-{self.counts[path]}"}})
        if path == "/query_result":
            if self.counts[path] <= options.get("poll_timeouts", 0):
                raise httpx.ReadTimeout("offline-private-provider-detail")
            ticket = json.loads(request.content)["task_id_list"][0]
            state = 0 if options.get("mode") == "capacity" and not options.get("release") else 1
            if options.get("terminal_failure"):
                state = 2
            file = "http://outside.invalid/v1/audio?path=x" if options.get("foreign_download") else "/v1/audio?path=offline"
            return httpx.Response(200, json={"code": 200, "error": None, "data": [{
                "task_id": ticket, "status": state, "result": json.dumps([{
                    "file": file, "dit_model": "acestep-v15-xl-turbo", "status": 1}])}]})
        if path == "/v1/audio":
            if self.counts[path] <= options.get("download_timeouts", 0):
                raise httpx.ReadTimeout("offline-private-provider-detail")
            return httpx.Response(200, content=b"broken WAV" if options.get("bad_audio") else self.wav,
                                  headers={"content-type": "audio/wav"})
        raise AssertionError("Unexpected offline request path")


@contextmanager
def app_context(wire):
    import httpx
    from jukebox.app import create_app
    from jukebox.providers import ClassProviders
    factory = lambda settings: ClassProviders(settings, transport=httpx.MockTransport(wire))
    with patch("jukebox.app.ClassProviders", side_effect=factory), \
         patch("jukebox.sessions.MUSIC_POLL_INTERVAL", 0.1):
        yield create_app(wire.settings())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True)
    parser.add_argument("--control", required=True)
    parser.add_argument("--port", type=int, default=8168)
    args = parser.parse_args()
    load_source(args.source)
    import uvicorn
    from starlette.responses import JSONResponse
    wire = Wire(control=args.control)
    with app_context(wire) as app:
        # Audit-only visibility into counters. This route never exists in the app.
        @app.get("/audit/counters")
        def counters():
            return JSONResponse(dict(wire.counts))
        uvicorn.run(app, host="127.0.0.1", port=args.port, access_log=False)


if __name__ == "__main__":
    main()
