"""Team schemas for the Manager API."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CreateTeam(BaseModel):
    """Create team"""

    title: str


class ReadTeam(BaseModel):
    """Team"""

    id: uuid.UUID
    title: str
    user_id: uuid.UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class UpdateTeam(BaseModel):
    """Update team"""

    title: Optional[str]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class CreateTeamMember(BaseModel):
    """Create team member"""

    team_id: uuid.UUID
    user_id: uuid.UUID

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class ReadTeamMember(BaseModel):
    """Team member"""

    id: uuid.UUID
    team_id: uuid.UUID
    user_id: uuid.UUID
    created_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )
