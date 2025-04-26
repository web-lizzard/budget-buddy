from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_budget_by_id_query_handler import (
    GetBudgetByIdQueryHandler,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_budget_statistics_query_handler import (
    GetBudgetStatisticsQueryHandler,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_budgets_query_handler import (
    GetBudgetsQueryHandler,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_categories_query_handler import (
    GetCategoriesQueryHandler,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_category_by_id_query_handler import (
    GetCategoryByIdQueryHandler,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_transaction_by_id_query_handler import (
    GetTransactionByIdQueryHandler,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_transactions_query_handler import (
    GetTransactionsQueryHandler,
)
from adapters.outbound.persistence.in_memory.statistics_repository import (
    InMemoryStatisticsRepository,
)
from adapters.outbound.persistence.in_memory.transaction_repository import (
    InMemoryTransactionRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.ports.uow.uow import UnitOfWork
from application.queries.get_budget_by_id_query import GetBudgetByIdQuery
from application.queries.get_budget_statistics_query import GetBudgetStatisticsQuery
from application.queries.get_budgets_query import GetBudgetsQuery
from application.queries.get_categories_query import GetCategoriesQuery
from application.queries.get_category_by_id_query import GetCategoryByIdQuery
from application.queries.get_transaction_by_id_query import GetTransactionByIdQuery
from application.queries.get_transactions_query import GetTransactionsQuery
from dependency_injector import containers, providers
from domain.ports.budget_repository import BudgetRepository
from domain.ports.outbound.statistics_repository import StatisticsRepository
from domain.ports.transaction_repository import TransactionRepository

from .publisher_container import PublisherContainer


class PersistenceContainer(containers.DeclarativeContainer):
    """Dependency injection container for persistence."""

    publisher_container: providers.Container[PublisherContainer] = providers.Container(
        PublisherContainer
    )

    query_handlers = providers.Dict(
        {
            GetBudgetByIdQuery: providers.Factory(GetBudgetByIdQueryHandler),
            GetBudgetsQuery: providers.Factory(GetBudgetsQueryHandler),
            GetCategoriesQuery: providers.Factory(GetCategoriesQueryHandler),
            GetCategoryByIdQuery: providers.Factory(GetCategoryByIdQueryHandler),
            GetTransactionsQuery: providers.Factory(GetTransactionsQueryHandler),
            GetTransactionByIdQuery: providers.Factory(GetTransactionByIdQueryHandler),
            GetBudgetStatisticsQuery: providers.Factory(
                GetBudgetStatisticsQueryHandler
            ),
        }
    )

    repositories = providers.Dict(
        {
            BudgetRepository: providers.Factory(
                InMemoryBudgetRepository, users=None, budgets=None
            ),
            TransactionRepository: providers.Factory(InMemoryTransactionRepository),
            StatisticsRepository: providers.Factory(InMemoryStatisticsRepository),
        }
    )

    uow: providers.Factory[UnitOfWork] = providers.Factory(
        InMemoryUnitOfWork, event_publisher=publisher_container.domain_publisher
    )

    get_query_handler = providers.Callable(
        lambda query_type, handlers: handlers[query_type], handlers=query_handlers
    )

    get_repository = providers.Callable(
        lambda repository_type, repositories: repositories[repository_type],
        repositories=repositories,
    )
