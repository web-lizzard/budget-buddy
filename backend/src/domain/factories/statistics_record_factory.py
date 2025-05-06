import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from domain.aggregates.budget import Budget
from domain.aggregates.statistics_record import StatisticsRecord
from domain.aggregates.transaction import Transaction
from domain.services.statistics_calculation_service import StatisticsCalculationService


class StatisticsRecordFactoryParams:
    pass


T = TypeVar("T", bound=StatisticsRecordFactoryParams)


@dataclass(frozen=True)
class StatisticsRecordCreateParameters(StatisticsRecordFactoryParams):
    """Parameters for creating a StatisticsRecord."""

    budget: Budget
    transactions: list[Transaction]
    transaction_id: uuid.UUID


@dataclass(frozen=True)
class StatisticsRecordReproduceParameters(StatisticsRecordFactoryParams):
    """Parameters for reproducing a StatisticsRecord."""

    budget: Budget
    transactions: list[Transaction]
    occurred_date: datetime
    record: StatisticsRecord


class StatisticsRecordFactory(ABC, Generic[T]):
    """Abstract factory for creating StatisticsRecord domain objects."""

    @abstractmethod
    async def create(self, params: T) -> StatisticsRecord:
        """Abstract method to create a StatisticsRecord instance."""
        raise NotImplementedError


class CreateNewStatisticsRecordFactory(
    StatisticsRecordFactory[StatisticsRecordCreateParameters]
):
    """Factory for creating instances of StatisticsRecord domain objects.

    This factory is responsible for creating StatisticsRecord objects
    by leveraging the provided services to calculate statistics based
    on the user's budget and transactions.

    Attributes:
        statistics_calculation_service: Service used for calculating statistics.
    """

    def __init__(
        self,
        statistics_calculation_service: StatisticsCalculationService,
    ):
        self._statistics_calculation_service = statistics_calculation_service

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
        record = self._statistics_calculation_service.calculate_statistics(
            params.budget, params.transactions
        )
        record.set_transaction_id(params.transaction_id)

        return record


class ReproduceStatisticsRecordFactory(
    StatisticsRecordFactory[StatisticsRecordReproduceParameters]
):
    """Factory for reproducing a StatisticsRecord domain objects.

    This factory is responsible for reproducing StatisticsRecord objects
    by leveraging the provided services to calculate statistics based
    on the user's budget and transactions.

    Attributes:
    """

    def __init__(
        self,
        statistics_calculation_service: StatisticsCalculationService,
    ):
        self._statistics_calculation_service = statistics_calculation_service

    async def create(
        self, params: StatisticsRecordReproduceParameters
    ) -> StatisticsRecord:
        """
        Creates a StatisticsRecord instance based on provided parameters.
        """
        record = self._statistics_calculation_service.calculate_statistics(
            params.budget, params.transactions
        )
        record.set_creation_date(params.occurred_date)
        record.set_id(params.record.id)
        return record
