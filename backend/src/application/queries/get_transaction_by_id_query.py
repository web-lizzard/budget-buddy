from dataclasses import dataclass
from uuid import UUID

from .query import Query


@dataclass
class GetTransactionByIdQuery(Query):
    """
    Query for retrieving details of a specific transaction within a budget.

    Attributes:
        budget_id (UUID): The unique identifier of the budget.
        transaction_id (str): The unique identifier of the transaction.
    """

    budget_id: UUID
    user_id: UUID
    transaction_id: str
