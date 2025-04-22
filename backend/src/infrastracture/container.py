from adapters.outbound.persistence.in_memory import InMemoryBudgetRepository
from dependency_injector import containers, providers
from domain.ports.budget_repository import BudgetRepository

from .settings import Settings, get_settings


class Container(containers.DeclarativeContainer):
    """Dependency injection container."""

    wiring_config = containers.WiringConfiguration(
        packages=[
            "adapters.inbound.api",
        ],
        modules=[],
    )

    # Configuration
    config: providers.Provider[Settings] = providers.Singleton(get_settings)

    # Repositories
    budget_repository: providers.Provider[BudgetRepository] = providers.Singleton(
        InMemoryBudgetRepository,
        budgets=None,
        users=None,
    )
