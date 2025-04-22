from domain.strategies.budget_strategy.budget_strategy import BudgetStrategy
from domain.strategies.budget_strategy.monthly_budget_strategy import (
    MonthlyBudgetStrategy,
)
from domain.strategies.budget_strategy.yearly_budget_strategy import (
    YearlyBudgetStrategy,
)
from domain.value_objects import BudgetStrategyType

__all__ = [
    "BudgetStrategy",
    "MonthlyBudgetStrategy",
    "YearlyBudgetStrategy",
    "create_strategy",
]


def create_strategy(budget_strategy_type: BudgetStrategyType) -> BudgetStrategy:
    """
    Factory method for creating budget strategy instances.

    Args:
        budget_strategy_type: Type of the budget strategy

    Returns:
        Budget strategy instance

    Raises:
        ValueError: If the strategy type is not supported
    """
    strategies = {
        BudgetStrategyType.MONTHLY: MonthlyBudgetStrategy,
        BudgetStrategyType.YEARLY: YearlyBudgetStrategy,
    }

    if budget_strategy_type not in strategies:
        raise ValueError(f"Unsupported budget strategy type: {budget_strategy_type}")

    strategy_cls = strategies[budget_strategy_type]
    return strategy_cls()
