from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetTransactionsQuery(Query):
    """
    Query to retrieve a list of transactions for a specified budget.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
        date_from (str | None): Start date filter (YYYY-MM-DD).
        date_to (str | None): End date filter (YYYY-MM-DD).
        page (int): Page number for pagination.
        limit (int): Number of transactions per page.
        sort (str | None): Field to sort transactions (e.g., 'occurred_date').
    """

    budget_id: UUID
    user_id: UUID
    date_from: str | None = None
    date_to: str | None = None
    page: int = 1
    limit: int = 10
    sort: str | None = None
