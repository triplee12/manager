"""User schemas"""

import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from fastapi_users import schemas
from src.models.user_models import Roles


class User(BaseModel):
    """User"""

    name: str

    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore"
    )


class UserCreate(schemas.BaseUserCreate):
    """Create user"""

    first_name: str
    last_name: str
    role: Optional[Roles] = Roles.MEMBER


class UserRead(schemas.BaseUser[uuid.UUID]):
    """User read"""

    id: uuid.UUID
    first_name: str
    last_name: str
    profile_picture: Optional[str]
    bio: Optional[str]
    role: Roles
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(
        extra="ignore",
        from_attributes = True,
        arbitrary_types_allowed = True
    )


class UserUpdate(schemas.BaseUserUpdate):
    """Update user"""

    first_name: Optional[str]
    last_name: Optional[str]
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    role: Optional[Roles] = Roles.MEMBER

    model_config = ConfigDict(
        extra="ignore",
        from_attributes = True
    )
