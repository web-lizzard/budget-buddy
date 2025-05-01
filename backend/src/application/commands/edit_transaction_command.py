from datetime import datetime
from uuid import UUID

from domain.value_objects import TransactionType

from application.commands.command import Command


class EditTransactionCommand(Command):
    """Command for editing an existing transaction."""

    transaction_id: UUID
    budget_id: UUID
    user_id: UUID
    category_id: UUID | None
    amount: float | None
    transaction_type: TransactionType | None
    description: str | None
    occurred_date: datetime | None

    def __init__(
        self,
        transaction_id: UUID,
        budget_id: UUID,
        user_id: UUID,
        category_id: UUID | None = None,
        amount: float | None = None,
        transaction_type: TransactionType | None = None,
        description: str | None = None,
        occurred_date: datetime | None = None,
    ):
        """Initialize the edit transaction command.

        Args:
            transaction_id: ID of the transaction to edit
            budget_id: ID of the budget containing the transaction
            user_id: ID of the user making the change
            category_id: New category ID (optional)
            amount: New transaction amount (optional)
            transaction_type: New transaction type (optional)
            description: New transaction description (optional)
            occurred_date: New transaction occurred date (optional)
        """
        self.transaction_id = transaction_id
        self.budget_id = budget_id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.occurred_date = occurred_date
