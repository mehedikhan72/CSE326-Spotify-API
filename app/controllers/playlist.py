"""
Playlist Controller

Handles playlist lifecycle operations:
- Creating a new playlist for the current user
- Retrieving playlist details and listing user playlists
- Changing playlist details (name, public/private, collaborative, description)
- Deleting a playlist (unfollowing)

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

from fastapi import APIRouter, Path, Query, Response, status

from app.schemas.common import SpotifyError
from app.schemas.playlist import (
    CreatePlaylistRequest,
    PlaylistListResponse,
    PlaylistResponse,
    UpdatePlaylistDetailsRequest,
)

router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.post(
    "",
    response_model=PlaylistResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def create_playlist(body: CreatePlaylistRequest):
    """
    Create a playlist for the current user.

    The playlist will be empty until you add tracks.

    **Flow** (from sequence diagram — Creating Playlist):
    1. Validate the playlist name via `validateName()`.
    2. If invalid, return error.
    3. If valid, create the playlist record via `createPlaylistRecord(name, type, owner_id)`.
    4. If `collaborative` is true (and `public` is false), automatically generate an invite link
       via `generateInviteLink()`.
    5. Return the created playlist object.

    **State Transition:** Idle → Validating → Creating → Processing → Created

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`
    """
    ...


@router.get(
    "",
    response_model=PlaylistListResponse,
    summary="Get current user's playlists",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def get_current_user_playlists(
    limit: int = Query(20, ge=1, le=50, description="The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50."),
    offset: int = Query(0, ge=0, description="The index of the first item to return. Default: 0 (the first item)."),
):
    """
    Get a list of the playlists owned or followed by the current user.

    Results include both owned playlists and playlists where the user is a collaborator.

    **Required scope:** `playlist-read-private`
    """
    ...


@router.get(
    "/{playlist_id}",
    response_model=PlaylistResponse,
    summary="Get playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def get_playlist(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
    fields: str | None = Query(None, description="Filters for the query: a comma-separated list of the fields to return"),
):
    """
    Get a playlist owned by a Spotify user.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    - Corresponds to `getPlaylistMetadata()` followed by `renderInitialView()`.
    - Returns current name, description, public/collaborative status, images, and owner info.
    """
    ...


@router.put(
    "/{playlist_id}",
    status_code=status.HTTP_200_OK,
    summary="Change playlist details",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def change_playlist_details(
    body: UpdatePlaylistDetailsRequest,
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Change a playlist's name, public/private state, collaborative status, and/or description.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    1. User updates name (`enterPlaylistName`), visibility (`selectVisibility`),
       and/or cover (`selectPlaylistCover`).
    2. On `confirmUpdate()`, the controller calls `updatePlaylist(name, cover, visibility)`.
    3. The database validates and persists the changes.
    4. Returns empty body on success.

    **State Transition:** Editing → Confirming → [isValid] Saved / [!isValid] Error

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`
    """
    ...


@router.delete(
    "/{playlist_id}/followers",
    status_code=status.HTTP_200_OK,
    summary="Unfollow playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def unfollow_playlist(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Remove the current user as a follower of a playlist.
    For the owner, this effectively deletes the playlist.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    1. `deletePlaylist()` triggers `processDeletion()` on the controller.
    2. Controller sends `isDeletionConfirmed()` — the client must have confirmed.
    3. On confirmation, calls `deletePlaylist()` on the database.
    4. Returns success and the UI navigates back to playlist list via `showPlaylistUI()`.

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`
    """
    ...
