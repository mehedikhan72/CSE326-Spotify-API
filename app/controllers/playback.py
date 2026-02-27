"""
Playback Controller

Handles music playback operations:
- Get playback state
- Start / resume playback
- Pause playback
- Skip to next track
- Seek to position
- Stop (transfer to idle)

Sequence Diagram Covered:
- Integrate Music Playback

State Transitions (Integrate Music Playback):
  Idle -> Loading (selectPlay / startLoading)
    -> [trackValid] Active.Playing (songLoaded / beginPlayback)
    -> [error] Error (loadFailed / notifyFailure)
    -> [cancel] Idle (cancelLoad / abortReq)

  Active.Playing -> Active.Paused (pause / suspendAudio)
  Active.Paused -> Active.Playing (resume / resumeAudio)

  Active -> Loading (seek / bufferFrom(newPosition))
  Loading -> Active.Playing (seekCompleted / beginPlayback)

  Active -> Loading (playNext [hasNextTrack] / loadNextTrack)
  Active -> Idle (stop / terminatePlayback)

  Error -> Idle (dismiss / clearError)
  Error -> Loading (retry / startLoading(previousTrack))
"""

from fastapi import APIRouter, Query, Response, status

from app.schemas.common import SpotifyError
from app.schemas.playback import (
    PlaybackStateResponse,
    StartPlaybackRequest,
)

router = APIRouter(prefix="/me/player", tags=["Player"])


@router.get(
    "",
    response_model=PlaybackStateResponse,
    summary="Get playback state",
    responses={
        204: {"description": "Playback not available or active"},
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def get_playback_state():
    """
    Get information about the user's current playback state, including track, progress,
    and active device.

    **Flow** (from sequence diagram — Integrate Music Playback):
    - On page load, the PlaybackController calls `getLastPlayedSong()` on PlaylistDB
      and `getLastPlayedSongData()` on TrackDB.
    - Then `renderInitialView()` displays the current state.

    Returns 204 if no playback is active.

    **Required scope:** `user-read-playback-state`
    """
    ...


@router.put(
    "/play",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Start/resume playback",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        404: {"model": SpotifyError, "description": "Device not found"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def start_resume_playback(
    body: StartPlaybackRequest | None = None,
    device_id: str | None = Query(None, description="The ID of the device to target. If not supplied, the user's currently active device is the target."),
):
    """
    Start a new context or resume current playback on the user's active device.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectPlay()`.
    2. Controller calls `processPlaySong()` which loads the track.
    3. Playback starts — state transitions to Playing.

    **State Transition:** Idle → Loading → Active.Playing

    Provide `context_uri` to play a playlist/album/artist context, or `uris` to play specific tracks.
    Omit body to resume current playback.

    **Required scope:** `user-modify-playback-state`
    """
    ...


@router.put(
    "/pause",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Pause playback",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def pause_playback(
    device_id: str | None = Query(None, description="The ID of the device to target"),
):
    """
    Pause playback on the user's account.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectPause()`.
    2. Controller calls `processPauseSong()`.
    3. Playback is suspended.

    **State Transition:** Active.Playing → Active.Paused (suspendAudio)

    **Required scope:** `user-modify-playback-state`
    """
    ...


@router.post(
    "/next",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Skip to next",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def skip_to_next(
    device_id: str | None = Query(None, description="The ID of the device to target"),
):
    """
    Skips to next track in the user's queue.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectNext()`.
    2. Controller calls `processPlayNext()`.
    3. Fetches next track via `getNextSong()` from PlaylistDB
       and `getNextSongData()` from TrackDB.
    4. Plays the next song via `playNextSong()`.

    **State Transition:** Active → Loading (loadNextTrack) → Active.Playing

    **Required scope:** `user-modify-playback-state`
    """
    ...


@router.put(
    "/seek",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Seek to position",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def seek_to_position(
    position_ms: int = Query(..., ge=0, description="The position in milliseconds to seek to"),
    device_id: str | None = Query(None, description="The ID of the device to target"),
):
    """
    Seeks to the given position in the user's currently playing track.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectSeek()`.
    2. Controller calls `processSeek()`.
    3. Audio engine performs `seekSong()` to the new position.

    **State Transition:** Active → Loading (bufferFrom(newPosition)) → Active.Playing (seekCompleted)

    **Required scope:** `user-modify-playback-state`
    """
    ...


@router.put(
    "/stop",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Stop playback",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Bad OAuth request"},
        429: {"model": SpotifyError, "description": "Rate limit exceeded"},
    },
)
async def stop_playback(
    device_id: str | None = Query(None, description="The ID of the device to target"),
):
    """
    Stop playback entirely and return to idle state.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `exitPlayback()`.
    2. Controller calls `exitPlayBack()`.
    3. UI navigates back to playlist view via `renderPlaylistUI()`.

    **State Transition:** Active → Idle (terminatePlayback)

    **Required scope:** `user-modify-playback-state`
    """
    ...
