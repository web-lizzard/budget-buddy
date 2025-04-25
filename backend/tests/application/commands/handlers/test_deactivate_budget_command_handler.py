import uuid
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands import DeactivateBudgetCommand
from application.commands.handlers.deactivate_budget_command_handler import (
    DeactivateBudgetCommandHandler,
)
from domain.aggregates.budget import Budget
from domain.events import BudgetDeactivated
from domain.value_objects import BudgetName, Limit, Money, MonthlyBudgetStrategyInput


def _create_budget(user_id: uuid.UUID) -> tuple[uuid.UUID, Budget]:
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
    DeactivateBudgetCommandHandler, InMemoryBudgetRepository, InMemoryDomainPublisher
]:
    """Get the dependencies for the test."""
    domain_publisher = InMemoryDomainPublisher()
    repository = _get_repository(user_id, budget_id, budget)
    unit_of_work = InMemoryUnitOfWork(domain_publisher)
    return (
        DeactivateBudgetCommandHandler(
            budget_repository=repository,
            unit_of_work=unit_of_work,
        ),
        repository,
        domain_publisher,
    )


@pytest.fixture
def user_id() -> uuid.UUID:
    """Return a fixed user ID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


class TestDeactivateBudgetCommandHandler:
    """Tests for the DeactivateBudgetCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_deactivates_budget(self, user_id):
        """Test that handling the command deactivates a budget."""
        # Arrange
        budget_id, budget = _create_budget(user_id)
        command = DeactivateBudgetCommand(
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

        domain_publisher.subscribe(BudgetDeactivated, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that budget was deactivated
        _, updated_budget = budget_repository._budgets[budget_id]
        assert updated_budget.deactivation_date is not None
        assert not updated_budget.is_active

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, BudgetDeactivated)
        assert event.budget_id == str(budget_id)
        assert event.deactivation_date == updated_budget.deactivation_date

    @pytest.mark.asyncio
    async def test_handle_already_deactivated_budget(self, user_id):
        """Test handling a command for an already deactivated budget."""
        # Arrange
        budget_id, budget = _create_budget(user_id)
        # Deactivate the budget
        budget.deactivate_budget()
        assert not budget.is_active

        command = DeactivateBudgetCommand(
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

        domain_publisher.subscribe(BudgetDeactivated, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, BudgetDeactivated)
        assert event.budget_id == str(budget_id)

    @pytest.mark.asyncio
    async def test_handle_nonexistent_budget(self, user_id):
        """Test handling a command for a non-existent budget."""
        # Arrange
        non_existent_budget_id = uuid.uuid4()
        command = DeactivateBudgetCommand(
            budget_id=non_existent_budget_id,
            user_id=user_id,
        )

        # Create a mock repository that raises BudgetNotFoundError
        mock_repository = MagicMock()
        mock_repository.find_by = AsyncMock(side_effect=Exception("Budget not found"))

        # Create a mock unit of work
        mock_unit_of_work = MagicMock()
        mock_unit_of_work.commit = AsyncMock()
        mock_unit_of_work.rollback = AsyncMock()

        command_handler = DeactivateBudgetCommandHandler(
            budget_repository=mock_repository,
            unit_of_work=mock_unit_of_work,
        )

        # Act & Assert
        with pytest.raises(Exception, match="Budget not found"):
            await command_handler.handle(command)

        # Verify that rollback was called
        mock_unit_of_work.rollback.assert_called_once()
