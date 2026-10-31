"""Bounded, process-local sessions and cover/music jobs shared with song orchestration."""
from dataclasses import dataclass, field
import io
import secrets
from threading import RLock
import time
from uuid import UUID, uuid4

from .contracts import GenerationJob, JobState, MediaRef, Playback, SafeError, SessionSnapshot, SongSettings, Track
from .providers import MediaBytes, MusicTicket, ProviderFailure

SESSION_COOKIE = "jukebox_session"
SESSION_SECONDS = 7200
MAX_SESSIONS = 32
MAX_TRACKS = 20
MAX_JOBS = 100
MAX_ACTIVE_COVERS = 2
MAX_ACTIVE_MUSIC = 2
MAX_ACTIVE_TEXT = 1
MAX_MEDIA_BYTES = 64_000_000
# Reference-voice bounds: temporary uploaded MP3/WAV clips for Chatterbox DJ
# speech. Kept in session memory only (never disk, snapshot or archives),
# consumed once by a speech job, expired with the session.
MAX_REFERENCES = 4
MAX_REFERENCE_BYTES = 5_000_000
MIN_REFERENCE_SECONDS = 1
MAX_REFERENCE_SECONDS = 60
# Operational music bounds: the class server's 20 MB response cap limits a
# 48 kHz/16-bit/stereo WAV to roughly 104 seconds, and 60 seconds leaves safe
# margin for headers/overhead while staying well within the global media budget.
MAX_MUSIC_DURATION = 60
MUSIC_POLL_INTERVAL = 3.0
MUSIC_DEADLINE_SECONDS = 300


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
    # Temporary voice references: browser uploads -> server-private bytes used
    # once by a speech job. Never exposed in snapshots, never written to disk.
    references: dict[UUID, MediaBytes] = field(default_factory=dict)
    playback: Playback = field(default_factory=Playback)
    # Each entry is one in-flight job (track id, job kind); a track may have an
    # art job and a music job running at the same time.
    active: set[tuple[UUID, str]] = field(default_factory=set)
    # Server-private ACE-Step submission tickets retained for the job's polls;
    # never exposed to the browser, snapshots or logs.
    tickets: dict[UUID, MusicTicket] = field(default_factory=dict)
    touched: float = field(default_factory=time.monotonic)


def cover_prompt(track: Track) -> str:
    return ("Create original square album cover art for this song.\n"
            f"Song title and theme: {track.title}\n"
            f"Musical style: {track.settings.style}\n"
            f"Mood: {track.settings.mood}\n"
            "Reflect this song's theme, musical style and mood in the imagery and colors. "
            "Use an original visual composition, no lettering, logos or copied album artwork.")


def music_prompt(track: Track) -> str:
    return ("Compose an original instrumental song; no vocals and no lyrics.\n"
            f"Song title and theme: {track.title}\n"
            f"Musical style: {track.settings.style}\n"
            f"Mood: {track.settings.mood}\n"
            f"Approximate length: {track.settings.duration_seconds} seconds.\n"
            "Create a cohesive, playable instrumental piece that matches this style and mood.")


def vocal_music_prompt(track: Track) -> str:
    return ("Compose an original song with expressive sung vocals that perform the provided lyrics.\n"
            f"Song title and theme: {track.title}\n"
            f"Musical style: {track.settings.style}\n"
            f"Mood: {track.settings.mood}\n"
            f"Approximate length: {track.settings.duration_seconds} seconds.\n"
            "Create a cohesive, playable vocal piece that matches this style and mood.")


def lyrics_prompt(track: Track) -> str:
    line_count = min(16, max(6, round(track.settings.duration_seconds / 4)))
    return ("Write original song lyrics for a new song.\n"
            f"Song title and theme: {track.title}\n"
            f"Musical style: {track.settings.style}\n"
            f"Mood: {track.settings.mood}\n"
            f"Target length: about {track.settings.duration_seconds} seconds, roughly {line_count} short lines.\n"
            "Return only the lyrics: original, plain, one line per verse line, "
            "no section headings, no song title, no commentary. English.")


def validate_reference_audio(content: bytes) -> str:
    """Return the canonical media type of a REAL MP3/WAV file, or raise.

    Byte-level structural validation only: WAV must be RIFF/WAVE with a
    full PCM fmt chunk and a physically present, non-empty data chunk;
    MP3 must start with a valid ID3v2 tag (or a frame immediately) and
    contain at least one reachable MPEG audio frame. Header-only or
    truncated uploads are rejected here rather than trusted from their
    bytes. Never echoes content; safe messages only.
    """
    if content.startswith(b"RIFF") and content[8:12] == b"WAVE":
        _validate_wav_structure(content)
        return "audio/wav"
    if content.startswith(b"ID3"):
        _validate_mp3_structure(content, id3=True)
        return "audio/mpeg"
    if len(content) >= 2 and content[0] == 0xFF and (content[1] & 0xE0) == 0xE0:
        _validate_mp3_structure(content, id3=False)
        return "audio/mpeg"
    raise SessionFailure(422, "Reference must be an MP3 or WAV audio file.")


def _validate_wav_structure(content: bytes) -> None:
    """Require a real PCM WAV: RIFF/WAVE, fmt chunk, physical data chunk."""
    if len(content) < 12:
        raise SessionFailure(422, "The WAV reference could not be read.")
    offset = 12
    fmt = None
    data = None
    found_data = False
    while offset + 8 <= len(content):
        chunk_id = content[offset : offset + 4]
        size = int.from_bytes(content[offset + 4 : offset + 8], "little")
        payload = offset + 8
        if payload + size > len(content):
            if found_data:
                # Tolerated trailing bytes after the keep-audio chunk (some
                # writers append metadata); the required structure is intact.
                break
            raise SessionFailure(422, "The WAV reference is truncated.")
        if chunk_id == b"fmt ":
            fmt = content[payload : payload + size]
        elif chunk_id == b"data":
            data = (payload, size)
            found_data = True
        offset = payload + size + (size & 1)  # RIFF pads odd sizes
    if fmt is None or data is None:
        raise SessionFailure(422, "The WAV reference is missing required chunks.")
    if len(fmt) < 16:
        raise SessionFailure(422, "The WAV reference could not be read.")
    format_tag = int.from_bytes(fmt[0:2], "little")
    channels = int.from_bytes(fmt[2:4], "little")
    sample_rate = int.from_bytes(fmt[4:8], "little")
    byte_rate = int.from_bytes(fmt[8:12], "little")
    block_align = int.from_bytes(fmt[12:14], "little")
    bits = int.from_bytes(fmt[14:16], "little")
    data_offset, data_size = data
    if format_tag != 1 or not 1 <= channels <= 8:
        raise SessionFailure(422, "The WAV reference must be uncompressed PCM.")
    if not 1 <= sample_rate <= 384_000 or byte_rate <= 0 or block_align <= 0 or bits not in (8, 16, 24, 32):
        raise SessionFailure(422, "The WAV reference could not be read.")
    if data_size < 1:
        raise SessionFailure(422, "The WAV reference contains no audio data.")
    if data_offset + data_size > len(content):
        raise SessionFailure(422, "The WAV reference is truncated.")
    duration = data_size / byte_rate
    if not MIN_REFERENCE_SECONDS <= duration <= MAX_REFERENCE_SECONDS:
        raise SessionFailure(
            422, f"Reference audio must be {MIN_REFERENCE_SECONDS}-{MAX_REFERENCE_SECONDS} seconds.")


def _validate_mp3_structure(content: bytes, *, id3: bool) -> None:
    """Require a parseable ID3v2 tag and at least one reachable MPEG frame."""
    skip = 0
    if id3:
        if len(content) < 10:
            raise SessionFailure(422, "The MP3 reference is truncated.")
        version = content[3:5]
        if version[0] == 0xFF or version[1] == 0xFF:
            raise SessionFailure(422, "The MP3 reference could not be read.")
        size_bytes = content[6:10]
        tag_size = 0
        for byte in size_bytes:
            tag_size = (tag_size << 7) | (byte & 0x7F)
        if 10 + tag_size > len(content):
            raise SessionFailure(422, "The MP3 reference is truncated.")
        skip = 10 + tag_size
    scan_limit = min(len(content) - 2, skip + 65_536)
    for index in range(skip, scan_limit):
        if content[index] == 0xFF and (content[index + 1] & 0xE0) == 0xE0 and (content[index + 1] & 0x06) != 0:
            return
    raise SessionFailure(422, "The MP3 reference contains no playable audio frames.")


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

    def _active_count(self, kind):
        return sum(1 for value in self.sessions.values() for (_, active_kind) in value.active if active_kind == kind)

    def queue_cover(self, session, track_id):
        with self.lock:
            if track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            if (track_id, "art") in session.active:
                raise SessionFailure(409, "A cover is already being generated for this track.")
            if self._active_count("art") >= MAX_ACTIVE_COVERS:
                raise SessionFailure(429, "Cover generation is busy. Try again shortly.", retryable=True)
            if len(session.jobs) >= MAX_JOBS:
                raise SessionFailure(429, "This session has reached its generation limit. Start a new session to continue.")
            job = GenerationJob(track_id=track_id, kind="art")
            session.jobs[job.id] = job
            session.active.add((track_id, "art"))
            return job

    def queue_music(self, session, track_id):
        with self.lock:
            if track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            track = session.tracks[track_id]
            if track.settings.mode == "vocal" and track.lyrics is None:
                raise SessionFailure(409, "Generate the song's lyrics before requesting vocal music.")
            duration = session.tracks[track_id].settings.duration_seconds
            if not 10 <= duration <= MAX_MUSIC_DURATION:
                raise SessionFailure(422, f"Song duration must be between 10 and {MAX_MUSIC_DURATION} seconds.")
            if (track_id, "music") in session.active:
                raise SessionFailure(409, "Music generation is already in progress for this track.")
            if self._active_count("music") >= MAX_ACTIVE_MUSIC:
                raise SessionFailure(429, "Music generation is busy. Try again shortly.", retryable=True)
            if len(session.jobs) >= MAX_JOBS:
                raise SessionFailure(429, "This session has reached its generation limit. Start a new session to continue.")
            job = GenerationJob(track_id=track_id, kind="music")
            session.jobs[job.id] = job
            session.active.add((track_id, "music"))
            return job

    def queue_lyrics(self, session, track_id):
        "Queue one deliberate Qwen lyrics generation for a vocal track."
        with self.lock:
            if track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            if session.tracks[track_id].settings.mode != "vocal":
                raise SessionFailure(422, "Only vocal tracks use AI lyrics.")
            if (track_id, "text") in session.active:
                raise SessionFailure(409, "Lyrics generation is already in progress for this track.")
            if self._active_count("text") >= MAX_ACTIVE_TEXT:
                raise SessionFailure(429, "Lyrics generation is busy. Try again shortly.", retryable=True)
            if len(session.jobs) >= MAX_JOBS:
                raise SessionFailure(429, "This session has reached its generation limit. Start a new session to continue.")
            job = GenerationJob(track_id=track_id, kind="text")
            session.jobs[job.id] = job
            session.active.add((track_id, "text"))
            return job

    def resume_music(self, session, failed_job_id, track_id):
        """Continue polling/downloading an existing submitted task without creating a new one.

        Only a failed music job with a retained provider ticket can be resumed, and
        the URL track must own the failed job. ALL validation happens before any
        job/slot allocation, so an invalid resume request has zero side effects.
        The resumed job never calls submit_music; it re-polls the same provider
        task ID and inherits the ticket association so further resumes work.
        Vocal tracks need no lyrics check here: the resumed task was already
        submitted with the lyrics it had then, and resume never resubmits — a
        lyrics re-generation is picked up only by a fresh 'Generate new vocal
        song' request, never by a resume.
        """
        with self.lock:
            previous = session.jobs.get(failed_job_id)
            if previous is None or previous.kind != "music" or previous.state != JobState.FAILED or not previous.error.retryable:
                raise SessionFailure(404, "No resumable music job found in this session.")
            if previous.track_id != track_id or track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            duration = session.tracks[track_id].settings.duration_seconds
            if not 10 <= duration <= MAX_MUSIC_DURATION:
                raise SessionFailure(422, f"Song duration must be between 10 and {MAX_MUSIC_DURATION} seconds.")
            if failed_job_id not in session.tickets:
                kind = "vocal song" if session.tracks[track_id].settings.mode == "vocal" else "instrumental"
                raise SessionFailure(409, f"The previous music submission was never confirmed, so it cannot be resumed. Generating a new {kind} will submit a new request.")
            if (track_id, "music") in session.active:
                raise SessionFailure(409, "Music generation is already in progress for this track.")
            if self._active_count("music") >= MAX_ACTIVE_MUSIC:
                raise SessionFailure(429, "Music generation is busy. Try again shortly.", retryable=True)
            if len(session.jobs) >= MAX_JOBS:
                raise SessionFailure(429, "This session has reached its generation limit. Start a new session to continue.")
            job = GenerationJob(track_id=track_id, kind="music")
            session.jobs[job.id] = job
            session.active.add((track_id, "music"))
            return job, failed_job_id

    def generate_cover(self, session, job_id, providers):
        with self.lock:
            job = session.jobs[job_id]
            job = job.transition(JobState.RUNNING)
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
                session.active.discard((job.track_id, "art"))
                session.touched = time.monotonic()

    def generate_lyrics(self, session, job_id, providers):
        """One deliberate Qwen lyrics call; the text attaches to its vocal track."""
        with self.lock:
            job = session.jobs[job_id]
            job = job.transition(JobState.RUNNING, progress=.3)
            session.jobs[job_id] = job
            track = session.tracks[job.track_id]
        try:
            lyrics = providers.lyrics(lyrics_prompt(track))
            if not lyrics.strip():
                raise ProviderFailure(SafeError(
                    code="generation_failed", message="The text service returned empty lyrics.", retryable=False))
            with self.lock:
                current = session.tracks[job.track_id]
                updated = Track.model_validate({**current.model_dump(), "lyrics": lyrics})
                session.tracks[current.id] = updated
                session.jobs[job.id] = job.transition(JobState.SUCCEEDED)
        except Exception as exc:
            error = exc.error if isinstance(exc, ProviderFailure) else SafeError(
                code="internal_error", message="Lyrics generation could not be completed. You can try again.", retryable=True)
            with self.lock:
                session.jobs[job.id] = job.transition(JobState.FAILED, error=error)
        finally:
            with self.lock:
                session.active.discard((job.track_id, "text"))
                session.touched = time.monotonic()

    def generate_music(self, session, job_id, providers, resume_from=None):
        """Submit one ACE-Step task, poll it with a bounded deadline, then download and attach the WAV.

        With resume_from set, no submission occurs: the poll/download continues the
        retained provider ticket of the named failed job. Progress stages are
        truthful: polling never rises above 0.79 (still generating), and the
        downloading stage (0.9) is set only after the poll actually succeeds.
        """
        with self.lock:
            job = session.jobs[job_id]
            job = job.transition(JobState.RUNNING, progress=.35 if resume_from is not None else .1)
            session.jobs[job_id] = job
            track = session.tracks[job.track_id]
        try:
            if resume_from is None:
                # Vocal tracks submit the track's current AI lyrics in the same
                # verified ACE-Step request; a vocal submission without lyrics
                # must fail loudly rather than silently produce another
                # instrumental with the frozen "[Instrumental]" marker.
                current = session.tracks[job.track_id]
                vocal = current.settings.mode == "vocal"
                if vocal and not current.lyrics:
                    raise ProviderFailure(SafeError(
                        code="generation_failed",
                        message="Lyrics are missing. Generate the song's lyrics before requesting vocal music.",
                        retryable=False))
                prompt = vocal_music_prompt(current) if vocal else music_prompt(current)
                lyrics = current.lyrics if vocal else "[Instrumental]"
                ticket = providers.submit_music(prompt, duration_seconds=current.settings.duration_seconds,
                                                lyrics=lyrics)
                with self.lock:
                    session.tickets[job_id] = ticket
                    job = session.jobs[job_id].with_progress(.3)
                    session.jobs[job_id] = job
            else:
                with self.lock:
                    ticket = session.tickets.get(resume_from)
                    if ticket is None:
                        kind = "vocal song" if session.tracks[job.track_id].settings.mode == "vocal" else "instrumental"
                        raise ProviderFailure(SafeError(
                            code="generation_failed",
                            message=f"The previous music job can no longer be resumed. Generate a new {kind} instead.",
                            retryable=False))
                    # Associate the ticket with this job too, so a further resume
                    # of THIS job can locate it (repeated resumes of one task).
                    session.tickets[job_id] = ticket
            deadline = time.monotonic() + MUSIC_DEADLINE_SECONDS
            result = None
            while result is None:
                if time.monotonic() >= deadline:
                    raise ProviderFailure(SafeError(
                        code="generation_failed",
                        message="Music generation is taking longer than expected. Check the class service queue before retrying.",
                        retryable=True))
                try:
                    polled = providers.poll_music(ticket)
                except ProviderFailure as exc:
                    if resume_from is not None and exc.error.code == "generation_failed":
                        # The provider reports the TASK itself failed; re-polling
                        # cannot ever succeed, so this is not endlessly resumable.
                        raise ProviderFailure(SafeError(
                            code="generation_failed",
                            message="The music task failed on the class service. Generate a new instrumental to start a new request.",
                            retryable=False)) from None
                    raise
                if polled.state == "succeeded":
                    result = polled
                else:
                    with self.lock:
                        job = session.jobs[job_id].with_progress(min(job.progress + .05, .79))
                        session.jobs[job_id] = job
                    time.sleep(MUSIC_POLL_INTERVAL)
            with self.lock:
                job = session.jobs[job_id].with_progress(.9)
                session.jobs[job_id] = job
            audio = providers.download_music(result)
            with self.lock:
                used = sum(len(media.content) for value in self.sessions.values() for media in value.media.values())
                if used + len(audio.content) > MAX_MEDIA_BYTES:
                    raise ProviderFailure(SafeError(code="generation_failed", message="Session media capacity reached. Existing tracks are preserved."))
                identifier = uuid4()
                reference = MediaRef(id=identifier, url=f"/api/media/{identifier}", content_type=audio.content_type)
                # Read the latest track: its cover may have completed while music was generating.
                current = session.tracks[job.track_id]
                updated = Track.model_validate({**current.model_dump(), "audio": reference, "status": "ready"})
                session.media[identifier] = audio
                session.tracks[current.id] = updated
                session.jobs[job.id] = job.transition(JobState.SUCCEEDED)
                # Clear every app job that pointed at this provider ticket
                # (the original submission and any intermediate resumes).
                for key in [key for key, item in session.tickets.items() if item == ticket]:
                    session.tickets.pop(key, None)
                session.tickets.pop(job_id, None)
                if current.audio is not None:
                    session.media.pop(current.audio.id, None)
        except Exception as exc:
            error = exc.error if isinstance(exc, ProviderFailure) else SafeError(
                code="internal_error", message="Music generation could not be completed. You can try again.", retryable=True)
            with self.lock:
                session.jobs[job.id] = job.transition(JobState.FAILED, error=error)
                # Keep provider tickets so a future recovery action can reuse them;
                # a new or resumed app job never auto-submits another task.
        finally:
            with self.lock:
                session.active.discard((job.track_id, "music"))
                session.touched = time.monotonic()

    def get_media(self, session, identifier):
        with self.lock:
            media = session.media.get(identifier)
            if media is None:
                raise SessionFailure(404, "Media not found in this session.")
            return media

    def upload_reference(self, session, content: bytes):
        """Validate and store one temporary MP3/WAV voice reference.

        Returns (id, normalized media type). The bytes live only in session
        memory; they are consumed once by a speech job, deleted explicitly, or
        dropped with the session. Nothing here touches disk, the snapshot or
        Git (uploads are excluded from archives by the repo safeguards).
        """
        with self.lock:
            if len(content) > MAX_REFERENCE_BYTES:
                raise SessionFailure(422, f"Reference audio must be {MAX_REFERENCE_BYTES // 1_000_000} MB or smaller.")
            media_type = validate_reference_audio(content)
            if len(session.references) >= MAX_REFERENCES:
                raise SessionFailure(429, "Too many reference uploads in this session. Delete one before uploading again.", retryable=True)
            identifier = uuid4()
            session.references[identifier] = MediaBytes(content, media_type)
            session.touched = time.monotonic()
            return identifier, media_type

    def take_reference(self, session, identifier):
        """Consume a reference exactly once; the speech job that uses it removes it."""
        with self.lock:
            return session.references.pop(identifier, None)

    def drop_reference(self, session, identifier):
        with self.lock:
            if identifier not in session.references:
                raise SessionFailure(404, "Reference not found in this session.")
            del session.references[identifier]
            session.touched = time.monotonic()
