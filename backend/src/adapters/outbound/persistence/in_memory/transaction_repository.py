from datetime import datetime
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
    ) -> list[Transaction]:
        """Find all transactions for a given budget.

        Args:
            budget_id: The ID of the budget
            user_id: The ID of the user who owns the budget

        Returns:
            List of transactions
        """
        if budget_id not in self._budgets:
            return []

        budget_data = self._budgets[budget_id]
        # Check if the budget data is a tuple (version, budget) or just a budget
        if isinstance(budget_data, tuple):
            _, budget = budget_data
        else:
            budget = budget_data

        if budget.user_id != user_id:
            return []

        result = [
            transaction
            for transaction in self._transactions.values()
            if transaction.user_id == user_id
            and any(
                transaction.category_id == category.id for category in budget.categories
            )
        ]

        return result

    async def find_by_category_id(
        self, category_id: UUID, user_id: UUID
    ) -> list[Transaction]:
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

    async def save_bulk(self, transactions: list[Transaction]) -> None:
        """Save multiple transactions to repository.

        Args:
            transactions: List of transactions to save
        """
        for transaction in transactions:
            self._transactions[transaction.id] = transaction

    async def delete_bulk(self, transactions: list[Transaction]) -> None:
        """Delete multiple transactions from repository.

        Args:
            transactions: The transactions to delete
        """
        for transaction in transactions:
            if transaction.id in self._transactions:
                del self._transactions[transaction.id]

    async def find_by_budget_id_and_date_range(
        self, budget_id: UUID, user_id: UUID, end_date: datetime
    ) -> list[Transaction]:
        """Find transactions by budget ID and date range.

        Args:
            budget_id: The ID of the budget
            user_id: The ID of the user who owns the budget
            end_date: The end date of the date range

        Returns:
            List of transactions
        """
        if budget_id not in self._budgets:
            return []

        budget_data = self._budgets[budget_id]
        # Check if the budget data is a tuple (version, budget) or just a budget
        if isinstance(budget_data, tuple):
            _, budget = budget_data
        else:
            budget = budget_data

        if budget.user_id != user_id:
            return []

        result = [
            transaction
            for transaction in self._transactions.values()
            if transaction.user_id == user_id and transaction.date <= end_date
        ]

        return result
