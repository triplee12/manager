"""User routers"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from src.models.user_models import User
from src.services.user_services import UserManager, get_user_db
from src.schemas.user_schemas import UserRead
from src.api.v1.auth.auths import current_active_user

user_router = APIRouter(tags=["users"])


@user_router.get(
    "/users", status_code=status.HTTP_200_OK,
    response_model=Optional[UserRead]
)
async def get_all_users(
    order: str = Query(...),
    limit: int = Query(...), offset: int = Query(...),
    user_manager: UserManager = Depends(get_user_db),
    user: User = Depends(current_active_user)
) -> Optional[UserRead]:
    """
    Retrieve all users from the database.

    Args:
        order (str): Order of the users (asc or desc).
        limit (int): Maximum number of users to retrieve.
        offset (int): Number of users to skip.

    Returns:
        List[User]: A list of users both admin and non-admin.
    """
    try:
        if not user.is_superuser and not user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        users = await user_manager.get_all_users(
            order=order, limit=limit, offset=offset
        )
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@user_router.get(
    "/admins", status_code=status.HTTP_200_OK,
    response_model=List[UserRead]
)
async def get_all_admins(
    order: str = Query(...),
    limit: int = Query(...), offset: int = Query(...),
    user_manager: UserManager = Depends(get_user_db),
    user: User = Depends(current_active_user)
) -> List[UserRead]:
    """
    Retrieve all admin users from the database.

    Args:
        order (str): Order of the users (asc or desc).
        limit (int): Maximum number of users to retrieve.
        offset (int): Number of users to skip.

    Returns:
        List[User]: A list of admin users.
    """
    try:
        if not user.is_superuser and not user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        admins = await user_manager.get_all_admins(
            order=order, limit=limit, offset=offset
        )
        return admins
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )


@user_router.get(
    "/members", status_code=status.HTTP_200_OK,
    response_model=List[UserRead]
)
async def get_all_members(
    order: str = Query(...),
    limit: int = Query(...), offset: int = Query(...),
    user_manager: UserManager = Depends(get_user_db),
    user: User = Depends(current_active_user)
) -> List[UserRead]:
    """
    Retrieve all member users from the database.

    Args:
        order (str): Order of the users (asc or desc).
        limit (int): Maximum number of users to retrieve.
        offset (int): Number of users to skip.

    Returns:
        List[User]: A list of member users.
    """
    try:
        if not user.is_superuser and not user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
            )
        members = await user_manager.get_all_members(
            order=order, limit=limit, offset=offset
        )
        return members
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error"
        )
