import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.clock.fixed_clock import FixedClock
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands import RenewBudgetCommand
from application.commands.handlers.renew_budget_command_handler import (
    RenewBudgetCommandHandler,
)
from domain.aggregates.budget import Budget
from domain.entities.category import Category
from domain.events import BudgetRenewed
from domain.exceptions import CannotRenewDeactivatedBudgetError
from domain.factories.budget_factory import BudgetFactory
from domain.services.budget_renewal_service import BudgetRenewalService
from domain.strategies.budget_strategy import (
    MonthlyBudgetStrategy,
    YearlyBudgetStrategy,
)
from domain.value_objects import (
    BudgetName,
    CategoryName,
    Limit,
    Money,
    MonthlyBudgetStrategyInput,
)


def _create_category(budget_id: uuid.UUID, name: str, limit: int) -> Category:
    """Create a test category."""
    return Category(
        id=uuid.uuid4(),
        budget_id=budget_id,
        name=CategoryName(name),
        limit=Limit(Money(limit, "USD")),
    )


def _create_budget(
    user_id: uuid.UUID, categories: bool = True
) -> tuple[uuid.UUID, Budget]:
    """Create a test budget."""
    budget_id = uuid.uuid4()
    budget = Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(1000, "USD")),
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 1, 31, 23, 59, 59),
        strategy_input=MonthlyBudgetStrategyInput(start_day=1),
        name=BudgetName("Test Budget"),
    )

    if categories:
        budget._categories = [
            _create_category(budget_id, "Groceries", 300),
            _create_category(budget_id, "Entertainment", 200),
        ]

    return budget_id, budget


def _get_repository(user_id: uuid.UUID, budget_id: uuid.UUID, budget: Budget):
    """Get a repository with a pre-populated budget."""
    repository = InMemoryBudgetRepository(
        budgets={budget_id: (0, budget)},
        users={user_id: {"id": user_id, "name": "Test User"}},
    )
    return repository


def _get_deps(
    user_id: uuid.UUID, budget_id: uuid.UUID, budget: Budget
) -> tuple[
    RenewBudgetCommandHandler, InMemoryBudgetRepository, InMemoryDomainPublisher
]:
    """Get the dependencies for the test."""
    domain_publisher = InMemoryDomainPublisher()
    repository = _get_repository(user_id, budget_id, budget)
    unit_of_work = InMemoryUnitOfWork(domain_publisher)
    clock = FixedClock(datetime(2023, 1, 1, 12, 0, 0))
    strategies = [MonthlyBudgetStrategy(), YearlyBudgetStrategy()]
    budget_factory = BudgetFactory(strategies=strategies)
    renewal_service = BudgetRenewalService(budget_factory)

    return (
        RenewBudgetCommandHandler(
            budget_repository=repository,
            budget_renewal_service=renewal_service,
            unit_of_work=unit_of_work,
            clock=clock,
        ),
        repository,
        domain_publisher,
    )


@pytest.fixture
def user_id() -> uuid.UUID:
    """Return a fixed user ID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


class TestRenewBudgetCommandHandler:
    """Tests for the RenewBudgetCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_renews_budget(self, user_id):
        """Test that handling the command renews a budget."""
        # Arrange
        budget_id, budget = _create_budget(user_id)
        command = RenewBudgetCommand(
            budget_id=budget_id,
            user_id=user_id,
        )
        command_handler, budget_repository, domain_publisher = _get_deps(
            user_id, budget_id, budget
        )

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(BudgetRenewed, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that a new budget was created
        assert len(budget_repository._budgets) == 2

        # Find the new budget
        new_budget_id = None
        for bid in budget_repository._budgets.keys():
            if bid != budget_id:
                new_budget_id = bid
                break

        assert new_budget_id is not None
        _, new_budget = budget_repository._budgets[new_budget_id]

        # Check that new budget has the expected properties
        assert new_budget.user_id == user_id
        assert new_budget.total_limit.value.amount == 1000
        assert new_budget.start_date == budget.end_date
        assert len(new_budget.categories) == 2

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, BudgetRenewed)
        assert event.old_budget_id == str(budget_id)
        assert event.budget_id == str(new_budget_id)
        assert event.user_id == str(user_id)
        assert event.start_date == new_budget.start_date
        assert event.end_date == new_budget.end_date

    @pytest.mark.asyncio
    async def test_handle_deactivated_budget(self, user_id):
        """Test that handling the command for a deactivated budget raises an error."""
        # Arrange
        budget_id, budget = _create_budget(user_id)
        clock = FixedClock(datetime(2023, 1, 1, 12, 0, 0))
        # Deactivate the budget
        budget.deactivate_budget(clock.now())
        assert not budget.is_active

        command = RenewBudgetCommand(
            budget_id=budget_id,
            user_id=user_id,
        )
        command_handler, _, _ = _get_deps(user_id, budget_id, budget)

        # Act & Assert
        with pytest.raises(CannotRenewDeactivatedBudgetError):
            await command_handler.handle(command)

    @pytest.mark.asyncio
    async def test_handle_nonexistent_budget(self, user_id):
        """Test handling a command for a non-existent budget."""
        # Arrange
        non_existent_budget_id = uuid.uuid4()
        command = RenewBudgetCommand(
            budget_id=non_existent_budget_id,
            user_id=user_id,
        )

        # Create a mock repository that raises an exception
        mock_repository = MagicMock()
        mock_repository.find_by = AsyncMock(side_effect=Exception("Budget not found"))

        # Create a mock unit of work
        mock_unit_of_work = MagicMock()
        mock_unit_of_work.commit = AsyncMock()
        mock_unit_of_work.rollback = AsyncMock()

        # Create a mock clock
        mock_clock = FixedClock(datetime(2023, 1, 1, 12, 0, 0))

        # Create a mock factory and service
        strategies = [MonthlyBudgetStrategy(), YearlyBudgetStrategy()]
        mock_factory = BudgetFactory(strategies=strategies)
        mock_service = BudgetRenewalService(mock_factory)

        command_handler = RenewBudgetCommandHandler(
            budget_repository=mock_repository,
            budget_renewal_service=mock_service,
            unit_of_work=mock_unit_of_work,
            clock=mock_clock,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Budget not found"):
            await command_handler.handle(command)

        # Verify that rollback was called
        mock_unit_of_work.rollback.assert_called_once()
