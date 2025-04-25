# Assuming domain Budget exists and IN_MEMORY_DATABASE structure
from typing import Any

from application.dtos import BudgetDTO
from application.queries import GetBudgetByIdQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError

from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,
    IN_MEMORY_DATABASE,
)

from .mappers import map_budget_to_dto


class GetBudgetByIdQueryHandler(QueryHandler[GetBudgetByIdQuery, BudgetDTO]):
    """Handles the GetBudgetByIdQuery for the in-memory repository.
    NOTE: Uses DEFAULT_USER_ID as user_id is not part of the query.
    """

    def __init__(self, database_dict: dict[str, dict[Any, Any]] | None = None) -> None:
        """Initializes the handler, optionally injecting a database dictionary.

        Args:
            database_dict: An optional dictionary representing the database tables.
                         If None, uses the default IN_MEMORY_DATABASE.
        """
        self._db = (
            database_dict
            if database_dict is not None
            else IN_MEMORY_DATABASE.get_database()
        )

    async def handle(self, query: GetBudgetByIdQuery) -> BudgetDTO:
        """Retrieves a budget by its ID for the default user.

        Args:
            query: The GetBudgetByIdQuery containing budget_id.

        Returns:
            The corresponding BudgetDTO.

        Raises:
            BudgetNotFoundError: If the budget with the given ID is not found for the default user.
        """
        user_id_to_check = DEFAULT_USER_ID  # Use default user ID

        # Use the stored database dictionary
        budgets_table = self._db.get("budgets", {})

        # In-memory stores budget tuple: (version, budget_object)
        budget_data = budgets_table.get(query.budget_id)
        if not budget_data or budget_data.user_id != user_id_to_check:
            raise BudgetNotFoundError(
                f"Budget with ID {query.budget_id} not found for user {user_id_to_check}"
            )

        return map_budget_to_dto(budget_data)
