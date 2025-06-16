"""Task services for the Manager API."""

import uuid
from datetime import date
from typing import List, Optional
from fastapi import Depends
from sqlalchemy import or_, select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from src.db.db_session import get_async_session
from src.models.task_models import TaskStatus, TaskPriority, Task, TaskComment
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices


class TaskServices:
    """Task services for the Manager API."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TaskServices with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session
        self.activity_logs = ActivityServices(self.session)

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
            await self.session.refresh(task)
            data={
                "user_id": task.user_id,
                "task_id": task.id,
                "project_id": task.project_id,
                "description": f"Task {task.id} has been created.",
                "activity_type": ActivityType.CREATE,
                "entity": "task",
                "entity_id": task.id
            }

            await self.activity_logs.create_activity(
                activity_data=data
            )
            return task
        except SQLAlchemyError:
            await self.session.rollback()
            return None

    async def get_tasks_by_project_id(
        self, project_id: uuid.UUID, user_id: uuid.UUID,
        order: str = "asc", limit: int = 10, offset: int = 0
    ) -> List[Task]:
        """
        Get tasks for a specific project.

        Args:
        project_id (uuid.UUID): The ID of the project to retrieve tasks for.
        user_id (uuid.UUID): The ID of the user to retrieve tasks for.
        order (str, optional): The order in which to retrieve tasks. Defaults to "asc".
        limit (int, optional): The maximum number of tasks to retrieve. Defaults to 10.
        offset (int, optional): The number of tasks to skip before retrieving tasks. Defaults to 0.

        Returns:
        List[Task]: A list of tasks associated with the project.
        """
        try:
            statement = select(Task).where(Task.project_id == project_id,
                or_(Task.user_id == user_id, Task.assigned_id == user_id)
            )

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

    async def get_task_by_id(self, task_id: uuid.UUID, user_id: uuid.UUID) -> Task | None:
        """
        Get a task by its ID.

        Args:
        task_id (uuid.UUID): The ID of the task to retrieve.
        user_id (uuid.UUID): The ID of the user who created the task.

        Returns:
        Task: The task with the specified ID.
        """
        try:
            statement = select(Task).where(Task.id == task_id,
                or_(Task.user_id == user_id, Task.assigned_id == user_id)
            )
            result = await self.session.execute(statement)
            task = result.scalars().first()
            return task
        except SQLAlchemyError:
            return None

    async def filter_tasks(
        self, project_id: uuid.UUID, task_status: Optional[str],
        task_priority: Optional[str], user_id: uuid.UUID,
        assignee_id: Optional[uuid.UUID], due_date: Optional[date]
    ) -> List[Task]:
        """
        Filter tasks based on the provided criteria.

        Args:
            project_id (uuid.UUID): The ID of the project to filter tasks by.
            task_status (str, optional): The status of the tasks to filter by.
            task_priority (str, optional): The priority of the tasks to filter by.
            user_id (uuid.UUID): The ID of the user who created the tasks.
            assignee_id (uuid.UUID, optional): The ID of the assignee to filter tasks by.
            due_date (date, optional): The due date to filter tasks by.

        Returns:
            List[Task]: A list of tasks that match the filter criteria.
        """
        try:
            statement = select(Task).where(
                Task.project_id == project_id, or_(
                    Task.user_id == user_id, Task.assigned_id == user_id
                )
            )
            if task_status:
                statement = statement.where(Task.status == TaskStatus(task_status))

            if task_priority:
                statement = statement.where(Task.priority == TaskPriority(task_priority))

            if assignee_id:
                statement = statement.where(Task.assigned_id == assignee_id)

            if due_date:
                statement = statement.where(Task.due_date == due_date)

            result = await self.session.execute(statement)
            tasks = result.scalars().all()
            return tasks
        except SQLAlchemyError:
            return None

    async def delete_task(self, task_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Delete a task by its ID.

        Args:
        task_id (uuid.UUID): The ID of the task to delete.
        user_id (uuid.UUID): The ID of the user who created the task.

        Returns:
        bool: True if the task was deleted. Or None if the task was not found.
        """
        try:
            statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
            result = await self.session.execute(statement)
            task = result.scalars().first()
            if task:
                data={
                    "user_id": task.user_id,
                    "task_id": task.id,
                    "project_id": task.project_id,
                    "description": f"Task {task.id} has been deleted.",
                    "activity_type": ActivityType.DELETE,
                    "entity": "task",
                    "entity_id": task.id
                }

                await self.activity_logs.create_activity(
                    activity_data=data
                )
                await self.session.delete(task)
                await self.session.commit()
                return True
            return None
        except SQLAlchemyError:
            return None

    async def update_task(
        self, task_id: uuid.UUID,
        user_id: uuid.UUID, data: dict
    ) -> Task | None:
        """
        Update a task by its ID in the database.

        Args:
        task_id (uuid.UUID): The ID of the task to update.
        user_id (uuid.UUID): The ID of the user who is updating the task.
        data (dict): The data to update the task with.

        Returns:
        Task: The updated task. Or None if the task was not found.
        """
        try:
            statement = select(Task).where(
                Task.id == task_id, or_(
                    Task.assigned_id == user_id, Task.user_id == user_id
                )
            )
            result = await self.session.execute(statement)
            task = result.scalars().first()
            if task:
                ALLOWED_FIELDS = {
                    "title", "description", "status", "priority", "due_date", "assigned_id"
                }
                for key, value in data.items():
                    if key in ALLOWED_FIELDS:
                        setattr(task, key, value)
                await self.session.commit()
                await self.session.refresh(task)
                data={
                    "user_id": task.user_id,
                    "task_id": task.id,
                    "project_id": task.project_id,
                    "description": f"Task {task.id} has been updated.",
                    "activity_type": ActivityType.UPDATE,
                    "entity": "task",
                    "entity_id": task.id
                }

                await self.activity_logs.create_activity(
                    activity_data=data
                )
                return task
            return None
        except SQLAlchemyError:
            return None


class TaskCommentService:
    """Task comment service."""

    def __init__(self, session: AsyncSession):
        """
        Initialize the TaskCommentService with a database session.

        Args:
        session (AsyncSession): The database session for executing queries.
        """
        self.session = session
        self.activity_logs = ActivityServices(self.session)

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
            data={
                "user_id": comment.user_id,
                "comment_id": comment.id,
                "task_id": comment.task_id,
                "description": f"Task {comment.id} has been created.",
                "activity_type": ActivityType.CREATE,
                "entity": "comment",
                "entity_id": comment.id
            }

            await self.activity_logs.create_activity(
                activity_data=data
            )
            return comment
        except SQLAlchemyError:
            await self.session.rollback()
            return None

    async def get_comment_by_id(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> TaskComment | None:
        """
        Get a comment by its ID.

        Args:
        comment_id (uuid.UUID): The ID of the comment to retrieve.
        user_id (uuid.UUID): The ID of the user who is a member of the team.

        Returns:
        Task: The comment with the specified ID.
        """
        try:
            statement = select(TaskComment).where(TaskComment.id == comment_id)
            result = await self.session.execute(statement)
            comment = result.scalars().first()
            return comment
        except SQLAlchemyError:
            return None

    async def get_comments_by_task_id(self, task_id: uuid.UUID, user_id: uuid.UUID) -> List[TaskComment]:
        """
        Get comments for a specific task.

        Args:
        task_id (uuid.UUID): The ID of the task to retrieve comments for.
        user_id (uuid.UUID): The ID of the user who is a member of the team.

        Returns:
        List[TaskComment]: A list of comments associated with the task.
        """
        try:
            statement = select(TaskComment).where(
                TaskComment.task_id == task_id
            ).order_by(TaskComment.created_at.desc())
            result = await self.session.execute(statement)
            comments = result.scalars().all()
            return comments
        except SQLAlchemyError:
            return None

    async def delete_comment(self, comment_id: uuid.UUID, user_id: uuid.UUID) -> bool | None:
        """
        Delete a comment by its ID.

        Args:
        comment_id (uuid.UUID): The ID of the comment to delete.
        user_id (uuid.UUID): The ID of the user who created the comment.

        Returns:
        bool: True if the comment was deleted. Or None if the comment was not found.
        """
        try:
            statement = select(TaskComment).where(
                TaskComment.user_id == user_id, TaskComment.id == comment_id
            )
            result = await self.session.execute(statement)
            comment = result.scalars().first()
            if comment:
                data={
                    "user_id": comment.user_id,
                    "comment_id": comment.id,
                    "task_id": comment.task_id,
                    "description": f"Task {comment.id} has been deleted.",
                    "activity_type": ActivityType.DELETE,
                    "entity": "comment",
                    "entity_id": comment.id
                }

                await self.activity_logs.create_activity(
                    activity_data=data
                )
                await self.session.delete(comment)
                await self.session.commit()
                return True
            return None
        except SQLAlchemyError:
            return None

    async def update_comment(
        self, comment_id: uuid.UUID,
        user_id: uuid.UUID, data: dict
    ) -> TaskComment | None:
        """
        Update a comment by its ID in the database.

        Args:
        comment_id (uuid.UUID): The ID of the comment to update.
        user_id (uuid.UUID): The ID of the user who created the comment.
        data (dict): The data to update the comment with.

        Returns:
        Task: The updated comment. Or None if the comment was not found.
        """
        try:
            statement = select(TaskComment).where(
                TaskComment.id == comment_id, TaskComment.user_id == user_id
            )
            result = await self.session.execute(statement)
            comment = result.scalars().first()
            if comment:
                for key, value in data.items():
                    setattr(comment, key, value)
                await self.session.commit()
                await self.session.refresh(comment)
                data={
                    "user_id": comment.user_id,
                    "comment_id": comment.id,
                    "task_id": comment.task_id,
                    "description": f"Task {comment.id} has been updated.",
                    "activity_type": ActivityType.UPDATE,
                    "entity": "comment",
                    "entity_id": comment.id
                }

                await self.activity_logs.create_activity(
                    activity_data=data
                )
                return comment
            return None
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
