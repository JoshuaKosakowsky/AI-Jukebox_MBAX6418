"""Real class-provider boundary. No requests occur until a caller invokes a method."""
import base64
import binascii
from copy import deepcopy
from dataclasses import dataclass
import json
import io
import time
import wave
from urllib.parse import parse_qs, urlsplit

import httpx
from PIL import Image, UnidentifiedImageError

from .config import ROOT, Settings
from .contracts import SafeError


PROBES = json.loads((ROOT / "contracts/service-probes.json").read_text(encoding="utf-8"))["services"]
MAX_BYTES = 20_000_000


class ProviderFailure(Exception):
    def __init__(self, error: SafeError):
        self.error = error
        super().__init__(error.message)


def fail(code, message, retryable=False):
    raise ProviderFailure(SafeError(code=code, message=message, retryable=retryable)) from None


@dataclass(frozen=True)
class MediaBytes:
    content: bytes
    content_type: str


@dataclass(frozen=True)
class MusicTicket:
    """Server-only provider identifier; never a browser job/track ID."""
    task_id: str


@dataclass(frozen=True)
class MusicPoll:
    state: str
    download_path: str | None = None


class ClassProviders:
    def __init__(self, settings: Settings, *, transport=None):
        self.settings = settings
        self.client = httpx.Client(transport=transport, follow_redirects=False, trust_env=False,
                                   timeout=httpx.Timeout(30, read=180))

    def close(self):
        self.client.close()

    def _request(self, role, path, payload=None):
        config = self.settings.services.get(role)
        if config is None:
            fail("not_configured", f"{role.capitalize()} service is not configured.")
        # Restrict every URL, including server-returned ACE download paths, before auth.
        try:
            parsed = urlsplit(path)
        except ValueError:
            fail("invalid_response", "Service returned an invalid route.")
        if parsed.scheme or parsed.netloc or not path.startswith("/") or path.startswith("//") or parsed.fragment:
            fail("invalid_response", "Service returned an invalid route.")
        if payload is None:
            try:
                parameters = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True)
            except ValueError:
                fail("invalid_response", "Service returned an invalid audio route.")
            if (role != "music" or parsed.path != "/v1/audio" or set(parameters) != {"path"}
                    or len(parameters["path"]) != 1 or not parameters["path"][0].strip()):
                fail("invalid_response", "Service returned an invalid audio route.")
        elif path not in {PROBES[role]["path"], "/query_result" if role == "music" else PROBES[role]["path"]}:
            fail("invalid_response", "Unsupported service route.")
        headers = {"Authorization": "Bearer " + config.key.get_secret_value()}
        try:
            start = time.monotonic()
            with self.client.stream("POST" if payload is not None else "GET", config.origin + path,
                                    json=payload if payload is not None else None, headers=headers) as response:
                status = response.status_code
                if status == 429:
                    fail("rate_limited", "The class service is busy. Wait before trying again.", True)
                if status >= 500:
                    fail("unavailable", "The class service is temporarily unavailable.", True)
                if status != 200:
                    fail("rejected", "The class service rejected the request. Check server configuration.")
                chunks, size = [], 0
                for chunk in response.iter_bytes(chunk_size=65536):
                    size += len(chunk)
                    if size > MAX_BYTES or time.monotonic() - start > 180:
                        fail("invalid_response", "Service response exceeded the supported size or time limit.")
                    chunks.append(chunk)
                return b"".join(chunks), response.headers.get("content-type", "").split(";", 1)[0].lower()
        except httpx.TimeoutException:
            fail("timeout", "The class service timed out. Check the existing job before retrying.", True)
        except httpx.HTTPError:
            fail("unavailable", "Could not reach the class service.", True)
        except httpx.InvalidURL:
            # InvalidURL inherits directly from Exception in the locked HTTPX version.
            fail("invalid_response", "Service returned an invalid route.")

    def _json(self, role, path, payload):
        raw, mime = self._request(role, path, payload)
        try:
            if mime != "application/json":
                raise ValueError()
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError()
            return value
        except (ValueError, UnicodeError):
            fail("invalid_response", "The class service returned an invalid response.")

    def _payload(self, role):
        return deepcopy(PROBES[role]["request"])

    def text(self, prompt: str) -> str:
        if not prompt.strip():
            raise ValueError("Text prompt is required")
        payload = self._payload("text")
        payload["messages"] = [{"role": "user", "content": prompt}]
        data = self._json("text", PROBES["text"]["path"], payload)
        try:
            choice = data["choices"][0]
            result = choice["message"]["content"]
            if data.get("model") != PROBES["text"]["request"]["model"] or not isinstance(result, str) or not result.strip() or choice.get("finish_reason") != "stop":
                raise ValueError()
            return result
        except (KeyError, IndexError, TypeError, ValueError):
            fail("invalid_response", "The text service returned no complete text.")

    def lyrics(self, prompt: str) -> str:
        """Song lyrics from Qwen; same endpoint/model as text() with a token
        budget sized for 10-60 second songs instead of the probe's short marker.
        The raised budget is a deliberate, documented deviation that requires
        live evidence (A3-03 acceptance), not a guessed payload."""
        if not prompt.strip():
            raise ValueError("Lyrics prompt is required")
        payload = self._payload("text")
        payload["messages"] = [{"role": "user", "content": prompt}]
        payload["max_completion_tokens"] = 512
        data = self._json("text", PROBES["text"]["path"], payload)
        try:
            choice = data["choices"][0]
            result = choice["message"]["content"]
            if data.get("model") != PROBES["text"]["request"]["model"] or not isinstance(result, str) or not result.strip() or choice.get("finish_reason") != "stop":
                raise ValueError()
            return result
        except (KeyError, IndexError, TypeError, ValueError):
            fail("invalid_response", "The text service returned no complete lyrics.")

    def cover(self, prompt: str) -> MediaBytes:
        if not prompt.strip():
            raise ValueError("Cover prompt is required")
        payload = self._payload("art")
        payload["prompt"] = prompt
        data = self._json("art", PROBES["art"]["path"], payload)
        try:
            raw = base64.b64decode(data["data"][0]["b64_json"], validate=True)
            if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
                raise ValueError()
            with Image.open(io.BytesIO(raw)) as image:
                if image.format != "PNG" or image.size != (512, 512):
                    raise ValueError()
                image.load()
            return MediaBytes(raw, "image/png")
        except (KeyError, IndexError, TypeError, ValueError, OSError, binascii.Error, UnidentifiedImageError, Image.DecompressionBombError):
            fail("invalid_response", "The art service returned an invalid image.")

    def speech(self, text: str) -> MediaBytes:
        if not 1 <= len(text.strip()) <= 4096:
            raise ValueError("Speech input must contain 1-4096 characters")
        payload = self._payload("speech")
        payload["input"] = text
        raw, mime = self._request("speech", PROBES["speech"]["path"], payload)
        return self._wav(raw, mime)

    def submit_music(self, prompt: str, *, duration_seconds=10, lyrics="[Instrumental]") -> MusicTicket:
        if not prompt.strip() or not 10 <= duration_seconds <= 600:
            raise ValueError("Music needs a prompt and duration of 10-600 seconds")
        payload = self._payload("music")
        # The probe's 80 BPM / C Major / 4/4 describes its piano sample, not
        # every song. Missing metadata lets ACE-Step infer it from the prompt.
        for field in ("bpm", "key_scale", "time_signature"):
            payload.pop(field, None)
        # Enable the supported music-LM caption enhancement and semantic audio
        # planning path. Audible genre fidelity still needs listening evidence.
        payload.update(prompt=prompt, audio_duration=duration_seconds, lyrics=lyrics,
                       thinking=True, use_cot_caption=True)
        data = self._json("music", "/release_task", payload)
        try:
            task_id = data["data"]["task_id"]
            if data.get("code") != 200 or data.get("error") is not None or not isinstance(task_id, str) or not task_id:
                raise ValueError()
            return MusicTicket(task_id)
        except (KeyError, TypeError, ValueError):
            fail("invalid_response", "The music service did not return a valid job.")

    def poll_music(self, ticket: MusicTicket) -> MusicPoll:
        data = self._json("music", "/query_result", {"task_id_list": [ticket.task_id]})
        try:
            if data.get("code") != 200 or data.get("error") is not None:
                raise ValueError()
            items = data["data"]
            if len(items) != 1 or items[0]["task_id"] != ticket.task_id:
                raise ValueError()
            item = items[0]
            if item["status"] == 0:
                return MusicPoll("running")
            if item["status"] == 2:
                fail("generation_failed", "Music generation failed. You can submit a new job.", True)
            if item["status"] != 1 or not isinstance(item["result"], str):
                raise ValueError()
            results = json.loads(item["result"])
            if not isinstance(results, list) or len(results) != 1:
                raise ValueError()
            if results[0].get("dit_model") != "acestep-v15-xl-turbo" or results[0].get("status") != 1:
                raise ValueError()
            path = results[0]["file"]
            if not isinstance(path, str):
                raise ValueError()
            return MusicPoll("succeeded", path)
        except (KeyError, IndexError, TypeError, ValueError):
            fail("invalid_response", "The music service returned an invalid job result.")

    def download_music(self, result: MusicPoll) -> MediaBytes:
        if result.state != "succeeded" or not result.download_path:
            raise ValueError("Only a completed music result can be downloaded")
        return self._wav(*self._request("music", result.download_path))

    @staticmethod
    def _wav(raw, mime):
        if mime not in {"audio/wav", "audio/x-wav"} or len(raw) < 44 or raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
            fail("invalid_response", "The speech/music service returned invalid WAV audio.")
        try:
            with wave.open(io.BytesIO(raw), "rb") as audio:
                frames, width, channels = audio.getnframes(), audio.getsampwidth(), audio.getnchannels()
                if frames < 1 or channels not in {1, 2} or width not in {1, 2, 3, 4}:
                    raise ValueError()
                if len(audio.readframes(frames)) != frames * width * channels:
                    raise ValueError()
        except (wave.Error, EOFError, ValueError):
            fail("invalid_response", "The speech/music service returned invalid WAV audio.")
        return MediaBytes(raw, "audio/wav")
