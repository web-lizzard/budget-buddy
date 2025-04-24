import uuid
from datetime import datetime

import pytest
from domain.aggregates.budget import Budget
from domain.entities.category import Category
from domain.exceptions import CannotRenewDeactivatedBudgetError
from domain.factories import BudgetFactory
from domain.services.budget_renewal_service import BudgetRenewalService
from domain.strategies.budget_strategy import (
    MonthlyBudgetStrategy,
    YearlyBudgetStrategy,
)
from domain.value_objects import CategoryName, Limit, Money, MonthlyBudgetStrategyInput


def _create_category(budget_id: uuid.UUID, name: str, limit: int) -> Category:
    """Create a test category."""
    return Category(
        id=uuid.uuid4(),
        budget_id=budget_id,
        name=CategoryName(name),
        limit=Limit(Money(limit, "USD")),
    )


def _create_budget(user_id: uuid.UUID, categories: bool = True) -> Budget:
    """Create a test budget."""
    budget_id = uuid.uuid4()
    strategy_input = MonthlyBudgetStrategyInput(start_day=1)
    budget = Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(1000, "USD")),
        start_date=datetime(2023, 1, 1),
        end_date=datetime(2023, 1, 31, 23, 59, 59),
        strategy_input=strategy_input,
    )

    if categories:
        budget._categories = [
            _create_category(budget_id, "Groceries", 300),
            _create_category(budget_id, "Entertainment", 200),
        ]

    return budget


@pytest.fixture
def user_id() -> uuid.UUID:
    """Return a fixed user ID for testing."""
    return uuid.UUID("11111111-1111-1111-1111-111111111111")


@pytest.fixture
def renewal_service() -> BudgetRenewalService:
    """Return a BudgetRenewalService instance for testing."""
    # Create a BudgetFactory with real strategies
    factory = BudgetFactory(
        strategies=[MonthlyBudgetStrategy(), YearlyBudgetStrategy()]
    )
    return BudgetRenewalService(budget_factory=factory)


class TestBudgetRenewalService:
    """Tests for the BudgetRenewalService."""

    @pytest.mark.asyncio
    async def test_renew_budget_creates_new_budget(self, user_id, renewal_service):
        """Test that renewing a budget creates a new budget with the same attributes."""
        # Arrange
        budget = _create_budget(user_id)

        # Act
        new_budget = await renewal_service.renew_budget(budget)

        # Assert
        assert new_budget.id != budget.id
        assert new_budget.user_id == budget.user_id
        assert new_budget.total_limit.value.amount == budget.total_limit.value.amount
        assert new_budget.start_date == budget.end_date
        assert new_budget.is_active

    @pytest.mark.asyncio
    async def test_renew_budget_copies_categories(self, user_id, renewal_service):
        """Test that renewing a budget copies all categories."""
        # Arrange
        budget = _create_budget(user_id)
        original_category_names = [c.name.value for c in budget.categories]
        original_category_limits = [c.limit.value.amount for c in budget.categories]

        # Act
        new_budget = await renewal_service.renew_budget(budget)

        # Assert
        assert len(new_budget.categories) == len(budget.categories)
        for i, category in enumerate(new_budget.categories):
            assert category.id != budget.categories[i].id
            assert category.name.value == original_category_names[i]
            assert category.limit.value.amount == original_category_limits[i]
            assert category.budget_id == new_budget.id

    @pytest.mark.asyncio
    async def test_renew_deactivated_budget_raises_error(
        self, user_id, renewal_service
    ):
        """Test that renewing a deactivated budget raises an error."""
        # Arrange
        budget = _create_budget(user_id)
        budget.deactivate_budget()
        assert not budget.is_active

        # Act & Assert
        with pytest.raises(CannotRenewDeactivatedBudgetError) as exc_info:
            await renewal_service.renew_budget(budget)

        assert str(budget.id) in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_renew_budget_without_categories(self, user_id, renewal_service):
        """Test that renewing a budget with no categories creates a budget with no categories."""
        # Arrange
        budget = _create_budget(user_id, categories=False)
        assert len(budget.categories) == 0

        # Act
        new_budget = await renewal_service.renew_budget(budget)

        # Assert
        assert len(new_budget.categories) == 0
