from typing import List

from application.commands.remove_category_command import RemoveCategoryCommand
from domain.events.category.category_removed import CategoryRemoved
from domain.exceptions import InvalidTransferPolicyError
from domain.ports.budget_repository import BudgetRepository
from domain.ports.domain_publisher import DomainPublisher
from domain.ports.transaction_repository import TransactionRepository
from domain.services.transaction_transfer_service import TransactionTransferService
from domain.strategies.delete_transactions_strategy import DeleteTransactionsStrategy
from domain.strategies.move_transactions_strategy import MoveTransactionsStrategy
from domain.strategies.transaction_transfer_strategy import TransactionTransferStrategy
from domain.value_objects.transaction_transfer_policy import (
    DeleteTransactionsTransferPolicyInput,
    MoveToOtherCategoryTransferPolicyInput,
    TransactionTransferPolicyInput,
    TransactionTransferPolicyType,
)


class RemoveCategoryHandler:
    """Handler for removing a category from a budget."""

    def __init__(
        self,
        budget_repository: BudgetRepository,
        transaction_repository: TransactionRepository,
        domain_publisher: DomainPublisher,
    ):
        self._budget_repository = budget_repository
        self._transaction_repository = transaction_repository
        self._domain_publisher = domain_publisher

        # Initialize strategies
        transaction_transfer_service = TransactionTransferService()
        self._strategies: List[TransactionTransferStrategy] = [
            MoveTransactionsStrategy(
                transaction_repository, transaction_transfer_service
            ),
            DeleteTransactionsStrategy(transaction_repository),
        ]

    async def handle(self, command: RemoveCategoryCommand) -> None:
        """Handle the remove category command.

        Args:
            command: The command to handle

        Raises:
            BudgetNotFoundError: When budget is not found
            CategoryNotFoundError: When category is not found
            InvalidTransferPolicyError: When transfer policy is invalid
            TargetCategoryRequiredError: When transfer policy is 'transfer' but no target category is provided
        """
        budget_version, budget = await self._budget_repository.find_by(
            command.budget_id, command.user_id
        )

        source_category = budget.get_category_by(command.category_id)
        category_transactions = await self._transaction_repository.find_by_category_id(
            source_category.id, command.user_id
        )

        # Create transfer policy
        transfer_policy = self._create_transfer_policy(command)

        # Find and execute appropriate strategy
        strategy = next(
            (s for s in self._strategies if s.is_active(transfer_policy.policy_type)),
            None,
        )
        if strategy:
            await strategy.manage_transactions(
                budget, category_transactions, transfer_policy, command.user_id
            )

        # Remove the category from budget
        budget.remove_category(source_category.id)
        await self._budget_repository.save(budget, budget_version)

        # Publish event
        event = CategoryRemoved(
            category_id=str(command.category_id),
            budget_id=str(command.budget_id),
            transfer_policy=str(transfer_policy),
        )
        await self._domain_publisher.publish(event)

    def _create_transfer_policy(
        self, command: RemoveCategoryCommand
    ) -> TransactionTransferPolicyInput:
        """Create transfer policy input from command."""
        if command.transfer_policy.upper() == str(
            TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY
        ):
            if not command.target_category_id:
                raise InvalidTransferPolicyError(
                    "Target category ID is required for transfer policy"
                )
            return MoveToOtherCategoryTransferPolicyInput(
                target_category_id=command.target_category_id
            )
        return DeleteTransactionsTransferPolicyInput()
        return DeleteTransactionsTransferPolicyInput()
