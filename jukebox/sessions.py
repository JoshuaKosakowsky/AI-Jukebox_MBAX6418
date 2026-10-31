"""Bounded, process-local sessions and cover/music jobs shared with song orchestration."""
from dataclasses import dataclass, field
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
MAX_ACTIVE_SPEECH = 2
MAX_QUEUE = MAX_TRACKS
MAX_MEDIA_BYTES = 64_000_000
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
    playback: Playback = field(default_factory=Playback)
    # Each entry is one in-flight job (track id, job kind); a track may have an
    # art job and a music job running at the same time.
    active: set[tuple[UUID, str]] = field(default_factory=set)
    # Server-private ACE-Step submission tickets retained for the job's polls;
    # never exposed to the browser, snapshots or logs.
    tickets: dict[UUID, MusicTicket] = field(default_factory=dict)
    # Server-private Qwen commentary texts for speech jobs (evidence/internal
    # use only; never in snapshots, logs or the browser).
    speech_prompts: dict[UUID, str] = field(default_factory=dict)
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


def dj_prompt(track: Track, prior: Track | None, position: int, total: int) -> str:
    """Song-specific spoken commentary for Qwen (default ChatGPT-style text).

    The prompt carries the queued song's title, style, mood and vocal mode plus
    transition context from the previous song; the result is spoken by
    Chatterbox's default voice. No user content or credentials are included.
    """
    if prior is None or position == 0:
        transition = "This is the first song of the set."
    elif position == total - 1:
        transition = f"After {prior.title}, this is our final song."
    else:
        transition = f"After {prior.title}, the set continues."
    mode = "vocal song" if track.settings.mode == "vocal" else "instrumental"
    return ("You are the jukebox DJ. Write 2-4 short, natural spoken sentences "
            "that introduce the next song for an automated radio show. Speak as "
            "a friendly radio DJ. Plain speech only: no stage directions, no "
            "sound effects, no section headings, no song titles in quotes.\n"
            f"{transition}\n"
            f"Song title and theme: {track.title}\n"
            f"Musical style: {track.settings.style}\n"
            f"Mood: {track.settings.mood}\n"
            f"Type: {mode}.")


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

    # ---- AI DJ queue -------------------------------------------------------

    def queue_playback(self, session, track_id):
        """Append one playable track to the DJ queue (one entry per track)."""
        with self.lock:
            if track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            if session.tracks[track_id].audio is None:
                raise SessionFailure(409, "Add this track to the DJ queue once its audio is ready.")
            if track_id in session.playback.queue:
                raise SessionFailure(409, "This track is already in the DJ queue.")
            if len(session.playback.queue) >= MAX_QUEUE:
                raise SessionFailure(429, "The DJ queue is full. Remove entries before adding more.")
            session.playback = Playback.model_validate({**session.playback.model_dump(),
                                                        "queue": [*session.playback.queue, track_id]})
            return session.playback

    def _queue_dj_speech(self, session, track_id, prior, position, total):
        """Create the commentary job for one track, best-effort.

        Silent skips (job already exists, commentary busy, session at its
        generation limit) keep the set flowing: commentary is an enhancement,
        never a blocker. The speech attaches to the TRACK itself, so a stale
        completion of a long-skipped track can never play while another track
        is current.
        """
        with self.lock:
            track = session.tracks[track_id]
            if track.speech is not None or (track_id, "speech") in session.active:
                return None
            # A previously REQUESTED introduction that FAILED must never be
            # silently resubmitted by replay, reload, polling or automatic
            # advancement: the failure is terminal for the session and stays
            # visible on its job record, music continues best-effort, and the
            # only retry path is an explicit user action (request_dj_speech).
            # Otherwise a transient provider failure would re-spend the
            # Qwen/Chatterbox budget on every replay.
            latest = next((job for job in reversed(list(session.jobs.values()))
                           if job.track_id == track_id and job.kind == "speech"), None)
            if latest is not None and latest.state == JobState.FAILED:
                return None
            if self._active_count("speech") >= MAX_ACTIVE_SPEECH or len(session.jobs) >= MAX_JOBS:
                return None
            job = GenerationJob(track_id=track_id, kind="speech")
            session.jobs[job.id] = job
            session.active.add((track_id, "speech"))
            session.speech_prompts[job.id] = dj_prompt(track, prior, position, total)
            return job

    def request_dj_speech(self, session, track_id):
        """Explicit user retry for a failed or absent DJ introduction.

        The only path that creates a NEW speech job after a failure; it is
        never called automatically (replay/reload/advance all skip via
        _queue_dj_speech). A track with commentary already attached or with a
        speech job already in flight rejects the request.
        """
        with self.lock:
            if track_id not in session.tracks:
                raise SessionFailure(404, "Track not found in this session.")
            track = session.tracks[track_id]
            if track.speech is not None:
                raise SessionFailure(409, "This track already has its DJ introduction.")
            if (track_id, "speech") in session.active:
                raise SessionFailure(409, "DJ commentary is already being generated for this track.")
            if self._active_count("speech") >= MAX_ACTIVE_SPEECH:
                raise SessionFailure(429, "DJ commentary is busy. Try again shortly.", retryable=True)
            if len(session.jobs) >= MAX_JOBS:
                raise SessionFailure(429, "This session has reached its generation limit. Start a new session to continue.")
            queue = session.playback.queue
            try:
                position = queue.index(track_id)
            except ValueError:
                position, queue_length = 0, 1
            else:
                queue_length = len(queue)
            prior_id = queue[position - 1] if position > 0 else None
            prior = session.tracks[prior_id] if prior_id is not None else None
            job = GenerationJob(track_id=track_id, kind="speech")
            session.jobs[job.id] = job
            session.active.add((track_id, "speech"))
            session.speech_prompts[job.id] = dj_prompt(track, prior, position, queue_length)
            return job

    def start_playback(self, session):
        """Start the queue at its first entry and request its DJ introduction."""
        with self.lock:
            if not session.playback.queue:
                raise SessionFailure(409, "Add songs to the DJ queue before starting.")
            if session.playback.state != "idle":
                raise SessionFailure(409, "Playback is already active. Pause it or skip ahead instead.")
            first = session.playback.queue[0]
            session.playback = Playback.model_validate({**session.playback.model_dump(), "state": "speaking",
                                                        "index": 0, "current_track_id": first})
        job = self._queue_dj_speech(session, first, None, 0, len(session.playback.queue))
        return session.playback, job

    def advance_playback(self, session):
        """Advance to the next queue entry (skip or natural end of a song).

        Idle at the end of the queue with the queue kept for another play;
        otherwise the new current track gets its introduction speech request.
        A paused advance stays paused.
        """
        with self.lock:
            queue, index = session.playback.queue, session.playback.index
            if session.playback.state == "idle":
                raise SessionFailure(409, "Playback is not active.")
            if index + 1 >= len(queue):
                session.playback = Playback.model_validate(
                    {**session.playback.model_dump(), "state": "idle", "index": 0,
                     "current_track_id": None,
                     # Advancing from a paused queue past the LAST track must
                     # clear the paused phase too — the idle state carrying
                     # paused_from violated the contract (500).
                     "paused_from": None})
                return session.playback, None
            previous = session.tracks[queue[index]]
            next_id = queue[index + 1]
            was_paused = session.playback.state == "paused"
            session.playback = Playback.model_validate(
                {**session.playback.model_dump(),
                 "state": "paused" if was_paused else "speaking",
                 "index": index + 1, "current_track_id": next_id,
                 # A paused advance stays paused on the NEW track, and the
                 # phase it would resume in is ALWAYS "speaking": the new
                 # track's DJ introduction comes before its music, even if
                 # the user paused during the PREVIOUS track's music.
                 # Preserving the old track's phase here made Resume land in
                 # "playing" and silently bypass the new track's
                 # introduction. The paused state MUST carry paused_from
                 # (contract validator).
                 "paused_from": "speaking" if was_paused else None})
        job = self._queue_dj_speech(session, next_id, previous, index + 1, len(session.playback.queue))
        return session.playback, job

    def set_phase(self, session, phase, track_id=None):
        """Record the transition speech -> music (or back) made by the player.

        The optional track_id makes the transition STALE-SAFE: a phase
        recorded for a track the user has already skipped past (an automatic
        speech-ended response arriving AFTER a Skip changed the current
        track) is rejected with 409 instead of silently flipping the NEW
        track's phase — otherwise a skipped track's speech phase could be
        consumed by the wrong track and the introduction would never play.
        """
        if phase not in ("speaking", "playing"):
            raise SessionFailure(422, "Playback phase must be speaking or playing.")
        with self.lock:
            if session.playback.state not in ("speaking", "playing"):
                raise SessionFailure(409, "No active playback to transition.")
            if track_id is not None and session.playback.current_track_id != track_id:
                raise SessionFailure(409, "The current track changed while playback was transitioning. Refresh and continue.")
            session.playback = Playback.model_validate({**session.playback.model_dump(), "state": phase})
            return session.playback

    def pause_playback(self, session, phase, track_id=None):
        if phase not in ("speaking", "playing"):
            raise SessionFailure(422, "Paused playback must record its phase as speaking or playing.")
        with self.lock:
            if session.playback.state not in ("speaking", "playing"):
                raise SessionFailure(409, "Playback is not active.")
            # The pause raced an automatic advance: the claimed phase belongs
            # to the OLD track. Preserve the pause intent (the user pressed
            # Pause) but record the phase that is true for the CURRENT track,
            # so Resume cannot resume the wrong phase of the new track.
            if track_id is not None and session.playback.current_track_id != track_id:
                phase = session.playback.state
            session.playback = Playback.model_validate(
                {**session.playback.model_dump(), "state": "paused", "paused_from": phase})
            return session.playback

    def resume_playback(self, session):
        with self.lock:
            if session.playback.state != "paused":
                raise SessionFailure(409, "Playback is not paused.")
            session.playback = Playback.model_validate(
                {**session.playback.model_dump(), "state": session.playback.paused_from, "paused_from": None})
            return session.playback

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

    def generate_dj_speech(self, session, job_id, providers):
        """One deliberate Qwen commentary -> Chatterbox default-voice speech.

        The spoken intro attaches to its OWN track (track.speech), so a job
        that completes after the user has skipped elsewhere can never play out
        of turn: the browser only plays the CURRENT track's speech. A failure
        is recorded on the job and the set continues without commentary.
        """
        with self.lock:
            job = session.jobs[job_id]
            job = job.transition(JobState.RUNNING, progress=.3)
            session.jobs[job_id] = job
            track = session.tracks[job.track_id]
            prompt = session.speech_prompts.get(job_id, "")
        try:
            if not prompt:
                raise ProviderFailure(SafeError(
                    code="generation_failed",
                    message="DJ commentary could not be started. The song plays without an introduction.",
                    retryable=False))
            text = providers.text(prompt)
            if not text.strip():
                raise ProviderFailure(SafeError(
                    code="generation_failed",
                    message="DJ commentary came back empty. The song plays without an introduction.",
                    retryable=False))
            audio = providers.speech(text)
            with self.lock:
                used = sum(len(media.content) for value in self.sessions.values() for media in value.media.values())
                if used + len(audio.content) > MAX_MEDIA_BYTES:
                    raise ProviderFailure(SafeError(
                        code="generation_failed", message="Session media capacity reached. The song plays without an introduction."))
                identifier = uuid4()
                reference = MediaRef(id=identifier, url=f"/api/media/{identifier}", content_type=audio.content_type)
                current = session.tracks[job.track_id]
                updated = Track.model_validate({**current.model_dump(), "speech": reference})
                session.media[identifier] = audio
                session.tracks[current.id] = updated
                session.jobs[job.id] = job.transition(JobState.SUCCEEDED)
                session.speech_prompts.pop(job_id, None)
        except Exception as exc:
            error = exc.error if isinstance(exc, ProviderFailure) else SafeError(
                code="internal_error",
                message="DJ commentary could not be generated. The song plays without an introduction.",
                retryable=True)
            with self.lock:
                session.jobs[job.id] = job.transition(JobState.FAILED, error=error)
        finally:
            with self.lock:
                session.active.discard((job.track_id, "speech"))
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
