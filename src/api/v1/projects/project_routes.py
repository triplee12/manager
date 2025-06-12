"""Project routes for the Manager API."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.models.user_models import User
from src.services.project_services import ProjectServices, get_project_services
from src.api.v1.auth.auths import current_active_user

project_router = APIRouter(tags=["projects"])


@project_router.get(
    "/",
    response_model=List,
    status_code=status.HTTP_200_OK
)
async def get_all_projects(
    user_id: Optional[uuid.UUID] = None,
    user: User = Depends(current_active_user),
    project_services: ProjectServices = Depends(get_project_services),
    order: str = Query("asc", min_length=3, max_length=3),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> Optional[List]:
    """
    Retrieve all projects from the database.

    Args:
    order (str): Order of the projects (asc or desc).
    limit (int): Maximum number of projects to retrieve.
    offset (int): Number of projects to skip.

    Returns:
    List: A list of projects.
    """
    try:
        if user.is_superuser and user.role == "admin":
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required")
            projects = await project_services.get_all_projects(
                user_id=user_id, order=order, limit=limit, offset=offset
            )
        projects = await project_services.get_all_projects(
            user_id=user.id, order=order, limit=limit, offset=offset
        )
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error retrieving projects',
        )


@project_router.post(
    "/create/new", status_code=status.HTTP_201_CREATED,
    response_model=uuid.UUID
)
async def create_project(
    project: CreateProject,
    user: User = Depends(current_active_user),
    project_services: ProjectServices = Depends(get_project_services)
) -> uuid.UUID:
    """
    Create a new project.

    Args:
    project (uuid.UUID): The project to be created.

    Returns:
    uuid.UUID: The created project.
    """
    try:
        project_data = project.model_dump().update(user_id=user.id)
        new_project = await project_services.create_project(data=project_data)
        if not new_project:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Project already exists',
            )
        return new_project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error creating project',
        )


@project_router.delete(
    "/{project_id}/delete/project", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_project(
    project_id: uuid.UUID,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
) -> None:
    """
    Delete a project by its ID from the database.

    Args:
    project_id (uuid.UUID): The ID of the project to delete.

    Raises:
    HTTPException: If the project is not found or if an error occurs during deletion.
    """
    try:
        deleted_project = await project_services.delete_project(
            project_id=project_id, user_id=user.id
        )
        if not deleted_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Project not found',
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error deleting project',
        )


@project_router.get(
    "/{project_id}", status_code=status.HTTP_200_OK,
    response_model=ReadProject
)
async def get_project_by_id(
    project_id: uuid.UUID,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
) -> ReadProject:
    """
    Retrieve a project by its ID from the database.

    Args:
    project_id (uuid.UUID): The ID of the project to retrieve.

    Returns:
    ReadProject: The retrieved project.
    """
    try:
        project = await project_services.get_user_project_by_id(
            user_id=user.id, project_id=project_id,
        )
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Project not found',
            )
        return project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error retrieving project',
        )
