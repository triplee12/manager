"""Entry point for the FastAPI app."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.db_session import init_db
from src.api.v1.auth.auths import fastapi_users, auth_backend
from src.schemas.user_schemas import (
    UserRead, UserCreate, UserUpdate
)
from src.api.v1.users.user_routes import user_router
from src.api.v1.teams import team_routes, member_routes
from src.api.v1.projects.project_routes import project_router
from src.api.v1.tasks import task_routes, comment_routes
from src.api.v1.activities.activity_routes import activity_router


@asynccontextmanager
async def life_span(manager: FastAPI):
    """Application lifetime"""
    print("Server is Starting...")
    await init_db()
    yield
    print("Server has been stopped")


VERSION = 'v1.0.0'

app = FastAPI(
    title="Manager API",
    description="A scalable and modern REST API for a collaborative task management system.",
    version=VERSION,
    swagger_ui_parameters={
        "persistAuthorization": True,
    },
    lifespan=life_span
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(f"/api/{VERSION}")
async def root() -> dict[str, str]:
    """Manager root endpoint."""
    return {"message": "Welcome to the Manager API"}


@app.get(f"/api/{VERSION}/health")
async def healthz():
    """Health check endpoint."""
    return {"status": "ok"}


app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix=f"/api/{VERSION}/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix=f"/api/{VERSION}/auth", tags=["auth"]
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix=f"/api/{VERSION}/auth/reset-password", tags=["auth"]
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix=f"/api/{VERSION}/auth/verify", tags=["auth"]
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix=f"/api/{VERSION}/users", tags=["users"]
)
app.include_router(
    user_router, prefix=f"/api/{VERSION}"
)
app.include_router(
    team_routes.team_router, prefix=f"/api/{VERSION}/teams"
)
app.include_router(
    member_routes.team_member_router, prefix=f"/api/{VERSION}/members"
)
app.include_router(
    project_router, prefix=f"/api/{VERSION}/projects"
)
app.include_router(
    task_routes.task_router, prefix=f"/api/{VERSION}/tasks"
)
app.include_router(
    comment_routes.comment_router, prefix=f"/api/{VERSION}/comments"
)
app.include_router(
    activity_router, prefix=f"/api/{VERSION}/activities"
)
