"""Entry point for the FastAPI app."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.db_session import init_db


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


def main():
    """
    Starts the FastAPI app.

    This is the entry point for the application, and should not be imported
    anywhere else.

    :return: None
    """
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
