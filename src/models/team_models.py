"""Team models for the Manager API."""
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
    from src.models.project_models import Project


class Team(Base):
    """Team database table model."""

    __tablename__ = "teams"
    __table_args__ = (
        UniqueConstraint('user_id', 'title', name='uq_user_team_title'),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(
        String(length=20), nullable=False
    )
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="teams")
    members: Mapped[list['TeamMember']] = relationship(back_populates="team", cascade="all, delete")
    projects: Mapped[list['Project']] = relationship(back_populates="team", cascade="all, delete")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        """Return a string representation of the Team object."""
        return f"""
        Team(id={self.id!r}, title={self.title!r},
        user_id={self.user_id!r}, created_at={self.created_at!r})
        """
    
    def __str__(self) -> str:
        """Return a string representation of the Team object."""
        return self.__repr__()
    
    @hybrid_property
    def members_count(self):
        """
        The number of members in the team.

        This property is a hybrid property and can be accessed both as an 
        instance method and as a column in a SQL query.

        Returns:
            int: The number of members in the team.
        """
        return len(self.members)
    
    @members_count.expression
    def members_count(cls):
        """
        The number of members in a team.

        This is a hybrid property expression that can be used in a SQL query
        to get the number of members in a team.

        Returns:
            sqlalchemy.sql.expression.Select: A SQL expression that returns 
            the number of members in a team.
        """

        from sqlalchemy import select, func
        return (
            select(func.count(TeamMember.id))
            .where(TeamMember.team_id == cls.id)
            .correlate(cls)
            .scalar_subquery()
        )


class TeamMember(Base):
    """Team member database table model."""

    __tablename__ = "team_members"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, index=True,
        default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[UUID_ID] = mapped_column(ForeignKey("user.id"), nullable=False)
    team_id: Mapped[UUID_ID] = mapped_column(ForeignKey("teams.id"), nullable=False)
    user: Mapped[User] = relationship(back_populates="team_members")
    team: Mapped[Team] = relationship(back_populates="members")
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False,
        default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self) -> str:
        """Return a string representation of the TeamMember object."""
        return f"""
        TeamMember(id={self.id!r}, user_id={self.user_id!r},
        team_id={self.team_id!r}, created_at={self.created_at!r})
        """
    
    def __str__(self) -> str:
        """Return a string representation of the TeamMember object."""
        return self.__repr__()
