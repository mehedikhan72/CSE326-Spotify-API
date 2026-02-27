from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID


class TrackResponse(BaseModel):
    id: UUID
    title: str
    artist: str
    album: str | None = None
    duration_ms: int
    cover_image_url: str | None = None


class PlaylistTrackResponse(BaseModel):
    id: UUID
    track: TrackResponse
    position: int
    added_by: UUID
    added_at: datetime


# --- Add Track to Playlist ---

class AddTrackToPlaylistRequest(BaseModel):
    track_id: UUID = Field(..., description="ID of the track to add")


class AddTrackToPlaylistResponse(BaseModel):
    message: str
    playlist_track: PlaylistTrackResponse


# --- Reorder Tracks ---

class ReorderTracksRequest(BaseModel):
    track_positions: list[dict] = Field(
        ...,
        description="List of {track_id, new_position} mappings representing the new order",
        examples=[[{"track_id": "uuid-1", "new_position": 0}, {"track_id": "uuid-2", "new_position": 1}]],
    )


class ReorderTracksResponse(BaseModel):
    message: str
    tracks: list[PlaylistTrackResponse]


# --- Remove Track ---

class RemoveTrackResponse(BaseModel):
    message: str


# --- Playlist Tracks List ---

class PlaylistTracksListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[PlaylistTrackResponse]
