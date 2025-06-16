"""Team member routes."""

from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from src.models.user_models import User
from src.services.team_services import TeamMemberServices, get_team_member_services
from src.schemas.team_schemas import CreateTeamMember, ReadTeamMember
from src.api.v1.auth.auths import current_active_user
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices, get_activity_service

team_member_router = APIRouter(tags=["team members"])


@team_member_router.post(
    "/add/new", status_code=status.HTTP_201_CREATED,
    response_model=ReadTeamMember
)
async def create_team_member(
    team_member: CreateTeamMember,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
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
        data={
            "user_id": new_team_member.user_id,
            "team_id": new_team_member.team_id,
            "description": f"""User with id {str(new_team_member.user_id)}
                            has been added to team {str(new_team_member.team_id)}.""",
            "activity_type": ActivityType.CREATE,
            "entity": "team_member",
            "entity_id": new_team_member.id
        }

        await activity_logs.create_activity(
            activity_data=data
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
    team_id: uuid.UUID, owner_id: Optional[uuid.UUID] = None,
    order: Optional[str] = "asc",
    limit: Optional[int] = 10, offset: Optional[int] = 0,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user)
) -> List[ReadTeamMember]:
    """
    Retrieve all team members from the database.

    Args:
    team_id (uuid.UUID): The ID of the team whose members to retrieve.
    owner_id (uuid.UUID): The ID of the user who owns the team.
    order (str): Order of the team members (asc or desc).
    limit (int): Maximum number of team members to retrieve.
    offset (int): Number of team members to skip.

    Returns:
    List[ReadTeamMember]: A list of all team members.

    Raises:
    HTTPException: If the user is not authorized.
    """
    try:
        if user.is_superuser or user.role == "admin":
            if not owner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Owner ID is required"
                )
            team_members = await team_member_manager.get_team_members(
                team_id=team_id, team_owner_id=owner_id,
                order=order, limit=limit, offset=offset
            )
            return team_members
        team_members = await team_member_manager.get_team_members(
                team_id=team_id, team_owner_id=user.id,
                order=order, limit=limit, offset=offset
            )
        return team_members
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
    team_member_id: uuid.UUID, owner_id: Optional[uuid.UUID] = None,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user)
) -> Optional[ReadTeamMember]:
    """
    Retrieve a team member by its ID from the database.

    Args:
    team_member_id (uuid.UUID): The ID of the team member to retrieve.
    owner_id (uuid.UUID): The ID of the user who owns the team.

    Returns:
    ReadTeamMember: The team member with the specified ID.

    Raises:
    HTTPException: If the user is not authorized, or if the team member is not found.
    """
    try:
        if user.is_superuser or user.role == "admin":
            if not owner_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Owner ID is required"
                )
            team_member = await team_member_manager.get_member_by_id(
                member_id=team_member_id, team_owner_id=owner_id
            )
            if not team_member:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Team member not found"
                )
            return team_member
        team_member = await team_member_manager.get_member_by_id(
            member_id=team_member_id, team_owner_id=user.id
        )
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        return team_member
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while getting the team member"
        ) from e


@team_member_router.delete(
    "/{team_member_id}/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_team_member_by_id(
    team_member_id: uuid.UUID, team_id: uuid.UUID,
    team_member_manager: TeamMemberServices = Depends(get_team_member_services),
    user: User = Depends(current_active_user),
    activity_logs: ActivityServices = Depends(get_activity_service)
):
    """
    Delete a team member by its ID from the database.

    Args:
    team_member_id (uuid.UUID): The ID of the team member to delete.
    team_id (uuid.UUID): The ID of the team whose member to delete.

    Returns:
    None

    Raises:
    HTTPException: If the user is not authorized, or if the team member is not found.
    """
    try:
        team_member = await team_member_manager.remove_member_from_team(
            team_owner_id=user.id, team_id=team_id, user_id=team_member_id
        )
        if not team_member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team member not found"
            )
        data={
            "user_id": team_member_id,
            "team_id": team_id,
            "description": f"""User with id {str(team_member_id)}
                            has been removed from team {str(team_id)}.""",
            "activity_type": ActivityType.DELETE,
            "entity": "team_member",
            "entity_id": team_member_id
        }
        await activity_logs.create_activity(
            activity_data=data
        )
        return
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while deleting the team member"
        ) from e
