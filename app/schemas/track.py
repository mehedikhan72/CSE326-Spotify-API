from pydantic import BaseModel, Field
from datetime import datetime

from app.schemas.playlist import ImageObject


class ArtistObject(BaseModel):
    id: str
    name: str
    href: str
    uri: str
    external_urls: dict[str, str] = {}


class AlbumObject(BaseModel):
    id: str
    name: str
    href: str
    uri: str
    images: list[ImageObject] = []
    release_date: str | None = None
    external_urls: dict[str, str] = {}


class TrackObject(BaseModel):
    id: str
    name: str
    href: str
    uri: str
    duration_ms: int
    artists: list[ArtistObject] = []
    album: AlbumObject | None = None
    external_urls: dict[str, str] = {}
    is_local: bool = False


class PlaylistTrackObject(BaseModel):
    added_at: datetime | None = None
    added_by: dict | None = None
    is_local: bool = False
    track: TrackObject


class AddedByObject(BaseModel):
    id: str
    href: str
    external_urls: dict[str, str] = {}


# --- Add Items to Playlist ---

class AddItemsRequest(BaseModel):
    uris: list[str] = Field(
        ...,
        max_length=100,
        description="A list of Spotify URIs to add (max 100). E.g. spotify:track:4iV5W9uYEdYUVa79Axb7Rh",
    )
    position: int | None = Field(None, ge=0, description="Zero-based position to insert the items. If omitted, items are appended.")


# --- Reorder / Replace Playlist Items ---

class ReorderItemsRequest(BaseModel):
    range_start: int = Field(..., ge=0, description="The position of the first item to be reordered")
    insert_before: int = Field(..., ge=0, description="The position where the items should be inserted")
    range_length: int = Field(1, ge=1, description="The number of items to be reordered (default: 1)")
    snapshot_id: str | None = Field(None, description="The playlist's snapshot ID against which you want to make the changes")


# --- Remove Items from Playlist ---

class TrackUri(BaseModel):
    uri: str = Field(..., description="Spotify URI. E.g. spotify:track:4iV5W9uYEdYUVa79Axb7Rh")


class RemoveItemsRequest(BaseModel):
    tracks: list[TrackUri] = Field(..., max_length=100, description="An array of objects containing Spotify URIs (max 100)")
    snapshot_id: str | None = Field(None, description="The playlist's snapshot ID against which you want to make the changes")


# --- Playlist Items List ---

class PlaylistItemsResponse(BaseModel):
    href: str
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int
    items: list[PlaylistTrackObject]
