"""User Authentication"""

import uuid
from fastapi_users import FastAPIUsers, models
from fastapi_users.authentication import AuthenticationBackend, JWTStrategy, BearerTransport
from src.services.user_services import get_user_manager
from src.models.user_models import User
from src.core.configs import settings

SECRET = settings.OAUTH_SECRET

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy[models.UP, models.ID]:
    """
    Returns a JWTStrategy instance with a secret key and lifetime seconds.
    """
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

current_active_user = fastapi_users.current_user(active=True)
