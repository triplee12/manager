"""Team routes."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.models.user_models import User
from src.services.team_services import TeamServices, get_team_services
from src.schemas.team_schemas import CreateTeam, ReadTeam, UpdateTeam
from src.api.v1.auth.auths import current_active_user

team_router = APIRouter(tags=["teams"])


@team_router.post(
    "/create/new", status_code=status.HTTP_201_CREATED,
    response_model=ReadTeam
)
async def create_team(
    team: CreateTeam,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> ReadTeam:
    """
    Create a new team.

    Args:
    team (CreateTeam): The team to be created.

    Returns:
    ReadTeam: The created team.

    Raises:
    HTTPException: If the user is not authorized, or if the team already exists.
    """
    try:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        team_data = team.model_dump().update({"user_id": user.id})
        new_team = await team_manager.create_team(data=team_data)
        if not new_team:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Team already exists"
            )
        return new_team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team"
        )


@team_router.get(
    "/", status_code=status.HTTP_200_OK,
    response_model=Optional[List[ReadTeam]]
)
async def get_all_teams(
    order: str = Query(...),
    limit: int = Query(...), offset: int = Query(...),
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> Optional[List[ReadTeam]]:
    """
    Retrieve all teams from the database.

    Args:
    order (str): Order of the teams (asc or desc).
    limit (int): Maximum number of teams to retrieve.
    offset (int): Number of teams to skip.

    Returns:
    List[ReadTeam]: A list of teams.

    Raises:
    HTTPException: If the user is not authorized, or if an error occurs.
    """
    try:
        if not user.is_superuser and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        teams = await team_manager.get_all_teams(
            order=order, limit=limit, offset=offset
        )
        return teams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting all teams"
        )


@team_router.get(
    "/{team_id}", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTeam]
)
async def get_team_by_id(
    team_id: uuid.UUID,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTeam]:
    """
    Retrieve a team by its ID from the database.

    Args:
    team_id (uuid.UUID): The ID of the team to retrieve.

    Returns:
    ReadTeam: The team with the specified ID.

    Raises:
    HTTPException: If the user is not authorized, or if the team is not found.
    """
    try:
        if not user.is_superuser and user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        team = await team_manager.get_team_by_id(team_id=team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )
        return team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the team"
        )


@team_router.get(
    "/{team_name}/user", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTeam]
)
async def get_user_team_by_name(
    team_name: str, owner_id: Optional[uuid.UUID] = None,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTeam]:
    """
    Retrieve a team by its name associated with a user from the database.

    Args:
    team_name (str): The name of the team to retrieve.
    owner_id (Optional[uuid.UUID]): The ID of the user whose team to retrieve.
                                   Required for superusers.

    Returns:
    ReadTeam: The team with the specified name associated with the user.

    Raises:
    HTTPException: If the user is not authorized, or if the team is not found.
    """
    try:
        if user.is_superuser or user.role == "admin":
            if not owner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Owner ID is required for superusers"
                )
            team = await team_manager.get_user_team_by_name(
                user_id=owner_id, team_name=team_name
            )
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )
            return team
        else:
            team = await team_manager.get_user_team_by_name(
                user_id=user.id, team_name=team_name
            )
            if not team:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
                )
            return team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the team"
        )


@team_router.get(
    "/{team_id}/user", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTeam]
)
async def get_user_team_by_id(
    team_id: uuid.UUID,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTeam]:
    """
    Retrieve a team by its ID associated with a user from the database.

    Args:
    team_id (uuid.UUID): The ID of the team to retrieve.

    Returns:
    ReadTeam: The team with the specified ID associated with the user.

    Raises:
    HTTPException: If the user is not authorized, or if the team is not found.
    """
    try:
        team = await team_manager.get_user_team_by_id(
            user_id=user.id, team_id=team_id
        )
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )
        return team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the team"
        )


@team_router.get(
    "/user/total/teams", status_code=status.HTTP_200_OK,
)
async def get_user_total_teams(
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> int:
    """
    Retrieve the total number of teams associated with the current user.

    Args:
    team_manager (TeamServices): The service to manage team-related operations.
    user (User): The current authenticated user.

    Returns:
    int: The total number of teams the user is associated with.

    Raises:
    HTTPException: If an error occurs while retrieving the total number of teams.
    """

    try:
        total_teams = await team_manager.get_total_teams(user_id=user.id)
        return total_teams
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the total teams"
        )


@team_router.get(
    "/{team_id}/total/members", status_code=status.HTTP_200_OK,
)
async def get_total_members(
    team_id: uuid.UUID,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> int:
    """
    Retrieve the total number of members associated with a team.

    Args:
    team_id (uuid.UUID): The ID of the team whose members to retrieve.

    Returns:
    int: The total number of members associated with the team.

    Raises:
    HTTPException: If the user is not authorized, or if an error occurs while
                   retrieving the total number of members.
    """
    try:
        if not user.is_superuser or user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        total_members = await team_manager.get_total_members(team_id=team_id)
        return total_members
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the total members"
        )


@team_router.patch(
    "/{team_id}/update/team", status_code=status.HTTP_200_OK,
    response_model=ReadTeam
)
async def update_team(
    team_id: uuid.UUID, team: UpdateTeam,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> ReadTeam:
    """
    Update a team by its ID in the database.

    Args:
    team_id (uuid.UUID): The ID of the team to update.
    team (UpdateTeam): The data to update the team with.

    Returns:
    ReadTeam: The updated team. Or None if the team was not found.

    Raises:
    HTTPException: If the user is not authorized, or if an error occurs.
    """
    try:
        updated_team = await team_manager.update_team(
            team_id=team_id, user_id=user.id, data=team.model_dump()
        )
        if not updated_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )
        return updated_team
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the team"
        )


@team_router.delete(
    "/{team_id}/delete/team", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_team(
    team_id: uuid.UUID,
    team_manager: TeamServices = Depends(get_team_services),
    user: User = Depends(current_active_user)
) -> None:
    """
    Delete a team by its ID from the database.

    Args:
    team_id (uuid.UUID): The ID of the team to delete.

    Raises:
    HTTPException: If the team is not found or if an error occurs during deletion.
    """

    try:
        deleted_team = await team_manager.delete_team(team_id=team_id, user_id=user.id)
        if not deleted_team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the team"
        )
