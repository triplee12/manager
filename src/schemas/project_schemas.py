"""Project schemas for the Manager API."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CreateProject(BaseModel):
    """Create Project schema for the Manager API."""

    title: str
    description: Optional[str]
    team_id: Optional[uuid.UUID]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class ReadProject(BaseModel):
    """Read Project schema for the Manager API."""

    id: uuid.UUID
    title: str
    description: Optional[str]
    user_id: uuid.UUID
    team_id: Optional[uuid.UUID]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class UpdateProject(BaseModel):
    """Update Project schema for the Manager API."""

    title: Optional[str]
    description: Optional[str]
    team_id: Optional[uuid.UUID]

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )
