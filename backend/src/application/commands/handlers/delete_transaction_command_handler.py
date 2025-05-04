from domain.events.transaction.transaction_removed import TransactionRemoved
from domain.exceptions import CannotAddTransactionToDeactivatedBudgetError
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.ports.transaction_repository import TransactionRepository

from application.commands.delete_transaction_command import DeleteTransactionCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class DeleteTransactionCommandHandler(CommandHandler[DeleteTransactionCommand]):
    """Handler for deleting transactions."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        budget_repository: BudgetRepository,
        unit_of_work: UnitOfWork,
        clock: Clock,
    ):
        """
        Initialize the command handler with dependencies.

        Args:
            transaction_repository: Repository for transaction operations
            budget_repository: Repository for budget operations
            unit_of_work: UnitOfWork for transaction management and event publishing
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._transaction_repository = transaction_repository
        self._budget_repository = budget_repository
        self._clock = clock

    async def _handle(self, command: DeleteTransactionCommand) -> TransactionRemoved:
        """Handle the delete transaction command.

        Args:
            command: The delete transaction command

        Returns:
            A transaction deleted event

        Raises:
            BudgetNotFoundError: If the budget is not found
            TransactionNotFoundError: If the transaction is not found
            CannotAddTransactionToDeactivatedBudgetError: If the budget is deactivated
        """
        # Verify the budget exists and is active
        budget_result = await self._budget_repository.find_by(
            command.budget_id, command.user_id
        )
        budget = budget_result[1]  # Extract budget from the tuple (version, budget)

        if not budget.is_active:
            raise CannotAddTransactionToDeactivatedBudgetError(
                "current_date", str(budget.deactivation_date)
            )

        # Verify the transaction exists
        transaction = await self._transaction_repository.find_by_id(
            command.transaction_id, command.user_id
        )

        # Delete the transaction
        await self._transaction_repository.delete(transaction)

        # Return the event
        return TransactionRemoved(
            transaction_id=str(command.transaction_id),
            occurred_on=self._clock.now(),
            category_id=str(transaction.category_id),
            budget_id=str(command.budget_id),
            user_id=str(command.user_id),
        )
