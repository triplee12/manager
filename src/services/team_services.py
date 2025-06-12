"""Team services for the Manager API."""

import uuid
from typing import Optional
from fastapi import Depends, HTTPException
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_session import get_async_session
from src.models.team_models import Team, TeamMember


class TeamServices:
    """Team services for the Manager API."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TeamServices with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session
    
    async def create_team(self, data: dict) -> Optional[Team]:
        """
        Create a new team.

        Args:
        data (dict): The data for the team to be created.

        Returns:
        Team: The created team.
        """
        try:
            team = Team(**data)
            self.session.add(team)
            await self.session.commit()
            await self.session.refresh(team)
            return team
        except Exception as e:
            return None
    
    async def get_all_teams(self, order: str = "asc", limit: int = 20, offset: int = 0):
        """
        Retrieve all teams from the database.

        Args:
        order (str): Order of the teams (asc or desc).
        limit (int): Maximum number of teams to retrieve.
        offset (int): Number of teams to skip.

        Returns:
        List[Team]: A list of teams.
        """
        statement = select(Team)
        if order == "desc":
            statement = statement.order_by(desc(Team.created_at))
        else:
            statement = statement.order_by(asc(Team.created_at))
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        teams = result.scalars().all()
        return teams
    
    async def get_team_by_id(self, team_id: uuid.UUID):
        """
        Retrieve a team by its ID from the database.

        Args:
        team_id (uuid.UUID): The ID of the team to retrieve.

        Returns:
        Team: The team with the specified ID.
        """
        statement = select(Team).where(Team.id == team_id)
        result = await self.session.execute(statement)
        team = result.scalars().first()
        return team
    
    async def get_user_teams(
        self, user_id: uuid.UUID, order: str = "asc",
        limit: int = 20, offset: int = 0
    ):
        """
        Retrieve all teams associated with a user from the database.

        Args:
        user_id (uuid.UUID): The ID of the user whose teams to retrieve.
        order (str): Order of the teams (asc or desc).
        limit (int): Maximum number of teams to retrieve.
        offset (int): Number of teams to skip.

        Returns:
        List[Team]: A list of teams associated with the user.
        """
        statement = select(Team).where(Team.user_id == user_id)
        if order == "desc":
            statement = statement.order_by(desc(Team.created_at))
        else:
            statement = statement.order_by(asc(Team.created_at))
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        teams = result.scalars().all()
        return teams
    
    async def get_user_team_by_id(self, user_id: uuid.UUID, team_id: uuid.UUID):
        """
        Retrieve a team by its ID associated with a user from the database.

        Args:
        user_id (uuid.UUID): The ID of the user whose team to retrieve.
        team_id (uuid.UUID): The ID of the team to retrieve.

        Returns:
        Team: The team with the specified ID associated with the user.
        """
        statement = select(Team).where(Team.user_id == user_id, Team.id == team_id)
        result = await self.session.execute(statement)
        team = result.scalars().first()
        return team
    
    async def get_user_team_by_name(self, user_id: uuid.UUID, team_name: str):
        """
        Retrieve a team by its name associated with a user from the database.

        Args:
        user_id (uuid.UUID): The ID of the user whose team to retrieve.
        team_name (str): The name of the team to retrieve.

        Returns:
        Team: The team with the specified name associated with the user.
        """
        statement = select(Team).where(Team.user_id == user_id, Team.name == team_name)
        result = await self.session.execute(statement)
        team = result.scalars().first()
        return team
    
    async def get_total_teams(self, user_id: uuid.UUID) -> int:
        """
        Retrieve the total number of teams a user has.

        Args:
        user_id (uuid.UUID): The ID of the user whose teams to calculate.

        Returns:
        int: The total number of teams.
        """
        statement = select(Team).where(Team.user_id == user_id)
        result = await self.session.execute(statement)
        total_teams = len(result.scalars().all())
        return total_teams
    
    async def get_total_members(self, team_id: uuid.UUID) -> int:
        """
        Retrieve the total number of members in a team.

        Args:
        team_id (uuid.UUID): The ID of the team whose members to calculate.

        Returns:
        int: The total number of members.
        """
        statement = select(Team.members_count).where(Team.id == team_id)
        result = await self.session.execute(statement)
        total_members = result.scalar_one_or_none()
        return total_members
    
    async def update_team(self, team_id: uuid.UUID, user_id: uuid.UUID, data: dict):
        """
        Update a team by its ID in the database.

        Args:
        team_id (uuid.UUID): The ID of the team to update.
        user_id (uuid.UUID): The ID of the user who owns the team.
        data (dict): The data to update the team with.

        Returns:
        Team: The updated team. Or None if the team was not found.
        """
        try:
            statement = select(Team).where(Team.id == team_id, Team.user_id == user_id)
            result = await self.session.execute(statement)
            team = result.scalars().first()
            if team:
                for key, value in data.items():
                    setattr(team, key, value)
                await self.session.commit()
                await self.session.refresh(team)
                return team
            return None
        except Exception as e:
            return None
    
    async def delete_team(self, team_id: uuid.UUID, user_id: uuid.UUID):
        """
        Delete a team by its ID from the database.

        Args:
        team_id (uuid.UUID): The ID of the team to delete.
        user_id (uuid.UUID): The ID of the user who owns the team.

        Returns:
        bool: True if the team was deleted successfully, False otherwise.
        """
        statement = select(Team).where(Team.id == team_id, Team.user_id == user_id)
        result = await self.session.execute(statement)
        team = result.scalars().first()
        if team:
            await self.session.delete(team)
            await self.session.commit()
            return True
        return False


class TeamMemberServices:
    """Team member services for the Manager API."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TeamMemberServices with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session

    async def add_member_to_team(self, team_owner_id: uuid.UUID, data: dict):
        """
        Add a member to a team in the database.

        Args:
        data (dict): The data for the member to be added.

        Returns:
        Team: The team with the added member.
        """
        try:
            team = await TeamServices(self.session).get_user_team_by_id(
                team_owner_id, data["team_id"]
            )
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")
            data["team_id"] = team.id
            member = TeamMember(**data)
            self.session.add(member)
            await self.session.commit()
            await self.session.refresh(member)
            return member
        except Exception as e:
            return None

    async def get_team_members(
        self, team_id: uuid.UUID, order: str = "asc",
        limit: int = 10, offset: int = 0
    ):
        """
        Retrieve all members of a team from the database.

        Args:
        team_id (uuid.UUID): The ID of the team whose members to retrieve.
        order (str): Order of the members (asc or desc).
        limit (int): Maximum number of members to retrieve.
        offset (int): Number of members to skip.

        Returns:
        List[TeamMember]: A list of team members.
        """
        statement = select(TeamMember).where(TeamMember.team_id == team_id)
        if order == "desc":
            statement = statement.order_by(desc(TeamMember.created_at))
        else:
            statement = statement.order_by(asc(TeamMember.created_at))
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        members = result.scalars().all()
        return members

    async def get_member_by_id(self, member_id: uuid.UUID):
        """
        Retrieve a member by its ID from the database.

        Args:
        member_id (uuid.UUID): The ID of the member to retrieve.

        Returns:
        TeamMember: The team member with the specified ID.
        """
        statement = select(TeamMember).where(TeamMember.id == member_id)
        result = await self.session.execute(statement)
        member = result.scalars().first()
        return member
    
    async def remove_member_from_team(
        self, team_owner_id: uuid.UUID,
        team_id: uuid.UUID, user_id: uuid.UUID
    ):
        """
        Remove a member from a team in the database.

        Args:
        team_owner_id (uuid.UUID): The ID of the user who owns the team.
        team_id (uuid.UUID): The ID of the team from which to remove the member.
        user_id (uuid.UUID): The ID of the user to remove from the team.

        Returns:
        bool: True if the member was removed successfully, False otherwise.
        """
        team = await TeamServices(self.session).get_user_team_by_id(
            team_owner_id, team_id
        )
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
        statement = select(TeamMember).where(
            TeamMember.team_id == team_id, TeamMember.user_id == user_id
        )
        result = await self.session.execute(statement)
        member = result.scalars().first()
        if member:
            await self.session.delete(member)
            await self.session.commit()
            return True
        return False


async def get_team_services(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency to provide the TeamServices instance.

    Args:
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    TeamServices: An instance of TeamServices initialized with the provided session.
    """

    yield TeamServices(session)


async def get_team_member_services(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency to provide the TeamMemberServices instance.

    Args:
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    TeamMemberServices: An instance of TeamMemberServices initialized with the provided session.
    """
    yield TeamMemberServices(session)
