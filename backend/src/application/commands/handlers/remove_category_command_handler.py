from uuid import UUID

from domain.events.category.category_removed import CategoryRemoved
from domain.events.domain_event import DomainEvent
from domain.exceptions import InvalidTransferPolicyError
from domain.ports.budget_repository import BudgetRepository
from domain.ports.transaction_repository import TransactionRepository
from domain.value_objects import (
    DeleteTransactionsTransferPolicyInput,
    MoveToOtherCategoryTransferPolicyInput,
    TransactionTransferPolicyInput,
    TransactionTransferPolicyType,
)

from application.commands.handlers.command_handler import CommandHandler
from application.commands.remove_category_command import RemoveCategoryCommand
from application.ports.uow import UnitOfWork


class RemoveCategoryCommandHandler(CommandHandler[RemoveCategoryCommand]):
    """Handler for removing a category from a budget."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
    ):
        """Initialize the command handler.

        Args:
            unit_of_work: Unit of work to manage transactions
            budget_repository: Repository for budget operations
            transaction_repository: Repository for transaction operations
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository

    async def _handle(self, command: RemoveCategoryCommand) -> DomainEvent:
        """Handle the remove category command.

        Args:
            command: Command to remove a category

        Returns:
            Domain event representing the removal of the category

        Raises:
            InvalidTransferPolicyError: When the transfer policy is invalid
        """
        # Create appropriate transfer policy based on command parameters
        transfer_policy = self._create_transfer_policy(command)

        # Find the budget
        budget_id = UUID(command.budget_id)
        user_id = UUID(command.user_id)
        category_id = UUID(command.category_id)

        version, budget = await self._budget_repository.find_by(budget_id, user_id)

        # Handle transactions according to policy
        if (
            transfer_policy.policy_type
            == TransactionTransferPolicyType.DELETE_TRANSACTIONS
        ):
            transactions = await self._transaction_repository.find_by_budget_id(
                budget_id, user_id
            )
            transactions_to_delete = [
                t for t in transactions if t.category_id == category_id
            ]
            if transactions_to_delete:
                await self._transaction_repository.delete_bulk(transactions_to_delete)
        elif (
            transfer_policy.policy_type
            == TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY
        ):
            target_category_id = UUID(command.target_category_id)
            transactions = await self._transaction_repository.find_by_budget_id(
                budget_id, user_id
            )
            transactions_to_update = [
                t for t in transactions if t.category_id == category_id
            ]

            # Update category ID for each transaction
            for transaction in transactions_to_update:
                transaction.update_category(target_category_id)

            if transactions_to_update:
                await self._transaction_repository.save_bulk(transactions_to_update)

        # Remove the category from the budget
        budget.remove_category(category_id)

        # Save the budget
        await self._budget_repository.save(budget, version)

        # Return domain event
        return CategoryRemoved(
            category_id=str(category_id),
            budget_id=str(budget_id),
            transfer_policy=str(transfer_policy),
        )

    def _create_transfer_policy(
        self, command: RemoveCategoryCommand
    ) -> TransactionTransferPolicyInput:
        """Create a transfer policy from the command parameters.

        Args:
            command: The command containing transfer policy information

        Returns:
            A concrete transfer policy instance

        Raises:
            InvalidTransferPolicyError: When the transfer policy is invalid
        """
        if command.handle_transactions == "delete":
            return DeleteTransactionsTransferPolicyInput()
        elif command.handle_transactions == "move":
            if not command.target_category_id:
                raise InvalidTransferPolicyError(
                    "Target category ID is required when moving transactions"
                )
            return MoveToOtherCategoryTransferPolicyInput(
                target_category_id=UUID(command.target_category_id)
            )
        else:
            raise InvalidTransferPolicyError(
                f"Invalid transfer policy: {command.handle_transactions}"
            )
