"""Task routes for the API."""

from datetime import date
from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.models.user_models import User
from src.services.task_services import TaskServices, get_task_services
from src.schemas.task_schemas import CreateTask, ReadTask, UpdateTask
from src.api.v1.auth.auths import current_active_user
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices, get_activity_service

task_router = APIRouter(tags=["tasks"])


@task_router.post(
    "/create/new", status_code=status.HTTP_201_CREATED,
    response_model=Optional[ReadTask]
)
async def create_task(
    task: CreateTask,
    task_manager: TaskServices = Depends(get_task_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> Optional[ReadTask]:
    """
    Create a new task.

    Args:
        task (CreateTask): New task to be created.
        task_manager (TaskServices, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        Optional[ReadTask]: _description_
    """
    try:
        task_data = task.model_dump()
        task_data["user_id"] = user.id
        new_task = await task_manager.create_task(task_data)
        if not new_task:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error creating task"
            )
        data={
            "user_id": new_task.user_id,
            "task_id": new_task.id,
            "project_id": new_task.project_id,
            "description": f"A new Task with id {str(new_task.id)} has been created.",
            "activity_type": ActivityType.CREATE,
            "entity": "task",
            "entity_id": str(new_task.id)
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return new_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e


@task_router.get(
    "/project/{project_id}", status_code=status.HTTP_200_OK,
    response_model=Optional[List[ReadTask]]
)
async def get_all_tasks_by_project_id(
    project_id: uuid.UUID, order: str = Query(...),
    limit: int = Query(...), offset: int = Query(...),
    task_manager: TaskServices = Depends(get_task_services),
    user: User = Depends(current_active_user)
) -> Optional[List[ReadTask]]:
    """
    Get all tasks for a specific project.

    Args:
        project_id (uuid.UUID): _description_
        order (str, optional): _description_. Defaults to Query(...).
        limit (int, optional): _description_. Defaults to Query(...).
        offset (int, optional): _description_. Defaults to Query(...).
        task_manager (TaskServices, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).
, user.id
    Returns:
        Optional[List[ReadTask]]: _description_
    """
    try:
        tasks = await task_manager.get_tasks_by_project_id(
            project_id=project_id, user_id=user.id,
            order=order, limit=limit, offset=offset
        )
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tasks found for this project"
            )
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting tasks"
        ) from e


@task_router.get(
    "/{task_id}", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTask]
)
async def get_task_by_id(
    task_id: uuid.UUID,
    task_manager: TaskServices = Depends(get_task_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTask]:
    """
    Get a task by its ID.

    Args:
        task_id (uuid.UUID): The ID of the task to retrieve.
        task_manager (TaskServices, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        Optional[ReadTask]: _description_
    """
    try:
        task = await task_manager.get_task_by_id(task_id, user.id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        return task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting task"
        ) from e


@task_router.get(
    "/filter/project/{project_id}", status_code=status.HTTP_200_OK,
    response_model=Optional[List[ReadTask]]
)
async def filter_tasks(
    project_id: uuid.UUID, task_status: Optional[str],
    task_priority: Optional[str], assignee_id: Optional[uuid.UUID],
    due_date: Optional[date],
    task_manager: TaskServices = Depends(get_task_services),
    user: User = Depends(current_active_user)
) -> Optional[List[ReadTask]]:
    """
    Filter tasks based on the provided criteria.

    Args:
        project_id (uuid.UUID): The ID of the project to filter tasks by.
        task_status (str, optional): The status of the tasks to filter by.
        task_priority (str, optional): The priority of the tasks to filter by.
        assignee_id (uuid.UUID, optional): The ID of the assignee to filter tasks by.
        due_date (date, optional): The due date to filter tasks by.

    Returns:
        Optional[List[ReadTask]]: A list of tasks that match the filter criteria.
    """
    try:
        tasks = await task_manager.filter_tasks(
            project_id, task_status, task_priority,
            user.id, assignee_id, due_date
        )
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tasks found for this project"
            )
        return tasks
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error getting tasks"
        ) from e


@task_router.patch(
    "/{task_id}/update", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTask]
)
async def update_task(
    task_id: uuid.UUID,
    task: UpdateTask,
    task_manager: TaskServices = Depends(get_task_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> Optional[ReadTask]:
    """
    Update a task.

    Args:
        task_id (uuid.UUID): The ID of the task to update.
        task (UpdateTask): _description_
        task_manager (TaskServices, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        Optional[ReadTask]: _description_
    """
    try:
        task_data = task.model_dump()
        updated_task = await task_manager.update_task(
            task_id, user.id, task_data
        )
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Error updating task"
            )
        data={
            "user_id": updated_task.user_id,
            "task_id": updated_task.id,
            "project_id": updated_task.project_id,
            "description": f"Task with id {str(updated_task.id)} has been updated.",
            "activity_type": ActivityType.UPDATE,
            "entity": "task",
            "entity_id": str(updated_task.id)
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return updated_task
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e


@task_router.delete(
    "/{task_id}/delete", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTask]
)
async def delete_task(
    task_id: uuid.UUID,
    task_manager: TaskServices = Depends(get_task_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> Optional[ReadTask]:
    """
    Delete a task.

    Args:
        task_id (uuid.UUID): The ID of the task to delete.
        task_manager (TaskServices, optional): Defaults to Depends(get_task_services).
        user (User, optional): Defaults to Depends(current_active_user).

    Returns:
        None
    """
    try:
        deleted_task = await task_manager.delete_task(task_id, user.id)
        if not deleted_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )
        data={
            "user_id": deleted_task.user_id,
            "task_id": deleted_task.id,
            "project_id": deleted_task.project_id,
            "description": f"Task with id {str(deleted_task.id)} has been deleted.",
            "activity_type": ActivityType.DELETE,
            "entity": "task",
            "entity_id": str(deleted_task.id)
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server error"
        ) from e
