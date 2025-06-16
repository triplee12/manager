"""Activity log models."""

from __future__ import annotations
import enum
import uuid
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, String, text, Enum
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users_db_sqlalchemy import UUID_ID
from src.models.user_models import Base, User

if TYPE_CHECKING:
    from src.models.project_models import Project
    from src.models.task_models import Task, TaskComment
    from src.models.team_models import Team


class ActivityType(str, enum.Enum):
    """Activity types enum."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    COMMENT = "comment"


class ActivityLog(Base):
    """Activity log database table model."""

    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=True)
    user: Mapped[User] = relationship(back_populates="activity_logs")
    project_id: Mapped[UUID_ID] = mapped_column(ForeignKey("projects.id"), nullable=True)
    project: Mapped["Project"] = relationship(back_populates="activity_logs")
    task_id: Mapped[UUID_ID] = mapped_column(ForeignKey("tasks.id"), nullable=True)
    task: Mapped["Task"] = relationship(back_populates="activity_logs")
    team_id: Mapped[UUID_ID] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="activity_logs")
    comment_id: Mapped[UUID_ID] = mapped_column(ForeignKey("task_comments.id"), nullable=True)
    task_comment: Mapped["TaskComment"] = relationship(back_populates="activity_logs")
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, name="logs"), nullable=True
    )
    entity: Mapped[str] = mapped_column(String(length=20), nullable=True)
    entity_id: Mapped[str] = mapped_column(String(length=100), nullable=True)
    description: Mapped[str] = mapped_column(String(length=320), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )

    def __repr__(self):
        return (
            f"ActivityLog({self.id}, {self.user_id}, {self.activity_type}, " \
            f"{self.entity}, {self.entity_id}, {self.description}, {self.created_at})"
        )

    def __str__(self):
        return self.__repr__()
