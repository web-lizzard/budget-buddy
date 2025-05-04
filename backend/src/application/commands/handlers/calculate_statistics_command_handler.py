from domain.events.statistics import StatisticsCalculated
from domain.ports import BudgetRepository, StatisticsRepository, TransactionRepository
from domain.ports.clock import Clock
from domain.services.statistics_calculation_service import StatisticsCalculationService

from application.commands import CalculateStatisticsCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class CalculateStatisticsCommandHandler(CommandHandler[CalculateStatisticsCommand]):
    """Handles the command to calculate statistics for a budget."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        statistics_repository: StatisticsRepository,
        statistics_calculation_service: StatisticsCalculationService,
        clock: Clock,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            unit_of_work: UnitOfWork for transaction management and event publishing
            budget_repository: Repository for budget operations
            transaction_repository: Repository for transaction operations
            statistics_repository: Repository for statistics operations
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._statistics_repository = statistics_repository
        self._statistics_calculation_service = statistics_calculation_service
        self._clock = clock

    async def _handle(
        self, command: CalculateStatisticsCommand
    ) -> StatisticsCalculated:
        """
        Fetches budget and transactions, calculates statistics, saves the result,
        and returns the StatisticsCalculated event.
        """
        _, budget = await self._budget_repository.find_by(
            command.budget_id, command.user_id
        )

        # Fetch transactions within the budget's date range
        transactions = await self._transaction_repository.find_by_budget_id(
            command.budget_id, command.user_id
        )

        # Calculate statistics
        statistics_record = self._statistics_calculation_service.calculate_statistics(
            budget=budget, transactions=transactions
        )

        await self._statistics_repository.save(statistics_record)

        return StatisticsCalculated(
            budget_id=budget.id,
            user_id=command.user_id,
            statistics_record_id=statistics_record.id,
            calculated_at=self._clock.now(),
            occurred_on=self._clock.now(),
        )
