import uuid
from dataclasses import dataclass

from application.commands.command import Command


@dataclass(frozen=True)
class CalculateStatisticsCommand(Command):
    """Command to trigger the calculation of statistics for a specific budget."""

    user_id: uuid.UUID
    budget_id: uuid.UUID
    transaction_id: uuid.UUID
