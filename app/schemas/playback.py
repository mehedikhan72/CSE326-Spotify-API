from pydantic import BaseModel, Field

from app.schemas.track import TrackObject


class DeviceObject(BaseModel):
    id: str | None = None
    is_active: bool = False
    name: str = ""
    type: str = ""
    volume_percent: int | None = None


class ContextObject(BaseModel):
    type: str
    href: str
    uri: str
    external_urls: dict[str, str] = {}


class ActionsObject(BaseModel):
    interrupting_playback: bool = False
    pausing: bool = False
    resuming: bool = False
    seeking: bool = False
    skipping_next: bool = False
    skipping_prev: bool = False
    toggling_repeat_context: bool = False
    toggling_shuffle: bool = False
    toggling_repeat_track: bool = False
    transferring_playback: bool = False


class PlaybackStateResponse(BaseModel):
    device: DeviceObject | None = None
    repeat_state: str = "off"
    shuffle_state: bool = False
    context: ContextObject | None = None
    timestamp: int = 0
    progress_ms: int | None = None
    is_playing: bool = False
    item: TrackObject | None = None
    currently_playing_type: str = "track"
    actions: ActionsObject = ActionsObject()


class StartPlaybackRequest(BaseModel):
    context_uri: str | None = Field(
        None,
        description="Spotify URI of the context to play (album, artist, playlist). E.g. spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",
    )
    uris: list[str] | None = Field(
        None,
        description="A list of Spotify track URIs to play",
    )
    offset: dict | None = Field(
        None,
        description="Indicates from where in the context playback should start. "
        'E.g. {"position": 5} or {"uri": "spotify:track:..."}',
    )
    position_ms: int | None = Field(None, ge=0, description="Position in milliseconds to seek to")


class SeekRequest(BaseModel):
    position_ms: int = Field(..., ge=0, description="The position in milliseconds to seek to")
