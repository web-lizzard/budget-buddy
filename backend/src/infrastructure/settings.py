from enum import Enum
from functools import lru_cache
from typing import Literal

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Application environment."""

    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class APISettings(BaseModel):
    """API configuration settings."""

    host: str = "0.0.0.0"
    port: int = 8000


class LoggerSettings(BaseModel):
    """Logger configuration settings."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class DatabaseSettings(BaseModel):
    """Database configuration settings."""

    user: str = "budget_buddy"
    password: str = "budget_buddy"
    host: str = "postgres"  # Service name in Docker network
    port: int = 5432
    db_name: str = "budget_buddy"
    echo: bool = False

    # async_url: str = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db_name}"
    async_url: str = (
        "postgresql+asyncpg://budget_buddy:budget_buddy@postgres:5432/budget_buddy"
    )


class Settings(BaseSettings):
    """Application settings."""

    # Environment configuration
    environment: Literal["dev", "prod"] = "dev"

    # Feature specific configuration
    api: APISettings = APISettings()
    logger: LoggerSettings = LoggerSettings()
    database: DatabaseSettings = DatabaseSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Settings: Application settings
    """
    return Settings()
