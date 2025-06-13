"""Check access utils."""

from functools import wraps
from fastapi import HTTPException
from src.models import project_models, team_models, task_models
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


def require_project_access(project_arg: str, user_arg: str):
    """
    Decorator to ensure the user has access to a project (owner or team member).
    `project_arg` and `user_arg` are the argument names in the function signature.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            project_id = kwargs.get(project_arg)
            user_id = kwargs.get(user_arg)
            if not project_id or not user_id:
                raise HTTPException(status_code=400, detail="Missing project_id or user_id")

            # Access check
            session: AsyncSession = self.session
            project = (await session.execute(select(
                project_models.Project
            ).where(project_models.Project.id == project_id))).scalar_one_or_none()
            if project is None:
                raise HTTPException(status_code=404, detail="Project not found")

            if project.owner_id != user_id:
                membership = (await session.execute(select(team_models.Team).where(
                    team_models.Team.projects.any(project_models.Project.id == project_id),
                    team_models.Team.user_id == user_id
                ))).scalar_one_or_none()

                if membership is None:
                    raise HTTPException(status_code=403, detail="Access denied to project")

            return await func(self, *args, **kwargs)

        return wrapper
    return decorator


def require_task_access(task_arg: str, user_arg: str):
    """
    Decorator to ensure the user has access to a task (assigned to the user).
    `task_arg` and `user_arg` are the argument names in the function signature.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            task_id = kwargs.get(task_arg)
            user_id = kwargs.get(user_arg)
            if not task_id or not user_id:
                raise HTTPException(status_code=400, detail="Missing task_id or user_id")

            # Access check
            session: AsyncSession = self.session
            task = (await session.execute(select(task_models.Task).where(
                task_models.Task.id == task_id
            ))).scalar_one_or_none()
            if task is None:
                raise HTTPException(status_code=404, detail="Task not found")

            if task.assigned_id != user_id:
                membership = (await session.execute(select(team_models.TeamMember).where(
                    team_models.Team.members.any(team_models.TeamMember.id == user_id)
                ))).scalar_one_or_none()

                if membership is None:
                    raise HTTPException(status_code=403, detail="Access denied to task")

            return await func(self, *args, **kwargs)

        return wrapper
    return decorator
