from uuid import UUID

from domain.aggregates.transaction import Transaction
from domain.events.category.category_removed import CategoryRemoved
from domain.events.domain_event import DomainEvent
from domain.exceptions import InvalidTransferPolicyError
from domain.ports.budget_repository import BudgetRepository
from domain.ports.clock import Clock
from domain.ports.transaction_repository import TransactionRepository
from domain.services.reassign_transactions_service import ReassignTransactionsService
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
        clock: Clock,
    ):
        """Initialize the command handler.

        Args:
            unit_of_work: Unit of work to manage transactions
            budget_repository: Repository for budget operations
            transaction_repository: Repository for transaction operations
            clock: Clock for getting current time
        """
        super().__init__(unit_of_work)
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._reassign_transactions_service = ReassignTransactionsService()
        self._clock = clock

    async def _handle(self, command: RemoveCategoryCommand) -> DomainEvent:
        """Handle the remove category command.

        Args:
            command: Command to remove a category

        Returns:
            Domain event representing the removal of the category

        Raises:
            InvalidTransferPolicyError: When the transfer policy is invalid
            BudgetNotFoundError: When the budget is not found
            CategoryNotFoundError: When the category is not found
        """
        transfer_policy = self._create_transfer_policy(command)

        budget_id = UUID(command.budget_id)
        user_id = UUID(command.user_id)
        category_id = UUID(command.category_id)

        version, budget = await self._budget_repository.find_by(budget_id, user_id)

        transactions = await self._transaction_repository.find_by_category_id(
            category_id, user_id
        )
        transfer_policy = self._create_transfer_policy(command)
        if transactions:
            await self._handle_associated_transactions(transactions, transfer_policy)

        budget.remove_category(category_id)

        # Save the budget
        await self._budget_repository.save(budget, version)

        # Return domain event
        return CategoryRemoved(
            category_id=str(category_id),
            budget_id=str(budget_id),
            transfer_policy=str(transfer_policy),
            occurred_on=self._clock.now(),
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
        if command.handle_transactions == "move":
            return MoveToOtherCategoryTransferPolicyInput(
                target_category_id=(
                    UUID(command.target_category_id)
                    if command.target_category_id
                    else None
                )
            )
        raise InvalidTransferPolicyError(
            f"Invalid transfer policy: {command.handle_transactions}"
        )

    async def _handle_associated_transactions(
        self, transactions: list[Transaction], policy: TransactionTransferPolicyInput
    ) -> None:
        if policy.policy_type == TransactionTransferPolicyType.DELETE_TRANSACTIONS:
            await self._transaction_repository.delete_bulk(transactions)
        elif policy.policy_type == TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY:
            assert isinstance(policy, MoveToOtherCategoryTransferPolicyInput)
            self._reassign_transactions_service.reassign_transactions(
                transactions, policy
            )
