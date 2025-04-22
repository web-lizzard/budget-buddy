from datetime import datetime, timedelta

from domain.strategies.budget_strategy.budget_strategy import BudgetStrategy
from domain.value_objects import BudgetStrategyInput, MonthlyBudgetStrategyInput


class MonthlyBudgetStrategy(BudgetStrategy):
    """
    Strategy for calculating monthly budget end date.

    A monthly budget starts on the specified day of the month
    and ends on the day before that date in the next month.
    """

    async def calculate_budget_date(
        self, budget_strategy_input: BudgetStrategyInput, start_date: datetime
    ) -> datetime:
        """
        Calculate the end date for a monthly budget.

        Args:
            budget_strategy_input: Input parameters for budget strategy calculation
            start_date: Start date for the budget

        Returns:
            End date for the budget

        Raises:
            TypeError: If the input is not a MonthlyBudgetStrategyInput
        """
        if not isinstance(budget_strategy_input, MonthlyBudgetStrategyInput):
            raise TypeError(
                f"Expected MonthlyBudgetStrategyInput, got {type(budget_strategy_input).__name__}"
            )

        # Calculate the end date (one month later from start_date)
        if start_date.month == 12:
            end_date = start_date.replace(year=start_date.year + 1, month=1)
        else:
            end_date = start_date.replace(month=start_date.month + 1)

        # Subtract 1 second to get the end of the previous day
        end_date = end_date - timedelta(seconds=1)

        return end_date
