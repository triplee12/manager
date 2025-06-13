"""Task database table model for the Manager API."""

from __future__ import annotations
import uuid
from enum import Enum
from typing import TYPE_CHECKING
from datetime import datetime, date
from sqlalchemy import (
    ForeignKey, String, UniqueConstraint,
    text, Enum as SAEnum
)
from sqlalchemy.dialects.postgresql import TIMESTAMP, DATE
from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users_db_sqlalchemy import UUID_ID
from src.models.user_models import Base, User

if TYPE_CHECKING:
    from src.models.project_models import Project
    from src.models.activity_models import ActivityLog

class TaskStatus(str, Enum):
    """Task status enumeration."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class TaskPriority(str, Enum):
    """Task priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Task(Base):
    """Task database table model."""

    __tablename__ = "tasks"
    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='uq_user_task_title'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    project_id: Mapped[UUID_ID] = mapped_column(ForeignKey("projects.id"), nullable=False)
    project: Mapped["Project"] = relationship(back_populates="tasks")
    title: Mapped[str] = mapped_column(String(length=20), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(length=320), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SAEnum(TaskStatus, name="status"), default=TaskStatus.TODO, nullable=False
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SAEnum(TaskPriority, name="priorities"), default=TaskPriority.LOW, nullable=False
    )
    due_date: Mapped[date] = mapped_column(DATE, nullable=False)
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(
        back_populates="tasks",
        foreign_keys=[user_id]
    )
    assigned_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=True)
    assigneds: Mapped[User] = relationship(
        "User",
        foreign_keys=[assigned_id],
        back_populates="assigned_tasks"
    )
    comments: Mapped[list[TaskComment]] = relationship(
        back_populates="task",
        cascade="all, delete"
    )
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        back_populates="task",
        cascade="all, delete"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        return (
            f"Task(id={self.id!r}, title={self.title!r}, description={self.description!r}, "
            f"user_id={self.user_id!r}, assignee_id={self.assigned_id!r}, status={self.status!r}, "
            f"priority={self.priority!r}, due_date={self.due_date!r}, "
            f"created_at={self.created_at!r}, updated_at={self.updated_at!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()


class TaskComment(Base):
    """Task comment database table model."""

    __tablename__ = "task_comments"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    task_id: Mapped[UUID_ID] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    task: Mapped["Task"] = relationship(back_populates="comments")
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(
        back_populates="task_comments",
        foreign_keys=[user_id]
    )
    comment: Mapped[str] = mapped_column(String(length=320), nullable=False)
    activity_logs: Mapped[list[ActivityLog]] = relationship(
        back_populates="task_comment",
        cascade="all, delete"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        return (
            f"TaskComment(id={self.id!r}, task_id={self.task_id!r}, user_id={self.user_id!r}, "
            f"comment={self.comment[0:20]!r}, created_at={self.created_at!r}, updated_at={self.updated_at!r})"
        )

    def __str__(self) -> str:
        return self.__repr__()
