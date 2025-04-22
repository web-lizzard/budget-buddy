from datetime import datetime, timedelta

import pytest
from domain.strategies.budget_strategy import MonthlyBudgetStrategy
from domain.value_objects import MonthlyBudgetStrategyInput


class TestMonthlyBudgetStrategy:
    @pytest.fixture
    def strategy(self):
        """Fixture for the monthly budget strategy."""
        return MonthlyBudgetStrategy()

    @pytest.mark.asyncio
    async def test_calculate_budget_date_same_month(self, strategy):
        """Test calculating budget end date for a start date in the same month."""
        # Arrange
        start_day = 15
        strategy_input = MonthlyBudgetStrategyInput(start_day=start_day)
        now = datetime.now()

        # Make sure start_date is on the specified start_day
        start_date = datetime(
            year=now.year,
            month=now.month,
            day=start_day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be the day before start_day in the next month
        if start_date.month == 12:
            expected_month = 1
            expected_year = start_date.year + 1
        else:
            expected_month = start_date.month + 1
            expected_year = start_date.year

        expected_date = datetime(
            year=expected_year,
            month=expected_month,
            day=start_day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.day == (
            start_day - 1
            if start_day > 1
            else [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
                (expected_month - 2) % 12
            ]
        )

    @pytest.mark.asyncio
    async def test_calculate_budget_date_leap_year(self, strategy):
        """Test calculating budget end date when February of a leap year is involved."""
        # Arrange - using a known leap year (2024) for predictability
        start_day = 15
        strategy_input = MonthlyBudgetStrategyInput(start_day=start_day)
        start_date = datetime(2024, 1, start_day, 0, 0, 0, 0)

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be Feb 14, 2024 at 23:59:59
        expected_date = datetime(2024, 2, start_day, 0, 0, 0, 0) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.month == 2
        assert end_date.day == 14  # Day before the 15th

    @pytest.mark.asyncio
    async def test_calculate_budget_date_month_transition(self, strategy):
        """Test calculating budget end date when transitioning between months."""
        # Arrange
        strategy_input = MonthlyBudgetStrategyInput(start_day=1)
        start_date = datetime(2023, 3, 1, 0, 0, 0, 0)

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be Mar 31, 2023 at 23:59:59
        expected_date = datetime(2023, 4, 1, 0, 0, 0, 0) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.month == 3
        assert end_date.day == 31  # Last day of March

    @pytest.mark.asyncio
    async def test_calculate_budget_date_incorrect_input_type(self, strategy):
        """Test calculating budget end date with incorrect input type."""

        # Arrange - Using a non-MonthlyBudgetStrategyInput
        class DummyInput:
            pass

        dummy_input = DummyInput()
        start_date = datetime.now()

        # Act & Assert
        with pytest.raises(TypeError):
            await strategy.calculate_budget_date(dummy_input, start_date)
