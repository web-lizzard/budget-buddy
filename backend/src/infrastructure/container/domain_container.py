from dependency_injector import containers, providers
from domain.factories.budget_factory import BudgetFactory
from domain.strategies.budget_strategy.monthly_budget_strategy import (
    MonthlyBudgetStrategy,
)
from domain.strategies.budget_strategy.yearly_budget_strategy import (
    YearlyBudgetStrategy,
)


class DomainContainer(containers.DeclarativeContainer):
    """Dependency injection container for domain services."""

    strategies: providers.List = providers.List(
        providers.Factory(MonthlyBudgetStrategy),
        providers.Factory(YearlyBudgetStrategy),
    )

    budget_factory: providers.Factory[BudgetFactory] = providers.Factory(
        BudgetFactory,
        strategies=strategies,
    )
