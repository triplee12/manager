"""Project routes for the Manager API."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.models.user_models import User
from src.services.project_services import ProjectServices, get_project_services
from src.schemas.project_schemas import CreateProject, ReadProject, UpdateProject
from src.api.v1.auth.auths import current_active_user
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices, get_activity_service

project_router = APIRouter(tags=["projects"])


@project_router.post(
    "/create/new", status_code=status.HTTP_201_CREATED,
    response_model=ReadProject
)
async def create_project(
    project: CreateProject,
    user: User = Depends(current_active_user),
    project_services: ProjectServices = Depends(get_project_services),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> ReadProject:
    """
    Create a new project.

    Args:
    project (uuid.UUID): The project to be created.

    Returns:
    uuid.UUID: The created project.
    """
    try:
        project_data = project.model_dump()
        project_data["user_id"] = user.id
        new_project = await project_services.create_project(data=project_data)
        if not new_project:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Project already exists or team not found',
            )
        data={
            "user_id": new_project.user_id,
            "team_id": new_project.team_id,
            "project_id": new_project.id,
            "description": f"A new Project with id {str(new_project.id)} has been created.",
            "activity_type": ActivityType.CREATE,
            "entity": "project",
            "entity_id": new_project.id
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return new_project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error creating project',
        ) from e


@project_router.get(
    "",
    response_model=List[ReadProject],
    status_code=status.HTTP_200_OK
)
async def get_all_projects(
    user_id: Optional[uuid.UUID] = None,
    user: User = Depends(current_active_user),
    project_services: ProjectServices = Depends(get_project_services),
    order: str = Query("asc", min_length=3, max_length=3),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[ReadProject]:
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
        ) from e


@project_router.get(
    "/team/project",
    response_model=List[ReadProject],
    status_code=status.HTTP_200_OK
)
async def get_team_projects_for_user(
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
) -> List[ReadProject]:
    """
    Retrieve all projects that the user is a member of from the database.

    Args:
    user_id (uuid.UUID): The ID of the user whose projects to retrieve.

    Returns:
    list: A list of all projects that the user is a member of.
    """
    try:
        projects = await project_services.get_team_projects_for_user(
            user_id=user.id
        )
        if not projects:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Projects not found for you',
            )
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error retrieving projects',
        ) from e


@project_router.get(
    "/{project_id}/team/is_member", status_code=status.HTTP_200_OK,
    response_model=ReadProject
)
async def get_project_if_member(
    project_id: uuid.UUID,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
):
    """
    Retrieve a project by its ID if the user is a member of the project.

    Args:
    project_id (uuid.UUID): The ID of the project to retrieve.

    Returns:
    ReadProject: The project if the user is a member of the project, otherwise None.
    """
    try:
        project = await project_services.get_project_if_member(
            project_id=project_id, user_id=user.id
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
        ) from e


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
        ) from e


@project_router.get(
    "title/{title}", status_code=status.HTTP_200_OK,
    response_model=ReadProject
)
async def get_project_by_title(
    title: str,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
) -> ReadProject:
    """
    Retrieve a project by its title from the database.

    Args:
    title (str): The title of the project to retrieve.

    Returns:
    ReadProject: The retrieved project.
    """
    try:
        project = await project_services.get_user_project_by_title(
            user_id=user.id, project_title=title,
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
        ) from e


@project_router.get(
    "/team/{team_id}", status_code=status.HTTP_200_OK,
    response_model=List[ReadProject]
)
async def get_projects_by_team_id(
    team_id: uuid.UUID, order: str = Query("asc", min_length=3, max_length=3),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
) -> List[ReadProject]:
    """
    Retrieve projects associated with a team by its ID from the database.

    Args:
    team_id (uuid.UUID): The ID of the team to retrieve projects for.

    Returns:
    List: A list of projects associated with the team.
    """
    try:
        projects = await project_services.get_all_team_projects(
            team_id=team_id, owner_id=user.id,
            order=order, limit=limit, offset=offset
        )
        return projects
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error retrieving projects',
        ) from e


@project_router.get(
    "/{project_id}/user/{user_id}", status_code=status.HTTP_200_OK,
    response_model=ReadProject
)
async def get_project_by_project_id_and_user_id(
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user)
) -> ReadProject:
    """
    Retrieve a project by its ID and user ID from the database.

    Args:
    project_id (uuid.UUID): The ID of the project to retrieve.
    user_id (uuid.UUID): The ID of the user to retrieve the project for.

    Returns:
    ReadProject: The retrieved project.
    """
    try:
        if user.is_superuser or user.role == "admin":
            if not user_id:
                raise HTTPException(status_code=400, detail="User ID is required")
            project = await project_services.get_user_project_by_id(
                user_id=user_id, project_id=project_id
            )
            if not project:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='Project not found',
                )
            return project
        project = await project_services.get_user_project_by_id(
            user_id=user.id, project_id=project_id
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
        ) from e


@project_router.patch(
    "/{project_id}/update", status_code=status.HTTP_200_OK,
    response_model=ReadProject
)
async def update_project(
    project_id: uuid.UUID,
    project: UpdateProject,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
) -> ReadProject:
    """
    Update a project by its ID in the database.

    Args:
    project_id (uuid.UUID): The ID of the project to update.
    project (UpdateProject): The updated project data.

    Returns:
    ReadProject: The updated project.
    """
    try:
        updated_project = await project_services.update_project(
            project_id=project_id, user_id=user.id, data=project.model_dump()
        )
        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Project not found',
            )
        data={
            "user_id": updated_project.user_id,
            "team_id": updated_project.team_id,
            "project_id": updated_project.id,
            "description": f"Project with id {str(updated_project.id)} has been updated.",
            "activity_type": ActivityType.UPDATE,
            "entity": "project",
            "entity_id": updated_project.id
        }

        await activity_logs.create_activity(
            activity_data=data
        )
        return updated_project
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error updating project',
        ) from e


@project_router.delete(
    "/{project_id}/delete", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_project(
    project_id: uuid.UUID,
    project_services: ProjectServices = Depends(get_project_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
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
        data={
            "user_id": deleted_project.user_id,
            "team_id": deleted_project.team_id,
            "project_id": deleted_project.id,
            "description": f"Project with id {str(deleted_project.id)} has been deleted.",
            "activity_type": ActivityType.DELETE,
            "entity": "project",
            "entity_id": deleted_project.id
        }

        await activity_logs.create_activity(
            activity_data=data
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Error deleting project',
        ) from e
