from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from domain.aggregates.budget import Budget
from domain.strategies.budget_strategy import BudgetStrategy
from domain.value_objects import BudgetName, BudgetStrategyInput, Limit
from domain.value_objects.category_name import CategoryName


@dataclass(frozen=True)
class CategoryInput:
    """Input for creating a Category."""

    name: CategoryName
    limit: Limit


@dataclass(frozen=True)
class BudgetFactoryParams:
    pass


T = TypeVar("T", bound=BudgetFactoryParams)


@dataclass(frozen=True)
class BudgetCreateParameters(BudgetFactoryParams):
    """Parameters for creating a Budget."""

    user_id: UUID
    total_limit: Limit
    budget_strategy_input: BudgetStrategyInput
    start_date: datetime
    categories: list[CategoryInput]
    name: BudgetName


class BudgetFactory(ABC, Generic[T]):
    """Abstract factory for creating Budget aggregates."""

    @abstractmethod
    async def create(self, params: T) -> Budget:
        """Abstract method to create a budget."""
        raise NotImplementedError


class CreateBudgetFactory(BudgetFactory[BudgetCreateParameters]):
    """Factory for creating Budget aggregates."""

    def __init__(self, strategies: list[BudgetStrategy]):
        """
        Initialize the factory with a strategy.

        Args:
            strategies: List of budget strategies to be used
        """
        self._strategies = strategies

    async def create(self, params: BudgetCreateParameters) -> Budget:
        """
        Create a budget using the factory's strategy based on provided parameters.

        Args:
            params: Budget creation parameters.

        Returns:
            A new Budget aggregate
        """
        strategy = self._get_strategy(params.budget_strategy_input)
        # Calculate end date using strategy
        end_date = await strategy.calculate_budget_date(
            budget_strategy_input=params.budget_strategy_input,
            start_date=params.start_date,
        )

        # Create and return a new budget
        budget = Budget(
            id=uuid4(),
            user_id=params.user_id,
            total_limit=params.total_limit,
            start_date=params.start_date,
            end_date=end_date,
            strategy_input=params.budget_strategy_input,
            name=params.name,
        )

        for category_input in params.categories:
            budget.add_category(
                name=category_input.name,
                limit=category_input.limit,
            )

        return budget

    def _get_strategy(
        self, budget_strategy_input: BudgetStrategyInput
    ) -> BudgetStrategy:
        for strategy in self._strategies:
            if strategy.is_active(budget_strategy_input=budget_strategy_input):
                return strategy
        raise ValueError(f"No strategy found for {budget_strategy_input}")
