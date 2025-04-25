from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetBudgetStatisticsQuery(Query):
    """
    Query for retrieving overall financial statistics for a budget.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
    """

    budget_id: UUID
