from dataclasses import dataclass

from .query import Query


# Define the query for getting all budgets for a user.
@dataclass(frozen=True)
class GetBudgetsQuery(Query):  # Query is not generic, remove type argument
    """
    Query to retrieve a list of budgets with filtering, pagination, and sorting options.

    Attributes:
        status (str | None): Filter budgets by status (e.g., 'active' or 'expired').
        page (int): Page number for pagination.
        limit (int): Number of budgets per page.
        sort (str | None): Field by which to sort the results (e.g., 'start_date').
    """

    status: str | None = None
    page: int = 1
    limit: int = 10
    sort: str | None = None
