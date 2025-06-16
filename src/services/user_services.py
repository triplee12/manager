"""User services for the Manager API."""

import uuid
from typing import Any, Dict, Optional, Union, List
from fastapi import Depends, Request, Response
from sqlalchemy import select, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users import BaseUserManager, InvalidPasswordException, UUIDIDMixin
from fastapi_users.db import SQLAlchemyUserDatabase
from src.core.configs import settings
from src.models.user_models import User
from src.db.db_session import get_async_session
from src.schemas.user_schemas import UserCreate
from src.models.activity_models import ActivityType
from src.services.activity_services import ActivityServices

SECRET = settings.OAUTH_SECRET


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """User manager for the Manager API."""

    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    def __init__(self, user_db, session: AsyncSession):
        """
        Initialize the UserManager with a user database and a database session.

        Args:
        user_db: The user database to be used for managing user data.
        session (AsyncSession): The database session for executing queries.
        """

        super().__init__(user_db)
        self.session = session
        self.activity_logs = ActivityServices(self.session)

    async def create(
        self,
        user_create,
        safe: bool = False,
        request: Optional[Request] = None,
    ) -> User:
        """
        Create a new user.

        Args:
        user_create (UserCreate): The user data to be created.
        safe (bool): Whether to create the user in a safe way.
        request (Optional[Request]): The request that triggered the user creation.

        Returns:
        User: The created user.
        """

        user = await super().create(user_create, safe=safe, request=request)
        await self.session.refresh(user)

        user_id = user.id
        data={
                "user_id": user_id,
                "description": f"A new User with id {str(user_id)} has registered.",
                "activity_type": ActivityType.CREATE,
                "entity": "user",
                "entity_id": user_id,
            }

        await self.activity_logs.create_activity(
            activity_data=data
        )
        print(
            f"User {user_id} has registered from {request.client.host}"
        )

        return user

    async def get_all_users(
        self, order: str = "asc",
        limit: int = 20, offset: int = 0
    ) -> List[User]:
        """
        Retrieve all users from the database.

        Args:
            limit (int): Maximum number of users to retrieve.
            offset (int): Number of users to skip.

        Returns:
            List[User]: A list of users both admin and non-admin.
        """
        statement = select(User)
        if order == "desc":
            statement = statement.order_by(desc(User.created_at))
        else:
            statement = statement.order_by(asc(User.created_at))
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        users = result.scalars().all()
        return users

    async def get_all_admins(
        self, order: str = "asc",
        limit: int = 20, offset: int = 0
    ) -> List[User]:
        """
        Retrieve all admin users from the database.

        Args:
            order (str): Order of the users (asc or desc).
            limit (int): Maximum number of users to retrieve.
            offset (int): Number of users to skip.

        Returns:
            List[User]: A list of admin users.
        """
        statement = select(User).where(User.role == "admin")
        if order == "desc":
            statement = statement.order_by(desc(User.created_at))
        else:
            statement = statement.order_by(asc(User.created_at))
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        users = result.scalars().all()
        return users

    async def get_all_members(
        self, order: str = "asc",
        limit: int = 20, offset: int = 0
    ) -> List[User]:
        """
        Retrieve all member users from the database.

        Args:
            order (str): Order of the users (asc or desc).
            limit (int): Maximum number of users to retrieve.
            offset (int): Number of users to skip.

        Returns:
            List[User]: A list of member users.
        """
        statement = select(User).where(User.role == "member")
        if order == "desc":
            statement = statement.order_by(desc(User.created_at))
        else:
            statement = statement.order_by(asc(User.created_at))
        statement = statement.limit(limit).offset(offset)
        result = await self.session.execute(statement)
        users = result.scalars().all()
        return users

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Triggered after a user registers.
        
        Args:
        user (User): The newly-created user.
        request (Optional[Request]): The request that triggered the registration.
        """
        print(f"User {user.id} has registered from {request.client.host}.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Triggered after a user has forgotten their password.

        Args:
        user (User): The user that forgot their password.
        token (str): The password reset token sent to the user.
        request (Optional[Request]): The request that triggered the password reset.
        """
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_reset_password(self, user: User, request: Optional[Request] = None):
        """
        Triggered after a user has reset their password.

        Args:
        user (User): The user that reset their password.
        request (Optional[Request]): The request that triggered the password reset.
        """
        print(f"User {user.id} has reset their password.")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Triggered after a user requests a verification.

        Args:
        user (User): The user that requested verification.
        token (str): The verification token sent to the user.
        request (Optional[Request]): The request that initiated the verification process.
        """
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    async def on_after_verify(
        self, user: User, request: Optional[Request] = None
    ):
        """
        Triggered after a user has been verified.

        Args:
        user (User): The user that was verified.
        request (Optional[Request]): The request that initiated the verification process.
        """
        print(f"User {user.id} has been verified")

    async def validate_password(
        self,
        password: str,
        user: Union[UserCreate, User],
    ) -> None:
        """
        Validate a password against a user.

        Args:
        password (str): The password to check.
        user (Union[UserCreate, User]): The user to check against.

        Raises:
        InvalidPasswordException: If the password is invalid.
        """
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )

    async def on_after_update(
        self,
        user: User,
        update_dict: Dict[str, Any],
        request: Optional[Request] = None,
    ):
        """
        Triggered after a user has been updated.

        Args:
        user (User): The user that was updated.
        update_dict (Dict[str, Any]): A dictionary of the fields that were updated.
        request (Optional[Request]): The request that initiated the update process.
        """
        await self.activity_logs.create_activity(
            activity_data = {
                "user_id": user.id,
                "description": f"User with id {str(user.id)} has been updated.",
                "activity_type": ActivityType.UPDATE,
                "entity": "user",
                "entity_id": user.id
            }
        )
        print(f"User {user.id} has been updated with {update_dict}.")

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        """
        Triggered after a user has been logged in.

        Args:
        user (User): The user that logged in.
        request (Optional[Request]): The request that initiated the login process.
        response (Optional[Response]): The response that will be sent back to the client.
        """
        print(f"User {user.id} logged in.")

    async def on_before_delete(self, user: User, request: Optional[Request] = None):
        """
        Triggered before a user is deleted.

        Args:
        user (User): The user that is about to be deleted.
        request (Optional[Request]): The request that initiated the deletion process.
        """
        print(f"User {user.id} is going to be deleted")

    async def on_after_delete(self, user: User, request: Optional[Request] = None):
        """
        Triggered after a user is deleted.
        
        Args:
        user (User): The user that was deleted.
        request (Optional[Request]): The request that triggered the deletion.
        """
        await self.activity_logs.create_activity(
            activity_data = {
                "user_id": user.id,
                "description": f"User with id {str(user.id)} is successfully deleted",
                "activity_type": ActivityType.DELETE,
                "entity": "user",
                "entity_id": user.id
            }
        )
        print(f"User {user.id} is successfully deleted")


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Dependency to provide the SQLAlchemyUserDatabase instance.

    Args:
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    SQLAlchemyUserDatabase: The SQLAlchemyUserDatabase instance.
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Dependency to provide the UserManager instance.

    Args:
    user_db (SQLAlchemyUserDatabase): The user database instance.
    session (AsyncSession): The database session to be used for executing queries.

    Yields:
    UserManager: The UserManager instance.
    """
    yield UserManager(user_db, session)
