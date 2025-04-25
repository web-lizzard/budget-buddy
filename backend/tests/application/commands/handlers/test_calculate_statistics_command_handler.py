import uuid
from datetime import datetime
from typing import Optional

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory import (
    InMemoryBudgetRepository,
    InMemoryStatisticsRepository,
    InMemoryTransactionRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands.calculate_statistics_command import CalculateStatisticsCommand
from application.commands.handlers.calculate_statistics_command_handler import (
    CalculateStatisticsCommandHandler,
)
from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.events.statistics import StatisticsCalculated
from domain.value_objects import (
    CategoryName,
    Limit,
    Money,
    MonthlyBudgetStrategyInput,
    TransactionType,
)

# Define a placeholder UUID for transactions without a real category
NULL_CATEGORY_UUID = uuid.UUID(int=0)


# --- Test Setup Helpers ---
def _create_test_budget(user_id: uuid.UUID, budget_id: uuid.UUID) -> Budget:
    """Creates a sample budget for testing."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31, 23, 59, 59)

    # Use fixed UUIDs for categories to ensure consistent testing
    groceries_cat_id = uuid.UUID("ecc557c7-7481-4e89-ad5c-0cc143f9d6c0")
    transport_cat_id = uuid.UUID("6565e619-9c2b-4250-a606-05f059192ab0")

    groceries_cat = Category(
        id=groceries_cat_id,
        budget_id=budget_id,
        name=CategoryName("Groceries"),
        limit=Limit(Money.mint(300.0, "USD")),
    )
    transport_cat = Category(
        id=transport_cat_id,
        budget_id=budget_id,
        name=CategoryName("Transport"),
        limit=Limit(Money.mint(100.0, "USD")),
    )
    strategy_input = MonthlyBudgetStrategyInput(start_day=1)

    # Debug print for category IDs
    print(f"DEBUG: Created categories with IDs: {groceries_cat_id}, {transport_cat_id}")

    return Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money.mint(1000.0, "USD")),
        start_date=start_date,
        end_date=end_date,
        strategy_input=strategy_input,
        categories=[groceries_cat, transport_cat],
    )


def _create_test_transactions(
    user_id: uuid.UUID, budget_id: uuid.UUID, budget: Budget
) -> list[Transaction]:
    """Creates sample transactions for testing."""
    # Ensure categories exist before accessing their IDs
    if not budget.categories or len(budget.categories) < 2:
        cat_groceries_id = uuid.UUID("ecc557c7-7481-4e89-ad5c-0cc143f9d6c0")
        cat_transport_id = uuid.UUID("6565e619-9c2b-4250-a606-05f059192ab0")
        print("DEBUG: Using hardcoded category IDs because budget.categories is empty")
    else:
        cat_groceries_id = budget.categories[0].id
        cat_transport_id = budget.categories[1].id
        print(
            f"DEBUG: Using budget category IDs: {cat_groceries_id}, {cat_transport_id}"
        )

    transactions = [
        Transaction(
            id=uuid.uuid4(),
            user_id=user_id,
            category_id=cat_groceries_id,
            amount=Money.mint(50.0, "USD"),
            transaction_type=TransactionType.EXPENSE,
            description="Weekly groceries",
            occurred_date=datetime(2024, 1, 5),
        ),
        Transaction(
            id=uuid.uuid4(),
            user_id=user_id,
            category_id=cat_transport_id,
            amount=Money.mint(20.0, "USD"),
            transaction_type=TransactionType.EXPENSE,
            description="Bus fare",
            occurred_date=datetime(2024, 1, 10),
        ),
        Transaction(
            id=uuid.uuid4(),
            user_id=user_id,
            # For income transactions without a category, use the first category's ID
            # to ensure it's not filtered out by the repository
            category_id=cat_groceries_id,  # Changed from NULL_CATEGORY_UUID
            amount=Money.mint(1500.0, "USD"),
            transaction_type=TransactionType.INCOME,
            description="Salary",
            occurred_date=datetime(2024, 1, 15),
        ),
        Transaction(
            id=uuid.uuid4(),
            user_id=user_id,
            category_id=cat_groceries_id,
            amount=Money.mint(75.50, "USD"),
            transaction_type=TransactionType.EXPENSE,
            description="More groceries",
            occurred_date=datetime(2024, 1, 20),
        ),
    ]

    # Debug print transaction details
    for i, tx in enumerate(transactions):
        print(
            f"DEBUG: Created test transaction {i+1}: type={tx.transaction_type}, amount={tx.amount}, category_id={tx.category_id}"
        )

    return transactions


def _convert_transactions_to_dict(
    transactions: Optional[list[Transaction]],
) -> dict[uuid.UUID, Transaction]:
    """Convert list of transactions to a dictionary keyed by transaction ID."""
    if not transactions:
        return {}

    result = {}
    for tx in transactions:
        result[tx.id] = tx
        print(
            f"DEBUG: Added transaction {tx.id} to dictionary with category {tx.category_id}"
        )

    return result


def _get_deps(
    user_id: uuid.UUID,
    budget: Budget,
    transactions: Optional[list[Transaction]] = None,
):
    """Sets up dependencies for the command handler tests."""
    # Convert transactions list to dictionary expected by repository
    tx_dict = _convert_transactions_to_dict(transactions)
    print(f"DEBUG: Created transaction dictionary with {len(tx_dict)} transactions")

    # Create a shared budget dictionary that both repositories will use
    budget_dict = {budget.id: (0, budget)}
    print(f"DEBUG: Created budget dictionary with ID {budget.id}")

    # Initialize repositories with the same budget reference
    budget_repo = InMemoryBudgetRepository(
        budgets=budget_dict,
        users={user_id: {"id": user_id, "name": "Test User"}},
    )

    tx_repo = InMemoryTransactionRepository(
        transactions=tx_dict,
        budgets=budget_dict,  # Use the same budget dict to ensure consistency
    )

    # Add debug print to directly verify the budget in the tx_repo
    print(f"DEBUG: Budget dict in tx_repo: {list(tx_repo._budgets.keys())}")
    if budget.id in tx_repo._budgets:
        budget_data = tx_repo._budgets[budget.id]
        print(
            f"DEBUG: Budget data type: {type(budget_data)}, is tuple: {isinstance(budget_data, tuple)}"
        )

    stats_repo = InMemoryStatisticsRepository()
    publisher = InMemoryDomainPublisher()
    uow = InMemoryUnitOfWork(event_publisher=publisher)
    handler = CalculateStatisticsCommandHandler(
        unit_of_work=uow,
        budget_repository=budget_repo,
        transaction_repository=tx_repo,
        statistics_repository=stats_repo,
    )
    return handler, uow, stats_repo, publisher, budget_repo, tx_repo


@pytest.fixture
def user_id() -> uuid.UUID:
    """Return a fixed user ID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def budget_id() -> uuid.UUID:
    """Return a fixed budget ID for testing."""
    return uuid.UUID("22222222-2222-2222-2222-222222222222")


@pytest.fixture
def test_budget(user_id, budget_id) -> Budget:
    """Create a test budget for testing."""
    return _create_test_budget(user_id, budget_id)


@pytest.fixture
def test_transactions(user_id, budget_id, test_budget) -> list[Transaction]:
    """Create test transactions for testing."""
    return _create_test_transactions(user_id, budget_id, test_budget)


class TestCalculateStatisticsCommandHandler:
    """Tests for the CalculateStatisticsCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_calculates_and_saves_statistics(
        self, user_id, budget_id, test_budget, test_transactions
    ):
        """Test successful calculation and saving of statistics."""
        # Arrange
        handler, uow, stats_repo, publisher, budget_repo, tx_repo = _get_deps(
            user_id, test_budget, test_transactions
        )

        command = CalculateStatisticsCommand(user_id=user_id, budget_id=budget_id)
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        publisher.subscribe(StatisticsCalculated, event_subscriber)

        # Act
        await handler.handle(command)

        # Assert
        assert uow.is_committed is True
        assert uow.is_rolled_back is False

        saved_records = await stats_repo.find_by_budget_id(
            budget_id=budget_id, user_id=user_id
        )
        assert len(saved_records) == 1
        saved_record = saved_records[0]

        # Check statistics record properties
        assert saved_record.budget_id == budget_id
        assert saved_record.user_id == user_id
        assert saved_record.used_limit.amount == 14550  # 145.50 USD (50 + 20 + 75.50)
        assert (
            saved_record.current_balance.amount == 135450
        )  # 1354.50 USD (1500 - 145.50)
        assert len(saved_record.categories_statistics) == len(test_budget.categories)

        # Check category statistics
        groceries_stat = next(
            (
                s
                for s in saved_record.categories_statistics
                if s.category_id == test_budget.categories[0].id
            ),
            None,
        )
        assert groceries_stat is not None
        assert groceries_stat.used_limit.amount == 12550  # 125.50 USD (50 + 75.50)

        # Check events
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, StatisticsCalculated)
        assert event.budget_id == budget_id
        assert event.user_id == user_id
        assert event.statistics_record_id == saved_record.id

    @pytest.mark.asyncio
    async def test_handle_no_transactions_calculates_zero_stats(
        self, user_id, budget_id, test_budget
    ):
        """Test that zero stats are calculated and saved if no transactions exist."""
        # Arrange
        handler, uow, stats_repo, publisher, _, _ = _get_deps(
            user_id, test_budget, None
        )

        command = CalculateStatisticsCommand(user_id=user_id, budget_id=budget_id)
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        publisher.subscribe(StatisticsCalculated, event_subscriber)

        # Act
        await handler.handle(command)

        # Assert
        assert uow.is_committed is True
        saved_records = await stats_repo.find_by_budget_id(
            budget_id=budget_id, user_id=user_id
        )
        assert len(saved_records) == 1
        saved_record = saved_records[0]

        # Check zero values
        assert saved_record.used_limit.amount == 0
        assert saved_record.current_balance.amount == 0
        assert len(saved_record.categories_statistics) == len(test_budget.categories)

        for cat_stat in saved_record.categories_statistics:
            assert cat_stat.used_limit.amount == 0
            assert cat_stat.current_balance.amount == 0

        # Check event publication
        assert len(captured_events) == 1
        assert captured_events[0].statistics_record_id == saved_record.id
