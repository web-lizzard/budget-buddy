from uuid import UUID

from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.events.transaction_edited_event import TransactionEditedEvent
from domain.exceptions import CannotAddTransactionToDeactivatedBudgetError
from domain.ports.budget_repository import BudgetRepository
from domain.ports.transaction_repository import TransactionRepository
from domain.value_objects import Money

from application.commands.edit_transaction_command import EditTransactionCommand
from application.commands.handlers.command_handler import CommandHandler
from application.ports.uow import UnitOfWork


class EditTransactionCommandHandler(CommandHandler[EditTransactionCommand]):
    """Handler for editing transactions."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        transaction_repository: TransactionRepository,
        budget_repository: BudgetRepository,
    ):
        """Initialize the edit transaction command handler.

        Args:
            unit_of_work: Unit of work for managing transactions
            transaction_repository: Repository for accessing transactions
            budget_repository: Repository for accessing budgets
        """
        super().__init__(unit_of_work)
        self._transaction_repository = transaction_repository
        self._budget_repository = budget_repository

    async def _handle(self, command: EditTransactionCommand) -> TransactionEditedEvent:
        """Handle the edit transaction command.

        Args:
            command: The edit transaction command

        Returns:
            A transaction edited event

        Raises:
            BudgetNotFoundError: If the budget is not found
            TransactionNotFoundError: If the transaction is not found
            CategoryNotFoundError: If the category is not found
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

        if command.occurred_date:
            budget.validate_transaction_date(command.occurred_date)

        # Update the transaction
        transaction.update(
            category_id=self._get_category_id(command, transaction, budget),
            amount=(
                Money.mint(command.amount, budget.currency)
                if command.amount
                else transaction.amount
            ),
            transaction_type=(command.transaction_type or transaction.transaction_type),
            description=(command.description or transaction.description),
            occurred_date=command.occurred_date or transaction.occurred_date,
        )

        # Save the updated transaction
        await self._transaction_repository.save(transaction)

        # Return the event - use updated values from the transaction aggregate
        return TransactionEditedEvent(
            transaction_id=transaction.id,
            budget_id=command.budget_id,
            user_id=command.user_id,
            category_id=transaction.category_id,
            amount=transaction.amount,
            transaction_type=transaction.transaction_type,
            description=transaction.description,
        )

    def _get_category_id(
        self, command: EditTransactionCommand, transaction: Transaction, budget: Budget
    ) -> UUID:
        if not command.category_id:
            return transaction.category_id

        budget.get_category_by(command.category_id)
        return command.category_id
