from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetCategoryByIdQuery(Query):
    """
    Query for retrieving details of a specific category within a budget.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
        category_id (UUID): The unique identifier of the category.
    """

    budget_id: UUID
    category_id: UUID
