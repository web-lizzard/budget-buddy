from dataclasses import dataclass
from uuid import UUID

from .command import Command


@dataclass(frozen=True)
class EditCategoryCommand(Command):
    """
    Command to edit an existing category in a budget.

    Attributes:
        category_id: The ID of the category to edit
        budget_id: The ID of the budget containing the category
        user_id: The ID of the user who owns the budget
        name: The new name of the category
        limit: The new spending limit of the category
    """

    category_id: UUID
    budget_id: UUID
    user_id: UUID
    name: str | None = None
    limit: float | None = None
