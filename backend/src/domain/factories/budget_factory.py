from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from domain.aggregates.budget import Budget
from domain.strategies.budget_strategy import BudgetStrategy
from domain.value_objects import BudgetStrategyInput, Limit
from domain.value_objects.category_name import CategoryName


@dataclass(frozen=True)
class CategoryInput:
    """Input for creating a Category."""

    name: CategoryName
    limit: Limit


class BudgetFactory:
    """Factory for creating Budget aggregates."""

    def __init__(self, strategies: list[BudgetStrategy]):
        """
        Initialize the factory with a strategy.

        Args:
            strategies: List of budget strategies to be used
        """
        self._strategies = strategies

    async def create_budget(
        self,
        user_id: UUID,
        total_limit: Limit,
        budget_strategy_input: BudgetStrategyInput,
        start_date: datetime,
        categories: list[CategoryInput],
    ) -> Budget:
        """
        Create a budget using the factory's strategy.

        Args:
            user_id: User ID
            total_limit: Total budget limit
            budget_strategy_input: Strategy input parameters
            start_date: Start date for the budget

        Returns:
            A new Budget aggregate
        """

        strategy = self._get_strategy(budget_strategy_input)
        # Calculate end date using strategy
        end_date = await strategy.calculate_budget_date(
            budget_strategy_input=budget_strategy_input, start_date=start_date
        )

        # Create and return a new budget
        budget = Budget(
            id=uuid4(),
            user_id=user_id,
            total_limit=total_limit,
            start_date=start_date,
            end_date=end_date,
            strategy_input=budget_strategy_input,
        )

        for category_input in categories:
            budget.add_category(
                name=category_input.name,
                limit=category_input.limit,
            )

        return budget

    def _get_strategy(
        self, budget_strategy_input: BudgetStrategyInput
    ) -> BudgetStrategy:
        for strategy in self._strategies:
            if strategy.is_active(budget_strategy_input):
                return strategy
        raise ValueError(f"No strategy found for {budget_strategy_input}")
