from dataclasses import dataclass
from uuid import UUID

from .command import Command


@dataclass(frozen=True)
class DeactivateBudgetCommand(Command):
    """Command for deactivating a budget."""

    budget_id: UUID
    user_id: UUID
