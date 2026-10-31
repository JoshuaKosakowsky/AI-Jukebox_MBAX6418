"""Bounded local catalog. Manifest inclusion is selection; candidates are never scanned."""
from dataclasses import dataclass
from datetime import date
import io
import json
from pathlib import Path, PurePosixPath
from uuid import UUID, uuid4
import wave

from PIL import Image, UnidentifiedImageError
from pydantic import Field, StrictBool, model_validator

from .contracts import Model, Track, SongSettings, MediaRef
from .providers import ClassProviders, MediaBytes, ProviderFailure

ERROR_MESSAGE = "Bundled samples could not be loaded. Check the sample manifest and assets, then restart the app."
MAX_ASSET_BYTES = 20_000_000


class SampleLibraryError(ValueError):
    pass


class SampleRecord(Model):
    id: UUID
    title: str = Field(min_length=1, max_length=120)
    audio: str
    cover: str
    instrumental: StrictBool
    lyrics: str | None = Field(default=None, max_length=12000)
    generated_at: str
    generation_notes: str = Field(min_length=1, max_length=8000)
    generated_with: dict[str, str]
    style: str = Field(default="Class-generated sample", min_length=1, max_length=120)
    mood: str = Field(default="Pregenerated", min_length=1, max_length=120)

    @model_validator(mode="after")
    def provenance(self):
        date.fromisoformat(self.generated_at)
        if self.generated_with.get("music") != "ACE-Step 1.5 XL Turbo" or self.generated_with.get("cover") != "FLUX.2 klein 4B":
            raise ValueError("Required class provenance missing")
        if not self.instrumental and (not self.lyrics or self.generated_with.get("lyrics") != "Qwen3.6-35B-A3B"):
            raise ValueError("Vocal sample needs AI lyrics and provenance")
        if self.instrumental and self.lyrics is not None:
            raise ValueError("Instrumental samples must not claim lyrics")
        return self


class Manifest(Model):
    samples: list[SampleRecord] = Field(max_length=3)


@dataclass(frozen=True)
class Sample:
    track: Track
    audio: MediaBytes
    cover: MediaBytes


def read_asset(root: Path, name: str, suffix: str) -> bytes:
    path = PurePosixPath(name)
    if (path.is_absolute() or '\\' in name or '..' in path.parts
            or path.parts[:2] != ('assets', 'samples') or path.suffix.lower() != suffix):
        raise ValueError("Invalid sample asset")
    resolved = (root / name).resolve()
    if not resolved.is_relative_to((root / 'assets/samples').resolve()) or not resolved.is_file():
        raise ValueError("Sample asset outside catalog")
    with resolved.open('rb') as stream:
        raw = stream.read(MAX_ASSET_BYTES + 1)
    if not raw or len(raw) > MAX_ASSET_BYTES:
        raise ValueError("Sample asset size unsupported")
    return raw


def load_samples(root: Path, *, max_bytes: int) -> tuple[Sample, ...]:
    """All-or-nothing validation with no network and no raw errors escaping."""
    try:
        catalog_dir = (root / 'assets/samples').resolve()
        manifest = (catalog_dir / 'manifest.json').resolve()
        if (not catalog_dir.is_relative_to(root.resolve())
                or not manifest.is_relative_to(catalog_dir) or not manifest.is_file()):
            raise ValueError("Manifest outside catalog")
        with manifest.open('rb') as stream:
            raw = stream.read(128_001)
        if len(raw) > 128_000:
            raise ValueError("Manifest too large")
        records = Manifest.model_validate(json.loads(raw)).samples
        if (len({r.id for r in records}) != len(records)
                or len({r.audio for r in records}) != len(records)
                or len({r.cover for r in records}) != len(records)):
            raise ValueError("Duplicate sample identity or assets")
        loaded, used, resolved_paths = [], 0, set()
        for r in records:
            for name in (r.audio, r.cover):
                resolved = (root / name).resolve()
                if resolved in resolved_paths:
                    raise ValueError("Aliased sample assets")
                resolved_paths.add(resolved)
            audio = ClassProviders._wav(read_asset(root, r.audio, '.wav'), 'audio/wav')
            with wave.open(io.BytesIO(audio.content), 'rb') as decoded:
                duration = decoded.getnframes() / decoded.getframerate()
            if not 10 <= duration <= 600:
                raise ValueError("Sample duration outside track limits")
            cover_raw = read_asset(root, r.cover, '.png')
            with Image.open(io.BytesIO(cover_raw)) as image:
                if image.format != 'PNG' or image.size != (512, 512):
                    raise ValueError("Invalid sample cover")
                image.load()
            used += len(audio.content) + len(cover_raw)
            if used > max_bytes:
                raise ValueError("Sample catalog exceeds media budget")
            refs = [MediaRef(id=i, url=f'/api/media/{i}', content_type=mime)
                    for i, mime in [(uuid4(), 'audio/wav'), (uuid4(), 'image/png')]]
            track = Track(id=r.id, title=r.title, status='ready', audio=refs[0], cover=refs[1],
                          lyrics=r.lyrics if not r.instrumental else None,
                          settings=SongSettings(style=r.style, mood=r.mood, duration_seconds=round(duration),
                                                mode='instrumental' if r.instrumental else 'vocal'))
            loaded.append(Sample(track, audio, MediaBytes(cover_raw, 'image/png')))
        return tuple(loaded)
    except (OSError, ValueError, TypeError, KeyError, EOFError, RuntimeError, wave.Error, ProviderFailure,
            UnidentifiedImageError, Image.DecompressionBombError):
        raise SampleLibraryError(ERROR_MESSAGE) from None
