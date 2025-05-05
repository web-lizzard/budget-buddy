import uuid
from datetime import datetime

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.clock.fixed_clock import FixedClock
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.transaction_repository import (
    InMemoryTransactionRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands.edit_transaction_command import EditTransactionCommand
from application.commands.handlers.edit_transaction_command_handler import (
    EditTransactionCommandHandler,
)
from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.events import TransactionUpdated
from domain.exceptions import (
    CannotAddTransactionToDeactivatedBudgetError,
    CategoryNotFoundError,
    TransactionNotFoundError,
)
from domain.value_objects import (
    BudgetName,
    CategoryName,
    Limit,
    Money,
    MonthlyBudgetStrategyInput,
    TransactionType,
)


def _create_test_budget(budget_id, user_id, categories=None):
    """Create a test budget for testing."""
    strategy_input = MonthlyBudgetStrategyInput(start_day=1)
    return Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(100000, "USD")),
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31, 23, 59, 59),
        strategy_input=strategy_input,
        categories=categories or [],
        name=BudgetName("Test Budget"),
    )


def _create_test_transaction(transaction_id, category_id, user_id):
    """Create a test transaction for testing."""
    return Transaction(
        id=transaction_id,
        category_id=category_id,
        amount=Money.mint(100.0, "USD"),
        transaction_type=TransactionType.EXPENSE,
        occurred_date=datetime(2023, 1, 1),
        user_id=user_id,
        description="Test transaction",
    )


def _get_test_category(budget_id, category_id):
    """Create a test category for testing."""
    return Category(
        id=category_id,
        budget_id=budget_id,
        name=CategoryName("Test Category"),
        limit=Limit(Money(10000, "USD")),
    )


def _get_dependencies(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    transaction_id: uuid.UUID,
    category_id: uuid.UUID,
    is_budget_active: bool = True,
):
    """Get dependencies for testing."""
    # Create category and budget
    category = _get_test_category(budget_id, category_id)
    budget = _create_test_budget(budget_id, user_id, [category])

    # Handle deactivated budget case
    if not is_budget_active:
        budget.deactivate_budget(datetime(2023, 1, 1))

    # Create transaction
    transaction = _create_test_transaction(transaction_id, category_id, user_id)

    # Setup repositories
    budget_repository = InMemoryBudgetRepository(
        budgets={budget_id: (0, budget)},
        users={user_id: {"id": user_id, "name": "Test User"}},
    )

    transaction_repository = InMemoryTransactionRepository(
        transactions={transaction_id: transaction},
        users={user_id: {"id": user_id, "name": "Test User"}},
        budgets={budget_id: (0, budget)},
    )

    # Setup event publisher and unit of work
    domain_publisher = InMemoryDomainPublisher()
    unit_of_work = InMemoryUnitOfWork(domain_publisher)
    clock = FixedClock(datetime(2023, 1, 1, 12, 0, 0))

    # Create handler
    handler = EditTransactionCommandHandler(
        unit_of_work=unit_of_work,
        transaction_repository=transaction_repository,
        budget_repository=budget_repository,
        clock=clock,
    )

    return (
        handler,
        budget_repository,
        transaction_repository,
        unit_of_work,
        domain_publisher,
        budget,
        transaction,
    )


@pytest.fixture
def user_id():
    """Return a fixed user ID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def budget_id():
    """Return a fixed budget ID for testing."""
    return uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def transaction_id():
    """Return a fixed transaction ID for testing."""
    return uuid.UUID("33333333-3333-3333-3333-333333333333")


@pytest.fixture
def category_id():
    """Return a fixed category ID for testing."""
    return uuid.UUID("44444444-4444-4444-4444-444444444444")


class TestEditTransactionCommandHandler:
    """Tests for the EditTransactionCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_edits_transaction(
        self, user_id, budget_id, transaction_id, category_id
    ):
        """Test that handling the command edits a transaction."""
        # Arrange
        (
            handler,
            _,
            transaction_repository,
            unit_of_work,
            domain_publisher,
            _,
            transaction,
        ) = _get_dependencies(user_id, budget_id, transaction_id, category_id)

        command = EditTransactionCommand(
            transaction_id=transaction_id,
            budget_id=budget_id,
            user_id=user_id,
            category_id=category_id,
            amount=200.0,
            transaction_type="INCOME",  # Changed to string
            description="Updated transaction",
            occurred_date=FixedClock().now(),  # Added occurred_date
        )

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(TransactionUpdated, event_subscriber)

        # Act
        await handler.handle(command)

        # Assert
        # Check that transaction was updated
        assert transaction.amount.amount == Money.mint(200.0, "USD").amount
        assert transaction.transaction_type == TransactionType.INCOME
        assert transaction.description == "Updated transaction"

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, TransactionUpdated)
        assert event.transaction_id == str(transaction_id)
        assert event.budget_id == str(budget_id)
        assert event.user_id == str(user_id)
        assert event.amount == Money.mint(200.0, "USD").amount
        assert event.type == str(TransactionType.INCOME)

        # Check UoW was committed
        assert unit_of_work.is_committed
        assert not unit_of_work.is_rolled_back

    @pytest.mark.asyncio
    async def test_handle_fails_when_budget_deactivated(
        self, user_id, budget_id, transaction_id, category_id
    ):
        """Test that handling the command fails when budget is deactivated."""
        # Arrange
        (
            handler,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = _get_dependencies(
            user_id, budget_id, transaction_id, category_id, is_budget_active=False
        )

        command = EditTransactionCommand(
            transaction_id=transaction_id,
            budget_id=budget_id,
            user_id=user_id,
            category_id=category_id,
            amount=200.0,
            transaction_type="INCOME",  # Changed to string
            description="Updated transaction",
            occurred_date=FixedClock().now(),  # Added occurred_date
        )

        # Act & Assert
        with pytest.raises(CannotAddTransactionToDeactivatedBudgetError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_when_transaction_not_found(
        self, user_id, budget_id, category_id
    ):
        """Test that handling the command fails when transaction is not found."""
        # Arrange
        nonexistent_transaction_id = uuid.UUID("99999999-9999-9999-9999-999999999999")

        (
            handler,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = _get_dependencies(user_id, budget_id, category_id, category_id)

        command = EditTransactionCommand(
            transaction_id=nonexistent_transaction_id,
            budget_id=budget_id,
            user_id=user_id,
            category_id=category_id,
            amount=200.0,
            transaction_type="INCOME",  # Changed to string
            description="Updated transaction",
            occurred_date=FixedClock().now(),  # Added occurred_date
        )

        # Act & Assert
        with pytest.raises(TransactionNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_when_category_not_found(
        self, user_id, budget_id, transaction_id
    ):
        """Test that handling the command fails when category is not found."""
        # Arrange
        nonexistent_category_id = uuid.UUID("99999999-9999-9999-9999-999999999999")

        (
            handler,
            _,
            _,
            _,
            _,
            _,
            _,
        ) = _get_dependencies(
            user_id, budget_id, transaction_id, transaction_id
        )  # Using transaction_id for category too

        command = EditTransactionCommand(
            transaction_id=transaction_id,
            budget_id=budget_id,
            user_id=user_id,
            category_id=nonexistent_category_id,  # This category doesn't exist
            amount=200.0,
            transaction_type="INCOME",  # Changed to string
            description="Updated transaction",
            occurred_date=FixedClock().now(),  # Added occurred_date
        )

        # Act & Assert
        with pytest.raises(CategoryNotFoundError):
            await handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_edits_transaction_with_occurred_date(
        self, user_id, budget_id, transaction_id, category_id
    ):
        """Test that handling the command updates the occurred date when provided."""
        (
            handler,
            _,
            transaction_repository,
            unit_of_work,
            domain_publisher,
            _,
            transaction,
        ) = _get_dependencies(user_id, budget_id, transaction_id, category_id)
        new_occurred_date = datetime(2023, 2, 1)
        command = EditTransactionCommand(
            transaction_id=transaction_id,
            budget_id=budget_id,
            user_id=user_id,
            category_id=category_id,
            amount=150.0,
            transaction_type=str(transaction.transaction_type),
            description="Updated transaction with new occurred date",
            occurred_date=new_occurred_date,
        )
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(TransactionUpdated, event_subscriber)
        await handler.handle(command)
        assert transaction.occurred_date == new_occurred_date
        assert transaction.amount.amount == Money.mint(150.0, "USD").amount
        assert transaction.description == "Updated transaction with new occurred date"
        assert len(captured_events) == 1
        event = captured_events[0]
        assert event.transaction_id == str(transaction_id)
        assert event.budget_id == str(budget_id)
        assert event.user_id == str(user_id)
        assert event.amount == Money.mint(150.0, "USD").amount
