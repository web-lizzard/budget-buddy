"""Dependency injection container for database related components."""

from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine


class DatabaseContainer(containers.DeclarativeContainer):
    """Dependency injection container for database components."""

    config = providers.Configuration()

    async_engine: providers.Singleton[AsyncEngine] = providers.Singleton(
        create_async_engine,
        url=providers.Callable(lambda c: c["database"]["async_url"], config),
        echo=providers.Callable(lambda c: c["database"]["echo"], config),
        pool_pre_ping=True,
    )

    sessionmaker: providers.Singleton[async_sessionmaker] = providers.Singleton(
        async_sessionmaker,
        bind=async_engine,
        expire_on_commit=False,
        autoflush=False,
    )
