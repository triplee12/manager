"""Project services for the Manager API."""

import uuid
from typing import List, Optional
from fastapi import Depends, HTTPException
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.db_session import get_async_session
from src.models.project_models import Project
from src.services.team_services import TeamServices


class ProjectServices:
    """Project services for the Manager API."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the ProjectServices with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session
        self.team_services = TeamServices(session)

    async def create_project(self, data: dict) -> Optional[Project]:
        """
        Create a new project.

        Args:
        team_owner_id (uuid.UUID): The ID of the user who owns the team.
        data (dict): The data for the project to be created.

        Returns:
        Project: The created project.
        """
        try:
            team = await self.team_services.get_user_team_by_id(
                data["user_id"], data["team_id"]
            )
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")
            project = Project(**data)
            self.session.add(project)
            await self.session.commit()
            await self.session.refresh(project)
            return project
        except Exception:
            return None

    async def get_all_projects(
        self, user_id: uuid.UUID, order: str = "asc",
        limit: int = 20, offset: int = 0
    ) -> List[Project]:
        """
        Retrieve all projects from the database.

        Args:
        user_id (uuid.UUID): The ID of the user who owns the projects.
        order (str, optional): The order to sort the projects by. Default is "asc".
        limit (int, optional): The maximum number of projects to retrieve. Default is 20.
        offset (int, optional): The number of projects to skip before
                retrieving the first project. Default is 0.

        Returns:
        list: A list of all projects.
        """
        try:
            statement = select(Project).where(Project.user_id == user_id)
            if order == "desc":
                statement = statement.order_by(desc(Project.created_at))
            else:
                statement = statement.order_by(asc(Project.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            projects = result.scalars().all()
            return projects
        except Exception:
            return None

    async def get_all_team_projects(
        self, team_id: uuid.UUID, owner_id: uuid.UUID,
        order: str = "asc", limit: int = 20, offset: int = 0
    ) -> List[Project]:
        """
        Retrieve all projects from the database.

        Args:
        team_id (uuid.UUID): The ID of the team who owns the projects.
        owner_id (uuid.UUID): The ID of the user who owns the team.
        order (str, optional): The order to sort the projects by. Default is "asc".
        limit (int, optional): The maximum number of projects to retrieve. Default is 20.
        offset (int, optional): The number of projects to skip before
                retrieving the first project. Default is 0.

        Returns:
        list: A list of all projects.
        """
        try:
            team = await self.team_services.get_user_team_by_id(owner_id, team_id)
            if not team:
                raise HTTPException(status_code=404, detail="Team not found")
            statement = select(Project).where(Project.team_id == team_id)
            if order == "desc":
                statement = statement.order_by(desc(Project.created_at))
            else:
                statement = statement.order_by(asc(Project.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            projects = result.scalars().all()
            return projects
        except Exception:
            return None

    async def get_user_project_by_id(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> Optional[Project]:
        """
        Retrieve a project by its ID and user ID from the database.

        Args:
        user_id (uuid.UUID): The ID of the user who owns the project.
        project_id (uuid.UUID): The ID of the project to retrieve.

        Returns:
        Project: The project with the specified ID and user ID.
        """
        try:
            statement = select(Project).where(
                Project.id == project_id, Project.user_id == user_id
            )
            result = await self.session.execute(statement)
            project = result.scalars().first()
            return project
        except Exception:
            return None

    async def get_user_project_by_title(
        self, user_id: uuid.UUID, project_title: str
    ) -> Optional[Project]:
        """
        Retrieve a project by its title and user ID from the database.

        Args:
        user_id (uuid.UUID): The ID of the user who owns the project.
        project_title (str): The title of the project to retrieve.

        Returns:
        Project: The project with the specified title and user ID.
        """
        try:
            statement = select(Project).where(
                Project.title == project_title, Project.user_id == user_id
            )
            result = await self.session.execute(statement)
            project = result.scalars().first()
            return project
        except Exception:
            return None

    async def update_project(
        self, project_id: uuid.UUID, user_id: uuid.UUID, data: dict
    ) -> Optional[Project]:
        """
        Update a project by its ID in the database.

        Args:
        project_id (uuid.UUID): The ID of the project to update.
        user_id (uuid.UUID): The ID of the user who owns the project.
        data (dict): The data to update the project with.

        Returns:
        Project: The updated project. Or None if the project was not found.
        """
        try:
            statement = select(Project).where(
                Project.id == project_id, Project.user_id == user_id
            )
            result = await self.session.execute(statement)
            project = result.scalars().first()
            if project:
                for key, value in data.items():
                    setattr(project, key, value)
                await self.session.commit()
                await self.session.refresh(project)
                return project
            return None
        except Exception:
            return None

    async def delete_project(
        self, project_id: uuid.UUID, user_id: uuid.UUID
    ) -> Optional[bool]:
        """
        Delete a project by its ID from the database.

        Args:
        project_id (uuid.UUID): The ID of the project to delete.
        user_id (uuid.UUID): The ID of the user who owns the project.

        Returns:
        bool: True if the project was deleted. Or None if the project was not found.
        """
        try:
            statement = select(Project).where(
                Project.id == project_id, Project.user_id == user_id
            )
            result = await self.session.execute(statement)
            project = result.scalars().first()
            if project:
                await self.session.delete(project)
                await self.session.commit()
                return True
            return None
        except Exception:
            return None


async def get_project_services(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency to provide the ProjectServices instance.

    Args:
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    ProjectServices: An instance of ProjectServices initialized with the provided session.
    """
    yield ProjectServices(session)
