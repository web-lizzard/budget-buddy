import uuid
from dataclasses import dataclass
from datetime import datetime

from application.commands.command import Command


@dataclass(frozen=True)
class RecalculateStatisticsAfterUpdateCommand(Command):
    """Command to recalculate statistics after a transaction update."""

    transaction_id: uuid.UUID
    budget_id: uuid.UUID
    user_id: uuid.UUID
    transaction_occurred_date: datetime
