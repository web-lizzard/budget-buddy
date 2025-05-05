import uuid

from domain.aggregates.statistics_record import StatisticsRecord
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.ports.factories.statistics_record_factory import StatisticsRecordFactory
from domain.ports.outbound.statistics_repository import StatisticsRepository
from domain.ports.transaction_repository import TransactionRepository
from domain.services.statistics_calculation_service import StatisticsCalculationService


class StatisticsRecordUpdateFactory(StatisticsRecordFactory):
    """
    Factory for updating StatisticsRecord domain objects.

    This factory is responsible for creating updated instances of StatisticsRecord
    by utilizing the provided services and repositories to calculate statistics
    based on the user's budget and transactions.

    Attributes:
        transaction_repository: Repository for transaction operations.
        budget_repository: Repository for budget operations.
        clock: Clock service for retrieving the current time.
        statistics_calculation_service: Service for calculating statistics.
        statistics_record_repository: Repository for statistics record operations.
    """

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        budget_repository: BudgetRepository,
        clock: Clock,
        statistics_calculation_service: StatisticsCalculationService,
        statistics_record_repository: StatisticsRepository,
    ):
        self._transaction_repository = transaction_repository
        self._budget_repository = budget_repository
        self._clock = clock
        self._statistics_calculation_service = statistics_calculation_service
        self._statistics_record_repository = statistics_record_repository

    async def create_statistics_record(
        self,
        user_id: uuid.UUID,
        budget_id: uuid.UUID,
        transaction_id: uuid.UUID,
    ) -> StatisticsRecord:
        """
        Creates or updates a StatisticsRecord instance.

        Args:
            user_id (uuid.UUID): The user's ID.
            budget_id (uuid.UUID): The budget's ID.
            transaction_id (uuid.UUID): The ID of the transaction associated with this record.

        Returns:
            StatisticsRecord: An updated instance of StatisticsRecord containing calculated statistics.
        """

        now = self._clock.now()
        _, budget = await self._budget_repository.find_by(budget_id, user_id)
        transactions = (
            await self._transaction_repository.find_by_budget_id_and_date_range(
                budget_id, user_id, now
            )
        )

        old_record = await self._statistics_record_repository.find_by_id(
            transaction_id, user_id
        )

        record = self._statistics_calculation_service.calculate_statistics(
            budget, transactions
        )

        record.set_id(old_record.id)
        record.set_transaction_id(transaction_id)

        return record
