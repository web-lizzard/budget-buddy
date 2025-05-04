from datetime import datetime

from domain.aggregates.budget import Budget
from domain.ports.clock import Clock


class BudgetDeactivationService:
    """Service responsible for deactivating a budget."""

    def __init__(self, clock: Clock):
        """
        Initialize the service with dependencies.

        Args:
            budget_repository: Repository for accessing budgets.
            clock: Clock provider for getting the current time.
        """
        self._clock = clock

    async def deactivate(self, budget: Budget) -> datetime:
        """
        Deactivates a budget for a given user.

        Fetches the budget, deactivates it using the current time,
        and returns the modified budget aggregate.
        The caller is responsible for saving the changes.

        Args:
            budget: The budget to deactivate.

        Returns:
            The deactivated Budget aggregate.

        Raises:
            BudgetNotFoundError: If the budget is not found for the user.
        """

        # Get the current time from the Clock port
        deactivation_time: datetime = self._clock.now()

        # Call the aggregate method to perform deactivation
        budget.deactivate_budget(deactivation_time=deactivation_time)

        # Note: Saving the budget is handled by the command handler's UoW

        return deactivation_time
