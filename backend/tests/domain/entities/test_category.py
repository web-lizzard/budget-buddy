import uuid
from datetime import datetime
from uuid import UUID

import pytest
from domain.entities import Category
from domain.exceptions import (
    CategoryNameTooLongError,
    CategoryNameTooShortError,
    EmptyCategoryNameError,
)
from domain.value_objects import CategoryName, Limit, Money
from domain.value_objects.transaction_type import TransactionType


@pytest.fixture
def category_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def budget_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def user_id() -> UUID:
    return uuid.uuid4()


@pytest.fixture
def category_name() -> CategoryName:
    return CategoryName("Test Category")


@pytest.fixture
def category_limit() -> Limit:
    return Limit(Money(1000, "USD"))


@pytest.fixture
def category(
    category_id: UUID,
    budget_id: UUID,
    category_name: CategoryName,
    category_limit: Limit,
) -> Category:
    return Category(
        id=category_id,
        budget_id=budget_id,
        name=category_name,
        limit=category_limit,
    )


class TestCategory:
    def test_init_valid_category(self):
        """Test creating a valid Category entity."""
        category_id = uuid.uuid4()
        budget_id = uuid.uuid4()
        name = CategoryName("Groceries")
        limit = Limit(Money(10000, "USD"))  # $100.00

        category = Category(category_id, budget_id, name, limit)

        assert category.id == category_id
        assert category.budget_id == budget_id
        assert category.name == name
        assert category.limit == limit

    def test_init_with_category_name_value_object(self):
        """Test creating Category with CategoryName value object."""
        category_id = uuid.uuid4()
        budget_id = uuid.uuid4()
        name = CategoryName("Entertainment")
        limit = Limit(Money(5000, "USD"))  # $50.00

        category = Category(category_id, budget_id, name, limit)

        assert category.id == category_id
        assert category.budget_id == budget_id
        assert category.name == name
        assert str(category.name) == "Entertainment"

    def test_init_with_string_ids(self):
        """Test creating Category with string IDs that get converted to UUID."""
        category_id_str = "12345678-1234-5678-1234-567812345678"
        budget_id_str = "87654321-4321-8765-4321-876543210987"
        name = CategoryName("Entertainment")
        limit = Limit(Money(5000, "USD"))  # $50.00

        # Explicitly convert strings to UUID
        category_id = UUID(category_id_str)
        budget_id = UUID(budget_id_str)

        category = Category(category_id, budget_id, name, limit)

        assert isinstance(category.id, UUID)
        assert str(category.id) == category_id_str
        assert isinstance(category.budget_id, UUID)
        assert str(category.budget_id) == budget_id_str

    @pytest.mark.parametrize(
        "invalid_name,expected_exception",
        [
            pytest.param("", EmptyCategoryNameError, id="empty_string"),
            pytest.param("ab", CategoryNameTooShortError, id="too_short"),
            pytest.param("a" * 256, CategoryNameTooLongError, id="too_long"),
        ],
    )
    def test_init_with_invalid_name(self, invalid_name, expected_exception):
        """Test that invalid name raises appropriate exception."""
        category_id = uuid.uuid4()
        budget_id = uuid.uuid4()
        limit = Limit(Money(10000, "USD"))

        with pytest.raises(expected_exception):
            Category(category_id, budget_id, CategoryName(invalid_name), limit)

    def test_change_name_valid(self):
        """Test changing category name with valid CategoryName object."""
        category = Category(
            uuid.uuid4(),
            uuid.uuid4(),
            CategoryName("Initial Name"),
            Limit(Money(10000, "USD")),
        )
        new_name = CategoryName("Updated Name")

        category.change_name(new_name)

        assert category.name == new_name
        assert str(category.name) == "Updated Name"

    @pytest.mark.parametrize(
        "invalid_name,expected_exception",
        [
            pytest.param("", EmptyCategoryNameError, id="empty_string"),
            pytest.param("ab", CategoryNameTooShortError, id="too_short"),
            pytest.param("a" * 256, CategoryNameTooLongError, id="too_long"),
        ],
    )
    def test_change_name_invalid(self, invalid_name, expected_exception):
        """Test that changing to invalid name raises appropriate exception."""
        category = Category(
            uuid.uuid4(),
            uuid.uuid4(),
            CategoryName("Initial Name"),
            Limit(Money(10000, "USD")),
        )

        with pytest.raises(expected_exception):
            category.change_name(CategoryName(invalid_name))

    def test_change_limit_valid(self):
        """Test changing category limit with valid new limit."""
        category = Category(
            uuid.uuid4(),
            uuid.uuid4(),
            CategoryName("Food"),
            Limit(Money(10000, "USD")),
        )
        new_limit = Limit(Money(20000, "USD"))

        category.change_limit(new_limit)

        assert category.limit == new_limit

    def test_string_representation(self):
        """Test string representation of Category."""
        category_id = uuid.uuid4()
        budget_id = uuid.uuid4()
        name = "Transportation"
        limit = Limit(Money(15000, "USD"))

        category = Category(category_id, budget_id, CategoryName(name), limit)

        # The string representation should now use CategoryName
        expected_str_part = f"Category: {name}"
        assert expected_str_part in str(category)
        assert str(category_id) in str(category)
        assert str(budget_id) in str(category)
        assert str(limit) in str(category)

    def test_create_category(self, category: Category):
        """Test creating a category with all required fields."""
        assert isinstance(category, Category)
        assert isinstance(category.id, UUID)
        assert isinstance(category.budget_id, UUID)
        assert isinstance(category.name, CategoryName)
        assert isinstance(category.limit, Limit)

    def test_change_category_name(
        self,
        category: Category,
    ):
        """Test changing category name."""
        new_name = CategoryName("New Category Name")
        category.change_name(new_name)
        assert category.name == new_name

    def test_change_category_limit(
        self,
        category: Category,
    ):
        """Test changing category limit."""
        new_limit = Limit(Money(2000, "USD"))
        category.change_limit(new_limit)
        assert category.limit == new_limit

    def test_create_transaction(
        self,
        category: Category,
        user_id: UUID,
    ):
        """Test creating a transaction in the category."""
        transaction_id = uuid.uuid4()
        amount = Money(500, "USD")
        transaction_type = TransactionType.EXPENSE
        occurred_date = datetime(2024, 1, 1, 12, 0)
        description = "Test transaction"

        transaction = category.create_transaction(
            id=transaction_id,
            amount=amount,
            transaction_type=transaction_type,
            occurred_date=occurred_date,
            user_id=user_id,
            description=description,
        )

        assert transaction.id == transaction_id
        assert transaction.category_id == category.id
        assert transaction.amount == amount
        assert transaction.transaction_type == transaction_type
        assert transaction.occurred_date == occurred_date
        assert transaction.description == description
        assert transaction.user_id == user_id

    def test_create_transaction_without_description(
        self,
        category: Category,
        user_id: UUID,
    ):
        """Test creating a transaction without description."""
        transaction = category.create_transaction(
            id=uuid.uuid4(),
            amount=Money(500, "USD"),
            transaction_type=TransactionType.EXPENSE,
            occurred_date=datetime(2024, 1, 1, 12, 0),
            user_id=user_id,
        )

        assert transaction.description is None

    def test_category_string_representation(self, category: Category):
        """Test the string representation of a category."""
        str_repr = str(category)

        assert str(category.name) in str_repr
        assert str(category.id) in str_repr
        assert str(category.budget_id) in str_repr
        assert str(category.limit) in str_repr
