from dataclasses import dataclass
from typing import Optional

from application.commands.command import Command


@dataclass(frozen=True)
class RemoveCategoryCommand(Command):
    """Command to remove a category from a budget."""

    category_id: str
    budget_id: str
    user_id: str
    handle_transactions: str  # "delete" or "move"
    target_category_id: Optional[str] = None  # Required if handle_transactions="move"
