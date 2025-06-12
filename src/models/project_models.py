"""Project models for the Manager API."""

from __future__ import annotations
import uuid
from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users_db_sqlalchemy import UUID_ID
from src.models.user_models import Base, User

if TYPE_CHECKING:
    from src.models.team_models import Team


class Project(Base):
    """Project database table model."""

    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='uq_user_project_title'),
    )
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(
        String(length=20), nullable=False
    )
    description: Mapped[str] = mapped_column(
        String(length=320), nullable=True
    )
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="projects")
    team_id: Mapped[UUID_ID] = mapped_column(ForeignKey("teams.id"), nullable=True)
    team: Mapped["Team"] = relationship(back_populates="projects")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self):
        return f"Project(id={self.id}, title={self.title}, user_id={self.user_id})"
    
    def __str__(self):
        return self.__repr__()
