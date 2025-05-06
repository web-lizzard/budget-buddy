from domain.events.statistics.statistics_calculated_event import StatisticsCalculated
from domain.factories.statistics_record_factory import (
    ReproduceStatisticsRecordFactory,
    StatisticsRecordReproduceParameters,
)
from domain.ports import BudgetRepository, StatisticsRepository, TransactionRepository
from domain.ports.clock import Clock

from application.commands.handlers.command_handler import CommandHandler
from application.commands.recalculate_statistics_after_update_command import (
    RecalculateStatisticsAfterUpdateCommand,
)
from application.ports.uow import UnitOfWork


class RecalculateStatisticsAfterUpdateCommandHandler(
    CommandHandler[RecalculateStatisticsAfterUpdateCommand]
):
    """Handles the command to recalculate statistics after a transaction update."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        statistics_repository: StatisticsRepository,
        statistics_record_factory: ReproduceStatisticsRecordFactory,
        clock: Clock,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
    ):
        """
        Initializes the command handler with the necessary dependencies.

        Args:
            unit_of_work (UnitOfWork): Manages transactions and event publishing.
            statistics_repository (StatisticsRepository): Repository for performing statistics operations.
            statistics_record_factory (ReproduceStatisticsRecordFactory): Factory responsible for reproducing StatisticsRecord objects.
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
        self, command: RecalculateStatisticsAfterUpdateCommand
    ) -> StatisticsCalculated:
        """
        Handles the recalculation of statistics after a transaction has been updated.

        Fetches the existing statistics record, budget and relevant transactions,
        recalculates statistics, updates the record and returns a StatisticsCalculated event.

        Args:
            command: The command containing data needed for recalculation.

        Returns:
            A StatisticsCalculated event.
        """
        # Find the statistics record to update by transaction ID
        statistics_record = await self._statistics_repository.find_by_transaction_id(
            command.transaction_id, command.user_id
        )

        # Get the budget
        _, budget = await self._budget_repository.find_by(
            command.budget_id, command.user_id
        )

        # Get all transactions for the budget up to the occurred date of the edited transaction
        transactions = (
            await self._transaction_repository.find_by_budget_id_and_date_range(
                budget_id=command.budget_id,
                user_id=command.user_id,
                end_date=command.transaction_occurred_date,
            )
        )

        # Create parameters for reproducing the statistics record
        reproduce_params = StatisticsRecordReproduceParameters(
            budget=budget,
            transactions=transactions,
            occurred_date=statistics_record.creation_date,
            record=statistics_record,
        )

        # Recalculate statistics and update the record
        updated_record = await self._statistics_record_factory.create(
            params=reproduce_params
        )

        # Save the updated record
        await self._statistics_repository.save(updated_record)

        # Return the event
        return StatisticsCalculated(
            occurred_on=self._clock.now(),
            budget_id=command.budget_id,
            user_id=command.user_id,
            statistics_record_id=updated_record.id,
            calculated_at=updated_record.creation_date,
        )
