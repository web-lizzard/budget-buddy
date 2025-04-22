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


class Settings(BaseSettings):
    """Application settings."""

    # Environment configuration
    environment: Literal["dev", "prod"] = "dev"

    # Feature specific configuration
    api: APISettings = APISettings()
    logger: LoggerSettings = LoggerSettings()

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
