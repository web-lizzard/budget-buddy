from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID, uuid4

from domain.aggregates.transaction import Transaction
from domain.ports.budget_repository import BudgetRepository
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


@dataclass(frozen=True)
class TransactionFactoryParams:
    pass


T = TypeVar("T", bound=TransactionFactoryParams)


@dataclass(frozen=True)
class TransactionCreateParameters(TransactionFactoryParams):
    """Parameters for creating a Transaction."""

    category_id: UUID
    amount: Money
    transaction_type: TransactionType
    budget_id: UUID
    user_id: UUID
    occurred_date: datetime
    description: str | None = None


class TransactionFactory(ABC, Generic[T]):
    """Abstract factory for creating transactions."""

    @abstractmethod
    async def create(self, params: T) -> Transaction:
        """Abstract method to create a transaction."""
        raise NotImplementedError


class CreateTransactionFactory(TransactionFactory):
    """Factory for creating transactions."""

    def __init__(self, budget_repository: BudgetRepository):
        """
        Initialize factory.

        Args:
            budget_repository: Repository for budget operations
        """
        self._budget_repository = budget_repository

    async def create(self, params: TransactionCreateParameters) -> Transaction:
        """Create a new transaction.

        Args:
            params: Transaction creation parameters.

        Returns:
            Created transaction

        Raises:
            BudgetNotFoundError: When budget is not found or belongs to different user
        """
        _, budget = await self._budget_repository.find_by(
            params.budget_id, params.user_id
        )

        category = budget.get_category_by(params.category_id)

        budget.validate_transaction_date(params.occurred_date)

        return category.create_transaction(
            id=uuid4(),
            amount=params.amount,
            transaction_type=params.transaction_type,
            occurred_date=params.occurred_date,
            description=params.description,
            user_id=params.user_id,
        )
