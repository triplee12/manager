"""Pytest configuration."""

import urllib.parse
import uuid
import pytest
import pytest_asyncio
import httpx
from sqlmodel import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.models.user_models import Base
from src.core.configs import settings
from src.main import app
from src.db.db_session import get_async_session as get_db_original
from asgi_lifespan import LifespanManager

PASSWORD = urllib.parse.quote(settings.PASSWORD, safe="")
DB_NAME = settings.DB_NAME_TEST
DB_USER = settings.DB_USER
TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{PASSWORD}@localhost:5432/{DB_NAME}"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine_test, expire_on_commit=False)

def pytest_configure(config):
    config.option.asyncio_mode = "auto"

@pytest.fixture(scope="session", autouse=True)
def configure_asyncio_scope(pytestconfig):
    pytestconfig._inicache["asyncio_default_fixture_loop_scope"] = "function"

@pytest_asyncio.fixture(scope="function")
async def prepare_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
        await conn.run_sync(Base.metadata.create_all)
    yield

async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session

app.dependency_overrides[get_db_original] = override_get_db

@pytest_asyncio.fixture(scope="function")
async def test_client():
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            yield client


@pytest_asyncio.fixture
async def authorized_headers(test_client):
    # Create user
    await test_client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    # Login
    res = await test_client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def fake_user():
    class User:
        id = uuid.uuid4()
        is_superuser = False
        role = "user"
    return User()


@pytest_asyncio.fixture
async def test_project():
    return {"id": "real-project-uuid", "title": "My Project"}


@pytest_asyncio.fixture
async def test_team():
    return {"id": "real-team-uuid"}


@pytest_asyncio.fixture
async def test_user():
    return {"id": "real-user-uuid", "token": "valid-user-jwt"}


@pytest_asyncio.fixture
async def admin_user():
    return {"id": "admin-user-uuid", "token": "admin-jwt"}
