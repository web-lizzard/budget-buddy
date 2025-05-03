from typing import AsyncGenerator

from adapters.outbound.persistence.sql_alchemy.repositories.budget_repository import (
    SQLAlchemyBudgetRepository,
)
from adapters.outbound.persistence.sql_alchemy.repositories.statistics_repository import (
    SQLAlchemyStatisticsRepository,
)
from adapters.outbound.persistence.sql_alchemy.repositories.transaction_repository import (
    SQLAlchemyTransactionRepository,
)
from adapters.outbound.persistence.sql_alchemy.uow.uow import SQLAlchemyUnitOfWork
from application.ports.uow.uow import UnitOfWork
from dependency_injector import containers, providers
from domain.ports.budget_repository import BudgetRepository
from domain.ports.outbound.statistics_repository import StatisticsRepository
from domain.ports.transaction_repository import TransactionRepository
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from .database_container import DatabaseContainer
from .publisher_container import PublisherContainer


async def _get_session(
    session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


async def _get_query_session(
    session_maker: async_sessionmaker,
) -> AsyncGenerator[AsyncSession, None]:
    async with session_maker() as session:
        yield session


class PersistenceContainer(containers.DeclarativeContainer):
    """Dependency injection container for persistence."""

    publisher_container: providers.Container[PublisherContainer] = providers.Container(
        PublisherContainer
    )
    database_container: providers.Container[DatabaseContainer] = providers.Container(
        DatabaseContainer
    )

    # Session for commands and repositories (used with UoW)
    command_session: providers.Resource[AsyncSession] = providers.Resource(
        _get_session, session_maker=database_container.sessionmaker
    )

    # Separate session factory for queries
    query_session: providers.Resource[AsyncSession] = providers.Resource(
        _get_query_session, session_maker=database_container.sessionmaker
    )

    repositories = providers.Dict(
        {
            BudgetRepository: providers.Factory(
                SQLAlchemyBudgetRepository, session=command_session
            ),
            TransactionRepository: providers.Factory(
                SQLAlchemyTransactionRepository, session=command_session
            ),
            StatisticsRepository: providers.Factory(
                SQLAlchemyStatisticsRepository, session=command_session
            ),
        }
    )

    uow: providers.Factory[UnitOfWork] = providers.Factory(
        SQLAlchemyUnitOfWork,
        session=command_session,
        event_publisher=publisher_container.domain_publisher,
    )

    get_repository = providers.Callable(
        lambda repository_type, repositories: repositories[repository_type],
        repositories=repositories,
    )
