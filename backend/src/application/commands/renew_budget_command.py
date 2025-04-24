from dataclasses import dataclass
from uuid import UUID

from .command import Command


@dataclass(frozen=True)
class RenewBudgetCommand(Command):
    """Command for renewing a budget."""

    budget_id: UUID
    user_id: UUID
