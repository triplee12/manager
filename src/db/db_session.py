"""Database connection module."""

import asyncio
import urllib.parse
from collections.abc import AsyncGenerator
from sqlmodel import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.core.configs import settings
from src.models.user_models import Base

PASSWORD = urllib.parse.quote(settings.PASSWORD, safe="")
DB_NAME = settings.DB_NAME
DB_USER = settings.DB_USER

if settings.ENV == "dev":
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{PASSWORD}@localhost:5432/{DB_NAME}"
else:
    DB_URL = settings.DB_URL

engine = create_async_engine(
    DB_URL,
    echo=True,
    pool_pre_ping=True
)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def init_db():
    """
    Initialize the database by creating necessary extensions and tables.

    This function establishes a connection to the database engine and executes
    SQL commands to create the 'pgcrypto' extension if it does not exist. It 
    then synchronously runs the metadata's create_all method to create all 
    tables defined in the ORM models.

    The function is asynchronous and should be awaited to ensure that the 
    operations complete successfully before proceeding.
    """

    for attempt in range(10):
        try:
            async with engine.begin() as conn:
                extension = text("CREATE EXTENSION IF NOT EXISTS pgcrypto")
                await conn.execute(extension)
                await conn.run_sync(Base.metadata.create_all)
                break
        except OperationalError as e:
            if attempt == 9:
                raise e
            await asyncio.sleep(1)
        else:
            raise RuntimeError("Database connection failed after 10 attempts")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Asynchronous context manager to generate an AsyncSession.

    This generator is an asynchronous context manager that yields an
    AsyncSession object. It is intended to be used with the 'async with'
    statement to ensure that the session is properly closed after use.

    The session is created using the async_session_maker which is defined
    at the module level. The maker is configured to use the database engine
    defined by the SQLALCHEMY_DATABASE_URL environment variable.

    The session is committed or rolled back automatically when the context
    manager is exited, depending on whether an exception was raised or not.
    """
    async with async_session_maker() as session:
        yield session
