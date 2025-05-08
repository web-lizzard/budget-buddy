from typing import AsyncGenerator

from application.services import (
    JWTSecurityService,
    SecurityService,
    SQLAlchemyUserService,
    UserService,
)
from dependency_injector import containers, providers
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infrastructure.container.database_container import DatabaseContainer
from infrastructure.container.persistence_container import PersistenceContainer
from infrastructure.settings import JWTSettings


async def _get_session(
    session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


class AuthContainer(containers.DeclarativeContainer):
    """Dependency injection container for authentication services."""

    config = providers.Configuration()

    database_container = providers.Container(DatabaseContainer)
    persistence_container = providers.Container(PersistenceContainer)

    session: providers.Resource[AsyncSession] = providers.Resource(
        _get_session, session_maker=database_container.sessionmaker
    )

    pwd_context: providers.Singleton[CryptContext] = providers.Singleton(
        CryptContext, schemes=["bcrypt"], deprecated="auto"
    )

    security_service: providers.Factory[SecurityService] = providers.Factory(
        JWTSecurityService,
        settings=providers.Callable(lambda c: JWTSettings(**c["jwt"]), config),
        pwd_context=pwd_context,
    )

    user_service: providers.Factory[UserService] = providers.Factory(
        SQLAlchemyUserService,
        session=session,
        security_service=security_service,
    )
