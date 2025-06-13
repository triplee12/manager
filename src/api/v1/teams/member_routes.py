"""Team member routes."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.models.user_models import User
from src.services.team_services import TeamMemberServices, get_team_member_services
from src.schemas.team_schemas import CreateTeamMember, ReadTeamMember
from src.api.v1.auth.auths import current_active_user

team_member_router = APIRouter(tags=["team members"])


@team_member_router.post(
    "/add/new", status_code=status.HTTP_201_CREATED,
    response_model=ReadTeamMember
)
async def create_team_member(
    team_member: CreateTeamMember,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user)
) -> ReadTeamMember:
    """
    Create a new team member.

    Args:
    team_member (CreateTeamMember): The team member to be created.

    Returns:
    ReadTeamMember: The created team member.

    Raises:
    HTTPException: If the user is not authorized, or if the team member already exists.
    """
    try:
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        team_member_data = team_member.model_dump()
        new_team_member = await team_member_manager.add_member_to_team(
            team_owner_id=user.id,
            data=team_member_data
        )
        if not new_team_member:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Team member already exists"
            )
        return new_team_member
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the team member"
        ) from e


@team_member_router.get(
    "/all", status_code=status.HTTP_200_OK,
    response_model=List[ReadTeamMember]
)
async def get_all_team_members(
    team_id: uuid.UUID, order: str = Query(...),
    limit: int = Query(...), offset: int = Query(...),
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user)
) -> List[ReadTeamMember]:
    """
    Retrieve all team members from the database.

    Args:
    team_id (uuid.UUID): The ID of the team whose members to retrieve.
    order (str): Order of the team members (asc or desc).
    limit (int): Maximum number of team members to retrieve.
    offset (int): Number of team members to skip.

    Returns:
    List[ReadTeamMember]: A list of all team members.

    Raises:
    HTTPException: If the user is not authorized.
    """
    try:
        if not user.is_superuser or user.role != "admin":
            team_members = await team_member_manager.get_team_members(
                team_id=team_id, team_owner_id=user.id,
                order=order, limit=limit, offset=offset
            )
            return team_members
        team_members = await team_member_manager.get_team_members(
            team_id=team_id, order=order, limit=limit, offset=offset
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the team members"
        ) from e


@team_member_router.get(
    "/{team_member_id}", status_code=status.HTTP_200_OK,
    response_model=Optional[ReadTeamMember]
)
async def get_team_member_by_id(
    team_member_id: uuid.UUID,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTeamMember]:
    """
    Retrieve a team member by its ID from the database.

    Args:
    team_member_id (uuid.UUID): The ID of the team member to retrieve.

    Returns:
    ReadTeamMember: The team member with the specified ID.

    Raises:
    HTTPException: If the user is not authorized, or if the team member is not found.
    """
    try:
        if not user.is_superuser or user.role != "admin":  
            team_member = await team_member_manager.get_member_by_id(
                member_id=team_member_id, team_owner_id=user.id
            )
            if not team_member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found"
                )
            return team_member
        team_member = await team_member_manager.get_member_by_id(
            member_id=team_member_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the team member"
        ) from e


@team_member_router.delete(
    "/{team_member_id}/delete", status_code=status.HTTP_200_OK,
    response_model=ReadTeamMember
)
async def delete_team_member_by_id(
    team_member_id: uuid.UUID, team_id: uuid.UUID,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user)
) -> ReadTeamMember:
    """
    Delete a team member by its ID from the database.

    Args:
    team_member_id (uuid.UUID): The ID of the team member to delete.
    team_id (uuid.UUID): The ID of the team whose member to delete.

    Returns:
    ReadTeamMember: The deleted team member.

    Raises:
    HTTPException: If the user is not authorized, or if the team member is not found.
    """
    try:
        team_member = await team_member_manager.remove_member_from_team(
            team_owner_id=user.id, team_id=team_id, user_id=team_member_id
        )
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Team member not found"
            )
        return team_member
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the team member"
        ) from e
