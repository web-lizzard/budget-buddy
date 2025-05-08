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

    level: str = "DEBUG"
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


class RabbitMQSettings(BaseModel):
    """RabbitMQ configuration settings."""

    host: str = "rabbitmq"  # Service name in Docker network
    port: int = 5672
    user: str = "guest"
    password: str = "guest"
    vhost: str = "/"
    celery_vhost: str = "/celery"
    events_vhost: str = "/events"
    exchange_name: str = "domain_events"

    @property
    def events_url(self) -> str:
        """URL for event publishing/subscribing."""
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.events_vhost}"

    @property
    def celery_url(self) -> str:
        """URL for Celery tasks."""
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}{self.celery_vhost}"

    url: str = f"amqp://{user}:{password}@{host}:{port}{vhost}"  # keeping for backward compatibility


class RedisSettings(BaseModel):
    """Redis configuration settings."""

    host: str = "redis"  # Service name in Docker network
    port: int = 6379
    db: int = 0

    @property
    def url(self) -> str:
        """URL for Redis connection."""
        return f"redis://{self.host}:{self.port}/{self.db}"

    @property
    def celery_broker_url(self) -> str:
        """URL for Celery broker."""
        return self.url


class JWTSettings(BaseModel):
    """JWT configuration settings."""

    secret_key: str = "your-secret-key"  # TODO: Change in production!
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30  # 30 minutes
    refresh_token_expire_days: int = 7  # 7 days


class Settings(BaseSettings):
    """Application settings."""

    # Environment configuration
    environment: Literal["dev", "prod"] = "dev"

    # Feature specific configuration
    api: APISettings = APISettings()
    logger: LoggerSettings = LoggerSettings()
    database: DatabaseSettings = DatabaseSettings()
    rabbitmq: RabbitMQSettings = RabbitMQSettings()
    redis: RedisSettings = RedisSettings()
    jwt: JWTSettings = JWTSettings()

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
