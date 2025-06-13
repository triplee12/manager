"""Task schemas for the API."""

import uuid
from typing import List, Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict


class CreateTask(BaseModel):
    """Create Task schema for the Manager API."""

    title: str
    description: Optional[str] = None
    due_date: date
    project_id: uuid.UUID
    status: Optional[str] = "todo"
    priority: Optional[str] = "low"
    assigned_id: uuid.UUID

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class UpdateTask(BaseModel):
    """Update Task schema for the Manager API."""

    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_id: Optional[uuid.UUID] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class ReadTask(BaseModel):
    """Read Task schema for the Manager API."""

    id: uuid.UUID
    title: str
    description: Optional[str] = None
    due_date: date
    status: str
    priority: str
    project_id: uuid.UUID
    user_id: uuid.UUID
    assigneds: List[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class CreateTaskComment(BaseModel):
    """Create Task Comment schema for the Manager API."""

    comment: str
    task_id: uuid.UUID

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class ReadTaskComment(BaseModel):
    """Read Task Comment schema for the Manager API."""

    id: uuid.UUID
    comment: str
    task_id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class UpdateTaskComment(BaseModel):
    """Update Task Comment schema for the Manager API."""

    comment: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )
