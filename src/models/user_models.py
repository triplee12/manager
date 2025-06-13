"""User models for the Manager API."""

from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import String, Enum as SAEnum
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)
from fastapi_users.db import SQLAlchemyBaseUserTableUUID

if TYPE_CHECKING:
    from src.models.team_models import Team, TeamMember
    from src.models.project_models import Project
    from src.models.task_models import Task, TaskComment
    from src.models.activity_models import ActivityLog


class Base(DeclarativeBase):
    """Base class for declarative models."""


class Roles(str, Enum):
    """User roles."""

    ADMIN = "admin"
    MEMBER = "member"


class User(SQLAlchemyBaseUserTableUUID, Base):
    """User database table model. Extends SQLAlchemyBaseUserTableUUID."""

    first_name: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=True
    )
    last_name: Mapped[str] = mapped_column(
        String(length=320), index=True, nullable=True
    )
    username: Mapped[str] = mapped_column(
        String(length=20), index=True, nullable=True, unique=True
    )
    phone_number: Mapped[str] = mapped_column(
        String(length=20), index=True, nullable=True
    )
    bio: Mapped[str] = mapped_column(
        String(length=320), nullable=True
    )
    profile_picture: Mapped[str] = mapped_column(
        String(length=320), nullable=True
    )
    role: Mapped[Roles] = mapped_column(
        SAEnum(Roles, name="roles"), default=Roles.MEMBER, nullable=False
    )
    teams: Mapped[list[Team]] = relationship(back_populates="user", cascade="all, delete")
    team_members: Mapped[list[TeamMember]] = relationship(
        back_populates="user", cascade="all, delete"
    )
    tasks: Mapped[list["Task"]] = relationship(
        back_populates="user",
        foreign_keys="[Task.user_id]"
    )
    assigned_tasks: Mapped[list["Task"]] = relationship(
        back_populates="assigneds",
        foreign_keys="[Task.assigned_id]"
    )
    task_comments: Mapped[list["TaskComment"]] = relationship(
        back_populates="user",
        foreign_keys="[TaskComment.user_id]"
    )
    projects: Mapped[list["Project"]] = relationship(back_populates="user", cascade="all, delete")
    activity_logs: Mapped[list["ActivityLog"]] = relationship(back_populates="user", cascade="all, delete")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        """Return a string representation of the User object."""
        fullname = f"{self.first_name} {self.last_name}"
        return f"""
        User(id={self.id!r}, username={self.username!r},
        fullname={fullname!r}, created_at={self.created_at!r})
        """

    def __str__(self) -> str:
        """Return a string representation of the User object."""
        return self.__repr__()
