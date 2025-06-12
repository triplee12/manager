"""Task services for the Manager API."""

import uuid
from datetime import date
from typing import List, Optional
from fastapi import Depends
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_session import get_async_session
from src.models.task_models import Task, TaskComment


class TaskServices:
    """Task services for the Manager API."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TaskServices with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session

    async def create_task(self, data: dict) -> Task | None:
        """
        Create a new task.

        Args:
        data (dict): The data for the task to be created.

        Returns:
        Task: The created task.
        """
        try:
            task = Task(**data)
            self.session.add(task)
            await self.session.commit()
            return task
        except SQLAlchemyError:
            return None

    async def get_tasks_by_project_id(
        self, project_id: uuid.UUID,
        order: str = "asc", limit: int = 10, offset: int = 0
    ) -> List[Task]:
        """
        Get tasks for a specific project.

        Args:
        project_id (uuid.UUID): The ID of the project to retrieve tasks for.

        Returns:
        List[Task]: A list of tasks associated with the project.
        """
        try:
            statement = select(Task).where(Task.project_id == project_id)

            if order == "desc":
                statement = statement.order_by(desc(Task.created_at))
            else:
                statement = statement.order_by(asc(Task.created_at))

            statement = statement.limit(limit).offset(offset)
            result = await self.session.execute(statement)
            tasks = result.scalars().all()
            return tasks
        except SQLAlchemyError:
            return None

    async def get_task_by_id(self, task_id: uuid.UUID) -> Task | None:
        """
        Get a task by its ID.

        Args:
        task_id (uuid.UUID): The ID of the task to retrieve.

        Returns:
        Task: The task with the specified ID.
        """
        try:
            statement = select(Task).where(Task.id == task_id)
            result = await self.session.execute(statement)
            task = result.scalars().first()
            return task
        except SQLAlchemyError:
            return None

    async def filter_tasks(
        self, project_id: uuid.UUID, task_status: Optional[str],
        task_priority: Optional[str],
        assignee_id: Optional[uuid.UUID], due_date: Optional[date]
    ) -> List[Task]:
        try:
            statement = select(Task).where(Task.project_id == project_id)
            if task_status:
                statement = statement.where(Task.status == task_status)

            if task_priority:
                statement = statement.where(Task.priority == task_priority)

            if assignee_id:
                statement = statement.where(Task.assigned_id == assignee_id)

            if due_date:
                statement = statement.where(Task.due_date == due_date)

            result = await self.session.execute(statement)
            tasks = result.scalars().all()
            return tasks
        except SQLAlchemyError:
            return None

    async def delete_task(self, task_id: uuid.UUID):
        """
        Delete a task by its ID.

        Args:
        task_id (uuid.UUID): The ID of the task to delete.

        Returns:
        bool: True if the task was deleted. Or None if the task was not found.
        """
        try:
            statement = select(Task).where(Task.id == task_id)
            result = await self.session.execute(statement)
            task = result.scalars().first()
            if task:
                await self.session.delete(task)
                await self.session.commit()
                return True
            return None
        except SQLAlchemyError:
            return None

    async def update_task(self, task_id: uuid.UUID, data: dict) -> Task | None:
        """
        Update a task by its ID in the database.

        Args:
        task_id (uuid.UUID): The ID of the task to update.
        data (dict): The data to update the task with.

        Returns:
        Task: The updated task. Or None if the task was not found.
        """
        try:
            statement = select(Task).where(Task.id == task_id)
            result = await self.session.execute(statement)
            task = result.scalars().first()
            if task:
                for key, value in data.items():
                    setattr(task, key, value)
                await self.session.commit()
                await self.session.refresh(task)
                return task
            return None
        except SQLAlchemyError:
            return None


class TaskCommentService:
    """Task comment service."""

    def __init__(self, session: AsyncSession):        
        self.session = session

    async def create_comment(self, data: dict) -> TaskComment | None:
        """
        Create a new comment.

        Args:
        data (dict): The new comment data to create.

        Return:
        Task: The new created comment. Otherwise None
        """
        try:
            comment = TaskComment(**data)
            await self.session.add(comment)
            await self.session.commit()
            await self.session.refresh(comment)
            return comment
        except SQLAlchemyError:
            return None


async def get_task_services(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency to provide the TaskServices instance.

    Args:
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    TaskServices: An instance of TaskServices initialized with the provided session.
    """
    yield TaskServices(session)


async def get_task_comment_services(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency to provide the TaskCommentService instance.

    Args:
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    TaskCommentService: An instance of TaskCommentService initialized with the provided session.
    """
    yield TaskCommentService(session)
