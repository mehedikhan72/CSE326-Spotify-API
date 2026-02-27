from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class CollaboratorRole(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"


class InviteLinkResponse(BaseModel):
    invite_link: str
    playlist_id: str
    expires_at: datetime | None = None


class AcceptInviteRequest(BaseModel):
    invite_token: str = Field(..., description="The invite token from the collaboration link")


class CollaboratorObject(BaseModel):
    id: str
    user_id: str
    display_name: str
    role: CollaboratorRole
    joined_at: datetime


class AcceptInviteResponse(BaseModel):
    message: str
    collaborator: CollaboratorObject
    playlist_id: str


class CollaboratorsListResponse(BaseModel):
    playlist_id: str
    owner_id: str
    collaborators: list[CollaboratorObject]
