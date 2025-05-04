from adapters.outbound.clock.time_aware_clock import TimeAwareClock
from dependency_injector import containers, providers
from domain.factories.budget_factory import BudgetFactory
from domain.ports.clock import Clock
from domain.services import BudgetDeactivationService
from domain.services.budget_renewal_service import BudgetRenewalService
from domain.services.statistics_calculation_service import StatisticsCalculationService
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

    clock: providers.Singleton[Clock] = providers.Singleton(TimeAwareClock)

    budget_factory: providers.Factory[BudgetFactory] = providers.Factory(
        BudgetFactory,
        strategies=strategies,
    )

    budget_deactivation_service: providers.Factory[BudgetDeactivationService] = (
        providers.Factory(
            BudgetDeactivationService,
            clock=clock,
        )
    )

    budget_renewal_service: providers.Factory[BudgetRenewalService] = providers.Factory(
        BudgetRenewalService,
        budget_factory=budget_factory,
    )

    statistics_calculation_service: providers.Factory[StatisticsCalculationService] = (
        providers.Factory(StatisticsCalculationService, clock=clock)
    )
