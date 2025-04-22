from typing import Any

import pytest
from domain.exceptions import (
    CategoryNameTooLongError,
    CategoryNameTooShortError,
    EmptyCategoryNameError,
)
from domain.value_objects.category_name import CategoryName


class TestCategoryName:
    def test_valid_category_name(self):
        """Test creating a valid CategoryName."""
        name = "Groceries"
        category_name = CategoryName(name)
        assert category_name.value == name
        assert str(category_name) == name

    def test_empty_category_name(self):
        """Test that empty category name raises EmptyCategoryNameError."""
        with pytest.raises(EmptyCategoryNameError):
            CategoryName("")

    def test_category_name_too_short(self):
        """Test that too short category name raises CategoryNameTooShortError."""
        with pytest.raises(CategoryNameTooShortError) as exc:
            CategoryName("AB")  # CategoryName._MIN_LENGTH is 3
        assert str(CategoryName._MIN_LENGTH) in str(exc.value)

    def test_category_name_min_length(self):
        """Test category name with exactly minimum length."""
        name = "ABC"  # Exactly 3 characters
        category_name = CategoryName(name)
        assert category_name.value == name

    def test_category_name_too_long(self):
        """Test that too long category name raises CategoryNameTooLongError."""
        too_long_name = "A" * (CategoryName._MAX_LENGTH + 1)
        with pytest.raises(CategoryNameTooLongError) as exc:
            CategoryName(too_long_name)
        assert str(CategoryName._MAX_LENGTH) in str(exc.value)

    def test_category_name_max_length(self):
        """Test category name with exactly maximum length."""
        name = "A" * CategoryName._MAX_LENGTH
        category_name = CategoryName(name)
        assert category_name.value == name

    def test_category_name_immutability(self):
        """Test that CategoryName is immutable."""
        category_name = CategoryName("Grocery")
        # This will raise exception because CategoryName is a frozen dataclass
        with pytest.raises(Exception):
            # Use Any to bypass type checking for test purposes
            any_category_name: Any = category_name
            any_category_name._value = "New Name"

    def test_category_name_equality(self):
        """Test that CategoryName objects with the same value are equal."""
        name1 = CategoryName("Entertainment")
        name2 = CategoryName("Entertainment")
        name3 = CategoryName("Groceries")

        assert name1 == name2
        assert name1 != name3
        assert name2 != name3

    def test_category_name_strips_whitespace(self):
        """Test that category name strips whitespace."""
        name_with_spaces = "  Groceries  "
        category_name = CategoryName(name_with_spaces)
        assert category_name.value == "Groceries"
