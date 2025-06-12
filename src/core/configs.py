"""Configuration for the application."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the application."""
    ENV : str
    PASSWORD : str
    DB_USER : str
    DB_NAME : str
    DB_URL: str
    OAUTH_SECRET : str
    ACCESS_TOKEN_EXPIRY_WEEKS : int
    ALGORITHM : str

    model_config = SettingsConfigDict(
        env_file="./.env",
        extra="ignore"
    )


settings = Settings()
