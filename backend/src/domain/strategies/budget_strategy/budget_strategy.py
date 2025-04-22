from abc import ABC, abstractmethod
from datetime import datetime

from domain.value_objects import BudgetStrategyInput


class BudgetStrategy(ABC):
    @abstractmethod
    async def calculate_budget_date(
        self, budget_strategy_input: BudgetStrategyInput, start_date: datetime
    ) -> datetime:
        pass

    @abstractmethod
    def is_active(self, budget_strategy_input: BudgetStrategyInput) -> bool:
        pass
