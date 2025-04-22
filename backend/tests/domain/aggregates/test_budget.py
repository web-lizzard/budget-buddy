import uuid
from datetime import datetime, timedelta
from uuid import UUID

import pytest
from domain.aggregates import Budget
from domain.entities import Category
from domain.exceptions import (
    CannotAddTransactionToDeactivatedBudgetError,
    CategoryLimitExceedsBudgetError,
    CategoryNotFoundError,
    CurrencyMismatchError,
    DuplicateCategoryNameError,
    MaxCategoriesReachedError,
    TransactionOutsideBudgetPeriodError,
)
from domain.value_objects import CategoryName, Limit, Money


class TestBudget:
    @pytest.fixture
    def valid_budget(self):
        """Fixture for a valid budget."""
        budget_id = uuid.uuid4()
        user_id = uuid.uuid4()
        total_limit = Limit(Money(50000, "USD"))  # $500.00
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        return Budget(
            id=budget_id,
            user_id=user_id,
            total_limit=total_limit,
            start_date=start_date,
            end_date=end_date,
        )

    def test_init_valid_budget(self, valid_budget):
        """Test creating a valid Budget aggregate."""
        assert isinstance(valid_budget.id, UUID)
        assert isinstance(valid_budget.user_id, UUID)
        assert isinstance(valid_budget.total_limit, Limit)
        assert isinstance(valid_budget.start_date, datetime)
        assert isinstance(valid_budget.end_date, datetime)
        assert valid_budget.currency == "USD"
        assert valid_budget.deactivation_date is None
        assert valid_budget.is_active is True
        assert valid_budget.categories == []

    def test_init_with_categories(self):
        """Test creating Budget with initial categories."""
        budget_id = uuid.uuid4()
        user_id = uuid.uuid4()
        total_limit = Limit(Money(50000, "USD"))
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)

        # Create some categories
        category1 = Category(
            id=uuid.uuid4(),
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(15000, "USD")),
        )

        category2 = Category(
            id=uuid.uuid4(),
            budget_id=budget_id,
            name=CategoryName("Entertainment"),
            limit=Limit(Money(10000, "USD")),
        )

        budget = Budget(
            id=budget_id,
            user_id=user_id,
            total_limit=total_limit,
            start_date=start_date,
            end_date=end_date,
            categories=[category1, category2],
        )

        # Test that categories were added
        assert len(budget.categories) == 2
        assert category1 in budget.categories
        assert category2 in budget.categories

    def test_add_category_success(self, valid_budget):
        """Test adding a category successfully."""
        name = CategoryName("Groceries")
        limit = Limit(Money(15000, "USD"))

        category = valid_budget.add_category(name, limit)

        assert category in valid_budget.categories
        assert len(valid_budget.categories) == 1
        assert category.name == name
        assert category.limit == limit
        assert category.budget_id == valid_budget.id

    def test_add_category_max_limit_reached(self, valid_budget):
        """Test that adding more than max categories raises an error."""
        # Add MAX_CATEGORIES categories
        for i in range(valid_budget._MAX_CATEGORIES):
            valid_budget.add_category(
                CategoryName(f"Category {i+1}"), Limit(Money(1000, "USD"))
            )

        # Try to add one more
        with pytest.raises(MaxCategoriesReachedError):
            valid_budget.add_category(
                CategoryName("One Too Many"), Limit(Money(1000, "USD"))
            )

    def test_add_category_duplicate_name(self, valid_budget):
        """Test that adding a category with an existing name raises an error."""
        name = CategoryName("Groceries")

        # Add first category
        valid_budget.add_category(name, Limit(Money(10000, "USD")))

        # Try to add another with the same name
        with pytest.raises(DuplicateCategoryNameError):
            valid_budget.add_category(name, Limit(Money(5000, "USD")))

    def test_add_category_exceeds_budget_limit(self, valid_budget):
        """Test that adding a category that exceeds budget limit raises an error."""
        # The budget has a limit of $500.00
        # Try to add a category with a limit of $600.00
        with pytest.raises(CategoryLimitExceedsBudgetError):
            valid_budget.add_category(
                CategoryName("Too Expensive"), Limit(Money(60000, "USD"))
            )

    def test_add_category_multiple_until_limit(self, valid_budget):
        """Test adding multiple categories until total limit is reached."""
        # Add categories consuming parts of the budget
        valid_budget.add_category(
            CategoryName("Category 1"), Limit(Money(10000, "USD"))
        )

        valid_budget.add_category(
            CategoryName("Category 2"), Limit(Money(20000, "USD"))
        )

        # Try to add another category that would exceed the limit
        # Budget total: $500, used: $300, remaining: $200
        # Try to add category with limit: $300
        with pytest.raises(CategoryLimitExceedsBudgetError):
            valid_budget.add_category(
                CategoryName("Category 3"), Limit(Money(30000, "USD"))
            )

        # Add a category that fits in the remaining budget
        category = valid_budget.add_category(
            CategoryName("Category 3"), Limit(Money(19000, "USD"))
        )

        assert category in valid_budget.categories
        assert len(valid_budget.categories) == 3

    def test_remove_category_success(self, valid_budget):
        """Test removing a category successfully."""
        # Add a category
        category = valid_budget.add_category(
            CategoryName("Test Category"), Limit(Money(10000, "USD"))
        )

        # Remove the category
        valid_budget.remove_category(category.id)

        assert category not in valid_budget.categories
        assert len(valid_budget.categories) == 0

    def test_deactivate_budget(self, valid_budget):
        """Test deactivating a budget."""

        valid_budget.deactivate_budget()

        assert valid_budget.deactivation_date is not None

    def test_validate_transaction_date_success(self, valid_budget):
        """Test validating a transaction date that is within budget period."""
        # Date in the middle of the budget period
        transaction_date = valid_budget.start_date + timedelta(days=15)

        # Should not raise an exception
        valid_budget.validate_transaction_date(transaction_date)

    def test_validate_transaction_date_before_start(self, valid_budget):
        """Test validating a transaction date before budget start date."""
        transaction_date = valid_budget.start_date - timedelta(days=1)

        with pytest.raises(TransactionOutsideBudgetPeriodError):
            valid_budget.validate_transaction_date(transaction_date)

    def test_validate_transaction_date_after_end(self, valid_budget):
        """Test validating a transaction date after budget end date."""
        transaction_date = valid_budget.end_date + timedelta(days=1)

        with pytest.raises(TransactionOutsideBudgetPeriodError):
            valid_budget.validate_transaction_date(transaction_date)

    def test_validate_transaction_date_deactivated_budget_raises_error(
        self, valid_budget
    ):
        """Test validating a transaction date after budget deactivation raises error."""
        # Deactivate the budget
        valid_budget.deactivate_budget()

        # Transaction date after deactivation
        transaction_date = datetime.now() + timedelta(days=1)

        with pytest.raises(CannotAddTransactionToDeactivatedBudgetError):
            valid_budget.validate_transaction_date(transaction_date)

    def test_validate_transaction_date_deactivated_budget_success(self, valid_budget):
        """Test validating a transaction date before budget deactivation succeeds."""
        # Deactivate the budget
        valid_budget._start_date = datetime.now() - timedelta(days=1)
        valid_budget.deactivate_budget()

        # Transaction date before deactivation
        transaction_date = valid_budget.deactivation_date - timedelta(hours=1)
        valid_budget.validate_transaction_date(transaction_date)

    def test_validate_transaction_currency_success(self, valid_budget):
        """Test validating a transaction currency that matches budget currency."""
        # Should not raise an exception
        valid_budget.validate_transaction_currency("USD")

    def test_validate_transaction_currency_mismatch(self, valid_budget):
        """Test validating a transaction currency that doesn't match budget currency."""
        with pytest.raises(CurrencyMismatchError):
            valid_budget.validate_transaction_currency("EUR")

    def test_string_representation(self, valid_budget):
        """Test string representation of Budget."""
        budget_str = str(valid_budget)

        assert f"Budget: {valid_budget.id}" in budget_str
        assert f"User: {valid_budget.user_id}" in budget_str
        assert f"Limit: {valid_budget.total_limit}" in budget_str
        assert "Active: True" in budget_str

    def test_get_category_by_id(self, valid_budget):
        """Test getting a category by ID."""
        category = valid_budget.add_category(
            CategoryName("Test Category"),
            Limit(Money(1000, "USD")),
        )

        found_category = valid_budget.get_category_by(category.id)
        assert found_category == category

    def test_get_category_by_id_not_found(self, valid_budget):
        """Test getting a non-existent category by ID."""
        with pytest.raises(CategoryNotFoundError):
            valid_budget.get_category_by(uuid.uuid4())

    def test_budget_string_representation(self, valid_budget):
        """Test the string representation of a budget."""
        str_repr = str(valid_budget)

        assert str(valid_budget.id) in str_repr
        assert str(valid_budget.user_id) in str_repr
        assert str(valid_budget.total_limit) in str_repr
        assert str(valid_budget.start_date) in str_repr
        assert str(valid_budget.end_date) in str_repr
        assert str(len(valid_budget.categories)) in str_repr
