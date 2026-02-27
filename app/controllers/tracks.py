"""
Track Management Controller

Handles track operations within a playlist:
- Searching tracks (with keyword and filters)
- Getting suggested tracks
- Adding a track to a playlist (with duplicate check)
- Reordering tracks in a playlist
- Removing a track from a playlist

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

from uuid import UUID

from fastapi import APIRouter, Path, Query, status

from app.schemas.common import ErrorResponse
from app.schemas.search import SearchFilterType, SearchTracksResponse, SuggestedTracksResponse
from app.schemas.track import (
    AddTrackToPlaylistRequest,
    AddTrackToPlaylistResponse,
    PlaylistTracksListResponse,
    RemoveTrackResponse,
    ReorderTracksRequest,
    ReorderTracksResponse,
)

router = APIRouter(tags=["Tracks"])


# --- Search ---

@router.get(
    "/tracks/search",
    response_model=SearchTracksResponse,
    tags=["Search"],
    summary="Search for tracks",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid query or filter"},
    },
)
async def search_tracks(
    query: str = Query(..., min_length=1, description="Search keyword"),
    filter: SearchFilterType = Query(SearchFilterType.ALL, description="Filter by field"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Search the track catalog by keyword with optional filtering.

    **Flow** (from sequence diagram — Search and Add Track to Playlist):
    1. User enters a keyword via `enterKeyword()`.
    2. Controller calls `searchViaKeyword()` → `getTracksViaQuery()` on TrackDB.
    3. Returns matching tracks.

    **Filtering** (from sequence diagram — chooseFilter/applyFilter):
    - After initial results are shown, user can apply filters.
    - `filter` parameter narrows results by title, artist, or album.

    **State Transition:** Idle → Searching → Results / Empty / Failure
    """
    ...


@router.get(
    "/playlists/{playlist_id}/suggested-tracks",
    response_model=SuggestedTracksResponse,
    tags=["Search"],
    summary="Get suggested tracks for a playlist",
)
async def get_suggested_tracks(
    playlist_id: UUID = Path(..., description="ID of the playlist"),
):
    """
    Get track suggestions based on the playlist's existing songs.

    **Flow** (from sequence diagram — Search and Add Track to Playlist):
    1. On page load, controller calls `getExistingSongs()` from PlaylistDB.
    2. Uses existing songs to call `getSuggestedTracks()` from TrackDB.
    3. Returns suggestions before the user types any search query.
    """
    ...


# --- Playlist Tracks CRUD ---

@router.get(
    "/playlists/{playlist_id}/tracks",
    response_model=PlaylistTracksListResponse,
    tags=["Tracks"],
    summary="List tracks in a playlist",
    responses={
        404: {"model": ErrorResponse, "description": "Playlist not found"},
    },
)
async def list_playlist_tracks(
    playlist_id: UUID = Path(..., description="ID of the playlist"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    Retrieve a paginated list of tracks in a playlist, ordered by position.

    **Flow** (from sequence diagram — Reorder or Remove Tracks):
    - Corresponds to `loadEditablePlaylist()` → `renderEditablePlaylist()`.
    - Returns tracks with their current positions.
    """
    ...


@router.post(
    "/playlists/{playlist_id}/tracks",
    response_model=AddTrackToPlaylistResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tracks"],
    summary="Add a track to a playlist",
    responses={
        404: {"model": ErrorResponse, "description": "Playlist or track not found"},
        409: {"model": ErrorResponse, "description": "Track already exists in playlist (duplicate)"},
    },
)
async def add_track_to_playlist(
    body: AddTrackToPlaylistRequest,
    playlist_id: UUID = Path(..., description="ID of the playlist"),
):
    """
    Add a track to a playlist after duplicate validation.

    **Flow** (from sequence diagram — Search and Add Track to Playlist):
    1. User selects a track via `addTrackToPlaylist()`.
    2. Controller calls `checkForDuplicates()` on PlaylistDB.
    3. If duplicate (`isDup`), return 409 with a duplicate warning.
    4. If not duplicate, call `addTrackToPlaylist()` on PlaylistDB.
    5. Return the newly added playlist track with confirmation.

    **State Transition:** Results → Validating → [!isDuplicate] Adding → Results
                                              → [isDuplicate] Duplicate (409)
    """
    ...


@router.put(
    "/playlists/{playlist_id}/tracks/reorder",
    response_model=ReorderTracksResponse,
    tags=["Tracks"],
    summary="Reorder tracks in a playlist",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid track positions"},
        404: {"model": ErrorResponse, "description": "Playlist not found"},
    },
)
async def reorder_tracks(
    body: ReorderTracksRequest,
    playlist_id: UUID = Path(..., description="ID of the playlist"),
):
    """
    Save a new track ordering for a playlist.

    **Flow** (from sequence diagram — Reorder or Remove Tracks):
    1. User performs drag-and-drop reordering (`dragAndDropReorder()`) — may happen multiple
       times in a loop, with `updateReorder()` updating the local UI state.
    2. User clicks save (`clickSaveOrder()`).
    3. Controller calls `saveOrder()` → `confirmUpdatedOrder()` on PlaylistDB.
    4. On success, returns the updated track list and UI navigates to view mode
       via `returnToViewmenu()`.

    **State Transition:** Reordering [loop] → Saving → Saved
    """
    ...


@router.delete(
    "/playlists/{playlist_id}/tracks/{track_id}",
    response_model=RemoveTrackResponse,
    tags=["Tracks"],
    summary="Remove a track from a playlist",
    responses={
        404: {"model": ErrorResponse, "description": "Playlist or track not found"},
    },
)
async def remove_track_from_playlist(
    playlist_id: UUID = Path(..., description="ID of the playlist"),
    track_id: UUID = Path(..., description="ID of the track to remove"),
):
    """
    Remove a specific track from a playlist.

    **Flow** (from sequence diagram — Reorder or Remove Tracks):
    1. User clicks remove (`clickRemoveTrack()`).
    2. Controller calls `stageRemoveTrack()` and shows a confirmation dialog
       via `hideAndShowConfirmation()`.
    3. User confirms (`confirmRemove()`).
    4. Controller calls `getRemovalConfirm()` → `removeTrackFromPlaylist()` on PlaylistDB.
    5. Returns success and refreshes the edit UI via `showPlaylistEditUI()`.

    **State Transition:** Idle → Removing → Confirming → Removed
    """
    ...
