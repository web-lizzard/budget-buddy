from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from application.commands.command import Command


@dataclass(frozen=True)
class EditTransactionCommand(Command):
    """Command for editing an existing transaction."""

    transaction_id: UUID
    budget_id: UUID
    user_id: UUID
    category_id: UUID | None
    amount: float | None
    transaction_type: str | None
    description: str | None
    occurred_date: datetime | None
