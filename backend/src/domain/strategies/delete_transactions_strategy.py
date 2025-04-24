from typing import List
from uuid import UUID

from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.strategies.transaction_transfer_strategy import TransactionTransferStrategy
from domain.value_objects.transaction_transfer_policy import (
    TransactionTransferPolicyInput,
    TransactionTransferPolicyType,
)


class DeleteTransactionsStrategy(TransactionTransferStrategy):
    """Strategy for deleting transactions."""

    def is_active(self, policy_type: TransactionTransferPolicyType) -> bool:
        """Check if this strategy should be used for given policy type."""
        return policy_type == TransactionTransferPolicyType.DELETE_TRANSACTIONS

    async def manage_transactions(
        self,
        budget: Budget,
        transactions: List[Transaction],
        policy: TransactionTransferPolicyInput,
        user_id: UUID,
    ) -> None:
        """Delete all transactions."""
        await self._transaction_repository.delete_bulk(transactions, user_id)
