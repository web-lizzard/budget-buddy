from domain.aggregates.budget import Budget
from domain.exceptions import CannotRenewDeactivatedBudgetError
from domain.factories.budget_factory import BudgetFactory, CategoryInput


class BudgetRenewalService:
    def __init__(self, budget_factory: BudgetFactory):
        self._budget_factory = budget_factory

    async def renew_budget(self, budget: Budget) -> Budget:
        """Service for renewing a budget."""

        """
        Renew a budget by creating a new one based on the provided budget.

        Args:
            budget: The budget to renew

        Returns:
            A new Budget instance with the same parameters but a new period

        Raises:
            CannotRenewDeactivatedBudgetError: If the budget is deactivated
        """
        # Check if the budget is deactivated
        if not budget.is_active:
            raise CannotRenewDeactivatedBudgetError(str(budget.id))

        # Create a new budget with the same parameters but a new period
        # Use the end date of the original budget as the start date for the new one
        categories_data = [
            CategoryInput(
                name=category.name,
                limit=category.limit,
            )
            for category in budget.categories
        ]

        new_budget = await self._budget_factory.create_budget(
            user_id=budget.user_id,
            total_limit=budget.total_limit,
            budget_strategy_input=budget.strategy_input,
            start_date=budget.end_date,
            categories=categories_data,
        )
        return new_budget
