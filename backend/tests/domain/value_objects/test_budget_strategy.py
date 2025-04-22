import pytest
from domain.exceptions import InvalidStrategyParameterError
from domain.value_objects.budget_strategy import (
    BudgetStrategyInput,
    BudgetStrategyType,
    CustomBudgetStrategyInput,
    MonthlyBudgetStrategyInput,
    YearlyBudgetStrategyInput,
)


class TestBudgetStrategy:
    def test_monthly_budget_strategy_input(self):
        """Test creating MonthlyBudgetStrategyInput."""
        strategy = MonthlyBudgetStrategyInput(start_day=15)
        assert strategy.strategy_type == BudgetStrategyType.MONTHLY
        assert strategy.start_day == 15

    def test_monthly_budget_strategy_input_default(self):
        """Test creating MonthlyBudgetStrategyInput with default values."""
        strategy = MonthlyBudgetStrategyInput()
        assert strategy.strategy_type == BudgetStrategyType.MONTHLY
        assert strategy.start_day == 1

    def test_monthly_budget_strategy_input_invalid_start_day(self):
        """Test that creating MonthlyBudgetStrategyInput with invalid start_day raises an exception."""
        with pytest.raises(InvalidStrategyParameterError) as exc:
            MonthlyBudgetStrategyInput(start_day=0)
        assert "start_day" in str(exc.value)

        with pytest.raises(InvalidStrategyParameterError) as exc:
            MonthlyBudgetStrategyInput(start_day=29)
        assert "start_day" in str(exc.value)

    def test_yearly_budget_strategy_input(self):
        """Test creating YearlyBudgetStrategyInput."""
        strategy = YearlyBudgetStrategyInput(start_month=3, start_day=15)
        assert strategy.strategy_type == BudgetStrategyType.YEARLY
        assert strategy.start_month == 3
        assert strategy.start_day == 15

    def test_yearly_budget_strategy_input_default(self):
        """Test creating YearlyBudgetStrategyInput with default values."""
        strategy = YearlyBudgetStrategyInput()
        assert strategy.strategy_type == BudgetStrategyType.YEARLY
        assert strategy.start_month == 1
        assert strategy.start_day == 1

    def test_yearly_budget_strategy_input_invalid_start_month(self):
        """Test that creating YearlyBudgetStrategyInput with invalid start_month raises an exception."""
        with pytest.raises(InvalidStrategyParameterError) as exc:
            YearlyBudgetStrategyInput(start_month=0)
        assert "start_month" in str(exc.value)

        with pytest.raises(InvalidStrategyParameterError) as exc:
            YearlyBudgetStrategyInput(start_month=13)
        assert "start_month" in str(exc.value)

    def test_yearly_budget_strategy_input_invalid_start_day(self):
        """Test that creating YearlyBudgetStrategyInput with invalid start_day raises an exception."""
        with pytest.raises(InvalidStrategyParameterError) as exc:
            YearlyBudgetStrategyInput(start_day=0)
        assert "start_day" in str(exc.value)

        with pytest.raises(InvalidStrategyParameterError) as exc:
            YearlyBudgetStrategyInput(start_day=29)
        assert "start_day" in str(exc.value)

    def test_custom_budget_strategy_input(self):
        """Test creating CustomBudgetStrategyInput."""
        strategy = CustomBudgetStrategyInput(duration_days=30)
        assert strategy.strategy_type == BudgetStrategyType.CUSTOM
        assert strategy.duration_days == 30

    def test_custom_budget_strategy_input_invalid_duration_days(self):
        """Test that creating CustomBudgetStrategyInput with invalid duration_days raises an exception."""
        with pytest.raises(InvalidStrategyParameterError) as exc:
            CustomBudgetStrategyInput(duration_days=0)
        assert "duration_days" in str(exc.value)

    @pytest.mark.parametrize(
        "strategy1, strategy2, should_be_equal",
        [
            pytest.param(
                MonthlyBudgetStrategyInput(start_day=1),
                MonthlyBudgetStrategyInput(start_day=1),
                True,
                id="same_monthly_strategy",
            ),
            pytest.param(
                MonthlyBudgetStrategyInput(start_day=1),
                MonthlyBudgetStrategyInput(start_day=15),
                False,
                id="different_start_days",
            ),
            pytest.param(
                MonthlyBudgetStrategyInput(start_day=1),
                YearlyBudgetStrategyInput(start_month=1, start_day=1),
                False,
                id="different_strategy_types",
            ),
            pytest.param(
                MonthlyBudgetStrategyInput(start_day=1),
                "not a strategy object",
                False,
                id="different_object_types",
            ),
        ],
    )
    def test_equality(self, strategy1, strategy2, should_be_equal):
        """Test that budget strategy objects with same values are equal."""
        if should_be_equal:
            assert strategy1 == strategy2
        else:
            assert strategy1 != strategy2

    def test_str_representation(self):
        """Test string representation of budget strategies."""
        monthly = MonthlyBudgetStrategyInput(start_day=15)
        assert str(monthly) == "monthly (start_day: 15)"

        yearly = YearlyBudgetStrategyInput(start_month=3, start_day=15)
        assert str(yearly) == "yearly (start_month: 3, start_day: 15)"

        custom = CustomBudgetStrategyInput(duration_days=30)
        assert str(custom) == "custom (duration_days: 30)"

    def test_immutability(self):
        """Test that budget strategy objects are immutable."""
        strategy = MonthlyBudgetStrategyInput()

        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            # Attempt to modify the start_day
            strategy.start_day = 15
