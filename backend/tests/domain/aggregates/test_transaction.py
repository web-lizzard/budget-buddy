from datetime import datetime
from uuid import UUID, uuid4

import pytest
from domain.aggregates.transaction import Transaction
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


@pytest.fixture
def transaction_id() -> UUID:
    return uuid4()


@pytest.fixture
def category_id() -> UUID:
    return uuid4()


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def amount() -> Money:
    return Money(100, "USD")


@pytest.fixture
def occurred_date() -> datetime:
    return datetime(2024, 1, 1, 12, 0)


@pytest.fixture
def description() -> str:
    return "Test transaction"


@pytest.fixture
def transaction(
    transaction_id: UUID,
    category_id: UUID,
    amount: Money,
    user_id: UUID,
    occurred_date: datetime,
    description: str,
) -> Transaction:
    return Transaction(
        id=transaction_id,
        category_id=category_id,
        amount=amount,
        transaction_type=TransactionType.EXPENSE,
        occurred_date=occurred_date,
        user_id=user_id,
        description=description,
    )


class TestTransaction:
    def test_create_transaction_with_all_fields(self, transaction: Transaction):
        """Test creating a transaction with all fields."""
        assert isinstance(transaction, Transaction)
        assert isinstance(transaction.id, UUID)
        assert isinstance(transaction.category_id, UUID)
        assert isinstance(transaction.amount, Money)
        assert isinstance(transaction.transaction_type, TransactionType)
        assert isinstance(transaction.occurred_date, datetime)
        assert isinstance(transaction.description, str)
        assert isinstance(transaction.user_id, UUID)

    def test_create_transaction_without_description(
        self,
        transaction_id: UUID,
        category_id: UUID,
        amount: Money,
        user_id: UUID,
        occurred_date: datetime,
    ):
        """Test creating a transaction without description."""
        transaction = Transaction(
            id=transaction_id,
            category_id=category_id,
            amount=amount,
            transaction_type=TransactionType.INCOME,
            occurred_date=occurred_date,
            user_id=user_id,
        )

        assert transaction.description is None

    @pytest.mark.parametrize(
        "transaction_type", [TransactionType.INCOME, TransactionType.EXPENSE]
    )
    def test_transaction_types(
        self,
        transaction_id: UUID,
        category_id: UUID,
        amount: Money,
        user_id: UUID,
        occurred_date: datetime,
        transaction_type: TransactionType,
    ):
        """Test creating transactions with different types."""
        transaction = Transaction(
            id=transaction_id,
            category_id=category_id,
            amount=amount,
            transaction_type=transaction_type,
            occurred_date=occurred_date,
            user_id=user_id,
        )

        assert transaction.transaction_type == transaction_type

    def test_transaction_string_representation(self, transaction: Transaction):
        """Test the string representation of a transaction."""
        str_repr = str(transaction)

        assert str(transaction.id) in str_repr
        assert str(transaction.category_id) in str_repr
        assert str(transaction.amount) in str_repr
        assert str(transaction.transaction_type) in str_repr
        assert str(transaction.occurred_date) in str_repr
        assert transaction.description in str_repr
