from typing import List

from application.dtos import CategoryDTO, CategoryListDTO
from application.queries import GetCategoriesQuery
from application.queries.handlers import QueryHandler
from domain.exceptions import BudgetNotFoundError

# Assuming domain Budget/Category exists and IN_MEMORY_DATABASE structure
from adapters.outbound.persistence.in_memory.database import (
    DEFAULT_USER_ID,  # Using default user ID for this handler
    IN_MEMORY_DATABASE,
)

from .mappers import map_category_to_dto


class GetCategoriesQueryHandler(QueryHandler[GetCategoriesQuery, CategoryListDTO]):
    """Handles the GetCategoriesQuery for the in-memory repository.
    NOTE: Uses DEFAULT_USER_ID as user_id is not part of the query.
    """

    async def handle(self, query: GetCategoriesQuery) -> CategoryListDTO:
        """Retrieves all categories for a specific budget owned by the default user.

        Args:
            query: The GetCategoriesQuery containing budget_id.

        Returns:
            A CategoryListDTO containing a list of CategoryDTOs.

        Raises:
            BudgetNotFoundError: If the budget is not found for the default user.
            Exception: For other mapping or processing errors.
        """
        user_id_to_check = DEFAULT_USER_ID

        budgets_table = IN_MEMORY_DATABASE.get_database().get("budgets", {})
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
        category_dtos: List[CategoryDTO] = []

        for category in domain_categories:
            category_dtos.append(map_category_to_dto(category))

        return CategoryListDTO(categories=category_dtos)
