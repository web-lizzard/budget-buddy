from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_budget_by_id_query_handler import (
    SQLGetBudgetByIdQueryHandler,
)
from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_budget_statistics_query_handler import (
    SQLGetBudgetStatisticsQueryHandler,
)
from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_budgets_query_handler import (
    SQLGetBudgetsQueryHandler,
)
from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_categories_query_handler import (
    SQLGetCategoriesQueryHandler,
)
from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_category_by_id_query_handler import (
    SQLGetCategoryByIdQueryHandler,
)
from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_transaction_by_id_query_handler import (
    SQLGetTransactionByIdQueryHandler,
)
from adapters.outbound.persistence.sql_alchemy.query_handlers.sql_get_transactions_query_handler import (
    SQLGetTransactionsQueryHandler,
)
from application.commands import (
    AddCategoryCommand,
    CreateBudgetCommand,
    CreateTransactionCommand,
    DeactivateBudgetCommand,
    DeleteTransactionCommand,
    EditCategoryCommand,
    EditTransactionCommand,
    RemoveCategoryCommand,
    RenewBudgetCommand,
)
from application.commands.calculate_statistics_command import CalculateStatisticsCommand
from application.commands.handlers.add_category_command_handler import (
    AddCategoryCommandHandler,
)
from application.commands.handlers.calculate_statistics_command_handler import (
    CalculateStatisticsCommandHandler,
)
from application.commands.handlers.create_budget_command_handler import (
    CreateBudgetCommandHandler,
)
from application.commands.handlers.create_transaction_command_handler import (
    CreateTransactionCommandHandler,
)
from application.commands.handlers.deactivate_budget_command_handler import (
    DeactivateBudgetCommandHandler,
)
from application.commands.handlers.delete_transaction_command_handler import (
    DeleteTransactionCommandHandler,
)
from application.commands.handlers.edit_category_command_handler import (
    EditCategoryCommandHandler,
)
from application.commands.handlers.edit_transaction_command_handler import (
    EditTransactionCommandHandler,
)
from application.commands.handlers.recalculate_statistics_after_update_command_handler import (
    RecalculateStatisticsAfterUpdateCommandHandler,
)
from application.commands.handlers.remove_category_command_handler import (
    RemoveCategoryCommandHandler,
)
from application.commands.handlers.renew_budget_command_handler import (
    RenewBudgetCommandHandler,
)
from application.commands.recalculate_statistics_after_update_command import (
    RecalculateStatisticsAfterUpdateCommand,
)
from application.queries import (
    GetBudgetByIdQuery,
    GetBudgetsQuery,
    GetBudgetStatisticsQuery,
    GetCategoriesQuery,
    GetCategoryByIdQuery,
    GetTransactionByIdQuery,
    GetTransactionsQuery,
)
from dependency_injector import containers, providers
from domain.factories.budget_factory import BudgetCreateParameters
from domain.factories.statistics_record_factory import (
    StatisticsRecordCreateParameters,
    StatisticsRecordReproduceParameters,
)
from domain.factories.transaction_factory import TransactionCreateParameters
from domain.ports.budget_repository import BudgetRepository
from domain.ports.outbound.statistics_repository import StatisticsRepository
from domain.ports.transaction_repository import TransactionRepository

# Forward references for type hinting - use classes directly if available
from .database_container import DatabaseContainer  # Import directly
from .domain_container import DomainContainer  # Import directly
from .persistence_container import PersistenceContainer  # Import directly


class ApplicationContainer(containers.DeclarativeContainer):
    """Dependency injection container for application layer components."""

    # Inject containers directly
    database_container: providers.Container[DatabaseContainer] = providers.Container(
        DatabaseContainer
    )
    persistence_container: providers.Container[PersistenceContainer] = (
        providers.Container(PersistenceContainer)
    )
    domain_container: providers.Container[DomainContainer] = providers.Container(
        DomainContainer
    )

    query_handlers = providers.Dict(
        {
            GetBudgetByIdQuery: providers.Factory(
                SQLGetBudgetByIdQueryHandler,
                session=persistence_container.query_session,
            ),
            GetBudgetsQuery: providers.Factory(
                SQLGetBudgetsQueryHandler, session=persistence_container.query_session
            ),
            GetCategoriesQuery: providers.Factory(
                SQLGetCategoriesQueryHandler,
                session=persistence_container.query_session,
            ),
            GetCategoryByIdQuery: providers.Factory(
                SQLGetCategoryByIdQueryHandler,
                session=persistence_container.query_session,
            ),
            GetTransactionsQuery: providers.Factory(
                SQLGetTransactionsQueryHandler,
                session=persistence_container.query_session,
            ),
            GetTransactionByIdQuery: providers.Factory(
                SQLGetTransactionByIdQueryHandler,
                session=persistence_container.query_session,
            ),
            GetBudgetStatisticsQuery: providers.Factory(
                SQLGetBudgetStatisticsQueryHandler,
                session=persistence_container.query_session,
                clock=domain_container.clock,
            ),
        }
    )

    command_handlers = providers.Dict(
        {
            CreateBudgetCommand: providers.Factory(
                CreateBudgetCommandHandler,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                budget_factory=domain_container.provided.get_budget_factory.call(
                    BudgetCreateParameters
                ),
                unit_of_work=persistence_container.uow,
                clock=domain_container.clock,
            ),
            DeactivateBudgetCommand: providers.Factory(
                DeactivateBudgetCommandHandler,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                budget_deactivation_service=domain_container.budget_deactivation_service,
                unit_of_work=persistence_container.uow,
                clock=domain_container.clock,
            ),
            RenewBudgetCommand: providers.Factory(
                RenewBudgetCommandHandler,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                unit_of_work=persistence_container.uow,
                budget_renewal_service=domain_container.budget_renewal_service,
                clock=domain_container.clock,
            ),
            CreateTransactionCommand: providers.Factory(
                CreateTransactionCommandHandler,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                transaction_repository=persistence_container.provided.get_repository.call(
                    TransactionRepository
                ),
                unit_of_work=persistence_container.uow,
                clock=domain_container.clock,
                transaction_factory=domain_container.provided.get_transaction_factory.call(
                    TransactionCreateParameters
                ),
            ),
            EditTransactionCommand: providers.Factory(
                EditTransactionCommandHandler,
                unit_of_work=persistence_container.uow,
                transaction_repository=persistence_container.provided.get_repository.call(
                    TransactionRepository
                ),
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                clock=domain_container.clock,
            ),
            DeleteTransactionCommand: providers.Factory(
                DeleteTransactionCommandHandler,
                unit_of_work=persistence_container.uow,
                transaction_repository=persistence_container.provided.get_repository.call(
                    TransactionRepository
                ),
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                clock=domain_container.clock,
            ),
            AddCategoryCommand: providers.Factory(
                AddCategoryCommandHandler,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                unit_of_work=persistence_container.uow,
                clock=domain_container.clock,
            ),
            EditCategoryCommand: providers.Factory(
                EditCategoryCommandHandler,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                unit_of_work=persistence_container.uow,
                clock=domain_container.clock,
            ),
            RemoveCategoryCommand: providers.Factory(
                RemoveCategoryCommandHandler,
                unit_of_work=persistence_container.uow,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                transaction_repository=persistence_container.provided.get_repository.call(
                    TransactionRepository
                ),
                clock=domain_container.clock,
            ),
            CalculateStatisticsCommand: providers.Factory(
                CalculateStatisticsCommandHandler,
                unit_of_work=persistence_container.uow,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                transaction_repository=persistence_container.provided.get_repository.call(
                    TransactionRepository
                ),
                statistics_repository=persistence_container.provided.get_repository.call(
                    StatisticsRepository
                ),
                clock=domain_container.clock,
                statistics_record_factory=domain_container.provided.get_statistics_record_factory.call(
                    StatisticsRecordCreateParameters
                ),
            ),
            RecalculateStatisticsAfterUpdateCommand: providers.Factory(
                RecalculateStatisticsAfterUpdateCommandHandler,
                unit_of_work=persistence_container.uow,
                budget_repository=persistence_container.provided.get_repository.call(
                    BudgetRepository
                ),
                transaction_repository=persistence_container.provided.get_repository.call(
                    TransactionRepository
                ),
                statistics_repository=persistence_container.provided.get_repository.call(
                    StatisticsRepository
                ),
                clock=domain_container.clock,
                statistics_record_factory=domain_container.provided.get_statistics_record_factory.call(
                    StatisticsRecordReproduceParameters
                ),
            ),
        }
    )

    get_query_handler = providers.Callable(
        lambda query_type, handlers: handlers[query_type], handlers=query_handlers
    )

    get_command_handler = providers.Callable(
        lambda command_type, handlers: handlers[command_type],
        handlers=command_handlers,
    )
