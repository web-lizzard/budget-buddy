# NOTE: Linter might complain about DTOs, assume they exist
from uuid import UUID

from application.dtos import StatisticsRecordDTO
from application.queries import GetBudgetStatisticsQuery
from application.queries.handlers import QueryHandler
from domain.aggregates.statistics_record import StatisticsRecord

# Import the concrete repository implementation and default user ID
from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,
    IN_MEMORY_DATABASE,
)
from adapters.outbound.persistence.in_memory.statistics_repository import (
    InMemoryStatisticsRepository,
)

from .mappers import map_statistics_record_to_dto


class GetBudgetStatisticsQueryHandler(
    QueryHandler[GetBudgetStatisticsQuery, StatisticsRecordDTO]
):
    """Handles the GetBudgetStatisticsQuery for the in-memory repository.
    NOTE: Uses DEFAULT_USER_ID as user_id is not part of the query.
    """

    def __init__(
        self, records_dict: dict[str, dict[UUID, StatisticsRecord]] | None = None
    ) -> None:
        """Initializes the handler, optionally injecting a records dictionary.

        Args:
            records_dict: An optional dictionary representing the records tables.
                         If None, uses the default IN_MEMORY_DATABASE.
        """
        records = (
            records_dict
            if records_dict is not None
            else IN_MEMORY_DATABASE.get_database()["statistic_records"]
        )
        # Initialize the repository (it will use the singleton DB instance)
        self.statistics_repo = InMemoryStatisticsRepository(records)

    async def handle(self, query: GetBudgetStatisticsQuery) -> StatisticsRecordDTO:
        """Retrieves the overall statistics record for a specific budget owned by the default user.

        Args:
            query: The GetBudgetStatisticsQuery containing budget_id.

        Returns:
            The corresponding StatisticsRecordDTO.

        Raises:
            StatisticsNotFoundError: If no statistics record is found for the specified budget and default user.
        """
        user_id_to_check = DEFAULT_USER_ID

        # Find statistics records associated with the budget ID and user ID
        statistics_records = await self.statistics_repo.find_by_budget_id(
            budget_id=query.budget_id, user_id=user_id_to_check
        )
        statistics_record = statistics_records[0]

        statistics_dto = map_statistics_record_to_dto(statistics_record)
        return statistics_dto
