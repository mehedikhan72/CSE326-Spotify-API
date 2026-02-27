from pydantic import BaseModel

from app.schemas.playlist import ImageObject


class ShareLinkResponse(BaseModel):
    share_url: str
    playlist_id: str
    playlist_name: str


class ShareMenuResponse(BaseModel):
    playlist_id: str
    playlist_name: str
    images: list[ImageObject] = []
    track_count: int
    share_url: str
