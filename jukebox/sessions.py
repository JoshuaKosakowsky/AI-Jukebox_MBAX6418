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
MAX_ACTIVE_SPEECH = 2
MAX_QUEUE = MAX_TRACKS
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
    if not 1 <= sample_rate <= 384_000 or bits not in (8, 16, 24, 32):
        raise SessionFailure(422, "The WAV reference could not be read.")
    # PCM alignment must be internally coherent; the header is not allowed to
    # under- or over-state the real byte/packet rates (a forged byte_rate field
    # must not shift the duration calculation).
    if byte_rate != sample_rate * channels * bits // 8 or block_align != channels * bits // 8:
        raise SessionFailure(422, "The WAV reference has an inconsistent audio header.")
    if data_size < 1:
        raise SessionFailure(422, "The WAV reference contains no audio data.")
    if data_offset + data_size > len(content):
        raise SessionFailure(422, "The WAV reference is truncated.")
    # Duration from the physical frame count, per the coherent header.
    frames = data_size // block_align
    duration = frames / sample_rate
    if not MIN_REFERENCE_SECONDS <= duration <= MAX_REFERENCE_SECONDS:
        raise SessionFailure(
            422, f"Reference audio must be {MIN_REFERENCE_SECONDS}-{MAX_REFERENCE_SECONDS} seconds.")


# MPEG audio frame tables (bitrate in kbps), keyed by [version_group][layer]
# where version_group 3 = MPEG-1 and 2 = MPEG-2/-2.5, layer 1 = III, 2 = II,
# 3 = I. Index 0 = free/bad and 15 = bad are rejected by the length lookup.
_MPEG_BITRATES = {
    1: {1: (0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320),
         2: (0, 32, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 384),
         3: (0, 32, 64, 96, 128, 160, 192, 224, 256, 288, 320, 352, 384, 416, 448)},
    2: {1: (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160),
         2: (0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160),
         3: (0, 32, 48, 56, 64, 80, 96, 112, 128, 144, 160, 176, 192, 224, 256)},
}
_MPEG_SAMPLE_RATES = {3: (44100, 48000, 32000), 2: (22050, 24000, 16000), 0: (11025, 12000, 8000)}


def _mpeg_frame_length(header: bytes) -> int | None:
    """Return the exact byte length of the MPEG frame starting at `header`.

    None means the four header bytes do not describe a decodable frame
    (invalid sync/version/layer, free or reserved bitrate, reserved sample
    rate). The caller must also verify that the whole frame is present.
    """
    if len(header) < 4 or header[0] != 0xFF or (header[1] & 0xE0) != 0xE0:
        return None
    version = (header[1] >> 3) & 3      # 3 = MPEG-1, 2 = MPEG-2, 0 = MPEG-2.5
    layer = (header[1] >> 1) & 3        # 1 = Layer III, 2 = Layer II, 3 = Layer I
    if version == 1 or layer == 0:
        return None
    bitrate_index = header[2] >> 4
    sample_index = (header[2] >> 2) & 3
    if bitrate_index in (0, 15) or sample_index == 3:
        return None
    version_group = 1 if version == 3 else 2
    kbps = _MPEG_BITRATES[version_group][layer][bitrate_index]
    sample_rate = _MPEG_SAMPLE_RATES[version][sample_index]
    padding = (header[2] >> 1) & 1
    if layer == 3:  # Layer I
        return (12 * kbps * 1000 // sample_rate + padding) * 4
    if version_group == 1:  # MPEG-1 Layer II/III
        return 144 * kbps * 1000 // sample_rate + padding
    return 72 * kbps * 1000 // sample_rate + padding  # MPEG-2/-2.5 Layer II/III


def _validate_mp3_structure(content: bytes, *, id3: bool) -> None:
    """Require a parseable ID3v2 tag and at least one COMPLETE MPEG frame.

    A frame only counts when its position has a decodable header AND the
    header's computed frame length is entirely present in the upload -
    partial sync bytes never pass.
    """
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
    for index in range(skip, max(skip, len(content) - 3)):
        frame_length = _mpeg_frame_length(content[index : index + 4])
        if frame_length is not None and index + frame_length <= len(content):
            return
    raise SessionFailure(422, "The MP3 reference contains no playable audio frames.")
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

    def __init__(self, sample_library=()):
        self.sample_library = tuple(sample_library)
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
                if self._media_bytes() > MAX_MEDIA_BYTES or len(self.sample_library) > MAX_TRACKS:
                    raise SessionFailure(429, "Session media capacity reached. Try again after another session expires.", retryable=True)
                session = Session()
                for sample in self.sample_library:
                    audio_id, cover_id = uuid4(), uuid4()
                    audio = MediaRef(id=audio_id, url=f"/api/media/{audio_id}", content_type=sample.audio.content_type)
                    cover = MediaRef(id=cover_id, url=f"/api/media/{cover_id}", content_type=sample.cover.content_type)
                    track = Track.model_validate({**sample.track.model_dump(), "audio": audio, "cover": cover})
                    session.tracks[track.id] = track
                    session.media[audio_id] = sample.audio
                    session.media[cover_id] = sample.cover
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

    def _media_bytes(self):
        # Catalog bytes are immutable and shared between sessions. Count them
        # once, including samples replaced in every session but retained for new ones.
        media = [item for sample in self.sample_library for item in (sample.audio, sample.cover)]
        media.extend(item for session in self.sessions.values() for item in session.media.values())
        return sum({id(item.content): len(item.content) for item in media}.values())

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
                used = self._media_bytes()
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
            # DJ speech needs the final introduction within the small output
            # budget, rather than spending that budget on model reasoning.
            text = providers.text(prompt, thinking=False)
            if not text.strip():
                raise ProviderFailure(SafeError(
                    code="generation_failed",
                    message="DJ commentary came back empty. The song plays without an introduction.",
                    retryable=False))
            audio = providers.speech(text)
            with self.lock:
                used = self._media_bytes()
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
                used = self._media_bytes()
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
