from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.aggregates.budget import Budget
from domain.aggregates.transaction import Transaction
from domain.ports.transaction_repository import TransactionRepository
from domain.value_objects.transaction_transfer_policy import (
    TransactionTransferPolicyInput,
    TransactionTransferPolicyType,
)


class TransactionTransferStrategy(ABC):
    """Base strategy for handling transaction transfers when removing a category."""

    def __init__(self, transaction_repository: TransactionRepository):
        self._transaction_repository = transaction_repository

    @abstractmethod
    def is_active(self, policy_type: TransactionTransferPolicyType) -> bool:
        """Check if this strategy should be used for given policy type.

        Args:
            policy_type: The policy type to check

        Returns:
            True if this strategy should be used, False otherwise
        """
        pass

    @abstractmethod
    async def manage_transactions(
        self,
        budget: Budget,
        transactions: List[Transaction],
        policy: TransactionTransferPolicyInput,
        user_id: UUID,
    ) -> None:
        """Manage transactions according to the strategy.

        Args:
            budget: The budget containing the categories
            transactions: List of transactions to manage
            policy: The transfer policy input
            user_id: The ID of the user who owns the transactions
        """
        pass
