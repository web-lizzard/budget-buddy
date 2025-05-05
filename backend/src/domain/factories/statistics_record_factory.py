import uuid

from domain.aggregates.statistics_record import StatisticsRecord
from domain.ports.budget_repository import BudgetRepository
from domain.ports.factories.statistics_record_factory import StatisticsRecordFactory
from domain.ports.transaction_repository import TransactionRepository
from domain.services.statistics_calculation_service import StatisticsCalculationService


class CreateNewStatisticsRecordFactory(StatisticsRecordFactory):
    """Factory for creating StatisticsRecord domain objects.

    This factory is responsible for creating instances of StatisticsRecord
    by utilizing the provided services and repositories to calculate statistics
    based on the user's budget and transactions.

    Attributes:
        statistics_calculation_service: Service for calculating statistics.
        transaction_repository: Repository for transaction operations.
        budget_repository: Repository for budget operations.
    """

    def __init__(
        self,
        statistics_calculation_service: StatisticsCalculationService,
        transaction_repository: TransactionRepository,
        budget_repository: BudgetRepository,
    ):
        self._statistics_calculation_service = statistics_calculation_service
        self._transaction_repository = transaction_repository
        self._budget_repository = budget_repository

    async def create_statistics_record(
        self,
        user_id: uuid.UUID,
        budget_id: uuid.UUID,
        transaction_id: uuid.UUID,
    ) -> StatisticsRecord:
        """
        Creates a StatisticsRecord instance.

        Args:
            user_id: The user's ID.
            budget_id: The budget's ID.
            transaction_id: The ID of the transaction triggering this record (optional).

        Returns:
            A new StatisticsRecord object containing calculated statistics.
        """

        _, budget = await self._budget_repository.find_by(budget_id, user_id)
        transactions = await self._transaction_repository.find_by_budget_id(
            budget_id, user_id
        )
        record = self._statistics_calculation_service.calculate_statistics(
            budget, transactions
        )

        record.set_transaction_id(transaction_id)

        return record
