from typing import List
from uuid import UUID

from domain.aggregates.transaction import Transaction
from domain.exceptions import TransactionNotFoundError
from domain.ports.transaction_repository import TransactionRepository

from .database import IN_MEMORY_DATABASE


class InMemoryTransactionRepository(TransactionRepository):
    """In-memory implementation of transaction repository."""

    def __init__(
        self,
        transactions: dict | None = None,
        users: dict | None = None,
        budgets: dict | None = None,
    ):
        """Initialize repository."""
        self._transactions = (
            transactions
            if transactions is not None
            else IN_MEMORY_DATABASE.get_database()["transactions"]
        )
        self._users = (
            users if users is not None else IN_MEMORY_DATABASE.get_database()["users"]
        )
        self._budgets = (
            budgets
            if budgets is not None
            else IN_MEMORY_DATABASE.get_database()["budgets"]
        )

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
        if transaction_id not in self._transactions:
            raise TransactionNotFoundError(str(transaction_id))

        transaction = self._transactions[transaction_id]

        if transaction.user_id != user_id:
            raise TransactionNotFoundError(str(transaction_id))

        return transaction

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
        print(
            f"DEBUG: find_by_budget_id called with budget_id={budget_id}, user_id={user_id}"
        )
        print(f"DEBUG: Available budgets: {list(self._budgets.keys())}")

        if budget_id not in self._budgets:
            print(f"DEBUG: Budget {budget_id} not found in repository")
            return []

        budget_data = self._budgets[budget_id]
        # Check if the budget data is a tuple (version, budget) or just a budget
        if isinstance(budget_data, tuple):
            print(f"DEBUG: Budget data is a tuple: {budget_data}")
            _, budget = budget_data
        else:
            print("DEBUG: Budget data is not a tuple")
            budget = budget_data

        print(f"DEBUG: Retrieved budget: {budget}")

        if budget.user_id != user_id:
            return []

        print(f"DEBUG: Available transactions: {len(self._transactions)}")
        for tx_id, tx in self._transactions.items():
            print(
                f"DEBUG: Transaction {tx_id}: user_id={tx.user_id}, category_id={tx.category_id}"
            )

        # Get category ids for easier debugging and comparison
        category_ids = [category.id for category in budget.categories]
        print(f"DEBUG: Budget category IDs: {category_ids}")

        result = [
            transaction
            for transaction in self._transactions.values()
            if transaction.user_id == user_id
            and any(
                transaction.category_id == category.id for category in budget.categories
            )
        ]

        print(f"DEBUG: Found {len(result)} transactions for budget {budget_id}")
        for tx in result:
            print(
                f"DEBUG: Found matching transaction: {tx.id}, type={tx.transaction_type}, amount={tx.amount}"
            )

        return result

    async def find_by_category_id(
        self, category_id: UUID, user_id: UUID
    ) -> List[Transaction]:
        """Find all transactions for a given category.

        Args:
            category_id: The ID of the category
            user_id: The ID of the user who owns the transactions

        Returns:
            List of transactions
        """
        return [
            transaction
            for transaction in self._transactions.values()
            if transaction.user_id == user_id and transaction.category_id == category_id
        ]

    async def save(self, transaction: Transaction) -> None:
        """Save transaction to repository.

        Args:
            transaction: The transaction to save
        """
        self._transactions[transaction.id] = transaction

    async def delete(self, transaction: Transaction) -> None:
        """Delete transaction from repository.

        Args:
            transaction: The transaction to delete

        Raises:
            TransactionNotFoundError: When transaction is not found or belongs to different user
        """
        if transaction.id not in self._transactions:
            raise TransactionNotFoundError(str(transaction.id))

        del self._transactions[transaction.id]

    async def save_bulk(self, transactions: List[Transaction]) -> None:
        """Save multiple transactions to repository.

        Args:
            transactions: List of transactions to save
        """
        for transaction in transactions:
            self._transactions[transaction.id] = transaction

    async def delete_bulk(self, transactions: List[Transaction]) -> None:
        """Delete multiple transactions from repository.

        Args:
            transactions: The transactions to delete
        """
        for transaction in transactions:
            if transaction.id in self._transactions:
                del self._transactions[transaction.id]
