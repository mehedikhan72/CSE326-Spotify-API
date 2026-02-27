from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import UUID


class CollaboratorRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"


class InviteLinkResponse(BaseModel):
    invite_link: str
    playlist_id: UUID
    expires_at: datetime | None = None


class AcceptInviteRequest(BaseModel):
    invite_token: str = Field(..., description="The invite token from the collaboration link")


class CollaboratorResponse(BaseModel):
    id: UUID
    user_id: UUID
    username: str
    role: CollaboratorRole
    joined_at: datetime


class AcceptInviteResponse(BaseModel):
    message: str
    collaborator: CollaboratorResponse
    playlist_id: UUID


class CollaboratorsListResponse(BaseModel):
    playlist_id: UUID
    owner_id: UUID
    collaborators: list[CollaboratorResponse]
