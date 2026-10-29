"""Bounded, process-local sessions and cover jobs shared with song orchestration."""
from dataclasses import dataclass, field
import secrets
from threading import RLock
import time
from uuid import UUID, uuid4

from .contracts import GenerationJob, JobState, MediaRef, Playback, SafeError, SessionSnapshot, SongSettings, Track
from .providers import MediaBytes, ProviderFailure

SESSION_COOKIE = "jukebox_session"
SESSION_SECONDS = 7200
MAX_SESSIONS = 32
MAX_TRACKS = 20
MAX_JOBS = 100
MAX_ACTIVE_COVERS = 2
MAX_MEDIA_BYTES = 64_000_000


class SessionFailure(Exception):
    def __init__(self, status, message, *, retryable=False):
        self.status = status
        self.error = SafeError(code="rejected", message=message, retryable=retryable)
        super().__init__(message)


@dataclass
class Session:
    token: str = field(default_factory=lambda: secrets.token_urlsafe(32))
    tracks: dict[UUID, Track] = field(default_factory=dict)
    jobs: dict[UUID, GenerationJob] = field(default_factory=dict)
    media: dict[UUID, MediaBytes] = field(default_factory=dict)
    playback: Playback = field(default_factory=Playback)
    active: set[UUID] = field(default_factory=set)
    touched: float = field(default_factory=time.monotonic)


def cover_prompt(track: Track) -> str:
    return ("Create original square album cover art for this song.\n"
            f"Song title and theme: {track.title}\n"
            f"Musical style: {track.settings.style}\n"
            f"Mood: {track.settings.mood}\n"
            "Reflect this song's theme, musical style and mood in the imagery and colors. "
            "Use an original visual composition, no lettering, logos or copied album artwork.")


class SessionStore:
    """One store per app process; no files, uploads or provider identifiers are persisted."""

    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self.lock = RLock()

    def resolve(self, token):
        with self.lock:
            now = time.monotonic()
            for key, value in list(self.sessions.items()):
                if not value.active and now - value.touched > SESSION_SECONDS:
                    del self.sessions[key]
            session = self.sessions.get(token)
            if session is None:
                if len(self.sessions) >= MAX_SESSIONS:
                    raise SessionFailure(429, "Session capacity reached. Try again later.", retryable=True)
                session = Session()
                self.sessions[session.token] = session
            session.touched = now
            return session

    def snapshot(self, session):
        with self.lock:
            return SessionSnapshot(tracks=list(session.tracks.values()), jobs=list(session.jobs.values()), playback=session.playback).model_copy(deep=True)

    def create_cover_track(self, session, title: str, settings: SongSettings):
        with self.lock:
            if len(session.tracks) >= MAX_TRACKS:
                raise SessionFailure(429, "This session has reached its track limit. Start a new session for more tracks.")
            track = Track(title=title, settings=settings)
            session.tracks[track.id] = track
            try:
                return self.queue_cover(session, track.id)
            except SessionFailure:
                del session.tracks[track.id]
                raise

    def queue_cover(self, session, track_id):
        with self.lock:
            if track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            if track_id in session.active:
                raise SessionFailure(409, "A cover is already being generated for this track.")
            if sum(len(value.active) for value in self.sessions.values()) >= MAX_ACTIVE_COVERS:
                raise SessionFailure(429, "Cover generation is busy. Try again shortly.", retryable=True)
            if len(session.jobs) >= MAX_JOBS:
                raise SessionFailure(429, "This session has reached its generation limit. Start a new session to continue.")
            job = GenerationJob(track_id=track_id, kind="art")
            session.jobs[job.id] = job
            session.active.add(track_id)
            return job

    def generate_cover(self, session, job_id, providers):
        with self.lock:
            job = session.jobs[job_id].transition(JobState.RUNNING)
            session.jobs[job_id] = job
            track = session.tracks[job.track_id]
        try:
            image = providers.cover(cover_prompt(track))
            with self.lock:
                used = sum(len(media.content) for value in self.sessions.values() for media in value.media.values())
                if used + len(image.content) > MAX_MEDIA_BYTES:
                    raise ProviderFailure(SafeError(code="generation_failed", message="Session media capacity reached. Existing covers are preserved."))
                identifier = uuid4()
                reference = MediaRef(id=identifier, url=f"/api/media/{identifier}", content_type=image.content_type)
                # Read the latest track: another feature may have attached audio during generation.
                current = session.tracks[job.track_id]
                updated = Track.model_validate({**current.model_dump(), "cover": reference})
                session.media[identifier] = image
                session.tracks[current.id] = updated
                session.jobs[job.id] = job.transition(JobState.SUCCEEDED)
                if current.cover is not None:
                    session.media.pop(current.cover.id, None)
        except Exception as exc:
            error = exc.error if isinstance(exc, ProviderFailure) else SafeError(
                code="internal_error", message="Cover generation could not be completed. You can try again.", retryable=True)
            with self.lock:
                session.jobs[job.id] = job.transition(JobState.FAILED, error=error)
        finally:
            with self.lock:
                session.active.discard(job.track_id)
                session.touched = time.monotonic()

    def get_media(self, session, identifier):
        with self.lock:
            media = session.media.get(identifier)
            if media is None:
                raise SessionFailure(404, "Media not found in this session.")
            return media
