from datetime import datetime, timedelta

import pytest
from domain.strategies.budget_strategy import YearlyBudgetStrategy
from domain.value_objects import YearlyBudgetStrategyInput


class TestYearlyBudgetStrategy:
    @pytest.fixture
    def strategy(self):
        """Fixture for the yearly budget strategy."""
        return YearlyBudgetStrategy()

    @pytest.mark.asyncio
    async def test_calculate_budget_date_same_year(self, strategy):
        """Test calculating budget end date for a start date in the same year."""
        # Arrange
        start_month = 6
        start_day = 15
        strategy_input = YearlyBudgetStrategyInput(
            start_month=start_month, start_day=start_day
        )
        now = datetime.now()

        # Make sure start_date is on the specified start_month and start_day
        start_date = datetime(
            year=now.year,
            month=start_month,
            day=start_day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be the day before start_day/start_month in the next year
        expected_date = datetime(
            year=start_date.year + 1,
            month=start_month,
            day=start_day,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        ) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.year == start_date.year + 1
        assert end_date.month == start_month
        assert end_date.day == start_day - 1  # Day before start_day

    @pytest.mark.asyncio
    async def test_calculate_budget_date_leap_year(self, strategy):
        """Test calculating budget end date when February 29 is involved in a leap year."""
        # Arrange - using a known leap year (2024) for predictability
        strategy_input = YearlyBudgetStrategyInput(start_month=2, start_day=28)
        start_date = datetime(2024, 2, 28, 0, 0, 0, 0)

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be Feb 27, 2025 at 23:59:59
        expected_date = datetime(2025, 2, 28, 0, 0, 0, 0) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.year == 2025
        assert end_date.month == 2
        assert end_date.day == 27  # Day before the 28th

    @pytest.mark.asyncio
    async def test_calculate_budget_date_year_transition(self, strategy):
        """Test calculating budget end date when transitioning between years."""
        # Arrange
        strategy_input = YearlyBudgetStrategyInput(start_month=12, start_day=25)
        start_date = datetime(2023, 12, 25, 0, 0, 0, 0)

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be Dec 24, 2024 at 23:59:59
        expected_date = datetime(2024, 12, 25, 0, 0, 0, 0) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.year == 2024
        assert end_date.month == 12
        assert end_date.day == 24  # Last day of December

    @pytest.mark.asyncio
    async def test_calculate_budget_date_first_day_of_month(self, strategy):
        """Test calculating budget end date when start day is first day of month."""
        # Arrange
        strategy_input = YearlyBudgetStrategyInput(start_month=3, start_day=1)
        start_date = datetime(2023, 3, 1, 0, 0, 0, 0)

        # Act
        end_date = await strategy.calculate_budget_date(strategy_input, start_date)

        # Assert
        # End date should be the last day of February
        expected_date = datetime(2024, 3, 1, 0, 0, 0, 0) - timedelta(seconds=1)

        assert end_date == expected_date
        assert end_date.year == 2024
        assert end_date.month == 2
        assert end_date.day == 29  # Last day of February in 2024 (leap year)

    @pytest.mark.asyncio
    async def test_calculate_budget_date_incorrect_input_type(self, strategy):
        """Test calculating budget end date with incorrect input type."""

        # Arrange - Using a non-YearlyBudgetStrategyInput
        class DummyInput:
            pass

        dummy_input = DummyInput()
        start_date = datetime.now()

        # Act & Assert
        with pytest.raises(TypeError):
            await strategy.calculate_budget_date(dummy_input, start_date)
