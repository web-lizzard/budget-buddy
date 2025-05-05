from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from .command import Command


@dataclass(frozen=True)
class CreateTransactionCommand(Command):
    """Command for creating a new transaction."""

    category_id: UUID
    budget_id: UUID
    user_id: UUID
    amount: float
    transaction_type: str
    occurred_date: datetime | None = None
    description: str | None = None
