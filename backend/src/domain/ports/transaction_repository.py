from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from domain.aggregates.transaction import Transaction


class TransactionRepository(ABC):
    """Port for transaction repository operations."""

    @abstractmethod
    async def find_by_id(self, transaction_id: UUID, user_id: UUID) -> Transaction:
        """Find transaction by ID.

        Args:
            transaction_id: ID of the transaction to find
            user_id: ID of the user who owns the transaction

        Returns:
            The transaction if found
        """
        pass

    @abstractmethod
    async def find_by_budget_id(
        self, budget_id: UUID, user_id: UUID
    ) -> List[Transaction]:
        """Find transactions by budget ID.

        Args:
            budget_id: ID of the budget
            user_id: ID of the user who owns the budget

        Returns:
            List of transactions for the given budget
        """
        pass

    @abstractmethod
    async def find_by_category_id(
        self, category_id: UUID, user_id: UUID
    ) -> List[Transaction]:
        """Find transactions by category ID.

        Args:
            category_id: ID of the category
            user_id: ID of the user who owns the transactions

        Returns:
            List of transactions for the given category
        """
        pass

    @abstractmethod
    async def save(self, transaction: Transaction) -> None:
        """Save transaction to repository.

        Args:
            transaction: The transaction to save
        """
        pass

    @abstractmethod
    async def delete(self, transaction: Transaction) -> None:
        """Delete transaction from repository.

        Args:
            transaction: The transaction to delete
            user_id: ID of the user who owns the transaction
        """
        pass

    @abstractmethod
    async def save_bulk(self, transactions: List[Transaction]) -> None:
        """Save multiple transactions to repository.

        Args:
            transactions: List of transactions to save
        """
        pass

    @abstractmethod
    async def delete_bulk(self, transactions: List[Transaction]) -> None:
        """Delete multiple transactions from repository.

        Args:
            transactions: List of transactions to delete
        """
        pass
