from pydantic import BaseModel
from uuid import UUID


class ShareLinkResponse(BaseModel):
    share_url: str
    playlist_id: UUID
    playlist_name: str


class ShareMenuResponse(BaseModel):
    playlist_id: UUID
    playlist_name: str
    cover_image_url: str | None = None
    track_count: int
    share_url: str
