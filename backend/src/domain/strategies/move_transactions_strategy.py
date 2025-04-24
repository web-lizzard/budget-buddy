from typing import List
from uuid import UUID

from domain.aggregates.transaction import Transaction
from domain.ports.transaction_repository import TransactionRepository
from domain.services.transaction_transfer_service import TransactionTransferService
from domain.strategies.transaction_transfer_strategy import TransactionTransferStrategy
from domain.value_objects.transaction_transfer_policy import (
    MoveToOtherCategoryTransferPolicyInput,
    TransactionTransferPolicyInput,
    TransactionTransferPolicyType,
)


class MoveTransactionsStrategy(TransactionTransferStrategy):
    """Strategy for moving transactions to another category."""

    def __init__(
        self,
        transaction_repository: TransactionRepository,
        transaction_transfer_service: TransactionTransferService,
    ):
        super().__init__(transaction_repository)
        self._transaction_transfer_service = transaction_transfer_service

    def is_active(self, policy_input: TransactionTransferPolicyInput) -> bool:
        """Check if this strategy should be used for given policy type."""
        return (
            policy_input.policy_type
            == TransactionTransferPolicyType.MOVE_TO_OTHER_CATEGORY
        )

    async def manage_transactions(
        self,
        transactions: List[Transaction],
        policy: TransactionTransferPolicyInput,
        user_id: UUID,
    ) -> None:
        """Move transactions to target category."""
        if not isinstance(policy, MoveToOtherCategoryTransferPolicyInput):
            return

        self._transaction_transfer_service.transfer_transactions(
            transactions, policy.target_category_id
        )
        await self._transaction_repository.save_bulk(transactions)
