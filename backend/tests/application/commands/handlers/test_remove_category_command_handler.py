import uuid
from datetime import datetime
from typing import List, Optional

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.transaction_repository import (
    InMemoryTransactionRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands import RemoveCategoryCommand
from application.commands.handlers import RemoveCategoryCommandHandler
from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.events.category import CategoryRemoved
from domain.exceptions import InvalidTransferPolicyError
from domain.value_objects import (
    CategoryName,
    Limit,
    Money,
    MonthlyBudgetStrategyInput,
    TransactionType,
)


def _get_budget_repository(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: Optional[List[Category]] = None,
) -> InMemoryBudgetRepository:
    """Create a budget repository with a single budget."""
    strategy_input = MonthlyBudgetStrategyInput(start_day=1)
    budget = Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(100000, "USD")),
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31, 23, 59, 59),
        strategy_input=strategy_input,
        categories=categories or [],
    )
    return InMemoryBudgetRepository(
        budgets={budget_id: (0, budget)},
        users={user_id: {"id": user_id, "name": "Test User"}},
    )


def _get_transaction_repository(
    budget_id: uuid.UUID,
    user_id: uuid.UUID,
    budgets: dict,
    transactions: Optional[List[Transaction]] = None,
) -> InMemoryTransactionRepository:
    """Create a transaction repository with optional transactions."""
    transaction_dict = {}
    if transactions:
        for transaction in transactions:
            transaction_dict[transaction.id] = transaction

    return InMemoryTransactionRepository(
        transactions=transaction_dict,
        users={user_id: {"id": user_id, "name": "Test User"}},
        budgets=budgets,  # Pass the same budgets dict as used in budget repository
    )


def _get_deps(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: Optional[List[Category]] = None,
    transactions: Optional[List[Transaction]] = None,
) -> tuple[
    RemoveCategoryCommandHandler,
    InMemoryBudgetRepository,
    InMemoryTransactionRepository,
    InMemoryDomainPublisher,
]:
    """Get dependencies for testing."""
    domain_publisher = InMemoryDomainPublisher()

    # Create budget repository first
    budget_repository = _get_budget_repository(user_id, budget_id, categories)

    # Create transaction repository with reference to the same budgets dictionary
    transaction_repository = _get_transaction_repository(
        budget_id,
        user_id,
        budget_repository._budgets,  # Share the same budgets reference
        transactions,
    )

    unit_of_work = InMemoryUnitOfWork(domain_publisher)

    return (
        RemoveCategoryCommandHandler(
            budget_repository=budget_repository,
            transaction_repository=transaction_repository,
            unit_of_work=unit_of_work,
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


class TestRemoveCategoryCommandHandler:
    """Tests for the RemoveCategoryCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_removes_category_from_budget(self, user_id, budget_id):
        """Test that handling the command removes a category from the budget."""
        # Arrange
        category_id = uuid.uuid4()
        category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(300, "USD")),
        )

        command = RemoveCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            handle_transactions="delete",
        )

        command_handler, budget_repository, _, domain_publisher = _get_deps(
            user_id, budget_id, [category]
        )

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(CategoryRemoved, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that budget was updated
        _, budget = budget_repository._budgets[budget_id]

        # Check category was removed
        assert len(budget.categories) == 0

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, CategoryRemoved)
        assert event.category_id == str(category_id)
        assert event.budget_id == str(budget_id)
        assert "DELETE_TRANSACTIONS" in event.transfer_policy

    @pytest.mark.asyncio
    async def test_handle_deletes_category_transactions(self, user_id, budget_id):
        """Test that handling the command with 'delete' policy removes associated transactions."""
        # Arrange
        category_id = uuid.uuid4()
        category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(300, "USD")),
        )

        # Create transactions associated with the category
        transaction1 = Transaction(
            id=uuid.uuid4(),
            category_id=category_id,
            amount=Money(100, "USD"),
            transaction_type=TransactionType.EXPENSE,
            occurred_date=datetime(2023, 2, 1),
            user_id=user_id,
            description="Groceries shopping",
        )

        transaction2 = Transaction(
            id=uuid.uuid4(),
            category_id=category_id,
            amount=Money(50, "USD"),
            transaction_type=TransactionType.EXPENSE,
            occurred_date=datetime(2023, 2, 2),
            user_id=user_id,
            description="More groceries",
        )

        command = RemoveCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            handle_transactions="delete",
        )

        command_handler, _, transaction_repository, _ = _get_deps(
            user_id, budget_id, [category], [transaction1, transaction2]
        )

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that transactions were deleted
        assert len(transaction_repository._transactions) == 0

    @pytest.mark.asyncio
    async def test_handle_moves_category_transactions(self, user_id, budget_id):
        """Test that handling the command with 'move' policy moves transactions to another category."""
        # Arrange
        category_id = uuid.uuid4()
        category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(300, "USD")),
        )

        target_category_id = uuid.uuid4()
        target_category = Category(
            id=target_category_id,
            budget_id=budget_id,
            name=CategoryName("Food"),
            limit=Limit(Money(500, "USD")),
        )

        # Create transactions associated with the category
        transaction1 = Transaction(
            id=uuid.uuid4(),
            category_id=category_id,
            amount=Money(100, "USD"),
            transaction_type=TransactionType.EXPENSE,
            occurred_date=datetime(2023, 2, 1),
            user_id=user_id,
            description="Groceries shopping",
        )

        transaction2 = Transaction(
            id=uuid.uuid4(),
            category_id=category_id,
            amount=Money(50, "USD"),
            transaction_type=TransactionType.EXPENSE,
            occurred_date=datetime(2023, 2, 2),
            user_id=user_id,
            description="More groceries",
        )

        command = RemoveCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            handle_transactions="move",
            target_category_id=str(target_category_id),
        )

        command_handler, _, transaction_repository, _ = _get_deps(
            user_id,
            budget_id,
            [category, target_category],
            [transaction1, transaction2],
        )

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that transactions were moved to target category
        assert len(transaction_repository._transactions) == 2
        for transaction in transaction_repository._transactions.values():
            assert transaction.category_id == target_category_id

    @pytest.mark.asyncio
    async def test_handle_fails_with_invalid_policy(self, user_id, budget_id):
        """Test that handling the command with an invalid policy fails."""
        # Arrange
        category_id = uuid.uuid4()
        category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(300, "USD")),
        )

        command = RemoveCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            handle_transactions="invalid_policy",  # Invalid policy
        )

        command_handler, _, _, _ = _get_deps(user_id, budget_id, [category])

        # Act with expectation
        with pytest.raises(InvalidTransferPolicyError):
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_with_move_policy_without_target(
        self, user_id, budget_id
    ):
        """Test that handling the command with 'move' policy but no target category fails."""
        # Arrange
        category_id = uuid.uuid4()
        category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(300, "USD")),
        )

        command = RemoveCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            handle_transactions="move",
            # Missing target_category_id
        )

        command_handler, _, _, _ = _get_deps(user_id, budget_id, [category])

        # Act with expectation
        with pytest.raises(InvalidTransferPolicyError):
            await command_handler.handle(command)
