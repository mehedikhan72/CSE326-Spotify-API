"""
Track Management Controller

Handles track operations within a playlist:
- Searching tracks (with keyword and type filter)
- Getting suggested tracks (recommendations)
- Adding items to a playlist (with duplicate check)
- Reordering items in a playlist
- Removing items from a playlist
- Listing playlist items

Sequence Diagrams Covered:
- Search and Add Track to Playlist
- Reorder or Remove Tracks

State Transitions (Search & Add Track):
  Idle -> Searching (enterKeyword)
    -> [hasResults] Results
    -> [!hasResults] Empty -> Idle (modifyQuery)
    -> [error] Failure -> Idle (retry)
  Results -> Validating (selectTrack)
    -> [!isDuplicate] Adding -> Results (addSuccess/showConfirmation)
    -> [isDuplicate] Duplicate -> Results (dismissWarning)

State Transitions (Reorder/Remove):
  Idle -> Reordering (dragAndDropReorder) [loop] -> Saving -> Idle
  Idle -> Removing -> Confirming -> Removed -> Idle
"""

from fastapi import APIRouter, Path, Query, status

from app.schemas.common import SnapshotResponse, SpotifyError
from app.schemas.search import SearchResponse, SuggestedTracksResponse
from app.schemas.track import (
    AddItemsRequest,
    PlaylistItemsResponse,
    RemoveItemsRequest,
    ReorderItemsRequest,
)

router = APIRouter(tags=["Tracks"])


# --- Search ---

@router.get(
    "/search",
    response_model=SearchResponse,
    tags=["Search"],
    summary="Search for item",
    responses={
        400: {"model": SpotifyError, "description": "Bad request"},
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def search_for_item(
    q: str = Query(..., min_length=1, description="Your search query. You can narrow results using field filters: artist, album, track."),
    type: str = Query(..., description="A comma-separated list of item types to search across. Valid types: track, artist, album."),
    limit: int = Query(20, ge=1, le=50, description="Maximum number of results to return. Default: 20. Maximum: 50."),
    offset: int = Query(0, ge=0, le=1000, description="The index of the first result to return. Default: 0. Maximum: 1000."),
):
    """
    Get Spotify catalog information about albums, artists, or tracks that match a keyword string.

    **Flow** (from sequence diagram — Search and Add Track to Playlist):
    1. User enters a keyword via `enterKeyword()`.
    2. Controller calls `searchViaKeyword()` → `getTracksViaQuery()` on TrackDB.
    3. Returns matching tracks.

    **Filtering** (from sequence diagram — chooseFilter/applyFilter):
    - The `q` parameter supports field filters like `artist:Coldplay` or `album:Parachutes`.
    - The `type` parameter controls which result sets are returned.

    **State Transition:** Idle → Searching → Results / Empty / Failure

    **Response** (`SearchResponse`):
    - `tracks`: Paginated result set containing:
      - `href`: API URL for this result page
      - `limit` / `offset` / `next` / `previous` / `total`: Pagination fields
      - `items`: List of `TrackObject` — each has `id`, `name`, `uri`, `duration_ms`,
        `artists` (list of `{id, name, href, uri}`), `album` (`{id, name, images, release_date}`),
        `href`, `external_urls`, `is_local`
    """
    ...


@router.get(
    "/playlists/{playlist_id}/recommendations",
    response_model=SuggestedTracksResponse,
    tags=["Search"],
    summary="Get recommended tracks for a playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
    },
)
async def get_recommended_tracks(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
    limit: int = Query(20, ge=1, le=100, description="The maximum number of recommendations to return"),
):
    """
    Get track recommendations based on the playlist's existing songs.

    **Flow** (from sequence diagram — Search and Add Track to Playlist):
    1. On page load, controller calls `getExistingSongs()` from PlaylistDB.
    2. Uses existing songs to call `getSuggestedTracks()` from TrackDB.
    3. Returns suggested tracks before the user types any search query.

    **Response** (`SuggestedTracksResponse`):
    - `tracks`: Flat list of recommended `TrackObject` items — each has `id`, `name`, `uri`,
      `duration_ms`, `artists`, `album`, `href`, `external_urls`, `is_local`
    """
    ...


# --- Playlist Items CRUD ---

@router.get(
    "/playlists/{playlist_id}/tracks",
    response_model=PlaylistItemsResponse,
    tags=["Tracks"],
    summary="Get playlist items",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
    },
)
async def get_playlist_items(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
    limit: int = Query(20, ge=1, le=50, description="The maximum number of items to return. Default: 20. Maximum: 50."),
    offset: int = Query(0, ge=0, description="The index of the first item to return. Default: 0."),
    fields: str | None = Query(None, description="Filters for the query: a comma-separated list of the fields to return"),
):
    """
    Get full details of the items of a playlist owned by a Spotify user.

    **Flow** (from sequence diagram — Reorder or Remove Tracks):
    - Corresponds to `loadEditablePlaylist()` → `renderEditablePlaylist()`.
    - Returns tracks with their current positions, ordered by position.

    **Response** (`PlaylistItemsResponse`):
    - `href` / `limit` / `offset` / `next` / `previous` / `total`: Standard pagination fields
    - `items`: List of `PlaylistTrackObject`, each containing:
      - `added_at`: ISO 8601 timestamp when the track was added; `null` for local files
      - `added_by`: Object identifying the user who added the track
      - `is_local`: Whether this is a locally stored file (not on Spotify servers)
      - `track`: Full `TrackObject` with `id`, `name`, `uri`, `duration_ms`,
        `artists`, `album`, `href`, `external_urls`, `is_local`
    """
    ...


@router.post(
    "/playlists/{playlist_id}/tracks",
    response_model=SnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tracks"],
    summary="Add items to playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def add_items_to_playlist(
    body: AddItemsRequest,
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Add one or more items to a user's playlist.

    Items are identified by their Spotify URIs (e.g. `spotify:track:4iV5W9uYEdYUVa79Axb7Rh`).
    A maximum of 100 items can be added in one request.

    **Flow** (from sequence diagram — Search and Add Track to Playlist):
    1. User selects a track via `addTrackToPlaylist()`.
    2. Controller calls `checkForDuplicates()` on PlaylistDB.
    3. If duplicate (`isDup`), return error.
    4. If not duplicate, call `addTrackToPlaylist()` on PlaylistDB.
    5. Returns `snapshot_id` confirming the playlist version.

    **State Transition:** Results → Validating → [!isDuplicate] Adding → Results

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`

    **Response** (`SnapshotResponse`):
    - `snapshot_id`: New version identifier of the playlist after the addition
    """
    ...


@router.put(
    "/playlists/{playlist_id}/tracks",
    response_model=SnapshotResponse,
    tags=["Tracks"],
    summary="Update playlist items",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def reorder_playlist_items(
    body: ReorderItemsRequest,
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Reorder items in a playlist.

    Uses `range_start`, `insert_before`, and `range_length` to describe the reorder operation.
    Optionally provide `snapshot_id` for optimistic concurrency control.

    **Flow** (from sequence diagram — Reorder or Remove Tracks):
    1. User performs drag-and-drop reordering (`dragAndDropReorder()`) — may happen multiple
       times in a loop, with `updateReorder()` updating the local UI state.
    2. User clicks save (`clickSaveOrder()`).
    3. Controller calls `saveOrder()` → `confirmUpdatedOrder()` on PlaylistDB.
    4. Returns `snapshot_id` of the updated playlist.

    **State Transition:** Reordering [loop] → Saving → Saved

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`

    **Response** (`SnapshotResponse`):
    - `snapshot_id`: New version identifier of the playlist after reordering
    """
    ...


@router.delete(
    "/playlists/{playlist_id}/tracks",
    response_model=SnapshotResponse,
    tags=["Tracks"],
    summary="Remove playlist items",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def remove_playlist_items(
    body: RemoveItemsRequest,
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Remove one or more items from a user's playlist.

    Items are identified by their Spotify URIs in the request body.
    A maximum of 100 items can be removed in one request.

    **Flow** (from sequence diagram — Reorder or Remove Tracks):
    1. User clicks remove (`clickRemoveTrack()`).
    2. Controller calls `stageRemoveTrack()` and shows a confirmation dialog
       via `hideAndShowConfirmation()`.
    3. User confirms (`confirmRemove()`).
    4. Controller calls `getRemovalConfirm()` → `removeTrackFromPlaylist()` on PlaylistDB.
    5. Returns `snapshot_id` of the updated playlist.

    **State Transition:** Idle → Removing → Confirming → Removed

    **Required scope:** `playlist-modify-public` or `playlist-modify-private`

    **Response** (`SnapshotResponse`):
    - `snapshot_id`: New version identifier of the playlist after removal
    """
    ...
