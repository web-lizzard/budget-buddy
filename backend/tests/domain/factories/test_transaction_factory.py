from datetime import datetime
from uuid import UUID, uuid4

import pytest
from adapters.outbound.persistence.in_memory.budget_repository import (
    InMemoryBudgetRepository,
)
from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.exceptions import BudgetNotFoundError, TransactionOutsideBudgetPeriodError
from domain.factories.transaction_factory import (
    CreateTransactionFactory,
    TransactionCreateParameters,
    TransactionFactory,
)
from domain.value_objects import (
    BudgetName,
    CategoryName,
    Limit,
    Money,
    MonthlyBudgetStrategyInput,
    TransactionType,
)


@pytest.fixture
def user_id() -> UUID:
    return uuid4()


@pytest.fixture
def budget_id() -> UUID:
    return uuid4()


@pytest.fixture
def category_id() -> UUID:
    return uuid4()


@pytest.fixture
def amount() -> Money:
    return Money(100, "USD")


@pytest.fixture
def occurred_date() -> datetime:
    return datetime(2024, 1, 1, 12, 0)


@pytest.fixture
def description() -> str:
    return "Test transaction"


@pytest.fixture
def budget(budget_id: UUID, user_id: UUID) -> Budget:
    """Create a test budget with one category."""
    return Budget(
        id=budget_id,
        user_id=user_id,
        total_limit=Limit(Money(5000, "USD")),
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        strategy_input=MonthlyBudgetStrategyInput(start_day=1),
        name=BudgetName("Test Budget"),
    )


@pytest.fixture
def category(budget: Budget, category_id: UUID) -> Category:
    """Create a test category within the budget."""
    category = Category(
        id=category_id,
        budget_id=budget.id,
        name=CategoryName("Test Category"),
        limit=Limit(Money(1000, "USD")),
    )
    budget._categories.append(category)
    return category


@pytest.fixture
def budgets_db(budget: Budget) -> dict:
    """Create an in-memory budget database with one budget."""
    return {budget.id: (1, budget)}


@pytest.fixture
def users_db(user_id: UUID) -> dict:
    """Create an in-memory users database with one user."""
    return {user_id: {"id": user_id}}


@pytest.fixture
def budget_repository(budgets_db: dict, users_db: dict) -> InMemoryBudgetRepository:
    """Create an in-memory budget repository with test data."""
    return InMemoryBudgetRepository(budgets=budgets_db, users=users_db)


@pytest.fixture
def transaction_factory(
    budget_repository: InMemoryBudgetRepository,
) -> TransactionFactory:
    """Create a transaction factory with the test repository."""
    return CreateTransactionFactory(budget_repository)


class TestTransactionFactory:
    @pytest.mark.asyncio
    async def test_create_transaction_success(
        self,
        transaction_factory: TransactionFactory,
        category: Category,
        budget_id: UUID,
        user_id: UUID,
        amount: Money,
        occurred_date: datetime,
        description: str,
    ):
        """Test creating a transaction successfully."""
        create_params = TransactionCreateParameters(
            category_id=category.id,
            amount=amount,
            transaction_type=TransactionType.EXPENSE,
            budget_id=budget_id,
            user_id=user_id,
            occurred_date=occurred_date,
            description=description,
        )
        transaction = await transaction_factory.create(params=create_params)

        assert isinstance(transaction, Transaction)
        assert isinstance(transaction.id, UUID)
        assert transaction.category_id == category.id
        assert transaction.amount == amount
        assert transaction.transaction_type == TransactionType.EXPENSE
        assert transaction.occurred_date == occurred_date
        assert transaction.description == description
        assert transaction.user_id == user_id

    @pytest.mark.asyncio
    async def test_create_transaction_without_description(
        self,
        transaction_factory: TransactionFactory,
        category: Category,
        budget_id: UUID,
        user_id: UUID,
        amount: Money,
        occurred_date: datetime,
    ):
        """Test creating a transaction without description."""
        create_params = TransactionCreateParameters(
            category_id=category.id,
            amount=amount,
            transaction_type=TransactionType.EXPENSE,
            budget_id=budget_id,
            user_id=user_id,
            occurred_date=occurred_date,
            description=None,
        )
        transaction = await transaction_factory.create(params=create_params)

        assert isinstance(transaction, Transaction)
        assert transaction.description is None

    @pytest.mark.asyncio
    async def test_create_transaction_budget_not_found(
        self,
        transaction_factory: TransactionFactory,
        category: Category,
        user_id: UUID,
        amount: Money,
        occurred_date: datetime,
    ):
        """Test creating a transaction with non-existent budget."""
        non_existent_budget_id = uuid4()
        create_params = TransactionCreateParameters(
            category_id=category.id,
            amount=amount,
            transaction_type=TransactionType.EXPENSE,
            budget_id=non_existent_budget_id,
            user_id=user_id,
            occurred_date=occurred_date,
            description="test",
        )

        with pytest.raises(BudgetNotFoundError):
            await transaction_factory.create(params=create_params)

    @pytest.mark.asyncio
    async def test_create_transaction_wrong_user(
        self,
        transaction_factory: TransactionFactory,
        category: Category,
        budget_id: UUID,
        amount: Money,
        occurred_date: datetime,
    ):
        """Test creating a transaction with wrong user ID."""
        wrong_user_id = uuid4()
        create_params = TransactionCreateParameters(
            category_id=category.id,
            amount=amount,
            transaction_type=TransactionType.EXPENSE,
            budget_id=budget_id,
            user_id=wrong_user_id,
            occurred_date=occurred_date,
            description="test",
        )

        with pytest.raises(BudgetNotFoundError):
            await transaction_factory.create(params=create_params)

    @pytest.mark.asyncio
    async def test_create_transaction_outside_budget_period(
        self,
        transaction_factory: TransactionFactory,
        category: Category,
        budget_id: UUID,
        user_id: UUID,
        amount: Money,
    ):
        """Test creating a transaction with date outside budget period."""
        invalid_date = datetime(2025, 1, 1)  # After budget end date
        create_params = TransactionCreateParameters(
            category_id=category.id,
            amount=amount,
            transaction_type=TransactionType.EXPENSE,
            budget_id=budget_id,
            user_id=user_id,
            occurred_date=invalid_date,
            description="test",
        )

        with pytest.raises(TransactionOutsideBudgetPeriodError):
            await transaction_factory.create(params=create_params)

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "transaction_type", [TransactionType.INCOME, TransactionType.EXPENSE]
    )
    async def test_create_transaction_different_types(
        self,
        transaction_factory: TransactionFactory,
        category: Category,
        budget_id: UUID,
        user_id: UUID,
        amount: Money,
        occurred_date: datetime,
        transaction_type: TransactionType,
    ):
        """Test creating transactions with different types."""
        create_params = TransactionCreateParameters(
            category_id=category.id,
            amount=amount,
            transaction_type=transaction_type,
            budget_id=budget_id,
            user_id=user_id,
            occurred_date=occurred_date,
            description="test",
        )
        transaction = await transaction_factory.create(params=create_params)

        assert transaction.transaction_type == transaction_type
