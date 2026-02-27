"""
Playlist Controller

Handles playlist lifecycle operations:
- Creating a new playlist (regular or collaborative)
- Retrieving playlist details and listing user playlists
- Updating playlist metadata (name, visibility, cover image)
- Deleting a playlist

Sequence Diagrams Covered:
- Creating Playlist
- Edit Playlist Metadata

State Transitions (Creating Playlist):
  Idle -> Waiting (openCreate) -> Validating (createPlaylist)
    -> [!isValid] Error -> Idle
    -> [isValid] Creating -> Processing -> Final (playlist created)

State Transitions (Edit Playlist Metadata):
  Idle -> Editing
    -> Substates: Renaming, Visibility, CoverChange, Confirming
    -> [!isValid] Error
    -> [isValid] Saved -> Idle
"""

from uuid import UUID

from fastapi import APIRouter, Path, Query, status

from app.schemas.common import ErrorResponse, SuccessMessage
from app.schemas.playlist import (
    CreatePlaylistRequest,
    PlaylistListResponse,
    PlaylistResponse,
    UpdatePlaylistMetadataRequest,
)

router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.post(
    "",
    response_model=PlaylistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new playlist",
    responses={
        400: {"model": ErrorResponse, "description": "Validation error (e.g. invalid name)"},
    },
)
async def create_playlist(body: CreatePlaylistRequest):
    """
    Create a new playlist for the authenticated user.

    **Flow** (from sequence diagram — Creating Playlist):
    1. Validate the playlist name via `validateName()`.
    2. If invalid, return 400 with error details.
    3. If valid, create the playlist record via `createPlaylistRecord(name, type, owner_id)`.
    4. If the playlist type is `collaborative`, automatically generate an invite link
       via `generateInviteLink()`.
    5. Return the created playlist with metadata and optional invite link.

    **State Transition:** Idle → Validating → Creating → Processing → Created
    """
    ...


@router.get(
    "",
    response_model=PlaylistListResponse,
    summary="List playlists for the authenticated user",
)
async def list_playlists(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Retrieve a paginated list of playlists owned by or shared with the authenticated user.

    Results include both owned playlists and playlists where the user is a collaborator.
    """
    ...


@router.get(
    "/{playlist_id}",
    response_model=PlaylistResponse,
    summary="Get playlist details",
    responses={
        404: {"model": ErrorResponse, "description": "Playlist not found"},
    },
)
async def get_playlist(
    playlist_id: UUID = Path(..., description="ID of the playlist to retrieve"),
):
    """
    Retrieve full details of a single playlist.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    - Corresponds to `getPlaylistMetadata()` followed by `renderInitialView()`.
    - Returns current name, visibility, cover image, track count, and owner info.
    """
    ...


@router.patch(
    "/{playlist_id}",
    response_model=PlaylistResponse,
    summary="Update playlist metadata",
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        404: {"model": ErrorResponse, "description": "Playlist not found"},
    },
)
async def update_playlist_metadata(
    body: UpdatePlaylistMetadataRequest,
    playlist_id: UUID = Path(..., description="ID of the playlist to update"),
):
    """
    Update the metadata of an existing playlist.

    Supports partial updates — only provided fields are changed. Omitted fields remain unchanged.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    1. User updates name (`enterPlaylistName`), visibility (`selectVisibility`),
       and/or cover image (`selectPlaylistCover`).
    2. On `confirmUpdate()`, the controller calls `updatePlaylist(name, cover, visibility)`.
    3. The database validates and persists the changes.
    4. If invalid, return 400 error. If valid, return the updated playlist.

    **State Transition:** Editing → Confirming → [isValid] Saved / [!isValid] Error
    """
    ...


@router.delete(
    "/{playlist_id}",
    response_model=SuccessMessage,
    summary="Delete a playlist",
    responses={
        404: {"model": ErrorResponse, "description": "Playlist not found"},
    },
)
async def delete_playlist(
    playlist_id: UUID = Path(..., description="ID of the playlist to delete"),
):
    """
    Permanently delete a playlist.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    1. `deletePlaylist()` triggers `processDeletion()` on the controller.
    2. Controller sends `isDeletionConfirmed()` — the client must have confirmed.
    3. On confirmation, calls `deletePlaylist()` on the database.
    4. Returns success and the UI navigates back to playlist list via `showPlaylistUI()`.

    Only the playlist owner can delete a playlist.
    """
    ...
