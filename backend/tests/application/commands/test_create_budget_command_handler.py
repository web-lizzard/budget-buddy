import uuid
from datetime import datetime

import pytest
from adapters.inbound.in_memory_domain_publisher import InMemoryDomainPublisher
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from adapters.outbound.persistence.in_memory.uow import InMemoryUnitOfWork
from application.commands import CategoryData, CreateBudgetCommand
from application.commands.handlers.create_budget_command_handler import (
    CreateBudgetCommandHandler,
)
from domain.events import BudgetCreated
from domain.factories.budget_factory import BudgetFactory
from domain.strategies.budget_strategy import (
    MonthlyBudgetStrategy,
    YearlyBudgetStrategy,
)
from domain.value_objects import (
    BudgetStrategyType,
    Money,
    MonthlyBudgetStrategyInput,
    YearlyBudgetStrategyInput,
)


def _get_repository(user_id: uuid.UUID):
    return InMemoryBudgetRepository(
        budgets={}, users={user_id: {"id": user_id, "name": "Test User"}}
    )


def _get_deps(
    user_id: uuid.UUID,
) -> tuple[
    CreateBudgetCommandHandler, InMemoryBudgetRepository, InMemoryDomainPublisher
]:
    domain_publisher = InMemoryDomainPublisher()
    repository = _get_repository(user_id)
    unit_of_work = InMemoryUnitOfWork(domain_publisher)
    return (
        CreateBudgetCommandHandler(
            budget_factory=BudgetFactory(
                strategies=[MonthlyBudgetStrategy(), YearlyBudgetStrategy()]
            ),
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


class TestCreateBudgetCommandHandler:
    """Tests for the CreateBudgetCommandHandler."""

    @pytest.mark.asyncio
    async def test_handle_creates_budget_with_categories(self, user_id):
        """Test that handling the command creates a budget with categories."""
        # Arrange
        start_date = datetime(2023, 5, 1)
        strategy_input = MonthlyBudgetStrategyInput(start_day=1)
        command = CreateBudgetCommand(
            user_id=user_id,
            total_limit=1000.0,
            currency="USD",
            strategy_input=strategy_input,
            start_date=start_date,
            categories=[
                CategoryData(name="Groceries", limit=300.0),
                CategoryData(name="Entertainment", limit=200.0),
            ],
        )
        command_handler, budget_repository, domain_publisher = _get_deps(user_id)

        # Setup event capture
        captured_events = []

        def event_subscriber(event):
            captured_events.append(event)

        domain_publisher.subscribe(BudgetCreated, event_subscriber)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that budget was saved
        assert len(budget_repository._budgets) == 1
        budget_id = list(budget_repository._budgets.keys())[0]
        version, budget = budget_repository._budgets[budget_id]

        # Check version
        assert version == 0

        # Check basic budget properties
        assert budget.user_id == user_id
        assert budget.total_limit.value.amount == Money.mint(1000.0, "USD").amount
        assert budget.start_date == start_date

        # Check categories
        assert len(budget.categories) == 2
        assert budget.categories[0].name.value == "Groceries"
        assert (
            budget.categories[0].limit.value.amount == Money.mint(300.0, "USD").amount
        )
        assert budget.categories[1].name.value == "Entertainment"
        assert (
            budget.categories[1].limit.value.amount == Money.mint(200.0, "USD").amount
        )

        # Check that event was published
        assert len(captured_events) == 1
        event = captured_events[0]
        assert isinstance(event, BudgetCreated)
        assert event.user_id == str(user_id)
        assert event.total_limit == Money.mint(1000.0, "USD").amount
        assert event.start_date == start_date
        assert event.strategy == str(BudgetStrategyType.MONTHLY)

    @pytest.mark.asyncio
    async def test_handle_creates_budget_with_yearly_strategy(self, user_id):
        """Test that handling the command creates a budget with yearly strategy."""
        # Arrange
        start_date = datetime(2023, 1, 1)
        strategy_input = YearlyBudgetStrategyInput(start_month=1, start_day=1)
        command = CreateBudgetCommand(
            user_id=user_id,
            total_limit=12000.0,
            currency="EUR",
            strategy_input=strategy_input,
            start_date=start_date,
            categories=[
                CategoryData(name="Housing", limit=6000.0),
                CategoryData(name="Food", limit=3000.0),
            ],
        )
        command_handler, budget_repository, _ = _get_deps(user_id)

        # Act
        await command_handler.handle(command)

        # Assert
        # Check that budget was saved
        assert len(budget_repository._budgets) == 1
        budget_id = list(budget_repository._budgets.keys())[0]
        _, budget = budget_repository._budgets[budget_id]

        # Check that end date is calculated according to yearly strategy
        # End date should be 1 year (365 days) after start date
        expected_end_date = datetime(2023, 12, 31, 23, 59, 59)
        assert budget.end_date.date() == expected_end_date.date()

    @pytest.mark.asyncio
    async def test_handle_creates_budget_without_categories(self, user_id):
        """Test that handling the command creates a budget without categories."""
        # Arrange
        start_date = datetime(2023, 5, 1)
        strategy_input = MonthlyBudgetStrategyInput(start_day=1)
        command = CreateBudgetCommand(
            user_id=user_id,
            total_limit=1000.0,
            currency="USD",
            strategy_input=strategy_input,
            start_date=start_date,
            categories=[],
        )
        command_handler, budget_repository, _ = _get_deps(user_id)

        # Act
        await command_handler.handle(command)

        # Assert
        assert len(budget_repository._budgets) == 1
        budget_id = list(budget_repository._budgets.keys())[0]
        _, budget = budget_repository._budgets[budget_id]

        # Check that no categories were created
        assert len(budget.categories) == 0

    @pytest.mark.asyncio
    async def test_handle_with_monthly_strategy_input(self, user_id):
        """Test handling command with explicit strategy input instance."""
        # Arrange
        start_date = datetime(2023, 5, 1)
        strategy_input = MonthlyBudgetStrategyInput(start_day=15)

        command = CreateBudgetCommand(
            user_id=user_id,
            total_limit=1000.0,
            currency="USD",
            strategy_input=strategy_input,
            start_date=start_date,
            categories=[],
        )
        command_handler, budget_repository, _ = _get_deps(user_id)

        # Act
        await command_handler.handle(command)

        # Assert
        assert len(budget_repository._budgets) == 1

    @pytest.mark.asyncio
    async def test_handle_with_yearly_strategy_input(self, user_id):
        """Test handling command with explicit yearly strategy input instance."""
        # Arrange
        start_date = datetime(2023, 5, 1)
        strategy_input = YearlyBudgetStrategyInput(start_month=3, start_day=15)

        command = CreateBudgetCommand(
            user_id=user_id,
            total_limit=5000.0,
            currency="USD",
            strategy_input=strategy_input,
            start_date=start_date,
            categories=[],
        )
        command_handler, budget_repository, _ = _get_deps(user_id)
        # Act
        await command_handler.handle(command)

        # Assert
        assert len(budget_repository._budgets) == 1
        budget_id = list(budget_repository._budgets.keys())[0]
        _, budget = budget_repository._budgets[budget_id]

        # Check that strategy was correctly applied
        # End date should be next year
        assert budget.end_date.year == start_date.year + 1
