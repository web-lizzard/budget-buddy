from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.query_handlers.get_budget_by_id_query_handler import (
    GetBudgetByIdQueryHandler,
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
from adapters.outbound.persistence.in_memory.query_handlers.get_transactions_query_handler import (
    GetTransactionsQueryHandler,
)
from adapters.outbound.persistence.in_memory.statistics_repository import (
    InMemoryStatisticsRepository,
)
from adapters.outbound.persistence.in_memory.transaction_repository import (
    InMemoryTransactionRepository,
)
from application.queries.get_budget_by_id_query import GetBudgetByIdQuery
from application.queries.get_budgets_query import GetBudgetsQuery
from application.queries.get_categories_query import GetCategoriesQuery
from application.queries.get_category_by_id_query import GetCategoryByIdQuery
from application.queries.get_transactions_query import GetTransactionsQuery
from dependency_injector import containers, providers
from domain.ports.budget_repository import BudgetRepository
from domain.ports.outbound.statistics_repository import StatisticsRepository
from domain.ports.transaction_repository import TransactionRepository


class PersistenceContainer(containers.DeclarativeContainer):
    """Dependency injection container for persistence."""

    query_handlers = providers.Dict(
        {
            GetBudgetByIdQuery: providers.Factory(GetBudgetByIdQueryHandler),
            GetBudgetsQuery: providers.Factory(GetBudgetsQueryHandler),
            GetCategoriesQuery: providers.Factory(GetCategoriesQueryHandler),
            GetCategoryByIdQuery: providers.Factory(GetCategoryByIdQueryHandler),
            GetTransactionsQuery: providers.Factory(GetTransactionsQueryHandler),
        }
    )

    repositories = providers.Dict(
        {
            BudgetRepository: providers.Factory(InMemoryBudgetRepository),
            TransactionRepository: providers.Factory(InMemoryTransactionRepository),
            StatisticsRepository: providers.Factory(InMemoryStatisticsRepository),
        }
    )
