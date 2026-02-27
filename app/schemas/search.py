from pydantic import BaseModel
from enum import Enum

from app.schemas.track import TrackObject


class SearchType(str, Enum):
    TRACK = "track"
    ARTIST = "artist"
    ALBUM = "album"


class TracksPage(BaseModel):
    href: str
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int
    items: list[TrackObject]


class SearchResponse(BaseModel):
    tracks: TracksPage | None = None


class SuggestedTracksResponse(BaseModel):
    tracks: list[TrackObject]
