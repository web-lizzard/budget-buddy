from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetBudgetByIdQuery(Query):
    """
    Query for retrieving a detailed budget by its ID for a specific user.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
        user_id (UUID): The unique identifier of the user requesting the budget.
    """

    budget_id: UUID
    user_id: UUID
