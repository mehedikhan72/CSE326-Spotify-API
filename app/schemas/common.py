from pydantic import BaseModel


class SpotifyErrorBody(BaseModel):
    status: int
    message: str


class SpotifyError(BaseModel):
    error: SpotifyErrorBody


class SnapshotResponse(BaseModel):
    snapshot_id: str


class CursorPaginationMixin(BaseModel):
    href: str
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int
