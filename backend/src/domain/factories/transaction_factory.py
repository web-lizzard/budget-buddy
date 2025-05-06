from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar
from uuid import uuid4

from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.entities.category import Category
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


@dataclass(frozen=True)
class TransactionFactoryParams:
    """Base parameters class for transaction factories."""

    pass


T = TypeVar("T", bound=TransactionFactoryParams)


@dataclass(frozen=True)
class TransactionCreateParameters(TransactionFactoryParams):
    """Parameters for creating a Transaction.

    Contains all necessary data to create a new transaction entity.
    """

    budget: Budget
    category: Category
    amount: float
    transaction_type: TransactionType
    occurred_date: datetime
    description: str | None = None


class TransactionFactory(ABC, Generic[T]):
    """Abstract factory for creating Transaction aggregates.

    This factory interface defines the contract for creating transaction objects
    based on provided parameters.
    """

    @abstractmethod
    async def create(self, params: T) -> Transaction:
        """Create a new Transaction aggregate.

        Args:
            params: Parameters required for transaction creation.

        Returns:
            A new Transaction aggregate.

        Raises:
            NotImplementedError: When called on the abstract class.
        """
        raise NotImplementedError


class CreateTransactionFactory(TransactionFactory):
    """Factory implementation for creating new Transaction aggregates.

    This factory creates new Transaction objects based on provided parameters
    without relying on external repositories.
    """

    async def create(self, params: TransactionCreateParameters) -> Transaction:
        """Create a new Transaction aggregate.

        Args:
            params: Parameters containing Budget, Category, and other transaction details.

        Returns:
            A new Transaction aggregate.

        Raises:
            ValueError: When transaction date is invalid or outside budget period.
        """
        budget = params.budget
        category = params.category

        money = Money.mint(params.amount, budget.currency)

        # Validate the transaction date against budget constraints
        budget.validate_transaction_date(params.occurred_date)

        # Create and return the transaction using the category
        return category.create_transaction(
            id=uuid4(),
            amount=money,
            transaction_type=params.transaction_type,
            occurred_date=params.occurred_date,
            description=params.description,
            user_id=budget.user_id,
        )
