import uuid
from datetime import date

from domain.aggregates.statistics_record import StatisticsRecord
from domain.exceptions.statistics_record_not_found_error import (
    StatisticsRecordNotFoundError,
)
from domain.ports.outbound.statistics_repository import StatisticsRepository

from .database import IN_MEMORY_DATABASE


class InMemoryStatisticsRepository(StatisticsRepository):
    """In-memory implementation of the StatisticsRepository port."""

    def __init__(
        self,
        records: dict[uuid.UUID, StatisticsRecord] | None = None,
    ) -> None:
        # Store records indexed by user_id, then statistic_id for efficient lookup
        self._records: dict[uuid.UUID, StatisticsRecord] = (
            records
            if records is not None
            else IN_MEMORY_DATABASE.get_database()["statistic_records"]
        )

    async def save(self, statistics_record: StatisticsRecord) -> None:
        """Saves (creates or updates) a statistics record in memory."""

        self._records[statistics_record.id] = statistics_record

    async def find_by_id(
        self, statistic_id: uuid.UUID, user_id: uuid.UUID
    ) -> StatisticsRecord:
        """Finds a statistics record by its ID for a specific user."""
        record = self._records.get(statistic_id)
        if record is None or record.user_id != user_id:
            raise StatisticsRecordNotFoundError(
                f"Statistics record with ID {statistic_id} not found for user {user_id}"
            )
        return record

    async def find_by_budget_id(
        self, budget_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records for a specific budget and user."""
        return [
            record for record in self._records.values() if record.budget_id == budget_id
        ]

    async def find_by_category_id(
        self, category_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """
        Finds all statistics records that have a specific category_id
        within their categories_statistics list for a specific user.
        NOTE: This assumes StatisticsRecord has categories_statistics list.
        If category_id is a direct attribute of StatisticsRecord (which was removed),
        the logic would be simpler.
        """
        return [
            record
            for record in self._records.values()
            if any(cs.category_id == category_id for cs in record.categories_statistics)
        ]

    async def find_by_date_range(
        self, start_date: date, end_date: date, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds all statistics records within a date range (based on creation_date) for a user."""
        return [
            record
            for record in self._records.values()
            if start_date <= record.creation_date.date() <= end_date
        ]

    async def find_by_budget_id_and_date_range(
        self, budget_id: uuid.UUID, start_date: date, end_date: date, user_id: uuid.UUID
    ) -> list[StatisticsRecord]:
        """Finds records for a specific budget and date range for a user."""
        return [
            record
            for record in self._records.values()
            if record.budget_id == budget_id
            and start_date <= record.creation_date.date() <= end_date
        ]

    async def find_by_transaction_id(
        self, transaction_id: uuid.UUID, user_id: uuid.UUID
    ) -> StatisticsRecord:
        """Finds a statistics record by its transaction ID for a specific user."""
        record = next(
            (
                record
                for record in self._records.values()
                if record.transaction_id == transaction_id
            ),
            None,
        )
        if record is None:
            raise StatisticsRecordNotFoundError(
                f"Statistics record with transaction ID {transaction_id} not found for user {user_id}"
            )
        return record
