import pytest
from domain.strategies.budget_strategy import (
    BudgetStrategy,
    MonthlyBudgetStrategy,
    YearlyBudgetStrategy,
    create_strategy,
)
from domain.value_objects import BudgetStrategyType


class TestCreateStrategy:
    def test_create_monthly_strategy(self):
        """Test creating a monthly budget strategy."""
        # Arrange
        strategy_type = BudgetStrategyType.MONTHLY

        # Act
        strategy = create_strategy(strategy_type)

        # Assert
        assert isinstance(strategy, BudgetStrategy)
        assert isinstance(strategy, MonthlyBudgetStrategy)

    def test_create_yearly_strategy(self):
        """Test creating a yearly budget strategy."""
        # Arrange
        strategy_type = BudgetStrategyType.YEARLY

        # Act
        strategy = create_strategy(strategy_type)

        # Assert
        assert isinstance(strategy, BudgetStrategy)
        assert isinstance(strategy, YearlyBudgetStrategy)

    def test_create_strategy_unsupported_type(self):
        """Test creating a strategy with an unsupported type."""
        # Arrange - use an invalid strategy type
        # Mocking an unsupported type by adding a new attribute to Enum
        # This will bypass the linter error but still test the ValueError

        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            # Use a string that doesn't exist in BudgetStrategyType
            # This will cause create_strategy to raise ValueError
            create_strategy("UNSUPPORTED_TYPE")  # type: ignore

        # Verify the error message
        assert "Unsupported budget strategy type" in str(exc_info.value)
