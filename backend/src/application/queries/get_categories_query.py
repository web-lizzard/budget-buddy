import uuid
from dataclasses import dataclass

from .query import Query


@dataclass(frozen=True)
class GetCategoriesQuery(Query):
    """
    Query for retrieving all categories for a given budget.

    Attributes:
        budget_id (uuid.UUID): The unique identifier of the budget.
    """

    budget_id: uuid.UUID
