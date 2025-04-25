import uuid
from abc import ABC, abstractmethod
from datetime import date

from domain.aggregates.statistics_record import StatisticsRecord


class StatisticsRepository(ABC):
    """Interface for managing statistics records."""

    @abstractmethod
    async def find_by_id(
        self, statistic_id: uuid.UUID, user_id: uuid.UUID
    ) -> StatisticsRecord:
        """Finds a statistics record by its ID for a specific user."""
        pass

    @abstractmethod
    async def find_by_budget_id(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records for a specific budget and user."""
        pass

    @abstractmethod
    async def find_by_category_id(
        self, category_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records for a specific category and user."""
        pass

    @abstractmethod
    async def find_by_date_range(
        self, start_date: date, end_date: date, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records within a date range for a specific user."""
        pass

    @abstractmethod
    async def find_by_budget_id_and_date_range(
        self, budget_id: uuid.UUID, start_date: date, end_date: date, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records for a specific budget and date range for a user."""
        pass

    @abstractmethod
    async def save(self, statistics_record: StatisticsRecord) -> None:
        """Saves (creates or updates) a statistics record."""
        pass
