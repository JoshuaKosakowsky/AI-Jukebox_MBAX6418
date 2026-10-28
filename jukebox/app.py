"""Same-origin startup shell. Generation/playback routes belong to later tasks."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .config import ROOT, Settings
from .contracts import SessionSnapshot, schema
from .providers import ClassProviders, ProviderFailure


def create_app(settings: Settings | None = None):
    settings = settings if settings is not None else Settings.load()

    @asynccontextmanager
    async def lifespan(app):
        app.state.providers = ClassProviders(settings)
        try:
            yield
        finally:
            app.state.providers.close()

    app = FastAPI(title="AI Jukebox", version="0.1.0", lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url="/api/openapi.json")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])

    @app.exception_handler(ProviderFailure)
    async def provider_error(request, exc):
        return JSONResponse({"error": exc.error.model_dump()}, status_code=502)

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
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; media-src 'self' blob:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/", include_in_schema=False)
    def home():
        return FileResponse(ROOT / "jukebox/web/index.html")

    @app.get("/api/health")
    def health():
        return {"status": "ok", "contract_version": 1}

    @app.get("/api/status")
    def status():
        return {"services": settings.public_status(), "configured": len(settings.services) == 4,
                "connectivity_checked": False, "generation_available": False}

    @app.get("/api/session", response_model=SessionSnapshot)
    def session():
        # Empty snapshots have no mutable global state. A3-02 adds per-session storage.
        return SessionSnapshot()

    @app.get("/api/contracts")
    def contracts():
        return schema()

    app.mount("/static", StaticFiles(directory=ROOT / "jukebox/web"), name="static")
    return app
