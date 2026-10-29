"""Version 1 application objects shared by the server and browser clients."""
from datetime import datetime, timezone
from enum import StrEnum
import json
from pathlib import Path
from typing import Literal
from uuid import UUID, uuid4

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)


class SafeError(Model):
    code: Literal["not_configured", "timeout", "unavailable", "rate_limited", "rejected", "invalid_response", "generation_failed", "internal_error"]
    message: str
    retryable: bool = False


class SongSettings(Model):
    style: str = Field(min_length=1, max_length=120)
    mood: str = Field(min_length=1, max_length=120)
    duration_seconds: int = Field(ge=10, le=600)
    mode: Literal["instrumental", "vocal"] = "instrumental"


class MediaRef(Model):
    id: UUID = Field(default_factory=uuid4, description="Unique across all track media references in the session")
    url: str = Field(pattern=r"^/api/media/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
    content_type: Literal["audio/wav", "audio/mpeg", "image/png"]

    @model_validator(mode="after")
    def matching_id(self):
        if self.url != f"/api/media/{self.id}":
            raise ValueError("Media ID and local URL must match")
        return self


class Track(Model):
    id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1, max_length=120)
    settings: SongSettings
    created_at: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: Literal["generating", "ready", "failed"] = "generating"
    audio: MediaRef | None = None
    cover: MediaRef | None = None
    lyrics: str | None = None
    dj_text: str | None = None
    speech: MediaRef | None = None

    @model_validator(mode="after")
    def audio_readiness(self):
        if self.status == "ready" and self.audio is None:
            raise ValueError("A ready track needs audio")
        if self.audio and not self.audio.content_type.startswith("audio/"):
            raise ValueError("Track audio must be audio")
        if self.cover and self.cover.content_type != "image/png":
            raise ValueError("Track cover must be an image")
        if self.speech and not self.speech.content_type.startswith("audio/"):
            raise ValueError("Track speech must be audio")
        return self


class JobState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"


class GenerationJob(Model):
    id: UUID = Field(default_factory=uuid4)
    track_id: UUID
    kind: Literal["text", "art", "music", "speech"]
    state: JobState = JobState.QUEUED
    progress: float = Field(default=0, ge=0, le=1)
    error: SafeError | None = None

    @model_validator(mode="after")
    def valid_outcome(self):
        if (self.state == JobState.FAILED) != (self.error is not None):
            raise ValueError("Only a failed job has an error, and it must have one")
        if self.state == JobState.SUCCEEDED and self.progress != 1:
            raise ValueError("Succeeded progress must equal one")
        return self

    def transition(self, state: JobState, *, progress=None, error=None):
        allowed = {JobState.QUEUED: {JobState.RUNNING, JobState.FAILED},
                   JobState.RUNNING: {JobState.SUCCEEDED, JobState.FAILED},
                   JobState.SUCCEEDED: set(), JobState.FAILED: set()}
        if state not in allowed[self.state]:
            raise ValueError("Invalid job transition")
        value = 1 if state == JobState.SUCCEEDED else self.progress if progress is None else progress
        if value < self.progress:
            raise ValueError("Progress cannot go backwards")
        return self.model_validate({**self.model_dump(), "state": state, "progress": value, "error": error})


class Playback(Model):
    state: Literal["idle", "speaking", "playing", "paused"] = "idle"
    queue: list[UUID] = Field(default_factory=list)
    index: int = Field(default=0, ge=0)
    current_track_id: UUID | None = None
    paused_from: Literal["speaking", "playing"] | None = None

    @model_validator(mode="after")
    def valid_position(self):
        if self.state != "idle":
            if self.index >= len(self.queue) or self.current_track_id != self.queue[self.index]:
                raise ValueError("Active playback must reference the current queue entry")
        elif self.current_track_id is not None:
            raise ValueError("Idle playback has no active track")
        if (self.state == "paused") != (self.paused_from is not None):
            raise ValueError("Only paused playback records its previous phase")
        return self


class SessionSnapshot(Model):
    contract_version: Literal[1] = 1
    tracks: list[Track] = Field(default_factory=list)
    jobs: list[GenerationJob] = Field(default_factory=list)
    playback: Playback = Field(default_factory=Playback)

    @model_validator(mode="after")
    def references_exist(self):
        tracks = {track.id for track in self.tracks}
        if len(tracks) != len(self.tracks) or len({job.id for job in self.jobs}) != len(self.jobs):
            raise ValueError("IDs must be unique")
        if any(job.track_id not in tracks for job in self.jobs) or any(track not in tracks for track in self.playback.queue):
            raise ValueError("Jobs and queue entries must reference session tracks")
        media = [asset.id for track in self.tracks for asset in (track.audio, track.cover, track.speech) if asset is not None]
        if len(media) != len(set(media)):
            raise ValueError("Media IDs must be unique across session tracks and roles")
        return self


def schema():
    return SessionSnapshot.model_json_schema()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Export the shared version 1 JSON Schema")
    parser.add_argument("--write", type=Path, required=True)
    args = parser.parse_args()
    args.write.write_text(json.dumps(schema(), indent=2) + "\n", encoding="utf-8", newline="\n")
