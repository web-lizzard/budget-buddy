from uuid import UUID

from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.events.transaction.transaction_updated import TransactionUpdated
from domain.exceptions import CannotAddTransactionToDeactivatedBudgetError
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.ports.transaction_repository import TransactionRepository
from domain.value_objects import Money, TransactionType

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
        clock: Clock,
    ):
        """Initialize the edit transaction command handler.

        Args:
            unit_of_work: Unit of work for managing transactions
            transaction_repository: Repository for accessing transactions
            budget_repository: Repository for accessing budgets
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._transaction_repository = transaction_repository
        self._budget_repository = budget_repository
        self._clock = clock

    async def _handle(self, command: EditTransactionCommand) -> TransactionUpdated:
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
            transaction_type=(
                self._get_transaction_type(command, transaction)
                or transaction.transaction_type
            ),
            description=(command.description or transaction.description),
            occurred_date=command.occurred_date or transaction.occurred_date,
        )

        # Save the updated transaction
        await self._transaction_repository.save(transaction)

        # Return the event - use updated values from the transaction aggregate
        return TransactionUpdated(
            occurred_on=self._clock.now(),
            transaction_id=str(transaction.id),  # Ensure transaction_id is a string
            category_id=str(transaction.category_id),  # Ensure category_id is a string
            amount=transaction.amount.amount,  # amount is already an int
            type=str(
                transaction.transaction_type
            ),  # Corrected parameter name to 'type'
            date=transaction.occurred_date,  # Corrected parameter name to 'date'
            user_id=str(command.user_id),
            budget_id=str(command.budget_id),
        )

    def _get_category_id(
        self, command: EditTransactionCommand, transaction: Transaction, budget: Budget
    ) -> UUID:
        if not command.category_id:
            return transaction.category_id

        budget.get_category_by(command.category_id)
        return command.category_id

    def _get_transaction_type(
        self, command: EditTransactionCommand, transaction: Transaction
    ) -> TransactionType:
        if not command.transaction_type:
            return transaction.transaction_type

        return TransactionType(command.transaction_type)
