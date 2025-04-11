from enum import Enum
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


class APISettings(BaseModel):
    version: str = "0.1.0"
    port: int = 8000


class Configuration(BaseSettings):
    environment: Environment = Environment.DEVELOPMENT

    api: APISettings = APISettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_configuration() -> Configuration:
    """Get the settings for the application."""
    return Configuration()
