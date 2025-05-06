import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from domain.aggregates.statistics_record import StatisticsRecord
from domain.ports.budget_repository import BudgetRepository
from domain.ports.transaction_repository import TransactionRepository
from domain.services.statistics_calculation_service import StatisticsCalculationService


class StatisticsRecordFactoryParams:
    pass


T = TypeVar("T", bound=StatisticsRecordFactoryParams)


@dataclass(frozen=True)
class StatisticsRecordCreateParameters(StatisticsRecordFactoryParams):
    """Parameters for creating a StatisticsRecord."""

    user_id: uuid.UUID
    budget_id: uuid.UUID
    transaction_id: uuid.UUID


class StatisticsRecordFactory(ABC, Generic[T]):
    """Abstract factory for creating StatisticsRecord domain objects."""

    @abstractmethod
    async def create(self, params: T) -> StatisticsRecord:
        """Abstract method to create a StatisticsRecord instance."""
        raise NotImplementedError


class CreateNewStatisticsRecordFactory(
    StatisticsRecordFactory[StatisticsRecordCreateParameters]
):
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

    async def create(
        self, params: StatisticsRecordCreateParameters
    ) -> StatisticsRecord:
        """
        Creates a StatisticsRecord instance based on provided parameters.

        Args:
            params: Statistics record creation parameters.

        Returns:
            A new StatisticsRecord object containing calculated statistics.
        """
        _, budget = await self._budget_repository.find_by(
            params.budget_id, params.user_id
        )
        transactions = await self._transaction_repository.find_by_budget_id(
            params.budget_id, params.user_id
        )
        record = self._statistics_calculation_service.calculate_statistics(
            budget, transactions
        )

        record.set_transaction_id(params.transaction_id)

        return record
