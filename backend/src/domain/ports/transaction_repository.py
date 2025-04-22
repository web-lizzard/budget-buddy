from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.aggregates.transaction import Transaction


class TransactionRepository(ABC):
    """Port for transaction repository operations."""

    @abstractmethod
    async def find_by_id(self, transaction_id: UUID, user_id: UUID) -> Transaction:
        """Find transaction by id.

        Args:
            transaction_id: The ID of the transaction to find
            user_id: The ID of the user who owns the transaction

        Returns:
            Transaction if found

        Raises:
            TransactionNotFoundError: When transaction is not found or belongs to different user
        """
        pass

    @abstractmethod
    async def find_by_budget_id(
        self, budget_id: UUID, user_id: UUID
    ) -> List[Transaction]:
        """Find all transactions for a given budget.

        Args:
            budget_id: The ID of the budget
            user_id: The ID of the user who owns the budget

        Returns:
            List of transactions
        """
        pass

    @abstractmethod
    async def save(self, transaction: Transaction) -> None:
        """Save transaction to repository.

        Args:
            transaction: The transaction to save

        Raises:
            TransactionNotFoundError: When user is not found
        """
        pass

    @abstractmethod
    async def delete(self, transaction: Transaction, user_id: UUID) -> None:
        """Delete transaction from repository.

        Args:
            transaction: The transaction to delete
            user_id: The ID of the user who owns the transaction

        Raises:
            TransactionNotFoundError: When transaction is not found or belongs to different user
        """
        pass

    @abstractmethod
    async def delete_bulk(self, transactions: List[Transaction], user_id: UUID) -> None:
        """Delete multiple transactions from repository.

        Args:
            transactions: The transactions to delete
            user_id: The ID of the user who owns the transactions
        """
        pass
