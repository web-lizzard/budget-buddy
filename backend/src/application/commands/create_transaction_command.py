from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.value_objects import TransactionType

from .command import Command


@dataclass(frozen=True)
class CreateTransactionCommand(Command):
    """Command for creating a new transaction."""

    category_id: UUID
    budget_id: UUID
    user_id: UUID
    amount: float
    transaction_type: TransactionType
    occurred_date: datetime | None = None
    description: str | None = None
