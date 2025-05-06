import uuid
from abc import ABC, abstractmethod

from domain.aggregates.statistics_record import StatisticsRecord


class StatisticsRecordFactory(ABC):
    """Abstract factory for creating StatisticsRecord instances."""

    @abstractmethod
    async def create_statistics_record(
        self,
        user_id: uuid.UUID,
        budget_id: uuid.UUID,
        transaction_id: uuid.UUID,
    ) -> StatisticsRecord:
        """
        Create a StatisticsRecord instance.

        Args:
            user_id (uuid.UUID): The ID of the user for whom the statistics record is created.
            budget_id (uuid.UUID): The ID of the budget associated with the statistics record.
            transaction_id (uuid.UUID): The ID of the transaction triggering this record.

        Returns:
            StatisticsRecord: A new instance of StatisticsRecord containing calculated statistics.
        """
        pass
