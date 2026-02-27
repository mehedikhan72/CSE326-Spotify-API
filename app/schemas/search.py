from pydantic import BaseModel, Field
from enum import Enum
from uuid import UUID

from app.schemas.track import TrackResponse


class SearchFilterType(str, Enum):
    ALL = "all"
    TITLE = "title"
    ARTIST = "artist"
    ALBUM = "album"


class SearchTracksResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    query: str
    filter: SearchFilterType
    items: list[TrackResponse]


class SuggestedTracksResponse(BaseModel):
    items: list[TrackResponse]
