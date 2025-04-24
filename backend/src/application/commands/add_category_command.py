from dataclasses import dataclass
from uuid import UUID

from .command import Command


@dataclass(frozen=True)
class AddCategoryCommand(Command):
    """Command for adding a new category to an existing budget."""

    budget_id: UUID
    user_id: UUID
    name: str
    limit: float
    currency: str
