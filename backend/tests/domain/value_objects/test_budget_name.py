import pytest
from domain.exceptions import (
    BudgetNameTooLongError,
    BudgetNameTooShortError,
    EmptyBudgetNameError,
)
from domain.value_objects.budget_name import BudgetName


class TestBudgetName:
    def test_valid_budget_name(self):
        """Test creation of a valid budget name."""
        name = BudgetName("Valid Budget Name")
        assert name.value == "Valid Budget Name"
        assert str(name) == "Valid Budget Name"

    def test_budget_name_whitespace_trimming(self):
        """Test that whitespace is trimmed from budget names."""
        name = BudgetName("  Whitespace Budget  ")
        assert name.value == "Whitespace Budget"

    def test_empty_budget_name_raises_error(self):
        """Test that empty budget name raises error."""
        with pytest.raises(EmptyBudgetNameError):
            BudgetName("")

    def test_whitespace_only_budget_name_raises_error(self):
        """Test that whitespace-only budget name raises error."""
        with pytest.raises(EmptyBudgetNameError):
            BudgetName("   ")

    def test_budget_name_too_short_raises_error(self):
        """Test that too short budget name raises error."""
        with pytest.raises(BudgetNameTooShortError) as exc_info:
            BudgetName("ab")
        assert "3" in str(exc_info.value)  # Check that message includes the min length

    def test_budget_name_too_long_raises_error(self):
        """Test that too long budget name raises error."""
        with pytest.raises(BudgetNameTooLongError) as exc_info:
            BudgetName("a" * 101)
        assert "100" in str(
            exc_info.value
        )  # Check that message includes the max length

    def test_budget_name_minimum_length(self):
        """Test budget name with minimum valid length."""
        name = BudgetName("abc")
        assert name.value == "abc"

    def test_budget_name_maximum_length(self):
        """Test budget name with maximum valid length."""
        max_name = "a" * 100
        name = BudgetName(max_name)
        assert name.value == max_name
        assert len(name.value) == 100
