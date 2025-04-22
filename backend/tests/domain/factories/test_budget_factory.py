import uuid
from datetime import datetime

import pytest
from domain.aggregates import Budget
from domain.factories import BudgetFactory
from domain.factories.budget_factory import CategoryInput
from domain.strategies.budget_strategy import create_strategy
from domain.value_objects import (
    BudgetStrategyType,
    CategoryName,
    Limit,
    Money,
    MonthlyBudgetStrategyInput,
    YearlyBudgetStrategyInput,
)


class TestBudgetFactory:
    @pytest.fixture
    def monthly_strategy(self):
        """Fixture for monthly budget strategy."""
        return create_strategy(BudgetStrategyType.MONTHLY)

    @pytest.fixture
    def yearly_strategy(self):
        """Fixture for yearly budget strategy."""
        return create_strategy(BudgetStrategyType.YEARLY)

    @pytest.fixture
    def budget_factory(self, monthly_strategy, yearly_strategy):
        """Fixture for a budget factory with both strategies."""
        return BudgetFactory(strategies=[monthly_strategy, yearly_strategy])

    @pytest.mark.asyncio
    async def test_create_budget_with_monthly_strategy(self, budget_factory):
        """Test creating a budget using monthly strategy."""
        # Arrange
        user_id = uuid.uuid4()
        total_limit = Limit(Money.mint(500.00, "USD"))
        strategy_input = MonthlyBudgetStrategyInput(start_day=15)
        start_date = datetime(2023, 5, 15)

        # Act
        budget = await budget_factory.create_budget(
            user_id=user_id,
            total_limit=total_limit,
            budget_strategy_input=strategy_input,
            start_date=start_date,
            categories=[],  # No categories
        )

        # Assert
        assert isinstance(budget, Budget)
        assert budget.user_id == user_id
        assert budget.total_limit == total_limit
        assert budget.start_date == start_date
        # Końcowa data powinna być około miesiąc później (14 czerwca 23:59:59)
        expected_end_date = datetime(2023, 6, 14, 23, 59, 59)
        assert budget.end_date == expected_end_date
        assert budget.categories == []

    @pytest.mark.asyncio
    async def test_create_budget_with_yearly_strategy(self, budget_factory):
        """Test creating a budget using yearly strategy."""
        # Arrange
        user_id = uuid.uuid4()
        total_limit = Limit(Money.mint(5000.00, "USD"))
        strategy_input = YearlyBudgetStrategyInput(start_month=3, start_day=15)
        start_date = datetime(2023, 3, 15)

        # Act
        budget = await budget_factory.create_budget(
            user_id=user_id,
            total_limit=total_limit,
            budget_strategy_input=strategy_input,
            start_date=start_date,
            categories=[],  # No categories
        )

        # Assert
        assert isinstance(budget, Budget)
        assert budget.user_id == user_id
        assert budget.total_limit == total_limit
        assert budget.start_date == start_date
        # Końcowa data powinna być rok później (14 marca 2024 23:59:59)
        expected_end_date = datetime(2024, 3, 14, 23, 59, 59)
        assert budget.end_date == expected_end_date
        assert budget.categories == []

    @pytest.mark.asyncio
    async def test_create_budget_with_categories(self, budget_factory):
        """Test creating a budget with categories."""
        # Arrange
        user_id = uuid.uuid4()
        total_limit = Limit(Money.mint(500.00, "USD"))
        strategy_input = MonthlyBudgetStrategyInput(start_day=1)
        start_date = datetime(2023, 5, 1)

        # Create category inputs
        category_inputs = [
            CategoryInput(
                name=CategoryName("Groceries"),
                limit=Limit(Money.mint(100.00, "USD")),
            ),
            CategoryInput(
                name=CategoryName("Entertainment"),
                limit=Limit(Money.mint(50.00, "USD")),
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
        assert isinstance(budget, Budget)
        assert budget.user_id == user_id
        assert budget.total_limit == total_limit
        assert budget.start_date == start_date
        expected_end_date = datetime(2023, 5, 31, 23, 59, 59)
        assert budget.end_date == expected_end_date
        assert len(budget.categories) == 2
        assert budget.categories[0].name.value == "Groceries"
        assert budget.categories[1].name.value == "Entertainment"

    @pytest.mark.asyncio
    async def test_strategy_selection(self, budget_factory):
        """Test that factory correctly selects strategy based on input type."""
        # Arrange
        user_id = uuid.uuid4()
        total_limit = Limit(Money.mint(1000.00, "USD"))
        monthly_input = MonthlyBudgetStrategyInput(start_day=1)
        yearly_input = YearlyBudgetStrategyInput(start_month=1, start_day=1)
        start_date = datetime(2023, 1, 1)

        # Act & Assert for monthly
        monthly_budget = await budget_factory.create_budget(
            user_id=user_id,
            total_limit=total_limit,
            budget_strategy_input=monthly_input,
            start_date=start_date,
            categories=[],
        )

        # End date should be end of January
        assert monthly_budget.end_date == datetime(2023, 1, 31, 23, 59, 59)

        # Act & Assert for yearly
        yearly_budget = await budget_factory.create_budget(
            user_id=user_id,
            total_limit=total_limit,
            budget_strategy_input=yearly_input,
            start_date=start_date,
            categories=[],
        )

        # End date should be end of the year
        assert yearly_budget.end_date == datetime(2023, 12, 31, 23, 59, 59)
