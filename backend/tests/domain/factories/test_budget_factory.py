import uuid
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest
from domain.aggregates import Budget
from domain.factories import BudgetFactory
from domain.strategies.budget_strategy import BudgetStrategy
from domain.value_objects import CategoryName, Limit, Money, MonthlyBudgetStrategyInput


class TestBudgetFactory:
    @pytest.fixture
    def mock_strategy(self):
        """Fixture for a mock budget strategy."""
        strategy = MagicMock(spec=BudgetStrategy)
        strategy.calculate_budget_date = AsyncMock()
        return strategy

    @pytest.fixture
    def budget_factory(self, mock_strategy):
        """Fixture for a budget factory with a mock strategy."""
        return BudgetFactory(strategy=mock_strategy)

    @pytest.mark.asyncio
    async def test_create_budget(self, budget_factory, mock_strategy):
        """Test creating a budget using the factory."""
        # Arrange
        user_id = uuid.uuid4()
        total_limit = Limit(Money(50000, "USD"))
        strategy_input = MonthlyBudgetStrategyInput(start_day=15)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        # Configure the mock strategy to return a specific end date
        mock_strategy.calculate_budget_date.return_value = end_date

        # Act
        budget = await budget_factory.create_budget(
            user_id=user_id,
            total_limit=total_limit,
            budget_strategy_input=strategy_input,
            start_date=start_date,
            categories=[],  # No categories
        )

        # Assert
        mock_strategy.calculate_budget_date.assert_called_once_with(
            budget_strategy_input=strategy_input, start_date=start_date
        )

        assert isinstance(budget, Budget)
        assert budget.user_id == user_id
        assert budget.total_limit == total_limit
        assert budget.start_date == start_date
        assert budget.end_date == end_date
        assert budget.categories == []

    @pytest.mark.asyncio
    async def test_create_budget_with_categories(self, budget_factory, mock_strategy):
        """Test creating a budget with categories using the factory."""
        # Arrange
        user_id = uuid.uuid4()
        total_limit = Limit(Money(50000, "USD"))
        strategy_input = MonthlyBudgetStrategyInput(start_day=15)
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        # Configure the mock strategy to return a specific end date
        mock_strategy.calculate_budget_date.return_value = end_date

        # Create category inputs
        class CategoryInput:
            def __init__(self, name, limit):
                self.name = name
                self.limit = limit

        category_inputs = [
            CategoryInput(
                name=CategoryName("Groceries"),
                limit=Limit(Money(10000, "USD")),
            ),
            CategoryInput(
                name=CategoryName("Entertainment"),
                limit=Limit(Money(5000, "USD")),
            ),
        ]

        # Act
        budget = await budget_factory.create_budget(
            user_id=user_id,
            total_limit=total_limit,
            budget_strategy_input=strategy_input,
            start_date=start_date,
            categories=category_inputs,
        )

        # Assert
        mock_strategy.calculate_budget_date.assert_called_once_with(
            budget_strategy_input=strategy_input, start_date=start_date
        )

        assert isinstance(budget, Budget)
        assert budget.user_id == user_id
        assert budget.total_limit == total_limit
        assert budget.start_date == start_date
        assert budget.end_date == end_date
        assert len(budget.categories) == 2
        assert budget.categories[0].name.value == "Groceries"
        assert budget.categories[1].name.value == "Entertainment"
