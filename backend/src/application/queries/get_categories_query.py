from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetCategoriesQuery(Query):
    """
    Query for retrieving all categories for a given budget.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
    """

    budget_id: UUID
