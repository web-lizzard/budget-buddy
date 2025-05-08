from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from application.commands.command import Command


@dataclass(frozen=True)
class RemoveCategoryCommand(Command):
    """Command to remove a category from a budget."""

    category_id: UUID
    budget_id: UUID
    user_id: UUID
    handle_transactions: str  # "delete" or "move"
    target_category_id: Optional[UUID] = None  # Required if handle_transactions="move"
