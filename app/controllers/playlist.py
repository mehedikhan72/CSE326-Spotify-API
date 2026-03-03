"""
Playlist Controller

Handles playlist lifecycle operations:
- Creating a new playlist for the current user
- Retrieving playlist details and listing user playlists
- Sorting playlist tracks by title, artist, album, date added, or duration
- Changing playlist details (name, public/private, collaborative, description)
- Deleting a playlist (unfollowing)

Sequence Diagrams Covered:
- Creating Playlist
- Edit Playlist Metadata
- Sort Playlist Tracks

State Transitions (Creating Playlist):
  Idle -> Waiting (openCreate) -> Validating (createPlaylist)
    -> [!isValid] Error -> Idle
    -> [isValid] Creating -> Processing -> Final (playlist created)

State Transitions (Edit Playlist Metadata):
  Idle -> Editing
    -> Substates: Renaming, Visibility, CoverChange, Confirming
    -> [!isValid] Error
    -> [isValid] Saved -> Idle

State Transitions (Sort Playlist Tracks):
  Idle -> Sorting (sortBy) -> Processing -> Sorted -> Idle
"""

from fastapi import APIRouter, Path, Query, Response, status

from app.schemas.common import SnapshotResponse, SpotifyError
from app.schemas.playlist import (
    CreatePlaylistRequest,
    PlaylistListResponse,
    PlaylistResponse,
    SortPlaylistRequest,
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

    **Response** (`PlaylistResponse`):
    - `id`: Unique Spotify ID of the new playlist
    - `name`: Display name
    - `description`: Optional user-set description
    - `public`: Whether the playlist is publicly visible
    - `collaborative`: Whether other users can modify it
    - `snapshot_id`: Version identifier; changes on every modification
    - `href`: API URL for the full playlist object
    - `uri`: Spotify URI (e.g. `spotify:playlist:...`)
    - `external_urls`: Map of service name → external web URL
    - `owner`: Object containing `id`, `display_name`, `href`, `external_urls`
    - `images`: List of cover images, each with `url`, `height`, `width`
    - `tracks`: Paginated sub-object with `href` and `total`
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
    limit: int = Query(
        20,
        ge=1,
        le=50,
        description="The maximum number of items to return. Default: 20. Minimum: 1. Maximum: 50.",
    ),
    offset: int = Query(
        0,
        ge=0,
        description="The index of the first item to return. Default: 0 (the first item).",
    ),
):
    """
    Get a list of the playlists owned or followed by the current user.

    Results include both owned playlists and playlists where the user is a collaborator.

    **Required scope:** `playlist-read-private`

    **Response** (`PlaylistListResponse`):
    - `href`: API URL for this result set
    - `limit`: Max items returned per page
    - `next`: URL for the next page; `null` if on the last page
    - `offset`: Starting index of this page
    - `previous`: URL for the previous page; `null` if on the first page
    - `total`: Total number of playlists the user owns or follows
    - `items`: Array of `PlaylistResponse` objects (see `create_playlist` for field details)
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
    fields: str | None = Query(
        None,
        description="Filters for the query: a comma-separated list of the fields to return",
    ),
):
    """
    Get a playlist owned by a Spotify user.

    **Flow** (from sequence diagram — Edit Playlist Metadata):
    - Corresponds to `getPlaylistMetadata()` followed by `renderInitialView()`.
    - Returns current name, description, public/collaborative status, images, and owner info.

    **Response** (`PlaylistResponse`):
    - `id`: Spotify ID of the playlist
    - `name`: Current display name
    - `description`: Current description, or `null`
    - `public`: Visibility status
    - `collaborative`: Whether collaborative editing is enabled
    - `snapshot_id`: Current version identifier
    - `href` / `uri` / `external_urls`: Addressing fields
    - `owner`: Owner's `id`, `display_name`, `href`, `external_urls`
    - `images`: Cover image list with `url`, `height`, `width`
    - `tracks`: Paginated sub-object with `href` and `total`
    """
    ...


@router.post(
    "/{playlist_id}/sort",
    response_model=SnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Sort playlist tracks",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def sort_playlist_tracks(
    body: SortPlaylistRequest,
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Sort playlist tracks by specified criteria.

    **Sorting Options:**
    - **title**: Sort by track name alphabetically
    - **artist**: Sort by primary artist name alphabetically
    - **album**: Sort by album name alphabetically
    - **recently_added**: Sort by date added to playlist (newest or oldest first)
    - **duration**: Sort by track duration (shortest or longest first)

    **Sort Order:**
    - **asc**: Ascending order (A-Z, oldest-newest, shortest-longest)
    - **desc**: Descending order (Z-A, newest-oldest, longest-shortest)

    **Flow:**
    1. Fetch all tracks from the playlist via `getPlaylistTracks()`.
    2. Sort tracks based on the specified field and order via `sortTracks(field, order)`.
    3. Reorder tracks in the playlist via `reorderPlaylistTracks()`.
    4. Return a new snapshot_id indicating the playlist state has changed.

    **State Transition:** Idle → Sorting → Processing → Sorted → Idle

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`

    **Note:** This operation reorders the tracks in place. The original order cannot be restored
    unless you manually reorder or have a backup of the original sequence.

    **Response** (`SnapshotResponse`):
    - `snapshot_id`: New version identifier of the playlist reflecting the sorted order
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

    **Response:** Empty body on success (HTTP 200).
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

    **Response:** Empty body on success (HTTP 200).
    """
    ...
