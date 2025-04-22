import uuid
from datetime import datetime

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.transaction_repository import (
    InMemoryTransactionRepository,
)
from application.commands import CreateTransactionCommand
from application.commands.handlers.create_transaction_command_handler import (
    CreateTransactionCommandHandler,
)
from domain.aggregates.budget import Budget
from domain.entities.category import Category
from domain.events.transaction import TransactionAdded
from domain.value_objects import CategoryName, Limit, Money, TransactionType


def _get_budget_repository(
    user_id: uuid.UUID, budget_id: uuid.UUID, categories: list[Category]
) -> InMemoryBudgetRepository:
    """Create a budget repository with a single budget."""
    budget = Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(10000, "USD")),
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31, 23, 59, 59),
        categories=categories,
    )
    return InMemoryBudgetRepository(
        budgets={budget_id: (0, budget)},
        users={user_id: {"id": user_id, "name": "Test User"}},
    )


def _get_deps(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: list[Category],
) -> tuple[
    CreateTransactionCommandHandler,
    InMemoryBudgetRepository,
    InMemoryTransactionRepository,
    InMemoryDomainPublisher,
]:
    """Get dependencies for the command handler."""
    domain_publisher = InMemoryDomainPublisher()
    budget_repository = _get_budget_repository(user_id, budget_id, categories)
    transaction_repository = InMemoryTransactionRepository(
        transactions={},
        users={user_id: {"id": user_id, "name": "Test User"}},
        budgets=budget_repository._budgets,
    )

    return (
        CreateTransactionCommandHandler(
            budget_repository=budget_repository,
            transaction_repository=transaction_repository,
            domain_publisher=domain_publisher,
        ),
        budget_repository,
        transaction_repository,
        domain_publisher,
    )


@pytest.fixture
def user_id() -> uuid.UUID:
    """Return a fixed user ID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def budget_id() -> uuid.UUID:
    """Return a fixed budget ID for testing."""
    return uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def category_id() -> uuid.UUID:
    """Return a fixed category ID for testing."""
    return uuid.UUID("33333333-3333-3333-3333-333333333333")


@pytest.fixture
def categories(category_id, budget_id) -> list[Category]:
    """Return a list of categories for testing."""
    return [
        Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(5000, "USD")),
        )
    ]


class TestCreateTransactionCommandHandler:
    """Tests for the CreateTransactionCommandHandler."""

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "amount, currency, transaction_type, occurred_date, description, expected_description",
        [
            (
                50.0,
                "USD",
                TransactionType.EXPENSE,
                datetime(2023, 5, 15),
                "Groceries shopping",
                "Groceries shopping",
            ),
            (
                100.0,
                "USD",
                TransactionType.INCOME,
                datetime(2023, 5, 20),
                "Salary",
                "Salary",
            ),
        ],
    )
    async def test_handle_creates_transaction(
        self,
        user_id,
        budget_id,
        category_id,
        categories,
        amount,
        currency,
        transaction_type,
        occurred_date,
        description,
        expected_description,
    ):
        """Test that handling the command creates a transaction with the correct type."""
        # Arrange
        command = CreateTransactionCommand(
            category_id=category_id,
            budget_id=budget_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            transaction_type=transaction_type,
            occurred_date=occurred_date,
            description=description,
        )

        (
            command_handler,
            _,
            transaction_repository,
            domain_publisher,
        ) = _get_deps(user_id, budget_id, categories)

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(TransactionAdded, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that transaction was saved
        assert len(transaction_repository._transactions) == 1
        transaction_id = list(transaction_repository._transactions.keys())[0]
        transaction = transaction_repository._transactions[transaction_id]

        # Check basic transaction properties
        assert transaction.user_id == user_id
        assert transaction.category_id == category_id
        assert transaction.amount.amount == Money.mint(amount, currency).amount
        assert transaction.transaction_type == transaction_type
        assert transaction.occurred_date == occurred_date
        assert transaction.description == expected_description

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, TransactionAdded)
        assert event.transaction_id == str(transaction_id)
        assert event.category_id == str(category_id)
        assert event.amount == Money.mint(amount, currency).amount
        assert event.type == str(transaction_type)
        assert event.date == occurred_date

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, TransactionAdded)
        assert event.transaction_id == str(transaction_id)
        assert event.category_id == str(category_id)
        assert event.amount == Money.mint(amount, currency).amount
        assert event.type == str(transaction_type)
        assert event.date == occurred_date

    @pytest.mark.asyncio
    async def test_handle_creates_transaction_without_description(
        self, user_id, budget_id, category_id, categories
    ):
        """Test that handling the command creates a transaction without description."""
        # Arrange
        occurred_date = datetime(2023, 6, 1)
        command = CreateTransactionCommand(
            category_id=category_id,
            budget_id=budget_id,
            user_id=user_id,
            amount=75.0,
            currency="USD",
            transaction_type=TransactionType.EXPENSE,
            occurred_date=occurred_date,
            description=None,
        )

        (
            command_handler,
            _,
            transaction_repository,
            _,
        ) = _get_deps(user_id, budget_id, categories)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that transaction was saved
        assert len(transaction_repository._transactions) == 1
        transaction_id = list(transaction_repository._transactions.keys())[0]
        transaction = transaction_repository._transactions[transaction_id]

        # Check that description is None
        assert transaction.description is None
