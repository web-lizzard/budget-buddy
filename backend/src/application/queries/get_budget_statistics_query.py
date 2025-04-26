from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetBudgetStatisticsQuery(Query):
    """
    Query for retrieving overall financial statistics for a budget for a specific user.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
        user_id (UUID): The unique identifier of the user requesting the statistics.
    """

    budget_id: UUID
    user_id: UUID
