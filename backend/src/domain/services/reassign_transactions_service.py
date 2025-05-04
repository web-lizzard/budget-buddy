from typing import List

from domain.aggregates.transaction import Transaction
from domain.value_objects import MoveToOtherCategoryTransferPolicyInput


class ReassignTransactionsService:
    """
    Service responsible for reassigning transactions based on a policy.

    This service encapsulates the logic for handling transaction reassignment
    when categories are removed or reorganized in a budget.
    """

    def reassign_transactions(
        self,
        transactions: List[Transaction],
        policy: MoveToOtherCategoryTransferPolicyInput,
    ) -> None:
        """
        Reassigns transactions based on the provided policy.

        Args:
            transactions: List of transactions to reassign
            policy: Policy that determines how transactions should be reassigned

        Returns:
            None
        """
        target_category_id = policy.target_category_id

        if target_category_id is None:
            return

        for transaction in transactions:
            transaction.update_category(target_category_id)
