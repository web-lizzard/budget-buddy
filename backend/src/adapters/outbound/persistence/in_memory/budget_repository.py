from typing import Tuple
from uuid import UUID

from domain.aggregates.budget import Budget
from domain.exceptions import BudgetNotFoundError, NotCompatibleVersionError
from domain.ports.budget_repository import BudgetRepository

from .database import IN_MEMORY_DATABASE


class InMemoryBudgetRepository(BudgetRepository):
    """In-memory implementation of budget repository."""

    def __init__(self, budgets: dict | None, users: dict | None):
        """Initialize repository."""
        self._budgets = budgets or IN_MEMORY_DATABASE.get_database()["budgets"]
        self._users = users or IN_MEMORY_DATABASE.get_database()["users"]

    async def find_by(self, budget_id: UUID, user_id: UUID) -> Tuple[int, Budget]:
        """Find budget by id and user id.

        Args:
            budget_id: The ID of the budget to find
            user_id: The ID of the user who owns the budget

        Returns:
            Tuple containing version number and budget

        Raises:
            BudgetNotFoundError: When budget is not found or belongs to different user
        """
        if budget_id not in self._budgets:
            raise BudgetNotFoundError(str(budget_id))

        if user_id not in self._users:
            raise BudgetNotFoundError(str(budget_id))

        version, budget = self._budgets.get(budget_id, None)

        if budget is None or budget.user_id != user_id:
            raise BudgetNotFoundError(str(budget_id))

        return version, budget

    async def save(self, budget: Budget, version: int) -> None:
        """Save budget to repository.

        Args:
            budget: The budget to save

        Raises:
            NotCompatibleVersionError: When budget version conflict is detected
        """
        current_version = 0
        if budget.id in self._budgets:
            current_version = self._budgets[budget.id][0]

        if current_version != version:
            raise NotCompatibleVersionError(
                str(budget.id), expected_version=version, actual_version=current_version
            )

        self._budgets[budget.id] = (version, budget)
