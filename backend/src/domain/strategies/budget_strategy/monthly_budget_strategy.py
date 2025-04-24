import calendar
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

        year = start_date.year
        month = start_date.month + 1
        if month > 12:
            month = 1
            year += 1
        last_day_of_next_month = calendar.monthrange(year, month)[1]
        day = min(start_date.day, last_day_of_next_month)
        end_date_raw = datetime(year, month, day)
        end_date = end_date_raw - timedelta(seconds=1)

        return end_date

    def is_active(self, budget_strategy_input: BudgetStrategyInput) -> bool:
        """
        Check if this strategy is applicable for the given input.

        Args:
            budget_strategy_input: Input parameters for budget strategy

        Returns:
            True if this strategy should be used for the given input, False otherwise
        """
        return isinstance(budget_strategy_input, MonthlyBudgetStrategyInput)
