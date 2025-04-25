# Assuming domain Budget/Category exists and IN_MEMORY_DATABASE structure
from typing import Any

from application.dtos import CategoryDTO
from application.queries import GetCategoryByIdQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError, CategoryNotFoundError

from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,  # Using default user ID for this handler
    IN_MEMORY_DATABASE,
)

from .mappers import map_category_to_dto


class GetCategoryByIdQueryHandler(QueryHandler[GetCategoryByIdQuery, CategoryDTO]):
    """Handles the GetCategoryByIdQuery for the in-memory repository.
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

    async def handle(self, query: GetCategoryByIdQuery) -> CategoryDTO:
        """Retrieves a specific category by its ID within a budget owned by the default user.

        Args:
            query: The GetCategoryByIdQuery containing budget_id and category_id.

        Returns:
            The corresponding CategoryDTO.

        Raises:
            BudgetNotFoundError: If the budget is not found for the default user.
            CategoryNotFoundError: If the category is not found within the specified budget.
        """
        user_id_to_check = DEFAULT_USER_ID

        budgets_table = self._db.get("budgets", {})
        budget_data = budgets_table.get(query.budget_id)

        if not budget_data:
            raise BudgetNotFoundError(f"Budget with ID {query.budget_id} not found.")

        _version, budget = budget_data

        # Verify user ownership
        if budget.user_id != user_id_to_check:
            raise BudgetNotFoundError(
                f"Budget with ID {query.budget_id} not found for user {user_id_to_check}"
            )

        # Assuming budget domain object has a 'categories' list attribute
        domain_categories = getattr(budget, "categories", [])
        found_category = None
        for category in domain_categories:
            # Assuming category domain object has an 'id' attribute
            if getattr(category, "id", None) == query.category_id:
                found_category = category
                break

        if found_category is None:
            raise CategoryNotFoundError(
                f"Category with ID {query.category_id} not found in budget {query.budget_id}"
            )

        category_dto = map_category_to_dto(found_category)
        return category_dto
