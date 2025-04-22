from abc import ABC, abstractmethod
from uuid import UUID

from domain.aggregates.budget import Budget


class BudgetRepository(ABC):
    """Port for budget repository operations."""

    @abstractmethod
    async def find_by(self, budget_id: UUID, user_id: UUID) -> tuple[int, Budget]:
        """Find budget by id and user id.

        Args:
            budget_id: The ID of the budget to find
            user_id: The ID of the user who owns the budget

        Returns:
            Tuple containing version number and budget if found, otherwise None

        Raises:
            BudgetNotFoundError: When budget is not found or belongs to different user
        """
        pass

    @abstractmethod
    async def save(self, budget: Budget, version: int) -> None:
        """Save budget to repository.

        Args:
            budget: The budget to save
            version: The version number of the budget

        Raises:
            NotCompatibleVersionError: When budget version conflict is detected
        """
        pass
