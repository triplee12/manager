"""Activity routes for the Manager API."""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices, get_activity_service
from src.schemas.activity_schemas import CreateActivity, ReadActivity
from src.api.v1.auth.auths import current_active_user
from src.models.user_models import User

activity_router = APIRouter(tags=["activities"])


@activity_router.post("/create/new", response_model=ReadActivity)
async def create_activity(
    activity: CreateActivity,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Create a new activity log.

    Args:
    activity (CreateActivity): The activity log to create.

    Returns:
    ReadActivity: The created activity log.
    """
    try:
        activity_data = activity.model_dump()
        activity_data["user_id"] = user.id
        return await activity_services.create_activity(
            activity_data=activity_data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "", response_model=List[ReadActivity]
)
async def get_activities(
    project_id: UUID, order: str = "asc", limit: int = 10, offset: int = 0,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve activities for a given project.

    Args:
    project_id (UUID): The ID of the project whose activities to retrieve.
    order (str): Order of the activities (asc or desc).
    limit (int): Maximum number of activities to retrieve.
    offset (int): Number of activities to skip.

    Returns:
    List[ReadActivity]: A list of ReadActivity objects representing the retrieved activities.
    """
    try:
        activities = await activity_services.get_all_activities(
            project_id=project_id,
            user_id=user.id, order=order,
            limit=limit, offset=offset
        )
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activities not found"
            )
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "/users/{user_id}/activities", response_model=List[ReadActivity]
)
async def get_user_activities(
    user_id: UUID, order: str = "asc", limit: int = 10, offset: int = 0,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve activities for a specific user.

    Args:
    user_id (UUID): The ID of the user whose activities to retrieve.
    order (str): Order of the activities (asc or desc).
    limit (int): Maximum number of activities to retrieve.
    offset (int): Number of activities to skip.

    Returns:
    List[ReadActivity]: A list of ReadActivity objects representing the retrieved activities.
    """
    try:
        activities = await activity_services.get_all_user_activities(
            user_id=user_id, order=order,
            limit=limit, offset=offset
        )
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activities not found"
            )
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "/teams/{team_id}/tasks/{task_id}/activities", response_model=List[ReadActivity]
)
async def get_team_activities(
    team_id: UUID, task_id: UUID,
    order: str = "asc", limit: int = 10, offset: int = 0,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve activities for a specific team and user.

    Args:
    team_id (UUID): The ID of the team whose activities to retrieve.
    task_id (UUID): The ID of the task whose activities to retrieve.
    order (str): Order of the activities (asc or desc).
    limit (int): Maximum number of activities to retrieve.
    offset (int): Number of activities to skip.

    Returns:
    List[ReadActivity]: A list of ReadActivity objects representing the retrieved activities.
    """
    try:
        activities = await activity_services.get_all_team_activities(
            team_id=team_id, task_id=task_id,
            user_id=user.id, order=order,
            limit=limit, offset=offset
        )
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activities not found"
            )
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "/projects/{project_id}/activities", response_model=List[ReadActivity]
)
async def get_project_activities(
    project_id: UUID, order: str = "asc", limit: int = 10, offset: int = 0,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve activities for a specific project and user.

    Args:
    project_id (UUID): The ID of the project whose activities to retrieve.
    order (str): Order of the activities (asc or desc).
    limit (int): Maximum number of activities to retrieve.
    offset (int): Number of activities to skip.

    Returns:
    List[ReadActivity]: A list of ReadActivity objects representing the retrieved activities.
    """
    try:
        activities = await activity_services.get_all_project_activities(
            project_id=project_id, user_id=user.id, order=order,
            limit=limit, offset=offset
        )
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activities not found"
            )
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "/{activity_id}/projects/{project_id}/activities", response_model=ReadActivity
)
async def get_activity_by_id(
    activity_id: UUID, project_id: UUID,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve an activity log by its ID.

    Args:
    activity_id (UUID): The ID of the activity log to retrieve.

    Returns:
    ReadActivity: The retrieved activity log.
    """
    try:
        activity = await activity_services.get_activity_by_id(
            project_id=project_id,
            user_id=user.id,
            activity_id=activity_id
        )
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
        return activity
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "/tasks/{task_id}/activities", response_model=List[ReadActivity]
)
async def get_task_activities(
    task_id: UUID, order: str = "asc", limit: int = 10, offset: int = 0,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve all activities for a specific task from the database.

    Args:
    task_id (UUID): The ID of the task whose activities to retrieve.
    order (str): Order of the activities (asc or desc).
    limit (int): Maximum number of activities to retrieve.
    offset (int): Number of activities to skip.

    Returns:
    List[ReadActivity]: A list of ReadActivity objects representing the retrieved activities.
    """
    try:
        activities = await activity_services.get_all_task_activities(
            task_id=task_id, user_id=user.id,
            order=order, limit=limit, offset=offset
        )
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activities not found"
            )
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.get(
    "/filter", response_model=List[ReadActivity]
)
async def filter_activities(
    project_id: UUID, activity_type: ActivityType,
    entity: Optional[str] = None,
    order: str = "asc", limit: int = 10, offset: int = 0,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Retrieve activities filtered by type and entity from the database.

    Args:
    project_id (UUID): The ID of the project whose activities to retrieve.
    activity_type (ActivityType): The type of activities to filter.
    entity (Optional[str]): The entity to filter for. Defaults to None.
    order (str): Order of the activities (asc or desc). Defaults to "asc".
    limit (int): Maximum number of activities to retrieve. Defaults to 10.
    offset (int): Number of activities to skip. Defaults to 0.

    Returns:
    List[ReadActivity]: A list of ReadActivity objects representing the filtered activities.
    """
    try:
        activities = await activity_services.filter_activities(
            project_id=project_id,
            activity_type=activity_type,
            entity=entity,
            user_id=user.id,
            order=order,
            limit=limit,
            offset=offset
        )
        if not activities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activities not found"
            )
        return activities
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


@activity_router.delete(
    "/{activity_id}/projects/{project_id}/delete", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_activity_by_id(
    activity_id: UUID, project_id: UUID,
    activity_services: ActivityServices = Depends(get_activity_service),
    user: User = Depends(current_active_user),
):
    """
    Delete an activity log by its ID.

    Args:
    activity_id (UUID): The ID of the activity log to delete.

    Returns:
    None
    """
    try:
        activity = await activity_services.delete_activity(
            activity_id=activity_id,
            project_id=project_id,
            user_id=user.id
        )
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e
