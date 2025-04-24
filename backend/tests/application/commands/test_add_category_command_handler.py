import uuid
from datetime import datetime
from typing import Optional

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.uow import InMemoryUnitOfWork
from application.commands import AddCategoryCommand
from application.commands.handlers.add_category_command_handler import (
    AddCategoryCommandHandler,
)
from domain.aggregates.budget import Budget
from domain.entities.category import Category
from domain.events.category import CategoryAdded
from domain.value_objects import CategoryName, Limit, Money


def _get_budget_repository(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: Optional[list[Category]] = None,
) -> InMemoryBudgetRepository:
    """Create a budget repository with a single budget."""
    budget = Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(100000, "USD")),
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 12, 31, 23, 59, 59),
        categories=categories or [],
    )
    return InMemoryBudgetRepository(
        budgets={budget_id: (0, budget)},
        users={user_id: {"id": user_id, "name": "Test User"}},
    )


def _get_deps(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: Optional[list[Category]] = None,
) -> tuple[
    AddCategoryCommandHandler, InMemoryBudgetRepository, InMemoryDomainPublisher
]:
    """Get dependencies for testing."""
    domain_publisher = InMemoryDomainPublisher()
    budget_repository = _get_budget_repository(user_id, budget_id, categories)
    unit_of_work = InMemoryUnitOfWork(domain_publisher)

    return (
        AddCategoryCommandHandler(
            budget_repository=budget_repository,
            unit_of_work=unit_of_work,
        ),
        budget_repository,
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


class TestAddCategoryCommandHandler:
    """Tests for the AddCategoryCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_adds_category_to_budget(self, user_id, budget_id):
        """Test that handling the command adds a category to the budget."""
        # Arrange
        command = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="Groceries",
            limit=300.0,
            currency="USD",
        )
        command_handler, budget_repository, domain_publisher = _get_deps(
            user_id, budget_id
        )

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(CategoryAdded, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that budget was updated
        _, budget = budget_repository._budgets[budget_id]

        # Check category was added
        assert len(budget.categories) == 1
        assert budget.categories[0].name.value == "Groceries"
        assert (
            budget.categories[0].limit.value.amount == Money.mint(300.0, "USD").amount
        )

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, CategoryAdded)
        assert event.budget_id == str(budget_id)
        assert event.name == "Groceries"
        assert event.limit == Money.mint(300.0, "USD").amount

    @pytest.mark.asyncio
    async def test_handle_adds_category_with_different_currency(
        self, user_id, budget_id
    ):
        """Test that handling the command adds a category with a different currency."""
        # Arrange
        command = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="Travel",
            limit=500.0,
            currency="EUR",
        )
        command_handler, budget_repository, _ = _get_deps(user_id, budget_id)

        # Act with expectation
        with pytest.raises(Exception):  # Should raise currency mismatch error
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_adds_multiple_categories(self, user_id, budget_id):
        """Test that handling multiple commands adds multiple categories."""
        # Arrange
        command1 = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="Groceries",
            limit=300.0,
            currency="USD",
        )
        command2 = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="Entertainment",
            limit=200.0,
            currency="USD",
        )
        command_handler, budget_repository, _ = _get_deps(user_id, budget_id)

        # Act
        await command_handler.handle(command1)
        await command_handler.handle(command2)

        # Assert
        _, budget = budget_repository._budgets[budget_id]

        # Check categories were added
        assert len(budget.categories) == 2
        assert budget.categories[0].name.value == "Groceries"
        assert (
            budget.categories[0].limit.value.amount == Money.mint(300.0, "USD").amount
        )
        assert budget.categories[1].name.value == "Entertainment"
        assert (
            budget.categories[1].limit.value.amount == Money.mint(200.0, "USD").amount
        )

    @pytest.mark.asyncio
    async def test_handle_fails_with_duplicate_category_name(self, user_id, budget_id):
        """Test that handling a command with a duplicate category name fails."""
        # Arrange
        existing_category = Category(
            id=uuid.uuid4(),
            budget_id=budget_id,
            name=CategoryName("Groceries"),
            limit=Limit(Money(300, "USD")),
        )

        command = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="Groceries",  # Same name as existing category
            limit=200.0,
            currency="USD",
        )
        command_handler, _, _ = _get_deps(user_id, budget_id, [existing_category])

        # Act with expectation
        with pytest.raises(Exception):  # Should raise duplicate category name error
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_when_max_categories_reached(self, user_id, budget_id):
        """Test that handling a command fails when max categories is reached."""
        # Arrange - create budget with max categories (5)
        categories = [
            Category(
                id=uuid.uuid4(),
                budget_id=budget_id,
                name=CategoryName(f"Category {i}"),
                limit=Limit(Money(100, "USD")),
            )
            for i in range(5)  # Budget.MAX_CATEGORIES is 5
        ]

        command = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="One Too Many",
            limit=100.0,
            currency="USD",
        )
        command_handler, _, _ = _get_deps(user_id, budget_id, categories)

        # Act with expectation
        with pytest.raises(Exception):  # Should raise max categories reached error
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_with_category_limit_exceeds_budget(
        self, user_id, budget_id
    ):
        """Test that handling fails if category limit would exceed budget limit."""
        # Arrange
        command = AddCategoryCommand(
            budget_id=budget_id,
            user_id=user_id,
            name="Expensive Category",
            limit=20000.0,  # Exceeds budget limit of 10000
            currency="USD",
        )
        command_handler, _, _ = _get_deps(user_id, budget_id)

        # Act with expectation
        with pytest.raises(
            Exception
        ):  # Should raise category limit exceeds budget error
            await command_handler.handle(command)
