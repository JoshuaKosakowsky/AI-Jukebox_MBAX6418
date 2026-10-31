"""Same-origin local app with session-scoped FLUX cover generation."""
from contextlib import asynccontextmanager
from typing import Literal
from uuid import UUID

from fastapi import BackgroundTasks, Depends, FastAPI, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import Field
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import ROOT, Settings
from .contracts import GenerationJob, Model, Playback, SessionSnapshot, SongSettings, schema
from .providers import ClassProviders, ProviderFailure, fail
from .sessions import MAX_MEDIA_BYTES, SESSION_COOKIE, SESSION_SECONDS, SessionFailure, SessionStore
from .samples import load_samples, SampleLibraryError


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

    def require_dj():
        if "text" not in settings.services:
            fail("not_configured", "DJ commentary needs the Qwen text service configured.")
        if "speech" not in settings.services:
            fail("not_configured", "DJ speech needs the Chatterbox speech service configured.")

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

    # ---- AI DJ queue -------------------------------------------------------

    class QueueBody(Model):
        track_id: UUID

    class PhaseBody(Model):
        phase: Literal["speaking", "playing"]
        track_id: UUID | None = None

    @app.post("/api/playback/queue", response_model=Playback)
    def playback_queue(data: QueueBody, current=Depends(browser_session)):
        require_dj()
        return store.queue_playback(current, data.track_id)

    @app.post("/api/playback/speech", response_model=GenerationJob, status_code=202)
    def playback_speech(data: QueueBody, tasks: BackgroundTasks = BackgroundTasks,
                        current=Depends(browser_session)):
        """Explicit user retry for a failed/absent DJ introduction.

        Never invoked automatically: replay, reload, polling and automatic
        advancement skip failed or cached commentary via the store guard. A
        failed introduction is only regenerated through this deliberate
        action, so provider budget cannot be re-spent by playback alone.
        """
        require_dj()
        job = store.request_dj_speech(current, data.track_id)
        tasks.add_task(store.generate_dj_speech, current, job.id, app.state.providers)
        return job

    @app.post("/api/playback/start", response_model=Playback)
    def playback_start(tasks: BackgroundTasks = BackgroundTasks, current=Depends(browser_session)):
        require_dj()
        playback, job = store.start_playback(current)
        if job is not None:
            tasks.add_task(store.generate_dj_speech, current, job.id, app.state.providers)
        return playback

    @app.post("/api/playback/advance", response_model=Playback)
    def playback_advance(tasks: BackgroundTasks = BackgroundTasks, current=Depends(browser_session)):
        require_dj()
        playback, job = store.advance_playback(current)
        if job is not None:
            tasks.add_task(store.generate_dj_speech, current, job.id, app.state.providers)
        return playback

    @app.post("/api/playback/phase", response_model=Playback)
    def playback_phase(data: PhaseBody, current=Depends(browser_session)):
        require_dj()
        return store.set_phase(current, data.phase, data.track_id)

    @app.post("/api/playback/pause", response_model=Playback)
    def playback_pause(data: PhaseBody, current=Depends(browser_session)):
        require_dj()
        return store.pause_playback(current, data.phase, data.track_id)

    @app.post("/api/playback/resume", response_model=Playback)
    def playback_resume(current=Depends(browser_session)):
        require_dj()
        return store.resume_playback(current)

    @app.get("/api/media/{media_id}")
    def media(media_id: UUID, current=Depends(browser_session)):
        image = store.get_media(current, media_id)
        return Response(image.content, media_type=image.content_type)

    @app.get("/api/contracts")
    def contracts():
        return schema()

    app.mount("/static", StaticFiles(directory=ROOT / "jukebox/web"), name="static")
    return app
