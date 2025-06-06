from typing import Any

from application.dtos import BudgetDTO
from application.dtos.paginated_item_dto import PaginatedItemDTO
from application.queries import GetBudgetsQuery
from application.queries.handlers import QueryHandler

# Assuming domain Budget exists and IN_MEMORY_DATABASE structure
from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,  # Using default user ID for this handler
    IN_MEMORY_DATABASE,
)

from .mappers import map_budget_to_dto


class GetBudgetsQueryHandler(
    QueryHandler[GetBudgetsQuery, PaginatedItemDTO[BudgetDTO]]
):
    """Handles the GetBudgetsQuery for the in-memory repository.
    NOTE: Uses DEFAULT_USER_ID as user_id is not part of the query.
          Performs pagination in memory.
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

    async def handle(self, query: GetBudgetsQuery) -> PaginatedItemDTO[BudgetDTO]:
        """Retrieves budgets for the default user with pagination.

        Args:
            query: The GetBudgetsQuery containing pagination options.

        Returns:
            A PaginatedItemDTO containing the paginated list of BudgetDTOs for the default user.
        """
        user_id_to_check = DEFAULT_USER_ID

        budgets_table = self._db.get("budgets", {})
        all_user_budgets_domain = []

        for _budget_id, budget_data in budgets_table.items():
            _version, budget = budget_data
            if budget.user_id == user_id_to_check:
                all_user_budgets_domain.append(budget)

        total_count = len(all_user_budgets_domain)
        skip = (query.page - 1) * query.limit
        start_index = skip
        end_index = start_index + query.limit
        paginated_budgets_domain = all_user_budgets_domain[start_index:end_index]

        budget_dtos: list[BudgetDTO] = [
            map_budget_to_dto(budget) for budget in paginated_budgets_domain
        ]

        return PaginatedItemDTO[BudgetDTO](
            items=budget_dtos,
            total=total_count,
            skip=skip,
            limit=query.limit,
        )
