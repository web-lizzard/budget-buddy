from domain.events.statistics import StatisticsCalculated
from domain.factories.statistics_record_factory import (
    StatisticsRecordCreateParameters,
    StatisticsRecordFactory,
)
from domain.ports import BudgetRepository, StatisticsRepository, TransactionRepository
from domain.ports.clock import Clock

from application.commands import CalculateStatisticsCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class CalculateStatisticsCommandHandler(CommandHandler[CalculateStatisticsCommand]):
    """Handles the command to calculate statistics for a budget."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        statistics_repository: StatisticsRepository,
        statistics_record_factory: StatisticsRecordFactory,
        clock: Clock,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
    ):
        """
        Initializes the command handler with the necessary dependencies.

        Args:
            unit_of_work (UnitOfWork): Manages transactions and event publishing.
            statistics_repository (StatisticsRepository): Repository for performing statistics operations.
            statistics_record_factory (StatisticsRecordFactory): Factory responsible for creating StatisticsRecord objects.
            clock (Clock): Provides the current time.
            budget_repository (BudgetRepository): Repository for managing budget data.
            transaction_repository (TransactionRepository): Repository for managing transaction data.
        """
        super().__init__(unit_of_work)
        self._statistics_repository = statistics_repository
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._statistics_record_factory = statistics_record_factory
        self._clock = clock

    async def _handle(
        self, command: CalculateStatisticsCommand
    ) -> StatisticsCalculated:
        """
        Fetches budget and transactions, calculates statistics using the service,
        creates the StatisticsRecord using the factory, saves the result,
        and returns the StatisticsCalculated event.
        """
        _, budget = await self._budget_repository.find_by(
            command.budget_id, command.user_id
        )
        transactions = await self._transaction_repository.find_by_budget_id(
            command.budget_id, command.user_id
        )

        create_params = StatisticsRecordCreateParameters(
            budget=budget,
            transactions=transactions,
            transaction_id=command.transaction_id,
        )

        record = await self._statistics_record_factory.create(params=create_params)

        await self._statistics_repository.save(record)

        return StatisticsCalculated(
            occurred_on=self._clock.now(),
            budget_id=command.budget_id,
            user_id=command.user_id,
            statistics_record_id=record.id,
            calculated_at=record.creation_date,
        )
