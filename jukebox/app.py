"""Same-origin local app with session-scoped FLUX cover generation."""
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import BackgroundTasks, Depends, FastAPI, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from multipart import MultipartParser
from multipart.multipart import parse_options_header
from python_multipart.exceptions import MultipartParseError
from pydantic import Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import ROOT, Settings
from .contracts import GenerationJob, Model, SessionSnapshot, SongSettings, schema
from .providers import ClassProviders, ProviderFailure, fail
from .samples import SampleLibraryError, load_samples
from .sessions import (MAX_MEDIA_BYTES, MAX_REFERENCE_BYTES, SESSION_COOKIE, SESSION_SECONDS,
                       SessionFailure, SessionStore)


# Room for the multipart boundary, part headers and trailing CRLF beyond the
# file-size cap; the parser itself enforces this total via max_size.
MULTIPART_OVERHEAD = 64 * 1024


def _extract_file_part(raw: bytes, content_type: str) -> bytes:
    """Pull the single 'file' part bytes out of an in-memory multipart body.

    Parsing happens entirely in memory through python-multipart callbacks:
    no temp files are ever created, so oversized or malformed uploads cannot
    spool to disk. Raises on anything but exactly one named 'file' part.
    """
    if not content_type.lower().startswith("multipart/form-data"):
        raise ValueError("not multipart")
    _, options = parse_options_header(content_type)
    boundary = options.get(b"boundary")
    if not boundary:
        raise ValueError("missing boundary")
    parts: list[dict] = []
    current: dict | None = None
    header_field = bytearray()
    header_value = bytearray()

    def on_part_begin():
        nonlocal current
        current = {"headers": {}, "data": bytearray()}

    def on_header_field(data, start, end):
        header_field.extend(data[start:end])

    def on_header_value(data, start, end):
        header_value.extend(data[start:end])

    def on_header_end():
        if current is not None:
            current["headers"][header_field.decode("latin-1").strip().lower()] = bytes(header_value)

    def on_headers_finished():
        header_field.clear()
        header_value.clear()

    def on_part_data(data, start, end):
        if current is not None:
            current["data"].extend(data[start:end])

    def on_part_end():
        if current is not None:
            parts.append(current)

    parser = MultipartParser(
        boundary,
        {
            "on_part_begin": on_part_begin,
            "on_header_field": on_header_field,
            "on_header_value": on_header_value,
            "on_header_end": on_header_end,
            "on_headers_finished": on_headers_finished,
            "on_part_data": on_part_data,
            "on_part_end": on_part_end,
        },
        max_size=MAX_REFERENCE_BYTES + MULTIPART_OVERHEAD,
    )
    parser.write(raw)
    parser.finalize()
    if len(parts) != 1:
        raise ValueError("expected one file part")
    headers = parts[0]["headers"]
    disposition = headers.get("content-disposition", b"")
    _, disp_options = parse_options_header(disposition)
    if disp_options.get(b"name") != b"file" or not disp_options.get(b"filename"):
        raise ValueError("expected a named file part")
    return bytes(parts[0]["data"])


class NewCoverTrack(Model):
    title: str = Field(min_length=1, max_length=120)
    settings: SongSettings


def create_app(settings: Settings | None = None):
    settings = settings if settings is not None else Settings.load()
    sample_error = None
    try:
        catalog = load_samples(ROOT, max_bytes=MAX_MEDIA_BYTES)
    except SampleLibraryError as exc:
        catalog, sample_error = (), str(exc)
    store = SessionStore(catalog)

    @asynccontextmanager
    async def lifespan(app):
        app.state.providers = ClassProviders(settings)
        try:
            yield
        finally:
            app.state.providers.close()

    app = FastAPI(title="AI Jukebox", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url="/api/openapi.json")
    app.state.sessions = store
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

    @app.exception_handler(ProviderFailure)
    async def provider_error(request, exc):
        return JSONResponse({"error": exc.error.model_dump()}, status_code=502)

    @app.exception_handler(SessionFailure)
    async def session_error(request, exc):
        return JSONResponse({"error": exc.error.model_dump()}, status_code=exc.status)

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        return JSONResponse({"error": {"code": "internal_error", "message": "The request could not be completed.", "retryable": False}}, status_code=500)

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            origin = request.headers.get("origin")
            if origin and origin != str(request.base_url).rstrip("/"):
                return JSONResponse({"error": "Cross-origin requests are not allowed"}, status_code=403)
        response = await call_next(request)
        current = getattr(request.state, "browser_session", None)
        if current is not None:
            response.set_cookie(SESSION_COOKIE, current.token, max_age=SESSION_SECONDS, httponly=True, samesite="strict")
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        response.headers["Cache-Control"] = "no-store"
        return response

    def browser_session(request: Request):
        session = store.resolve(request.cookies.get(SESSION_COOKIE))
        request.state.browser_session = session
        return session

    def require_art():
        if "art" not in settings.services:
            fail("not_configured", "Art service is not configured.")

    def require_music():
        if "music" not in settings.services:
            fail("not_configured", "Music service is not configured.")

    def require_text():
        if "text" not in settings.services:
            fail("not_configured", "Text service is not configured.")

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(ROOT / "jukebox/web/index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "contract_version": 1}

    @app.get("/api/status")
    def status():
        return {"services": settings.public_status(), "configured": len(settings.services) == 4,
                "connectivity_checked": False, "generation_available": False,
                "cover_generation_available": "art" in settings.services,
                "music_generation_available": "music" in settings.services,
                "lyrics_generation_available": "text" in settings.services,
                "sample_library": {"count": len(catalog), "error": sample_error}}

    @app.get("/api/session", response_model=SessionSnapshot)
    def session(current=Depends(browser_session)):
        return store.snapshot(current)

    @app.post("/api/tracks", response_model=GenerationJob, status_code=202)
    def create_track(data: NewCoverTrack, tasks: BackgroundTasks, current=Depends(browser_session)):
        require_art()
        job = store.create_cover_track(current, data.title, data.settings)
        tasks.add_task(store.generate_cover, current, job.id, app.state.providers)
        return job

    @app.post("/api/tracks/{track_id}/cover", response_model=GenerationJob, status_code=202)
    def generate_cover(track_id: UUID, tasks: BackgroundTasks, current=Depends(browser_session)):
        require_art()
        job = store.queue_cover(current, track_id)
        tasks.add_task(store.generate_cover, current, job.id, app.state.providers)
        return job

    @app.post("/api/tracks/{track_id}/music", response_model=GenerationJob, status_code=202)
    def generate_music(track_id: UUID, tasks: BackgroundTasks, current=Depends(browser_session)):
        require_music()
        job = store.queue_music(current, track_id)
        tasks.add_task(store.generate_music, current, job.id, app.state.providers)
        return job

    @app.post("/api/tracks/{track_id}/lyrics", response_model=GenerationJob, status_code=202)
    def generate_lyrics(track_id: UUID, tasks: BackgroundTasks, current=Depends(browser_session)):
        require_text()
        job = store.queue_lyrics(current, track_id)
        tasks.add_task(store.generate_lyrics, current, job.id, app.state.providers)
        return job

    @app.post("/api/tracks/{track_id}/music/resume", response_model=GenerationJob, status_code=202)
    def resume_music(track_id: UUID, from_job: UUID = Query(alias="from"), tasks: BackgroundTasks = BackgroundTasks,
                     current=Depends(browser_session)):
        require_music()
        # All ownership/state/capacity validation happens atomically inside the
        # store BEFORE a job or active slot is allocated; a mismatched track in
        # the URL has zero side effects.
        job, resume_from = store.resume_music(current, from_job, track_id)
        tasks.add_task(store.generate_music, current, job.id, app.state.providers, resume_from=resume_from)
        return job

    @app.get("/api/media/{media_id}")
    def media(media_id: UUID, current=Depends(browser_session)):
        image = store.get_media(current, media_id)
        return Response(image.content, media_type=image.content_type)

    @app.post("/api/references/speech", status_code=201)
    async def upload_speech_reference(request: Request, current=Depends(browser_session)):
        # Temporary MP3/WAV voice reference: bytes are validated and kept in
        # session memory only; never persisted, never in the snapshot, never
        # served back to the browser. The multipart body is parsed in memory
        # (no temp files, no disk spooling) with a hard capped stream.
        declared = request.headers.get("content-length")
        if declared:
            try:
                declared_length = int(declared)
            except ValueError:
                declared_length = None
            if declared_length is not None and declared_length > MAX_REFERENCE_BYTES + MULTIPART_OVERHEAD:
                raise SessionFailure(422, f"Reference audio must be {MAX_REFERENCE_BYTES // 1_000_000} MB or smaller.")
        raw = bytearray()
        async for chunk in request.stream():
            raw.extend(chunk)
            if len(raw) > MAX_REFERENCE_BYTES + MULTIPART_OVERHEAD:
                raise SessionFailure(422, f"Reference audio must be {MAX_REFERENCE_BYTES // 1_000_000} MB or smaller.")
        try:
            content = _extract_file_part(bytes(raw), request.headers.get("content-type", ""))
        except (MultipartParseError, ValueError, KeyError, IndexError, UnicodeDecodeError):
            raise SessionFailure(422, "The multipart upload could not be read.")
        identifier, media_type = store.upload_reference(current, content)
        return {"id": str(identifier), "media_type": media_type}

    @app.delete("/api/references/speech/{reference_id}", status_code=204)
    def delete_speech_reference(reference_id: UUID, current=Depends(browser_session)):
        store.drop_reference(current, reference_id)
        return Response(status_code=204)

    @app.get("/api/contracts")
    def contracts():
        return schema()

    app.mount("/static", StaticFiles(directory=ROOT / "jukebox/web"), name="static")
    return app
