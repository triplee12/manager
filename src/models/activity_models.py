"""Activity log models."""

from __future__ import annotations
import enum
import uuid
from datetime import datetime
from sqlalchemy import ForeignKey, String, text, Enum
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import Mapped, relationship, mapped_column
from fastapi_users_db_sqlalchemy import UUID_ID
from src.models.user_models import Base, User


class ActivityType(str, enum.Enum):
    """Activity types enum."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    COMMENT = "comment"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="activity_logs")
    activity_type: Mapped[ActivityType] = mapped_column(
        Enum(ActivityType, name="logs"), nullable=False
    )
    entity: Mapped[str] = mapped_column(String(length=20), nullable=False)
    entity_id: Mapped[UUID_ID] = mapped_column(String(length=67), nullable=False)
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
