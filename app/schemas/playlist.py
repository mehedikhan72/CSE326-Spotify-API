from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID


class PlaylistType(str, Enum):
    REGULAR = "regular"
    COLLABORATIVE = "collaborative"


class PlaylistVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"


# --- Create Playlist ---

class CreatePlaylistRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Name of the playlist")
    type: PlaylistType = Field(..., description="Type of playlist: regular or collaborative")


class PlaylistResponse(BaseModel):
    id: UUID
    name: str
    type: PlaylistType
    visibility: PlaylistVisibility
    cover_image_url: str | None = None
    owner_id: UUID
    invite_link: str | None = None
    track_count: int = 0
    created_at: datetime
    updated_at: datetime


# --- Update Playlist Metadata ---

class UpdatePlaylistMetadataRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100, description="Updated playlist name")
    visibility: PlaylistVisibility | None = Field(None, description="Updated visibility setting")
    cover_image_url: str | None = Field(None, description="Updated cover image URL")


# --- Playlist List ---

class PlaylistSummary(BaseModel):
    id: UUID
    name: str
    type: PlaylistType
    visibility: PlaylistVisibility
    cover_image_url: str | None = None
    track_count: int
    owner_id: UUID
    created_at: datetime


class PlaylistListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[PlaylistSummary]
