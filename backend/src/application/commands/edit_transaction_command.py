from uuid import UUID

from domain.value_objects import Money, TransactionType

from application.commands.command import Command


class EditTransactionCommand(Command):
    """Command for editing an existing transaction."""

    def __init__(
        self,
        transaction_id: UUID,
        budget_id: UUID,
        user_id: UUID,
        category_id: UUID,
        amount: Money,
        transaction_type: TransactionType,
        description: str | None = None,
    ):
        """Initialize the edit transaction command.

        Args:
            transaction_id: ID of the transaction to edit
            budget_id: ID of the budget containing the transaction
            user_id: ID of the user making the change
            category_id: New category ID
            amount: New transaction amount
            transaction_type: New transaction type
            description: New transaction description
        """
        self.transaction_id = transaction_id
        self.budget_id = budget_id
        self.user_id = user_id
        self.category_id = category_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
