from dataclasses import dataclass

from application.commands.command import Command


@dataclass(frozen=True)
class AddCategoryCommand(Command):
    """
    Command to add a new category to a budget.

    Attributes:
        budget_id: The ID of the budget to add the category to
        user_id: The ID of the user who owns the budget
        name: The name of the category
        limit: The spending limit of the category
    """

    budget_id: str
    user_id: str
    name: str
    limit: float
