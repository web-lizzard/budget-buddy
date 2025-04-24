from uuid import UUID

from application.commands.command import Command


class DeleteTransactionCommand(Command):
    """Command for deleting an existing transaction."""

    def __init__(
        self,
        transaction_id: UUID,
        budget_id: UUID,
        user_id: UUID,
    ):
        """Initialize the delete transaction command.

        Args:
            transaction_id: ID of the transaction to delete
            budget_id: ID of the budget containing the transaction
            user_id: ID of the user making the change
        """
        self.transaction_id = transaction_id
        self.budget_id = budget_id
        self.user_id = user_id
