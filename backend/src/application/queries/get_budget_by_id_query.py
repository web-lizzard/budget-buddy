from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetBudgetByIdQuery(Query):
    """
    Query for retrieving a detailed budget by its ID.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
    """

    budget_id: UUID
