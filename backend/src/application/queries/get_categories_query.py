import uuid
from dataclasses import dataclass

from .query import Query


@dataclass(frozen=True)
class GetCategoriesQuery(Query):
    """
    Query for retrieving all categories for a given budget and user.

    Attributes:
        budget_id (uuid.UUID): The unique identifier of the budget.
        user_id (uuid.UUID): The unique identifier of the user requesting categories.
    """

    budget_id: uuid.UUID
    user_id: uuid.UUID
