"""
Collaboration Controller

Handles collaborative playlist operations:
- Generating / retrieving an invite link for a playlist
- Accepting an invite link (collaborator joins)
- Listing collaborators on a playlist
- Removing a collaborator

Sequence Diagram Covered:
- Invite Collaborators

State Transitions (Invite Collaborators):
  Idle -> Inviting (inviteCollaborators)
    -> getCollabLink() -> renderInitialView (link shown)

  Collaborator flow:
    Idle -> Accepting (acceptInviteLink)
      -> Validating (validate)
        -> [!isActive] Error (showError) -> Idle
        -> [isActive] Joining (updateCollaboratorLink) -> Joined (renderPlaylistUI)
"""

from fastapi import APIRouter, Path, status

from app.schemas.collaboration import (
    AcceptInviteRequest,
    AcceptInviteResponse,
    CollaboratorsListResponse,
    InviteLinkResponse,
)
from app.schemas.common import SpotifyError

router = APIRouter(tags=["Collaboration"])


@router.get(
    "/playlists/{playlist_id}/invite-link",
    response_model=InviteLinkResponse,
    summary="Get invite link for a collaborative playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Playlist is not collaborative or user is not the owner"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
    },
)
async def get_invite_link(
    playlist_id: str = Path(..., description="The Spotify ID of the collaborative playlist"),
):
    """
    Retrieve (or generate) the collaboration invite link for a playlist.

    **Flow** (from sequence diagram — Invite Collaborators):
    1. Playlist owner triggers `inviteCollaborators()`.
    2. Controller calls `getCollabLink()` on CollaboratorLink service.
    3. Returns the invite link and renders the initial invite view.

    Only the playlist owner can retrieve the invite link.
    The playlist must have `collaborative` set to `true`.
    """
    ...


@router.post(
    "/invites/accept",
    response_model=AcceptInviteResponse,
    summary="Accept a collaboration invite",
    responses={
        400: {"model": SpotifyError, "description": "Invalid or expired invite token"},
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        409: {"model": SpotifyError, "description": "User is already a collaborator"},
    },
)
async def accept_invite(body: AcceptInviteRequest):
    """
    Accept a collaboration invite link and join the playlist as a collaborator.

    **Flow** (from sequence diagram — Invite Collaborators):
    1. Collaborator clicks the invite link → `acceptInviteLink()`.
    2. Controller calls `validate()` on CollaboratorLink to verify the token.
    3. If the link is not active (`!isActive`), return 400 error via `showError()`.
    4. If active (`isActive`), call `updateCollaboratorLink()` to add the user.
    5. Returns the collaborator info and playlist ID; UI renders via `renderPlaylistUI()`.

    **State Transition:** Accepting → Validating → [isActive] Joined / [!isActive] Error
    """
    ...


@router.get(
    "/playlists/{playlist_id}/collaborators",
    response_model=CollaboratorsListResponse,
    summary="List collaborators on a playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        404: {"model": SpotifyError, "description": "Playlist not found"},
    },
)
async def list_collaborators(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
):
    """
    Retrieve all collaborators for a given playlist, including the owner.
    """
    ...


@router.delete(
    "/playlists/{playlist_id}/collaborators/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Remove a collaborator from a playlist",
    responses={
        401: {"model": SpotifyError, "description": "Bad or expired token"},
        403: {"model": SpotifyError, "description": "Only the owner can remove collaborators"},
        404: {"model": SpotifyError, "description": "Playlist or collaborator not found"},
    },
)
async def remove_collaborator(
    playlist_id: str = Path(..., description="The Spotify ID of the playlist"),
    user_id: str = Path(..., description="The Spotify ID of the collaborator to remove"),
):
    """
    Remove a collaborator from a playlist. Only the playlist owner can perform this action.
    """
    ...
