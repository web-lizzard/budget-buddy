from application.commands import CalculateStatisticsCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork
from domain.events.statistics import StatisticsCalculated
from domain.factories import StatisticsRecordFactory
from domain.ports import StatisticsRepository
from domain.ports.clock import Clock


class CalculateStatisticsCommandHandler(CommandHandler[CalculateStatisticsCommand]):
    """Handles the command to calculate statistics for a budget."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        statistics_repository: StatisticsRepository,
        statistics_record_factory: StatisticsRecordFactory,
        clock: Clock,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            unit_of_work: UnitOfWork for transaction management and event publishing
            statistics_repository: Repository for statistics operations
            statistics_record_factory: Factory for creating StatisticsRecord objects
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._statistics_repository = statistics_repository
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

        record = await self._statistics_record_factory.create_statistics_record(
            command.user_id,
            command.budget_id,
            command.transaction_id,
        )

        await self._statistics_repository.save(record)

        return StatisticsCalculated(
            occurred_on=self._clock.now(),
            budget_id=command.budget_id,
            user_id=command.user_id,
            statistics_record_id=record.id,
            calculated_at=record.creation_date,
        )
