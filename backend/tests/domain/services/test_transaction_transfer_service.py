from datetime import datetime
from uuid import UUID, uuid4

import pytest
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.services.transaction_transfer_service import TransactionTransferService
from domain.value_objects.category_name import CategoryName
from domain.value_objects.limit import Limit
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


@pytest.fixture
def budget_id() -> UUID:
    """Create a budget ID."""
    return uuid4()


@pytest.fixture
def target_category(budget_id: UUID) -> Category:
    """Create a Category with valid ID."""
    return Category(
        id=uuid4(),
        budget_id=budget_id,
        name=CategoryName("Target Category"),
        limit=Limit(Money(1000, "USD")),
    )


@pytest.fixture
def source_category(budget_id: UUID) -> Category:
    """Create a Category with valid ID."""
    return Category(
        id=uuid4(),
        budget_id=budget_id,
        name=CategoryName("Source Category"),
        limit=Limit(Money(1000, "USD")),
    )


@pytest.fixture
def transaction_transfer_service() -> TransactionTransferService:
    """Create an instance of TransactionTransferService."""
    return TransactionTransferService()


def create_transaction(category: Category) -> Transaction:
    """Helper function to create a transaction."""
    return Transaction(
        id=uuid4(),
        category_id=category.id,
        amount=Money(100, "USD"),
        transaction_type=TransactionType.EXPENSE,
        occurred_date=datetime.now(),
        description="Test transaction",
        user_id=uuid4(),
    )


@pytest.mark.parametrize(
    "transactions_count",
    [
        0,  # Empty list case
        1,  # Single transaction case
        5,  # Multiple transactions case
    ],
)
def test_transfer_transactions_count_cases(
    transaction_transfer_service: TransactionTransferService,
    source_category: Category,
    target_category: Category,
    transactions_count: int,
) -> None:
    """
    Test transferring different numbers of transactions.

    Args:
        transaction_transfer_service: Service instance
        source_category: Source category
        target_category: Target category
        transactions_count: Number of transactions to test
    """
    # Arrange
    transactions = [
        create_transaction(source_category) for _ in range(transactions_count)
    ]

    # Act
    transaction_transfer_service.transfer_transactions(transactions, target_category)

    # Assert
    for transaction in transactions:
        assert transaction.category_id == target_category.id


def test_transfer_transactions_updates_all_transactions(
    transaction_transfer_service: TransactionTransferService,
    source_category: Category,
    target_category: Category,
) -> None:
    """
    Test that all transactions are updated with new category.

    Args:
        transaction_transfer_service: Service instance
        source_category: Source category
        target_category: Target category
    """
    # Arrange
    transactions = [create_transaction(source_category) for _ in range(3)]
    original_category_ids = [transaction.category_id for transaction in transactions]

    # Act
    transaction_transfer_service.transfer_transactions(transactions, target_category)

    # Assert
    for transaction, original_category_id in zip(transactions, original_category_ids):
        assert transaction.category_id == target_category.id
        assert transaction.category_id != original_category_id


def test_transfer_transactions_correct_category_id(
    transaction_transfer_service: TransactionTransferService,
    source_category: Category,
    target_category: Category,
) -> None:
    """
    Test that transactions are updated with correct category ID.

    Args:
        transaction_transfer_service: Service instance
        source_category: Source category
        target_category: Target category
    """
    # Arrange
    transaction = create_transaction(source_category)
    original_category_id = transaction.category_id

    # Act
    transaction_transfer_service.transfer_transactions([transaction], target_category)

    # Assert
    assert transaction.category_id == target_category.id
    assert transaction.category_id != original_category_id
