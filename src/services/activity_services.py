"""Activity log services."""

import uuid
from typing import List, Optional
from fastapi import Depends
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_session import get_async_session
from src.models.activity_models import ActivityLog, ActivityType
from src.core.utils.check_access import require_project_access, require_task_access


class ActivityServices:
    """Activity log services for the Manager API."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the ActivityServices with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session
    
    async def create_activity(self, activity_data: dict):
        """
        Create a new activity log entry in the database.

        Args:
        activity_type (ActivityType): The type of activity to create.
        message (str): The message associated with the activity.
        user_id (uuid.UUID): The ID of the user associated with the activity.
        """
        try:
            activity = ActivityLog(**activity_data)
            self.session.add(activity)
            await self.session.commit()
            await self.session.refresh(activity)
            return activity
        except SQLAlchemyError:
            await self.session.rollback()
            return None

    @require_project_access(project_arg="project_id", user_arg="user_id")
    async def get_all_activities(
        self, project_id: uuid.UUID, user_id: uuid.UUID,
        order: str, limit: int, offset: int
    ) -> List[ActivityLog]:
        """
        Retrieve all activities from the database.

        Args:
        project_id (uuid.UUID): The ID of the project whose activities to retrieve.
        user_id (uuid.UUID): The ID of the user who is a member of the team.
        order (str): Order of the activities (asc or desc).
        limit (int): Maximum number of activities to retrieve.
        offset (int): Number of activities to skip.

        Returns:
        List[ActivityLog]: A list of ActivityLog objects representing the retrieved activities.
        """
        try:
            statement = select(ActivityLog).where(ActivityLog.project_id == project_id)
            if order == "desc":
                statement = statement.order_by(desc(ActivityLog.created_at))
            else:
                statement = statement.order_by(asc(ActivityLog.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            activities = result.scalars().all()
            return activities
        except SQLAlchemyError:
            return None

    @require_project_access(project_arg="project_id", user_arg="user_id")
    async def get_activity_by_id(
        self, project_id: uuid.UUID, user_id: uuid.UUID,
        activity_id: uuid.UUID
    ) -> Optional[ActivityLog]:
        """
        Retrieve an activity by its ID from the database.

        Args:
        project_id (uuid.UUID): The ID of the project whose activities to retrieve.
        user_id (uuid.UUID): The ID of the user who is a member of the team.
        activity_id (uuid.UUID): The ID of the activity to retrieve.

        Returns:
        ActivityLog: The ActivityLog object representing the retrieved activity, or None if not found.
        """
        try:
            statement = select(ActivityLog).where(
                ActivityLog.id == activity_id, ActivityLog.project_id == project_id
            )
            result = await self.session.execute(statement)
            activity = result.scalars().one_or_none()
            return activity
        except SQLAlchemyError:
            return None

    @require_task_access(task_arg="task_id", user_arg="user_id")
    async def get_all_user_activities(
        self, user_id: uuid.UUID, task_id: uuid.UUID,
        order: str, limit: int, offset: int
    ) -> List[ActivityLog]:
        """
        Retrieve all activities for a specific user from the database.

        Args:
        user_id (uuid.UUID): The ID of the user whose activities to retrieve.
        order (str): Order of the activities (asc or desc).
        limit (int): Maximum number of activities to retrieve.
        offset (int): Number of activities to skip.

        Returns:
        List[ActivityLog]: A list of ActivityLog objects representing the retrieved activities.
        """
        try:
            statement = select(ActivityLog).where(
                ActivityLog.task_id == task_id, ActivityLog.user_id == user_id
            )
            if order == "desc":
                statement = statement.order_by(desc(ActivityLog.created_at))
            else:
                statement = statement.order_by(asc(ActivityLog.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            activities = result.scalars().all()
            return activities
        except SQLAlchemyError:
            return None
    
    @require_task_access(task_arg="task_id", user_arg="user_id")
    async def get_all_team_activities(
        self, team_id: uuid.UUID, task_id: uuid.UUID, user_id: uuid.UUID,
        order: str, limit: int, offset: int
    ) -> List[ActivityLog]:
        """
        Retrieve all activities for a specific team from the database.

        Args:
        team_id (uuid.UUID): The ID of the team whose activities to retrieve.
        task_id (uuid.UUID): The ID of the task associated with the team.
        user_id (uuid.UUID): The ID of the user who is a member of the team.
        order (str): Order of the activities (asc or desc).
        limit (int): Maximum number of activities to retrieve.
        offset (int): Number of activities to skip.

        Returns:
        List[ActivityLog]: A list of ActivityLog objects representing the retrieved activities.
        """
        try:
            statement = select(ActivityLog).where(
                ActivityLog.task_id == task_id, ActivityLog.team_id == team_id
            )
            if order == "desc":
                statement = statement.order_by(desc(ActivityLog.created_at))
            else:
                statement = statement.order_by(asc(ActivityLog.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            activities = result.scalars().all()
            return activities
        except SQLAlchemyError:
            return None

    @require_project_access(project_arg="project_id", user_arg="user_id")
    async def get_all_project_activities(
        self, project_id: uuid.UUID, user_id: uuid.UUID,
        order: str, limit: int, offset: int
    ) -> List[ActivityLog]:
        """
        Retrieve all activities for a specific project from the database.

        Args:
        project_id (uuid.UUID): The ID of the project whose activities to retrieve.
        user_id (uuid.UUID): The ID of the user who is a member of the team.
        order (str): Order of the activities (asc or desc).
        limit (int): Maximum number of activities to retrieve.
        offset (int): Number of activities to skip.

        Returns:
        List[ActivityLog]: A list of ActivityLog objects representing the retrieved activities.
        """
        try:
            statement = select(ActivityLog).where(ActivityLog.project_id == project_id)
            if order == "desc":
                statement = statement.order_by(desc(ActivityLog.created_at))
            else:
                statement = statement.order_by(asc(ActivityLog.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            activities = result.scalars().all()
            return activities
        except SQLAlchemyError:
            return None
    
    @require_task_access(task_arg="task_id", user_arg="user_id")
    async def get_all_task_activities(
        self, task_id: uuid.UUID, user_id: uuid.UUID,
        order: str, limit: int, offset: int
    ) -> List[ActivityLog]:
        """
        Retrieve all activities for a specific task from the database.

        Args:
        task_id (uuid.UUID): The ID of the task whose activities to retrieve.
        user_id (uuid.UUID): The ID of the user who is a member of the team.
        order (str): Order of the activities (asc or desc).
        limit (int): Maximum number of activities to retrieve.
        offset (int): Number of activities to skip.

        Returns:
        List[ActivityLog]: A list of ActivityLog objects representing the retrieved activities.
        """
        try:
            statement = select(ActivityLog).where(ActivityLog.task_id == task_id)
            if order == "desc":
                statement = statement.order_by(desc(ActivityLog.created_at))
            else:
                statement = statement.order_by(asc(ActivityLog.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            activities = result.scalars().all()
            return activities
        except SQLAlchemyError:
            return None

    @require_project_access(project_arg="project_id", user_arg="user_id")
    async def filter_activities(
        self, type: ActivityType, project_id: uuid.UUID, user_id: uuid.UUID,
        entity: str | None, order: str, limit: int, offset: int
    ) -> List[ActivityLog]:
        """
        Retrieve activities filtered by type from the database.

        Args:
        type (ActivityType): The type of activities to filter.
        order (str): Order of the activities (asc or desc).
        limit (int): Maximum number of activities to retrieve.
        offset (int): Number of activities to skip.

        Returns:
        List[ActivityLog]: A list of ActivityLog objects representing the filtered activities.
        """
        try:
            statement = select(ActivityLog).where(ActivityLog.project_id == project_id)
            if entity:
                statement = select(ActivityLog).where(
                    ActivityLog.activity_type == type, ActivityLog.entity == entity
                )
            else:
                statement = select(ActivityLog).where(ActivityLog.activity_type == type)
            if order == "desc":
                statement = statement.order_by(desc(ActivityLog.created_at))
            else:
                statement = statement.order_by(asc(ActivityLog.created_at))
            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            activities = result.scalars().all()
            return activities
        except SQLAlchemyError:
            return None

    @require_project_access(project_arg="project_id", user_arg="user_id")
    async def delete_activity(
        self, activity_id: uuid.UUID,
        project_id: uuid.UUID, user_id: uuid.UUID
    ) -> bool:
        """
        Delete an activity by its ID from the database.

        Args:
        activity_id (uuid.UUID): The ID of the activity to delete.

        Returns:
        bool: True if the activity was deleted successfully, False otherwise.
        """
        try:
            statement = select(ActivityLog).where(
                ActivityLog.id == activity_id, ActivityLog.project_id == project_id
            )
            result = await self.session.execute(statement)
            activity = result.scalars().one_or_none()
            if activity:
                await self.session.delete(activity)
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError:
            return False


async def get_activity_service(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency function to retrieve the ActivityServices instance.

    Args:
    session (AsyncSession): The database session for executing queries.

    Returns:
    ActivityServices: The ActivityServices instance.
    """
    yield ActivityServices(session)