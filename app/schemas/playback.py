from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID

from app.schemas.track import TrackResponse


class PlaybackState(str, Enum):
    IDLE = "idle"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    ERROR = "error"


class PlaybackStatusResponse(BaseModel):
    state: PlaybackState
    current_track: TrackResponse | None = None
    position_ms: int = 0
    duration_ms: int = 0
    playlist_id: UUID | None = None


class PlayRequest(BaseModel):
    track_id: UUID = Field(..., description="ID of the track to play")
    playlist_id: UUID = Field(..., description="ID of the playlist context")


class SeekRequest(BaseModel):
    position_ms: int = Field(..., ge=0, description="Position to seek to in milliseconds")


class PlayNextResponse(BaseModel):
    message: str
    playback: PlaybackStatusResponse
