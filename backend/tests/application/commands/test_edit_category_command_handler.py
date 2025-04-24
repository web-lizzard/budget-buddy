import uuid
from datetime import datetime
from typing import Optional

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands import EditCategoryCommand
from application.commands.handlers import EditCategoryCommandHandler
from domain.aggregates.budget import Budget
from domain.entities.category import Category
from domain.events.category import CategoryEdited
from domain.exceptions import (
    CategoryLimitExceedsBudgetError,
    CategoryNotFoundError,
    DuplicateCategoryNameError,
)
from domain.value_objects import CategoryName, Limit, Money, MonthlyBudgetStrategyInput


def _get_budget_repository(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: Optional[list[Category]] = None,
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


def _get_deps(
    user_id: uuid.UUID,
    budget_id: uuid.UUID,
    categories: Optional[list[Category]] = None,
) -> tuple[
    EditCategoryCommandHandler, InMemoryBudgetRepository, InMemoryDomainPublisher
]:
    """Get dependencies for testing."""
    domain_publisher = InMemoryDomainPublisher()
    budget_repository = _get_budget_repository(user_id, budget_id, categories)
    unit_of_work = InMemoryUnitOfWork(domain_publisher)

    return (
        EditCategoryCommandHandler(
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


@pytest.fixture
def category_id() -> uuid.UUID:
    """Return a fixed category ID for testing."""
    return uuid.UUID("33333333-3333-3333-3333-333333333333")


class TestEditCategoryCommandHandler:
    """Tests for the EditCategoryCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_edits_category_in_budget(
        self, user_id, budget_id, category_id
    ):
        """Test that handling the command updates a category in the budget."""
        # Arrange
        existing_category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Old Name"),
            limit=Limit(Money(30000, "USD")),
        )

        command = EditCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            name="New Name",
            limit=500.0,
        )
        command_handler, budget_repository, domain_publisher = _get_deps(
            user_id, budget_id, [existing_category]
        )

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(CategoryEdited, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that budget was updated
        _, budget = budget_repository._budgets[budget_id]

        # Check category was updated
        assert len(budget.categories) == 1
        assert budget.categories[0].name.value == "New Name"
        assert (
            budget.categories[0].limit.value.amount == Money.mint(500.0, "USD").amount
        )

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, CategoryEdited)
        assert event.budget_id == str(budget_id)
        assert event.category_id == str(category_id)
        assert event.name == "New Name"
        assert event.limit == Money.mint(500.0, "USD").amount

    @pytest.mark.asyncio
    async def test_handle_edits_category_name_only(
        self, user_id, budget_id, category_id
    ):
        """Test that handling the command updates only category name."""
        # Arrange
        existing_category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Old Name"),
            limit=Limit(Money(30000, "USD")),
        )

        command = EditCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            name="New Name",
            limit=None,  # Not providing limit should keep the old one
        )

        command_handler, budget_repository, domain_publisher = _get_deps(
            user_id, budget_id, [existing_category]
        )

        # Act
        await command_handler.handle(command)

        # Assert
        _, budget = budget_repository._budgets[budget_id]

        # Check category was updated with only name changed
        assert len(budget.categories) == 1
        assert budget.categories[0].name.value == "New Name"
        assert budget.categories[0].limit.value.amount == 30000  # Original value

    @pytest.mark.asyncio
    async def test_handle_edits_category_limit_only(
        self, user_id, budget_id, category_id
    ):
        """Test that handling the command updates only category limit."""
        # Arrange
        existing_category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Category Name"),
            limit=Limit(Money(30000, "USD")),
        )

        command = EditCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            name=None,  # Not providing name should keep the old one
            limit=450.0,
        )

        command_handler, budget_repository, domain_publisher = _get_deps(
            user_id, budget_id, [existing_category]
        )

        # Act
        await command_handler.handle(command)

        # Assert
        _, budget = budget_repository._budgets[budget_id]

        # Check category was updated with only limit changed
        assert len(budget.categories) == 1
        assert budget.categories[0].name.value == "Category Name"  # Original value
        assert (
            budget.categories[0].limit.value.amount == Money.mint(450.0, "USD").amount
        )

    @pytest.mark.asyncio
    async def test_handle_fails_with_category_not_found(
        self, user_id, budget_id, category_id
    ):
        """Test that handling fails when category is not found."""
        # Arrange - empty budget
        command = EditCategoryCommand(
            category_id=str(category_id),  # Non-existent category
            budget_id=str(budget_id),
            user_id=str(user_id),
            name="New Name",
            limit=500.0,
        )
        command_handler, _, _ = _get_deps(user_id, budget_id)  # Empty budget

        # Act with expectation
        with pytest.raises(CategoryNotFoundError):  # More specific error
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_with_duplicate_category_name(
        self, user_id, budget_id, category_id
    ):
        """Test that handling fails when trying to rename to an existing name."""
        # Arrange - create two categories
        category1 = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Category 1"),
            limit=Limit(Money(10000, "USD")),
        )

        category2 = Category(
            id=uuid.uuid4(),
            budget_id=budget_id,
            name=CategoryName("Category 2"),
            limit=Limit(Money(20000, "USD")),
        )

        command = EditCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            name="Category 2",  # Try to rename to existing name
            limit=150.0,
        )
        command_handler, _, _ = _get_deps(user_id, budget_id, [category1, category2])

        # Act with expectation
        with pytest.raises(DuplicateCategoryNameError):  # More specific error
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_fails_with_category_limit_exceeds_budget(
        self, user_id, budget_id, category_id
    ):
        """Test that handling fails when new limit would exceed budget limit."""
        # Arrange
        existing_category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Category"),
            limit=Limit(Money(30000, "USD")),
        )

        # Add another category to consume part of the budget
        other_category = Category(
            id=uuid.uuid4(),
            budget_id=budget_id,
            name=CategoryName("Other Category"),
            limit=Limit(Money(80000, "USD")),
        )

        command = EditCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            name="Updated Category",
            limit=500.0,  # This plus other category (800) exceeds budget limit of 1000
        )
        command_handler, _, _ = _get_deps(
            user_id, budget_id, [existing_category, other_category]
        )

        # Act with expectation
        with pytest.raises(CategoryLimitExceedsBudgetError):  # More specific error
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_save_to_repository_with_correct_version(
        self, user_id, budget_id, category_id
    ):
        """Test that budget is saved to repository with correct version."""
        # Arrange
        existing_category = Category(
            id=category_id,
            budget_id=budget_id,
            name=CategoryName("Old Name"),
            limit=Limit(Money(30000, "USD")),
        )

        version = 42  # Specific version to check

        # Create repository with specific version
        repository = InMemoryBudgetRepository(
            budgets={
                budget_id: (
                    version,
                    Budget(
                        id=budget_id,
                        user_id=user_id,
                        total_limit=Limit(Money(100000, "USD")),
                        start_date=datetime(2023, 1, 1),
                        end_date=datetime(2023, 12, 31, 23, 59, 59),
                        strategy_input=MonthlyBudgetStrategyInput(start_day=1),
                        categories=[existing_category],
                    ),
                )
            },
            users={user_id: {"id": user_id, "name": "Test User"}},
        )

        # Create handler with this repository
        domain_publisher = InMemoryDomainPublisher()
        unit_of_work = InMemoryUnitOfWork(domain_publisher)
        command_handler = EditCategoryCommandHandler(
            budget_repository=repository,
            unit_of_work=unit_of_work,
        )

        command = EditCategoryCommand(
            category_id=str(category_id),
            budget_id=str(budget_id),
            user_id=str(user_id),
            name="New Name",
            limit=500.0,
        )

        # Act
        await command_handler.handle(command)

        # Assert - Verify save was called with correct version
        saved_version, saved_budget = repository._budgets[budget_id]
        assert (
            saved_version == version
        )  # Version should be unchanged in the repository's state

        # Also verify the budget was updated
        assert saved_budget.categories[0].name.value == "New Name"
