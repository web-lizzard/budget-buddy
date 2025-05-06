from adapters.outbound.clock.time_aware_clock import TimeAwareClock
from dependency_injector import containers, providers
from domain.factories.budget_factory import BudgetCreateParameters, CreateBudgetFactory
from domain.factories.statistics_record_factory import (
    CreateNewStatisticsRecordFactory,
    ReproduceStatisticsRecordFactory,
    StatisticsRecordCreateParameters,
    StatisticsRecordReproduceParameters,
)
from domain.factories.transaction_factory import (
    CreateTransactionFactory,
    TransactionCreateParameters,
)
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
from infrastructure.container.persistence_container import PersistenceContainer


class DomainContainer(containers.DeclarativeContainer):
    """Dependency injection container for domain services."""

    persistence_container: providers.Container = providers.Container(
        PersistenceContainer,
    )

    strategies: providers.List = providers.List(
        providers.Factory(MonthlyBudgetStrategy),
        providers.Factory(YearlyBudgetStrategy),
    )

    clock: providers.Singleton[Clock] = providers.Singleton(TimeAwareClock)

    budget_factories = providers.Dict(
        {
            BudgetCreateParameters: providers.Factory(
                CreateBudgetFactory, strategies=strategies
            ),
        }
    )

    get_budget_factory = providers.Callable(
        lambda params_type, factories: factories[params_type],
        factories=budget_factories,
    )

    transaction_factories = providers.Dict(
        {
            TransactionCreateParameters: providers.Factory(
                CreateTransactionFactory,
            ),
        }
    )

    get_transaction_factory = providers.Callable(
        lambda params_type, factories: factories[params_type],
        factories=transaction_factories,
    )

    budget_deactivation_service: providers.Factory[BudgetDeactivationService] = (
        providers.Factory(
            BudgetDeactivationService,
            clock=clock,
        )
    )

    budget_renewal_service: providers.Factory[BudgetRenewalService] = providers.Factory(
        BudgetRenewalService,
        budget_factory=get_budget_factory(BudgetCreateParameters),
    )

    statistics_calculation_service: providers.Factory[StatisticsCalculationService] = (
        providers.Factory(StatisticsCalculationService, clock=clock)
    )

    statistics_factories = providers.Dict(
        {
            StatisticsRecordCreateParameters: providers.Factory(
                CreateNewStatisticsRecordFactory,
                statistics_calculation_service=statistics_calculation_service,
            ),
            StatisticsRecordReproduceParameters: providers.Factory(
                ReproduceStatisticsRecordFactory,
                statistics_calculation_service=statistics_calculation_service,
            ),
        }
    )

    get_statistics_record_factory = providers.Callable(
        lambda params, factories: factories[params],
        factories=statistics_factories,
    )
