"""
Share Controller

Handles sharing playlist links:
- Getting the share menu (playlist metadata for sharing)
- Generating / fetching a shareable link

Sequence Diagram Covered:
- Share Playlist Link

State Transitions (Share Playlist Link):
  Idle -> ShareFlow (clickShare)
    ShareFlow:
      PreparingShare (entry)
        -> [!error] ShareMenuVisible (metadataLoaded / renderMenu)
        -> [error] Error (metadataLoaded[error] / showError)
      ShareMenuVisible -> FetchShareLink (clickCopyLink / startFetchLink)
        -> ShareMenuVisible (linkReady / showConfirmation)
        -> Error (linkFailed / showError)
      Error -> PreparingShare (retry / getShareView)
    ShareFlow -> Idle (closeShareMenu / cleanup)
"""

from fastapi import APIRouter, Path

from app.schemas.common import SpotifyError
from app.schemas.share import ShareLinkResponse, ShareMenuResponse

router = APIRouter(tags=["Share"])


@router.get(
    "/playlists/{playlist_id}/share",
    response_model=ShareMenuResponse,
    summary="Get share menu data for a playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
    },
)
async def get_share_menu(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist to share"),
):
    """
    Retrieve playlist metadata needed to render the share menu.

    **Flow** (from sequence diagram — Share Playlist Link):
    1. User clicks share (`clickShare()`) on PlaylistViewUI.
    2. Controller calls `getShareView()` → `getPlaylistMetadata()` on PlaylistDB.
    3. Returns playlist info and navigates to the share menu via `goToShareMenu()`.

    **State Transition:** Idle → PreparingShare → ShareMenuVisible (metadataLoaded / renderMenu)
    """
    ...


@router.get(
    "/playlists/{playlist_id}/share/link",
    response_model=ShareLinkResponse,
    summary="Get or generate a shareable link for a playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
        500: {"model": SpotifyError, "description": "Failed to generate share link"},
    },
)
async def get_share_link(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Generate or retrieve a shareable link for the playlist (copy-to-clipboard link).

    **Flow** (from sequence diagram — Share Playlist Link):
    1. User clicks "Copy Link" (`clickCopyLink()`) in the share menu.
    2. Controller calls `getCopyLink()` → `fetchCopyLink()` on PlaylistDB.
    3. Returns the share URL; UI shows confirmation via `showCopyConfirmation()`.

    **State Transition:** ShareMenuVisible → FetchShareLink → ShareMenuVisible (linkReady)
    On failure: FetchShareLink → Error (linkFailed / showError)
    """
    ...
