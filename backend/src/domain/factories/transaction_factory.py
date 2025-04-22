from datetime import datetime
from uuid import UUID, uuid4

from domain.aggregates.transaction import Transaction
from domain.ports.budget_repository import BudgetRepository
from domain.value_objects.money import Money
from domain.value_objects.transaction_type import TransactionType


class TransactionFactory:
    """Factory for creating transactions."""

    def __init__(self, budget_repository: BudgetRepository):
        """Initialize factory.

        Args:
            budget_repository: Repository for budget operations
        """
        self._budget_repository = budget_repository

    async def create_transaction(
        self,
        category_id: UUID,
        amount: Money,
        transaction_type: TransactionType,
        budget_id: UUID,
        user_id: UUID,
        occurred_date: datetime,
        description: str | None = None,
    ) -> Transaction:
        """Create a new transaction.

        Args:
            category_id: The ID of the category
            amount: Transaction amount
            type: Transaction type
            user_id: The ID of the user who owns the transaction
            occurred_date: Transaction date (defaults to current datetime)
            description: Optional transaction description

        Returns:
            Created transaction

        Raises:
            BudgetNotFoundError: When budget is not found or belongs to different user
        """
        _, budget = await self._budget_repository.find_by(budget_id, user_id)

        category = budget.get_category_by(category_id)

        budget.validate_transaction_date(occurred_date)

        return category.create_transaction(
            id=uuid4(),
            amount=amount,
            transaction_type=transaction_type,
            occurred_date=occurred_date,
            description=description,
            user_id=user_id,
        )
