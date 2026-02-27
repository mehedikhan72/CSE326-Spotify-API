from pydantic import BaseModel, Field


class ImageObject(BaseModel):
    url: str
    height: int | None = None
    width: int | None = None


class OwnerObject(BaseModel):
    id: str
    display_name: str
    href: str
    external_urls: dict[str, str] = {}


# --- Create Playlist ---

class CreatePlaylistRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="The name for the new playlist")
    public: bool = Field(True, description="If true the playlist will be public, if false it will be private")
    collaborative: bool = Field(
        False,
        description="If true, the playlist will be collaborative. "
        "Note: to create a collaborative playlist you must also set public to false.",
    )
    description: str | None = Field(None, max_length=300, description="Playlist description as displayed in Spotify Clients")


class PlaylistResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    public: bool
    collaborative: bool
    snapshot_id: str
    href: str
    uri: str
    external_urls: dict[str, str] = {}
    owner: OwnerObject
    images: list[ImageObject] = []
    tracks: dict = Field(default_factory=dict, description="Tracks pagination object")


# --- Update Playlist Details ---

class UpdatePlaylistDetailsRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100, description="The new name for the playlist")
    public: bool | None = Field(None, description="If true the playlist will be public, if false it will be private")
    collaborative: bool | None = Field(None, description="If true, other users can modify the playlist")
    description: str | None = Field(None, max_length=300, description="New playlist description")


# --- Playlist List ---

class PlaylistListResponse(BaseModel):
    href: str
    limit: int
    next: str | None = None
    offset: int
    previous: str | None = None
    total: int
    items: list[PlaylistResponse]
