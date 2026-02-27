"""
Playback Controller

Handles music playback operations:
- Play a track
- Pause playback
- Resume playback
- Skip to next track
- Seek to a position
- Get current playback status
- Exit / stop playback

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

from uuid import UUID

from fastapi import APIRouter, Path, Query, status

from app.schemas.common import ErrorResponse
from app.schemas.playback import (
    PlaybackState,
    PlaybackStatusResponse,
    PlayNextResponse,
    PlayRequest,
    SeekRequest,
)

router = APIRouter(prefix="/playback", tags=["Playback"])


@router.get(
    "/status",
    response_model=PlaybackStatusResponse,
    summary="Get current playback status",
)
async def get_playback_status():
    """
    Retrieve the current playback state for the authenticated user.

    **Flow** (from sequence diagram — Integrate Music Playback):
    - On page load, the PlaybackController calls `getLastPlayedSong()` on PlaylistDB
      and `getLastPlayedSongData()` on TrackDB.
    - Then `renderInitialView()` displays the current state.

    Returns the current state (idle, loading, playing, paused, error),
    the current track info, and position within the track.
    """
    ...


@router.post(
    "/play",
    response_model=PlaybackStatusResponse,
    summary="Play a track",
    responses={
        404: {"model": ErrorResponse, "description": "Track or playlist not found"},
        422: {"model": ErrorResponse, "description": "Track cannot be loaded"},
    },
)
async def play_track(body: PlayRequest):
    """
    Start playing a specific track within a playlist context.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectPlay()`.
    2. Controller calls `processPlaySong()` which loads the track.
    3. Returns `playSong()` — the playback state transitions to Playing.

    **State Transition:** Idle → Loading → Playing
    """
    ...


@router.post(
    "/pause",
    response_model=PlaybackStatusResponse,
    summary="Pause playback",
    responses={
        409: {"model": ErrorResponse, "description": "Playback is not currently playing"},
    },
)
async def pause_playback():
    """
    Pause the currently playing track.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectPause()`.
    2. Controller calls `processPauseSong()`.
    3. Returns `pauseSong()` — playback state transitions to Paused.

    **State Transition:** Active.Playing → Active.Paused (suspendAudio)
    """
    ...


@router.post(
    "/resume",
    response_model=PlaybackStatusResponse,
    summary="Resume playback",
    responses={
        409: {"model": ErrorResponse, "description": "Playback is not currently paused"},
    },
)
async def resume_playback():
    """
    Resume playback from the paused position.

    **State Transition:** Active.Paused → Active.Playing (resumeAudio)
    """
    ...


@router.post(
    "/next",
    response_model=PlayNextResponse,
    summary="Skip to next track",
    responses={
        404: {"model": ErrorResponse, "description": "No next track available in the playlist"},
        409: {"model": ErrorResponse, "description": "No active playback session"},
    },
)
async def play_next_track():
    """
    Skip to the next track in the current playlist.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectNext()`.
    2. Controller calls `processPlayNext()`.
    3. Fetches next track via `getNextSong()` from PlaylistDB
       and `getNextSongData()` from TrackDB.
    4. Returns `playNextSong()` with the new track info.

    **State Transition:** Active → Loading (loadNextTrack) → Active.Playing
    Returns 404 if no next track is available (`!hasNextTrack`).
    """
    ...


@router.post(
    "/seek",
    response_model=PlaybackStatusResponse,
    summary="Seek to a position in the current track",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid seek position"},
        409: {"model": ErrorResponse, "description": "No active playback session"},
    },
)
async def seek_position(body: SeekRequest):
    """
    Seek to a specific position in the currently playing track.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `selectSeek()`.
    2. Controller calls `processSeek()`.
    3. Audio engine performs `seekSong()` to the new position.

    **State Transition:** Active → Loading (bufferFrom(newPosition)) → Active.Playing (seekCompleted)
    """
    ...


@router.post(
    "/stop",
    response_model=PlaybackStatusResponse,
    summary="Stop playback and return to idle",
    responses={
        409: {"model": ErrorResponse, "description": "No active playback session"},
    },
)
async def stop_playback():
    """
    Stop playback entirely and return to idle state.

    **Flow** (from sequence diagram — Integrate Music Playback):
    1. User calls `exitPlayback()`.
    2. Controller calls `exitPlayBack()`.
    3. UI navigates back to playlist view via `renderPlaylistUI()`.

    **State Transition:** Active → Idle (terminatePlayback)
    """
    ...
