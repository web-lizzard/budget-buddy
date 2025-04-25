from domain.events.statistics import StatisticsCalculated
from domain.ports import (
    BudgetRepository,
    StatisticsRepository,  # Add direct import
    TransactionRepository,
)
from domain.services.statistics_calculation_service import StatisticsCalculationService

from application.commands import CalculateStatisticsCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork  # Keep UoW for commit/rollback


class CalculateStatisticsCommandHandler(CommandHandler[CalculateStatisticsCommand]):
    """Handles the command to calculate statistics for a budget."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,  # UoW is still needed for the base handler
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        statistics_repository: StatisticsRepository,  # Inject StatisticsRepository
    ):
        super().__init__(unit_of_work)  # Pass UoW to base class
        # Store injected repositories
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._statistics_repository = statistics_repository  # Store instance

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
        statistics_calculation_service = StatisticsCalculationService()

        # Fetch transactions within the budget's date range
        transactions = await self._transaction_repository.find_by_budget_id(
            command.budget_id, command.user_id
        )

        # Calculate statistics
        statistics_record = statistics_calculation_service.calculate_statistics(
            budget=budget, transactions=transactions
        )

        await self._statistics_repository.save(statistics_record)

        print(statistics_record.id)

        return StatisticsCalculated.create(
            budget_id=budget.id,
            user_id=budget.user_id,
            statistics_record_id=statistics_record.id,
        )
