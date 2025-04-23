from typing import List

from domain.aggregates.transaction import Transaction
from domain.entities.category import Category


class TransactionTransferService:
    """
    Service responsible for transferring transactions between categories.

    This service is part of the domain services layer and handles the business logic
    for transferring transactions from one category to another.
    """

    def transfer_transactions(
        self, transactions: List[Transaction], target_category: Category
    ) -> None:
        """
        Transfers a list of transactions to a target category.

        Args:
            transactions: List of transactions to transfer
            target_category: Target category to which transactions will be transferred

        Returns:
            None
        """
        for transaction in transactions:
            transaction.update_category(target_category.id)
