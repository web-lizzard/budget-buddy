from datetime import datetime, timedelta

from domain.strategies.budget_strategy.budget_strategy import BudgetStrategy
from domain.value_objects import BudgetStrategyInput, YearlyBudgetStrategyInput


class YearlyBudgetStrategy(BudgetStrategy):
    """
    Strategy for calculating yearly budget end date.

    A yearly budget starts on the specified day and month
    and ends on the day before that date in the next year.
    """

    async def calculate_budget_date(
        self, budget_strategy_input: BudgetStrategyInput, start_date: datetime
    ) -> datetime:
        """
        Calculate the end date for a yearly budget.

        Args:
            budget_strategy_input: Input parameters for budget strategy calculation
            start_date: Start date for the budget

        Returns:
            End date for the budget

        Raises:
            TypeError: If the input is not a YearlyBudgetStrategyInput
        """
        if not isinstance(budget_strategy_input, YearlyBudgetStrategyInput):
            raise TypeError(
                f"Expected YearlyBudgetStrategyInput, got {type(budget_strategy_input).__name__}"
            )

        # Calculate the end date (one year later from start_date)
        end_date = start_date.replace(year=start_date.year + 1)

        # Subtract 1 second to get the end of the previous day
        end_date = end_date - timedelta(seconds=1)

        return end_date
