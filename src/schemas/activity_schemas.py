"""Activity schemas for the Manager API."""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from src.models.activity_models import ActivityType


class ReadActivity(BaseModel):
    """Read Activity schema for the Manager API."""

    id: uuid.UUID
    user_id: uuid.UUID
    project_id: Optional[uuid.UUID] = None
    task_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    activity_type: ActivityType
    entity: str
    entity_id: uuid.UUID
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class CreateActivity(BaseModel):
    """Create Activity schema for the Manager API."""

    project_id: Optional[uuid.UUID] = None
    task_id: Optional[uuid.UUID] = None
    team_id: Optional[uuid.UUID] = None
    activity_type: ActivityType
    entity: str
    entity_id: uuid.UUID
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        use_enum_values=True
    )
